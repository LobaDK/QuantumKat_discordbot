from re import findall
from datetime import datetime
from calendar import monthrange
from requests import get
from discord.ext import commands
from tiktoken import encoding_for_model
from mimetypes import guess_extension
from magic import Magic
from PIL import Image
from io import BytesIO
from base64 import b64encode
from pathlib import Path

from QuantumKat import discord_helper

SUPPORTED_IMAGE_FORMATS = [
    ".png",
    ".jpeg",
    ".jpg",
    ".webp",
    # only static gifs are supported
    ".gif",
]


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


def get_image_as_base64(url: str) -> list[str]:
    """
    Retrieves an image from a given URL and returns it as a base64 encoded string.

    Args:
        url (str): The URL of the image to retrieve.

    Returns:
        list[str]: A list containing the base64 encoded string of the image. If the image is an animated GIF, the list
        will contain the base64 encoded frames of the GIF.

    Note:
        Refer to `utils.SUPPORTED_IMAGE_FORMATS` for the supported image formats.

    Raises:
        UnsupportedImageFormat: If the image format is not supported.
    """
    request = get(url)
    request.raise_for_status()

    if not verify_stream_is_supported_image(request.content):
        raise UnsupportedImageFormatError(
            f"The image from the URL <{url}> has {get_file_type(request.content)} format, but only {', '.join(SUPPORTED_IMAGE_FORMATS)} is supported."
        )
    if not verify_stream_is_under_limit(request.content, 20, "MB"):
        raise FileSizeLimitError(
            f"The image from the URL <{url}> is {round(len(request.content) / 1024**2, 2)} MB, which exceeds the 20 MB limit."
        )
    if is_animated_gif(request.content):
        return get_base64_encoded_frames_from_gif(request.content)

    return [encode_byte_stream_to_base64(request.content)]


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


def encode_byte_stream_to_base64(byte_stream: bytes) -> str:
    """
    Encodes a given byte stream to a base64 string.

    Parameters:
    - byte_stream (bytes): The byte stream to encode.

    Returns:
    - str: The base64 encoded string.
    """
    return b64encode(byte_stream).decode("utf-8")


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


def verify_stream_is_under_limit(
    file_path_or_stream: str | bytes, limit: int, unit: str
) -> bool:
    """
    Checks if a file or byte stream is over a certain size limit.

    Parameters:
    - file_path_or_stream (str | bytes): The file path or byte stream to check the size of.
    - limit (int): The size limit.
    - unit (str): The unit of the size limit ('B', 'KB', 'MB', 'GB').

    Returns:
    - bool: True if the file or byte stream is over the limit, False otherwise.
    """
    unit = unit.upper()
    units = {"B": 1, "KB": 1024, "MB": 1024**2, "GB": 1024**3}

    if unit not in units:
        raise ValueError("Invalid unit. Choose from 'B', 'KB', 'MB', 'GB'.")

    limit_in_bytes = limit * units[unit]
    if isinstance(file_path_or_stream, str):
        file_size = get_file_size(file_path_or_stream)
    else:
        file_size = len(file_path_or_stream)

    return file_size <= limit_in_bytes


def verify_stream_is_supported_image(data: bytes) -> bool:
    """
    Verifies that the given stream is a supported image format.

    Parameters:
    - data (bytes): The stream to verify.

    Returns:
    - bool: True if the stream is a supported image format, False otherwise.
    """
    file_type = get_file_type(data)
    return file_type in SUPPORTED_IMAGE_FORMATS


def get_urls_in_message(message: str) -> list:
    """
    Retrieves the URLs in a given message.

    Parameters:
    - message (str): The message to retrieve URLs from.

    Returns:
    - list: A list of URLs found in the message.
    """
    return findall(
        r"http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+\.[a-zA-Z]{2,6}(?:/[^\s]*)?",
        message,
    )


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
    if not discord_helper.is_dm(ctx):
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
