from re import findall
from datetime import datetime
from calendar import monthrange
from requests import get, head
from requests.exceptions import RequestException
from discord.ext import commands
from tiktoken import encoding_for_model
from mimetypes import guess_extension
from magic import Magic
from PIL import Image
from io import BytesIO
from base64 import b64encode
from pathlib import Path
from subprocess import check_output, STDOUT
from shutil import which
from discord import Guild, User
from os import path, listdir

from cogs.utils._logger import system_logger

SUPPORTED_IMAGE_FORMATS = [
    ".png",
    ".jpeg",
    ".jpg",
    ".webp",
    ".gif",
]

UNITS = {"B": 1, "KB": 1024, "MB": 1024**2, "GB": 1024**3}

OPENAI_IMAGE_SIZE_LIMIT_MB = 20


class FileInfoFromURL:
    def __init__(self, url: str):
        """
        Initialize a new instance of the class.

        Args:
            url (str): The URL of the file.

        Raises:
            ValueError: If the file cannot be accessed.

        """
        self.url = url
        try:
            header = head(url)
            header.raise_for_status()
        except RequestException:
            try:
                # If the header request fails, try using a streamed GET request to get the header
                header = get(url, stream=True)
                header.raise_for_status()
                header.close()
            except (
                RequestException
            ) as e:  # If this fails too, assume the file cannot be accessed
                raise ValueError(f"Could not access the file at {url}.") from e
        self.header = header.headers

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

    @property
    def get_header_mime_type(self) -> str:
        """
        Attempts to download the first 1 KB of the file and determine the MIME type.

        Returns:
            str: The MIME type of the header.
        """
        file = download_file(self.url, amount_or_limit=1, unit="KB")
        return get_file_type(file)


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


def get_field_from_1password(reference: str) -> str:
    """
    Retrieves the value of a field from 1Password and returns it as a string.

    Requires the 1Password CLI to be installed and configured.

    Args:
        reference (str): The reference to the token in 1Password.

    Returns:
        str: The token retrieved from 1Password.

    Raises:
        CalledProcessError: If the 1Password CLI command fails. The exception will include an `output` attribute containing the output of the command.
        EnvironmentError: If the 1Password CLI is not installed.
    """
    if which("op") is None:
        raise EnvironmentError("The 1Password CLI is not installed. Please install it.")
    token = (
        check_output(["op", "read", reference], stderr=STDOUT).decode("utf-8").strip()
    )
    return token


def download_file(
    url: str,
    amount_or_limit: int = None,
    unit: str = None,
    raise_exception: bool = False,
) -> bytes:
    """
    Downloads a file from the specified URL.

    Args:
        url (str): The URL of the file to download.
        amount_or_limit (int, optional): The maximum amount of data to download, specified in the given unit. Defaults to None.
        unit (str, optional): The unit of the amount to download. Must be one of 'B', 'KB', 'MB', 'GB'. Defaults to None.
        raise_exception (bool, optional): Whether to raise an exception if the downloaded file exceeds the specified limit. Defaults to False.

    Returns:
        bytes: The downloaded file.

    Raises:
        ValueError: If the unit is invalid or if the unit is provided without specifying the amount.
        FileSizeError: If the downloaded file exceeds the specified limit and raise_exception is True.
        ValueError: If the file at the specified URL cannot be accessed.
    """
    if amount_or_limit and unit not in ["B", "KB", "MB", "GB"]:
        if unit:
            raise ValueError("Invalid unit. Choose from 'B', 'KB', 'MB', 'GB'.")
        else:
            raise ValueError("Unit must be specified if amount is provided.")
    if unit and not amount_or_limit:
        raise ValueError("Amount must be specified if unit is provided.")

    original_amount_or_limit = amount_or_limit

    if amount_or_limit and unit:
        amount_or_limit = amount_or_limit * UNITS[unit]

    try:
        with get(url, stream=True) as response:
            response.raise_for_status()
            if amount_or_limit:
                data = b""
                for chunk in response.iter_content(chunk_size=1024):
                    data += chunk
                    if len(data) >= amount_or_limit:
                        if raise_exception:
                            raise FileSizeLimitError(
                                f"The image from {url} exceeds the specified limit of {original_amount_or_limit} {unit}."
                            )
            else:
                data = response.content
    except RequestException as e:
        raise ValueError(f"Could not access the file at {url}.") from e
    return data


def strip_embed_disabler(url: str) -> str:
    """
    Strips the greater-than and less-than symbols from a given URL.

    Args:
        url (str): The URL to strip them from.

    Returns:
        str: The URL with the greater-than and less-than symbols removed.
    """
    return url.replace("<", "").replace(">", "")


def get_image_as_base64(url_or_byte_stream: str | bytes) -> list[str]:
    """
    Converts an image from a URL or byte stream into a base64 encoded string.

    Args:
        url_or_byte_stream (str | bytes): The URL or byte stream of the image.

    Returns:
        list[str]: A list containing the base64 encoded string of the image.

    Raises:
        UnsupportedImageFormatError: If the image format is not supported.
        FileSizeError: If the image size exceeds the limit.

    """
    byte_stream = None

    if isinstance(url_or_byte_stream, bytes):
        stream_is_supported, file_type = stream_is_supported_image(
            url_or_byte_stream, return_file_type=True
        )
        if not stream_is_supported:
            raise UnsupportedImageFormatError(
                f"File type {file_type} is not supported. Supported image formats are {', '.join(SUPPORTED_IMAGE_FORMATS)}."
            )
        if content_size_is_over_limit(
            url_or_byte_stream, OPENAI_IMAGE_SIZE_LIMIT_MB, "MB"
        ):
            raise FileSizeLimitError(
                f"The image exceeds the size limit of {OPENAI_IMAGE_SIZE_LIMIT_MB} MB."
            )
        byte_stream = url_or_byte_stream

    if isinstance(url_or_byte_stream, str):
        file_info = FileInfoFromURL(url_or_byte_stream)
        file_size = file_info.header_file_size
        file_type = get_mime_type(
            file_info.header_mime_type or file_info.get_header_mime_type
        )
        if file_type not in SUPPORTED_IMAGE_FORMATS:
            raise UnsupportedImageFormatError(
                f"The image from the URL {url_or_byte_stream} has {file_type} format, but only {', '.join(SUPPORTED_IMAGE_FORMATS)} is supported."
            )
        if content_size_is_over_limit(file_size, OPENAI_IMAGE_SIZE_LIMIT_MB, "MB"):
            raise FileSizeLimitError(
                f"The image from the URL {url_or_byte_stream} exceeds the size limit of {OPENAI_IMAGE_SIZE_LIMIT_MB} MB."
            )
        byte_stream = download_file(
            url_or_byte_stream, amount_or_limit=20, unit="MB", raise_exception=True
        )

    return encode_byte_stream_to_base64(byte_stream)


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


def get_file_size(file_path: str) -> int:
    """
    Retrieves the size of a file.

    Parameters:
    - file_path (str): The path to the file to get the size of.

    Returns:
    - int: The size of the file in bytes.
    """
    return Path(file_path).stat().st_size


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


def stream_is_supported_image(
    data: bytes, return_file_type: bool = False
) -> bool | tuple[bool, str]:
    """
    Verifies that the given stream is a supported image format.

    Parameters:
    - data (bytes): The stream to verify.
    - return_file_type (bool): Whether to also return the file type of the stream.

    Returns:
    - bool: True if the stream is a supported image format, False otherwise. Returned if `return_file_type` is False.
    - tuple: A tuple containing a boolean indicating if the stream is a supported image format and the file type of the stream. Returned if `return_file_type` is True.
    """
    file_type = get_file_type(data)
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


def get_file_type(file_path_or_stream: str | bytes) -> str:
    """
    Retrieves the file type of a given filename.

    Parameters:
    - file_path_or_stream (str | bytes): The filename or byte stream to determine the file type of.
      If this is a string representing a filename, the function uses `Magic.from_file()`
      to determine the file type. If this is a byte stream, the function uses
      `Magic.from_buffer()` to determine the file type.

    Returns:
    - str: The file extension of the given file.
    """
    mime = Magic(mime=True)
    if isinstance(file_path_or_stream, bytes):
        mime_type = mime.from_buffer(file_path_or_stream)
    else:
        mime_type = mime.from_file(file_path_or_stream)
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
