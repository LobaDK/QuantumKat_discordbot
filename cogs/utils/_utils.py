from re import findall
from datetime import datetime
from calendar import monthrange
from requests import Response, get, head
from requests.exceptions import RequestException
from discord.ext import commands
from tiktoken import encoding_for_model
from PIL import Image
from io import BytesIO
from base64 import b64encode
from subprocess import check_output, STDOUT
from shutil import which
from discord import Guild, User
from os import path, listdir
from typing import Literal, overload, Optional, Union, Any

from cogs.utils._logger import system_logger

SUPPORTED_IMAGE_FORMATS: list[str] = [
    ".png",
    ".jpeg",
    ".jpg",
    ".webp",
    ".gif",
]

UNITS: dict[str, int] = {"B": 1, "KB": 1024, "MB": 1024**2, "GB": 1024**3}

DIRECT_MEDIA_TYPES: list[str] = ["image", "video", "audio"]
EXTRACT_MEDIA_TYPES: list[str] = ["text", "application"]

OPENAI_IMAGE_SIZE_LIMIT_MB = 20


class URLHandler:
    """
    A convenience class with methods and properties to make handling URLs easier.

    This class provides properties to access the file size and MIME type from the header information of a URL, as well as methods to download files from URLs.

    Attributes:
        url (str): The URL of the file.
        header (dict): The header information from the URL.

    Methods:
        download_file(url: str) -> bytes: Downloads a file from the specified URL.
        download_file(url: str, amount_or_limit: int, unit: str) -> bytes: Downloads a defined amount of data from the specified URL.
        download_file(url: str, amount_or_limit: int, unit: str, raise_exception: bool = True) -> bytes: Downloads a file from the specified URL and raises an exception if the file exceeds the specified limit.

    Properties:
        header_file_size: Returns the size of the file from the 'Content-Length' header.
        header_mime_type: Returns the MIME type from the 'Content-Type' header.
        get_header_mime_type: Attempts to download the first 1 KB of the file and determine the MIME type.
    """

    @overload
    def __init__(self, url: str, /) -> None:
        """
        Creates an instance of the URLHandler class.

        Automatically retrieves the header information from the URL, and exposes them as properties for convenience.

        Args:
            url (str): The URL of the file.

        Raises:
            ValueError: If the file at the specified URL cannot be accessed.
        """
        ...

    @overload
    def __init__(self, header: dict, /) -> None:
        """
        Creates an instance of the URLHandler class.

        Uses the provided header information to expose them as properties for convenience.

        Args:
            header (dict): The header from a URL.
        """
        ...

    def __init__(self, **kwargs: Any) -> None:
        url: Optional[str] = kwargs.get("url", None)
        header: Optional[dict] = kwargs.get("header", None)
        if url and header:
            raise ValueError("Both URL and header cannot be specified.")
        if not url and not header:
            raise ValueError("Either URL or header must be specified.")

        self.url: str = None
        self.header: dict = None

        if url:
            self.url = url
            try:
                headers: Response = head(url=self.url)
                headers.raise_for_status()
            except RequestException:
                try:
                    # If the header request fails, try using a streamed GET request to get the header
                    headers: Response = get(url=self.url, stream=True)
                    headers.raise_for_status()
                    headers.close()
                except (
                    RequestException
                ) as e:  # If this fails too, assume the file cannot be accessed
                    raise ValueError(f"Could not access the file at {self.url}.") from e
            self.header = headers.headers
        if header:
            self.header = header

    @property
    def header_file_size(self) -> int:
        """
        Returns the size of the file from the 'Content-Length' header.

        If the 'Content-Length' header is not present, returns None.

        Returns:
            int: The size of the file from the 'Content-Length' header, or None if not present.
        """
        try:
            return int(self.header["Content-Length"])
        except KeyError:
            return None

    @property
    def header_mime_type(self) -> str:
        """
        Returns the MIME type from the 'Content-Type' header.

        If the 'Content-Type' header is not present, returns None.

        Returns:
            str: The MIME type from the 'Content-Type' header, or None if not present.
        """
        try:
            return self.header["Content-Type"].split(";")[0]
        except KeyError:
            return None

    @overload
    def download_file(self) -> bytes:
        """
        Downloads the file.

        Returns:
            bytes: The downloaded file.

        Raises:
            ValueError: If the file at the URL cannot be accessed.
        """
        ...

    @overload
    def download_file(
        self, amount_or_limit: int, unit: str, /, *, raise_on_limit: bool = False
    ) -> bytes:
        """
        Downloads the file.

        Stops when either the file is fully downloaded or the specified amount/limit is reached.

        Args:
            amount_or_limit (int): The amount of data to download. Gets treated as a limit if raise_on_limit is True.
            unit (str): The unit of the amount to download. Must be one of 'B', 'KB', 'MB', 'GB'.
            raise_on_limit (bool, optional): Whether to raise an exception if the file exceeds the specified limit. Defaults to False.

        Returns:
            bytes: The downloaded file.

        Raises:
            ValueError: If the unit is invalid or either the unit or amount is missing.
            FileSizeLimitError: If the file exceeds the specified limit.
            ValueError: If the file at the specified URL cannot be accessed.
        """
        ...

    def download_file(
        self,
        amount_or_limit: Optional[int] = None,
        unit: Optional[str] = None,
        raise_on_limit: bool = False,
    ) -> bytes:
        if not amount_or_limit or not unit:
            raise ValueError("Both the amount and unit must be specified.")
        if unit not in UNITS:
            raise ValueError(f"Invalid unit. Choose from {', '.join(UNITS.keys())}.")

        if amount_or_limit:
            calculated_size: int = amount_or_limit * UNITS[unit]

        try:
            with get(url=self.url, stream=True) as response:
                response.raise_for_status()
                if amount_or_limit:
                    data: Literal[b""] = b""
                    for chunk in response.iter_content(chunk_size=1024):
                        data += chunk
                        if len(data) >= calculated_size:
                            if raise_on_limit:
                                raise FileSizeLimitError(
                                    f"The file from {self.url} exceeds the specified limit of {amount_or_limit} {unit}."
                                )
                            break
                else:
                    data = response.content
        except RequestException as e:
            raise ValueError(f"Could not access the file at {self.url}.") from e
        return data


class FileSizeLimitError(Exception):
    """
    Raised when a file or byte stream exceeds a certain size limit.

    Inherits from base Exception class.
    """

    pass


class UnsupportedImageFormatError(Exception):
    """
    Raised when an unsupported image format is encountered.

    Inherits from base Exception class.
    """

    pass


# Set the model encoding for tiktoken
encoding = encoding_for_model("gpt-4o")


def get_bot_header() -> dict:
    """
    Returns the header for the bot.

    Returns:
        dict: The header for the bot.
    """
    contact_email: str = get_field_from_1password(
        reference="op://Programming and IT security/QuantumKat Discord bot/Contact Email"
    )
    return {
        "User-Agent": f"QuantumKat Discord Bot/1.0; GitHub: https://github.com/LobaDK/QuantumKat-discordbot; Contact Email: {contact_email}"
    }


def guess_download_type(url: str) -> str:
    """
    Guesses the download type based on the Content-Type header from the URL.

    Args:
        url (str): The URL of the file or page.

    Returns:
        str: The download type, which can be one of the following:
            - "direct" if the file can be directly downloaded.
            - "extract" if the media is embedded in a webpage and needs to be extracted.
            - "unknown" if the download type cannot be determined.

    """
    file_info = URLHandler(url)
    type, subtype = tuple(iterable=file_info.header_mime_type.split(sep="/"))
    if type in DIRECT_MEDIA_TYPES:
        return "direct"
    if type in EXTRACT_MEDIA_TYPES:
        return "extract"
    return "unknown"


def get_field_from_1password(reference: str) -> str:
    """
    Retrieves the value of a field from 1Password and returns it as a string.

    Requires the 1Password CLI to be installed and configured.

    Args:
        reference (str): The reference to the field in 1Password.

    Returns:
        str: The value in the field retrieved from 1Password.

    Raises:
        CalledProcessError: If the 1Password CLI command fails. The exception will include an `output` attribute containing the output of the command.
        EnvironmentError: If the 1Password CLI is not installed.
    """
    if which(cmd="op") is None:
        raise EnvironmentError("The 1Password CLI is not installed. Please install it.")
    token: str = (
        check_output(args=["op", "read", reference], stderr=STDOUT)
        .decode(encoding="utf-8")
        .strip()
    )
    return token


def strip_embed_disabler(url: str) -> str:
    """
    Strips the greater-than and less-than symbols from a given URL.

    Args:
        url (str): The URL to strip them from.

    Returns:
        str: The URL with the greater-than and less-than symbols removed.
    """
    return url.replace("<", "").replace(">", "")


def get_base64_encoded_frames_from_gif(byte_stream: bytes) -> list:
    """
    Retrieves the frames from a GIF image and returns them as a list of base64 encoded strings.

    Parameters:
    - byte_stream (bytes): The GIF image to retrieve frames from.

    Returns:
    - list: A list of base64 encoded strings representing the frames of the GIF image.
    """
    img = Image.open(BytesIO(byte_stream))
    base64_frames = []
    try:
        while True:
            buffer = BytesIO()
            img.save(buffer, format="jpg")  # convert image to bytes
            img_bytes = buffer.getvalue()
            img_b64 = b64encode(img_bytes).decode()  # convert bytes to base64 string
            base64_frames.append(img_b64)
            img.seek(img.tell() + 1)  # move to next frame
    except EOFError:
        pass  # end of sequence

    return base64_frames


def encode_byte_stream_to_base64(byte_stream: bytes) -> list[str]:
    """
    Encodes a byte stream to base64 format.

    If the byte stream is an animated GIF, the function retrieves the frames from the GIF and encodes them into a list of base64 formatted strings.

    Args:
        byte_stream (bytes): The byte stream to be encoded.

    Returns:
        list[str]: A list of base64 encoded strings.

    """
    if is_animated_gif(byte_stream):
        return get_base64_encoded_frames_from_gif(byte_stream)
    return [b64encode(byte_stream).decode()]


def is_animated_gif(image: bytes) -> bool:
    """
    Determines if a given image is an animated GIF.

    Parameters:
    - image (bytes): The image to determine if it is an animated GIF.

    Returns:
    - bool: True if the image is an animated GIF, False otherwise.
    """
    try:
        img = Image.open(BytesIO(image))
        return getattr(img, "is_animated", False)
    except IOError:
        return False


def content_size_is_over_limit(
    file_path_or_stream_or_int: str | bytes | int, limit: int, unit: str
) -> bool:
    """
    Checks if a file or byte stream is over a certain size limit.

    Parameters:
    - file_path_or_stream_or_int (str | bytes | int): The file path, byte stream, or integer to check the size of.
    - limit (int): The size limit.
    - unit (str): The unit of the size limit ('B', 'KB', 'MB', 'GB').

    Returns:
    - bool: True if the file or byte stream is over the size limit, False otherwise.
    """
    unit = unit.upper()

    if unit not in UNITS:
        raise ValueError(f"Invalid unit. Choose from {', '.join(UNITS.keys())}.")

    limit_in_bytes = limit * UNITS[unit]
    if isinstance(file_path_or_stream_or_int, str):
        file_size = get_file_size(file_path_or_stream_or_int)
    if isinstance(file_path_or_stream_or_int, bytes):
        file_size = len(file_path_or_stream_or_int)
    if isinstance(file_path_or_stream_or_int, int):
        file_size = file_path_or_stream_or_int

    return file_size > limit_in_bytes


@overload
def stream_is_supported_image(
    data: bytes,
    /,
    *,
    return_file_type: Literal[
        False
    ] = False,  # Using Literal helps mypy and the IDE decide which overload to infer to.
) -> bool:
    """
    Verifies that the given stream is a supported image format.

    Parameters:
    - data (bytes): The stream to verify.
    - return_file_type (bool): Whether to also return the file type of the stream. Defaults to False.

    Returns:
    - bool: True if the stream is a supported image format, False otherwise.
    """
    ...


@overload
def stream_is_supported_image(
    data: bytes,
    /,
    *,
    return_file_type: Literal[True],
) -> tuple[bool, str]:
    """
    Verifies that the given stream is a supported image format.

    Parameters:
    - data (bytes): The stream to verify.
    - return_file_type (bool): Whether to also return the file type of the stream.

    Returns:
    - tuple: A tuple containing a boolean indicating if the stream is a supported image format and the file type of the stream.
    """
    ...


def stream_is_supported_image(
    data: bytes, /, *, return_file_type: bool = False
) -> Union[bool, tuple[bool, str]]:
    file_type = guess_file_extension(data)
    if return_file_type:
        return file_type in SUPPORTED_IMAGE_FORMATS, file_type
    return file_type in SUPPORTED_IMAGE_FORMATS


def get_urls_in_message(message: str) -> list:
    """
    Retrieves the URLs in a given message.

    Parameters:
    - message (str): The message to retrieve URLs from.

    Returns:
    - list: A list of URLs found in the message.
    """
    return findall(r"https?://[^\s]+", message)


def calculate_tokens(user_message: str, system_message: str) -> int:
    """
    Calculates the number of tokens in a given user message.

    Parameters:
    - user_message (str): The user message to calculate tokens for.
    - system_message (str): The system message to calculate tokens for.

    Returns:
    - int: The number of tokens in the user message.
    """
    messages = [user_message, system_message]
    tokens = 0
    for message in messages:
        tokens += len(encoding.encode(message))
    return tokens


def get_usage(session_key: str) -> dict:
    """
    Retrieves the usage statistics for the OpenAI API key.

    Parameters:
    - session_key (str): The OpenAI API key to retrieve usage statistics for.

    Returns:
        dict: A dictionary containing the usage statistics for the OpenAI API key.
    """
    month = datetime.now().month
    month = f"{month:02}"
    year = datetime.now().year
    last_day = monthrange(year, int(month))[1]
    response = get(
        f"https://api.openai.com/dashboard/billing/usage?end_date={year}-{month}-{last_day}&start_date={year}-{month}-01",
        headers={"Authorization": f"Bearer {session_key}"},
    )
    response.raise_for_status()
    return response.json()


def get_server_id_and_name(ctx: commands.Context) -> tuple:
    """
    Retrieves the server ID and name from the context object.

    Args:
        ctx (commands.Context): The context object representing the invocation context of the command.

    Returns:
        tuple: A tuple containing the server ID and name.
    """
    if not DiscordHelper.is_dm(ctx):
        server_id = ctx.guild.id
        server_name = ctx.guild.name
    else:
        server_id = ctx.channel.id
        server_name = "DM"
    return server_id, server_name


def split_message_by_sentence(message: str) -> list:
    """
    Splits a given message by sentence, into multiple messages with a maximum length of 2000 characters.

    Args:
        message (str): The message to be split into sentences.

    Returns:
        list: A list of sentences, each with a maximum length of 2000 characters.
    """
    sentences = message.split(". ")
    current_length = 0
    messages = []
    current_message = ""

    for sentence in sentences:
        if current_length + len(sentence) + 1 > 2000:  # +1 for the period
            messages.append(current_message)
            current_length = 0
            current_message = ""

        current_message += sentence + ". "
        current_length += len(sentence) + 1

    if current_message:  # Any leftover sentence
        messages.append(current_message)

    return messages


def get_mime_type(mime_type: str) -> str:
    """
    Returns the file extension corresponding to the given MIME type.

    Parameters:
    - mime_type (str): The MIME type for which to determine the file extension.

    Returns:
    - str: The file extension corresponding to the given MIME type.
    """
    return guess_extension(mime_type)


def guess_file_extension(
    file_path_or_stream: str | bytes, split_mime: bool = False
) -> str:
    """
    Guesses the file extension of the given file or byte stream based on its MIME type.

    Parameters:
    - file_path_or_stream (str | bytes): The filename or byte stream to determine the file type of.
      If this is a string representing a filename, the function uses `Magic.from_file()`
      to determine the file type. If this is a byte stream, the function uses
      `Magic.from_buffer()` to determine the file type.
    - split_mime (bool): Whether to return the MIME type as a split tuple (type, subtype), instead of the file extension.
      Defaults to False.

    Returns:
    - str | tuple: The file extension of the given file, or a tuple (type, subtype) if split_mime is True.

    Examples:
    - guess_file_extension("image.png") -> ".png"
    - guess_file_extension(b"image data") -> ".png"
    - guess_file_extension("image.png", split_mime=True) -> ("image", "png")
    - guess_file_extension(b"image data", split_mime=True) -> ("image", "png")
    """
    mime = Magic(mime=True)
    if isinstance(file_path_or_stream, bytes):
        mime_type = mime.from_buffer(file_path_or_stream)
    else:
        mime_type = mime.from_file(file_path_or_stream)
    if split_mime:
        return tuple(mime_type.split("/"))
    else:
        file_extension = get_mime_type(mime_type)
        return file_extension


class DiscordHelper:
    """
    A helper class for Discord-related operations.

    This class provides various methods to check different conditions related to Discord contexts and users.

    Attributes:
        None

    Methods:
        is_dm(ctx): Checks if the given context is a direct message (DM).
        is_bot_owner(ctx): Checks if the author of the given context is the owner of the bot.
        is_guild_owner(ctx): Checks if the author of the given context is the owner of the server.
        is_admin(ctx): Checks if the author of the given context has administrator permissions in the guild.
        is_mod(ctx): Checks if the author of the command has moderator permissions.
        is_privileged_user(ctx): Checks if the user is a privileged user.
        first_load_cogs(bot, cog_dir): Loads initial extensions (cogs) for the bot.
        user_in_guild(user, guild): Checks if a user is a member of a guild.
    """

    @staticmethod
    def is_dm(ctx: commands.Context) -> bool:
        """
        Checks if the given context is a direct message (DM).

        Args:
            ctx (discord.ext.commands.Context): The context object representing the command invocation.

        Returns:
            bool: True if the context is a DM, False otherwise.
        """
        return ctx.guild is None

    @staticmethod
    def is_bot_owner(ctx: commands.Context) -> bool:
        """
        Checks if the author of the given context is the owner of the bot.

        Args:
            ctx (discord.ext.commands.Context): The context object representing the command invocation.

        Returns:
            bool: True if the author is the owner of the bot, False otherwise.
        """
        return ctx.author.id in ctx.bot.owner_ids

    @staticmethod
    def is_guild_owner(ctx: commands.Context) -> bool:
        """
        Checks if the author of the given context is the owner of the server.

        Args:
            ctx (discord.ext.commands.Context): The context object representing the command invocation.

        Returns:
            bool: True if the author is the owner of the server, False otherwise.
        """
        return ctx.author.id == ctx.guild.owner_id

    @staticmethod
    def is_admin(ctx: commands.Context) -> bool:
        """
        Checks if the author of the given context has administrator permissions in the guild.

        Args:
            ctx (discord.ext.commands.Context): The context object representing the command invocation.

        Returns:
            bool: True if the author has administrator permissions, False otherwise.
        """
        return ctx.author.guild_permissions.administrator

    @staticmethod
    def is_mod(ctx: commands.Context) -> bool:
        """
        Checks if the author of the command has moderator permissions.

        Args:
            ctx (discord.ext.commands.Context): The context object representing the command invocation.

        Returns:
            bool: True if the author has moderator permissions, False otherwise.
        """
        # Since there is no official "moderator" role, we can instead check for some common moderator-only permissions.
        mod_perms = [
            "kick_members",
            "ban_members",
            "manage_messages",
            "manage_channels",
        ]
        return any([getattr(ctx.author.guild_permissions, perm) for perm in mod_perms])

    @staticmethod
    def is_privileged_user(ctx: commands.Context) -> bool:
        """
        Checks if the user is a privileged user.

        A privileged user is defined as a bot owner, guild owner, administrator, or moderator.

        Args:
            ctx: The context object representing the current command invocation.

        Returns:
            True if the user is a privileged user, False otherwise.
        """
        return (
            DiscordHelper.is_bot_owner(ctx)
            or DiscordHelper.is_guild_owner(ctx)
            or DiscordHelper.is_admin(ctx)
            or DiscordHelper.is_mod(ctx)
        )

    @staticmethod
    async def first_load_cogs(bot: commands.Bot, cog_dir: str):
        """
        Loads initial extensions (cogs) for the bot.

        This method iterates over the files in the specified `cog_dir` directory and loads the valid Python files
        as extensions for the bot.

        Args:
            bot: The bot instance.
            cog_dir (str): The directory path where the cogs are located.

        Returns:
            None
        """
        initial_extensions = []
        for cog in listdir(cog_dir):
            if cog.endswith(".py"):
                system_logger.info(f"Loading cog: {cog}")
                initial_extensions.append(f"cogs.{path.splitext(cog)[0]}")

        for extension in initial_extensions:
            await bot.load_extension(extension)

    @staticmethod
    def user_in_guild(user: User, guild: Guild) -> bool:
        """
        Checks if a user is a member of a guild.

        Args:
            user (discord.User): The user object to check.
            guild (discord.Guild): The guild object to check.

        Returns:
            bool: True if the user is a member of the guild, False otherwise.
        """
        return guild.get_member(user.id) is not None
