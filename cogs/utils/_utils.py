from re import findall
from datetime import datetime
from calendar import monthrange
from requests import Response, get, head
from requests.exceptions import RequestException
from discord.ext import commands
from tiktoken import encoding_for_model
from mimetypes import guess_extension
from magic import Magic  # type: ignore # TODO: Replace with `filetype` library. The overhead of having to deal with two different libraries depending on the OS is making it a bitch to work with.
from PIL import Image
from io import BytesIO
from base64 import b64encode
from pathlib import Path
from subprocess import check_output, STDOUT
from shutil import which
from discord import Guild, User
from os import path, listdir
from string import ascii_letters, digits
from random import choice
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


class FileHandler:
    # TODO: Create convenience class that contain file-related methods and properties
    @overload
    def __init__(self) -> None:
        """
        Initialize the class with no data.

        Args:
            None

        Raises:
            None
        """
        ...

    @overload
    def __init__(self, data: str, /) -> None:
        """
        Initialize the class with data.

        Args:
            data (str): The data to be stored.

        Raises:
            ValueError: If the provided data is not a string.
        """
        ...

    @overload
    def __init__(self, data: bytes, /) -> None:
        """
        Initialize the class with data.

        Args:
            data (bytes): The data to be stored.

        Raises:
            ValueError: If the provided data is not bytes.
        """
        ...

    def __init__(self, data: Optional[str | bytes] = None) -> None:
        """
        Initialize the FileHandler instance.

        Args:
            data (Optional[str | bytes], optional): The data to be stored. Defaults to None.

        Raises:
            ValueError: If the provided data is not a string or bytes.
        """
        if data is not None and not isinstance(data, (str, bytes)):
            raise ValueError("Data must be a string or bytes, if provided.")
        self.data: Optional[Union[str, bytes]] = data

    @staticmethod
    @overload
    def read(file_path: str, /, mode: Literal["r"] = "r") -> str:
        """
        Read the contents of a file.

        Args:
            file_path (str): The path to the file.
            mode (Literal["r"], optional): The mode in which the file should be opened. Defaults to "r".

        Returns:
            str: The contents of the file as a string.

        Raises:
            ValueError: If an invalid mode is provided.
        """
        ...

    @staticmethod
    @overload
    def read(file_path: str, /, mode: Literal["rb"]) -> bytes:
        """
        Read the contents of a file.

        Args:
            file_path (str): The path to the file.
            mode (Literal["rb"]): The mode in which the file should be opened.

        Returns:
            bytes: The contents of the file as bytes.

        Raises:
            ValueError: If an invalid mode is provided.
        """
        ...

    @staticmethod
    def read(file_path: str, /, mode: Literal["r", "rb"] = "r") -> Union[str, bytes]:
        """
        Read the contents of a file.

        Args:
            file_path (str): The path to the file.
            mode (Literal["r", "rb"], optional): The mode in which the file should be opened. Defaults to "r".

        Returns:
            Union[str, bytes]: The contents of the file as a string or bytes.

        Raises:
            ValueError: If an invalid mode is provided.
        """
        with open(file=file_path, mode=mode) as file:
            return file.read()

    @staticmethod
    def write_data(file_path: str, /, data: Union[str, bytes]) -> int:
        """
        Write data to a file.

        The data can be a string or bytes. The mode is determined based on the type of data.

        Args:
            file_path (str): The path and name of the file to write to.
            data (Union[str, bytes]): The data to write to the file.

        Returns:
            int: The number of characters or bytes written to the file.

        Raises:
            ValueError: If the data is not a string or bytes.
        """
        if not isinstance(data, (str, bytes)):
            raise ValueError("Data must be a string or bytes.")
        with open(file=file_path, mode="w" if isinstance(data, str) else "wb") as file:
            return file.write(data)

    def write(self, file_path: str) -> int:
        """
        Write the data stored in the instance to a file.

        Args:
            file_path (str): The path and name of the file to write to.

        Returns:
            int: The number of characters or bytes written to the file.

        Raises:
            ValueError: If no data is set in the instance.
        """
        if self.data is None:
            raise ValueError("No data to write. No data was set in the instance.")
        if not isinstance(self.data, (str, bytes)):
            raise ValueError("Data must be a string or bytes.")
        return self.write_data(file_path, data=self.data)

    @overload
    def convert_to_bytes(self) -> bytes:
        """
        Returns the instance data as bytes. If the data is already bytes, it is returned as is.

        Returns:
            bytes: The converted data in bytes.

        Raises:
            ValueError: If no data is set in the instance.

        """
        ...

    @overload
    def convert_to_bytes(self, data: str, /) -> bytes:
        """
        Converts the given data to bytes. If the data is already bytes, it is returned as is.

        Args:
            data (str): The data to be converted. If not provided, the data set in the instance will be used.

        Returns:
            bytes: The converted data in bytes.

        Raises:
            ValueError: If no data is provided and no data is set in the instance.
            ValueError: If the data is not a string.

        """
        ...

    def convert_to_bytes(self, data: Optional[str] = None) -> bytes:
        """
        Convert data to bytes.

        Args:
            data (Optional[str], optional): The data to be converted. If not provided, the data set in the instance will be used. Defaults to None.

        Returns:
            bytes: The converted data in bytes.

        Raises:
            ValueError: If no data is provided and no data is set in the instance.
            ValueError: If the data is not a string.

        """
        if data is None:
            if self.data is None:
                raise ValueError(
                    "No data to convert. No data was provided and no data was set in the instance."
                )
            if isinstance(self.data, bytes):
                return self.data
            data = self.data
        if isinstance(data, bytes):
            return data
        if not isinstance(data, str):
            raise ValueError("Data must be a string.")
        return data.encode()

    @overload
    def convert_to_str(self) -> str:
        """
        Returns the instance data as a string. If the data is already a string, it is returned as is.

        Returns:
            str: The converted string.

        Raises:
            ValueError: If no data is set in the instance.

        """
        ...

    @overload
    def convert_to_str(self, data: bytes, /) -> str:
        """
        Converts the given data to a string. If the data is already a string, it is returned as is.

        Args:
            data (bytes): The data to be converted.

        Returns:
            str: The converted string.

        Raises:
            ValueError: If no data is provided and no data is set in the instance.
            ValueError: If the data is not of type bytes.

        """
        ...

    def convert_to_str(self, data: Optional[bytes] = None) -> str:
        """
        Convert data to a string.

        Args:
            data (Optional[bytes], optional): The data to be converted. If not provided, the data set in the instance will be used. Defaults to None.

        Returns:
            str: The converted string.

        Raises:
            ValueError: If no data is provided and no data is set in the instance.
            ValueError: If the data is not of type bytes.

        """
        if data is None:
            if self.data is None:
                raise ValueError(
                    "No data to convert. No data was provided and no data was set in the instance."
                )
            if isinstance(self.data, str):
                return self.data
            data = self.data
        if isinstance(data, str):
            return data
        if not isinstance(data, bytes):
            raise ValueError("Data must be bytes.")
        return data.decode()

    def convert_to_base64(self, bytestream: bytes, /) -> str:
        """
        Converts a byte stream to base64 format.

        Args:
            bytestream (bytes): The byte stream to be converted.

        Returns:
            str: The byte stream in base64 format.

        Raises:
            ValueError: If the data is not bytes.

        """
        if not isinstance(bytestream, bytes):
            raise ValueError("Data must be bytes.")
        return b64encode(s=bytestream).decode()

    @overload
    def set_data(self, data: str, /) -> None:
        """
        Set the data in the instance.

        Args:
            data (str): The data to be set.

        Raises:
            ValueError: If the data is not a string.

        """
        ...

    @overload
    def set_data(self, data: bytes, /) -> None:
        """
        Set the data in the instance.

        Args:
            data (bytes): The data to be set.

        Raises:
            ValueError: If the data is not bytes.

        """
        ...

    def set_data(self, data: Union[str, bytes]) -> None:
        """
        Set the data in the instance.

        Args:
            data (Union[str, bytes]): The data to be set.

        Raises:
            ValueError: If the data is not a string or bytes.

        """
        if not isinstance(data, (str, bytes)):
            raise ValueError("Data must be a string or bytes.")
        self.data = data

    @overload
    @staticmethod
    def generate_random_filename(length: int = 10, /) -> str:
        """
        Generates a random filename consisting of alphanumeric characters.

        Args:
            length (int): The length of the filename to generate. Defaults to 10.

        Notes:
            - The generated filename is base62, consisting of uppercase and lowercase letters and digits.

        Returns:
            str: The randomly generated filename.

        """
        ...

    @overload
    @staticmethod
    def generate_random_filename(length: int = 10, *, charset: str) -> str:
        """
        Generates a random filename consisting of characters from the specified charset.

        Args:
            length (int): The length of the filename to generate. Defaults to 10.
            charset (str): The charset to use for generating the filename.

        Returns:
            str: The randomly generated filename.

        """
        ...

    @staticmethod
    def generate_random_filename(
        length: int = 10, *, charset: str = ascii_letters + digits
    ) -> str:
        return "".join(choice(seq=charset) for _ in range(length))

    @staticmethod
    @overload
    def exists(file_path: str, /) -> bool:
        """
        Check if a file exists at the given file path.

        Args:
            file_path (str): The path to the file.

        Returns:
            bool: A boolean indicating whether the file exists.
        """
        ...

    @staticmethod
    @overload
    def exists(file_path: str, /, *, ignore_extension: Literal[True]) -> bool:
        """
        Check if a file exists at the given file path.

        Args:
            file_path (str): The path to the file.
            ignore_extension (bool, optional): Whether to ignore the file extension when checking for existence. Defaults to False.

        Returns:
            bool: A boolean indicating whether the file exists.
        """
        ...

    @staticmethod
    @overload
    def exists(
        file_path: str,
        /,
        *,
        ignore_extension: Literal[True],
        return_extension: Literal[True],
    ) -> tuple[bool, str]:
        """
        Check if a file exists at the given file path.

        Args:
            file_path (str): The path to the file.
            ignore_extension (bool, optional): Whether to ignore the file extension when checking for existence. Defaults to False.
            return_extension (bool, optional): Whether to return the file extension if it exists. This argument is only valid if ignore_extension is True. Defaults to False.

        Returns:
            tuple[bool, str]: If ignore_extension is False, returns a boolean indicating whether the file exists. If ignore_extension is True and return_extension is True, returns a tuple with a boolean indicating whether the file exists and the file extension.

        Raises:
            ValueError: If return_extension is True and ignore_extension is False.

        """
        ...

    @staticmethod
    def exists(
        file_path: str,
        /,
        *,
        ignore_extension: bool = False,
        return_extension: bool = False,
    ) -> Union[bool, tuple[bool, str]]:
        if return_extension and not ignore_extension:
            raise ValueError(
                "ignore_extension must be True if return_extension is True."
            )
        if ignore_extension:
            file: Path = Path(file_path)
            for f in file.parent.iterdir():
                if f.stem == file.stem:
                    file_exists: bool = True
                    if return_extension:
                        return file_exists, f.suffix
                    return file_exists
        else:
            file_exists = path.exists(path=file_path)
        return file_exists

    @staticmethod
    def list_files_in_directory(directory: str, /) -> list[str]:
        """
        Lists all files in a given directory.

        Args:
            directory (str): The directory to list files from.

        Returns:
            list[str]: A list of filenames in the directory.
        """
        return [
            f
            for f in listdir(path=directory)
            if path.isfile(path=path.join(directory, f))
        ]

    @staticmethod
    def list_directories_in_directory(directory: str, /) -> list[str]:
        """
        Lists all directories in a given directory.

        Args:
            directory (str): The directory to list directories from.

        Returns:
            list[str]: A list of directory names in the directory.
        """
        return [
            d for d in listdir(path=directory) if path.isdir(s=path.join(directory, d))
        ]


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


@overload
def convert_to_base64(url: str, /) -> list[str]:
    """
    Converts a file from a URL into a base64 encoded string.

    If the file is a sequence of images (e.g., a GIF), the function retrieves the frames from the GIF and encodes them into a list of base64 formatted strings.

    Args:
        url (str): The URL of the file.

    Returns:
        list[str]: A list containing the base64 encoded string(s) of the file.

    Raises:
        UnsupportedImageFormatError: If the image format is not supported.
        FileSizeError: If the image size exceeds the limit.

    """
    ...


@overload
def convert_to_base64(bytestream: bytes, /) -> list[str]:
    """
    Converts a file from a byte stream into a base64 encoded string.

    If the file is a sequence of images (e.g., a GIF), the function retrieves the frames from the GIF and encodes them into a list of base64 formatted strings.

    Args:
        bytestream (bytes): The byte stream of the file.

    Returns:
        list[str]: A list containing the base64 encoded string(s) of the file.

    Raises:
        UnsupportedImageFormatError: If the image format is not supported.
        FileSizeError: If the image size exceeds the limit.

    """
    ...


def convert_to_base64(**kwargs: Any) -> list[str]:
    url: Optional[str] = kwargs.get("url", None)
    bytestream: Optional[bytes] = kwargs.get("bytestream", None)

    if bytestream:
        stream_is_supported, file_type = stream_is_supported_image(
            bytestream, return_file_type=True
        )
        if not stream_is_supported:
            raise UnsupportedImageFormatError(
                f"File type {file_type} is not supported. Supported image formats are {', '.join(SUPPORTED_IMAGE_FORMATS)}."
            )
        if content_size_is_over_limit(bytestream, OPENAI_IMAGE_SIZE_LIMIT_MB, "MB"):
            raise FileSizeLimitError(
                f"The image exceeds the size limit of {OPENAI_IMAGE_SIZE_LIMIT_MB} MB."
            )
        byte_stream = bytestream

    if url:
        file_info = URLHandler(url)
        file_size = file_info.header_file_size
        file_type = get_mime_type(file_info.header_mime_type)
        if file_type not in SUPPORTED_IMAGE_FORMATS:
            raise UnsupportedImageFormatError(
                f"The image from the URL {url} has {file_type} format, but only {', '.join(SUPPORTED_IMAGE_FORMATS)} is supported."
            )
        if content_size_is_over_limit(file_size, OPENAI_IMAGE_SIZE_LIMIT_MB, "MB"):
            raise FileSizeLimitError(
                f"The image from the URL {url} exceeds the size limit of {OPENAI_IMAGE_SIZE_LIMIT_MB} MB."
            )
        byte_stream = file_info.download_file(
            limit=OPENAI_IMAGE_SIZE_LIMIT_MB, unit="MB"
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
