from abc import ABC, abstractmethod
from base64 import b64encode
from typing import Any, LiteralString, overload, Union, Literal, Optional, Type
from random import choice
from string import ascii_letters, digits
from pathlib import Path
from filetype import guess
from json import dumps, loads
from requests.structures import (
    CaseInsensitiveDict,
)  # Why re-invent the wheel when you can borrow it ;).


BYTE_UNITS = CaseInsensitiveDict(
    data={"B": 1, "KB": 1024, "MB": 1024**2, "GB": 1024**3}
)
CHARSET: LiteralString = ascii_letters + digits


class FileHandlerBase(ABC):
    """
    Base class for file handling operations.

    Contains abstract methods which must be implemented by subclasses.
    The class also contains static methods for common file operations, which can be imported and used directly.
    """

    @abstractmethod
    def __init__(self, data: Any) -> None:
        self._data = data

    @abstractmethod
    def read(self) -> Any: ...

    @abstractmethod
    def write(self, data: Any) -> Any: ...

    @abstractmethod
    def set_data(self, data: Any) -> None: ...

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
    def generate_random_filename(length: int = 10, *, charset: str = CHARSET) -> str:
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
        file: Path = Path(file_path)
        if ignore_extension:
            for f in file.parent.iterdir():
                if f.stem == file.stem:
                    file_exists: bool = True
                    if return_extension:
                        return file_exists, f.suffix
                    return file_exists
        else:
            file_exists = file.exists()
        return file_exists

    @staticmethod
    def list_files_in_directory(directory: str, /) -> list[Path]:
        """
        Lists all files in a given directory.

        Args:
            directory (str): The directory to list files from.

        Returns:
            list[str]: A list of filenames in the directory.
        """
        dir = Path(directory)
        return [f for f in dir.iterdir() if f.is_file()]

    @staticmethod
    def list_directories_in_directory(directory: str, /) -> list[Path]:
        """
        Lists all directories in a given directory.

        Args:
            directory (str): The directory to list directories from.

        Returns:
            list[str]: A list of directory names in the directory.
        """
        dir = Path(directory)
        return [d for d in dir.iterdir() if d.is_dir()]

    @staticmethod
    def list_directory_contents(directory: str, /) -> list[Path]:
        """
        Lists all files and directories in a given directory.

        Args:
            directory (str): The directory to list files and directories from.

        Returns:
            list[str]: A list of filenames and directory names in the directory.
        """
        dir = Path(directory)
        return [f for f in dir.iterdir()]

    @staticmethod
    @overload
    def get_size(file_path: str, /) -> int:
        """
        Retrieves the size of a file.

        Args:
            file_path (str): The path to the file.

        Returns:
            int: The size of the file in bytes.
        """
        ...

    @staticmethod
    @overload
    def get_size(file_path: str, /, unit: str) -> float:
        """
        Retrieves the size of a file.

        Args:
            file_path (str): The path to the file.
            unit (str): The unit to return the size in. Must be one of 'B', 'KB', 'MB', 'GB'.

        Returns:
            float: The size of the file in the specified unit.
        """
        ...

    @staticmethod
    def get_size(file_path: str, /, unit: str = "MB") -> Union[int, float]:
        """
        Retrieves the size of a file.

        Args:
            file_path (str): The path to the file.
            unit (Optional[str], optional): The unit to return the size in. Must be one of 'B', 'KB', 'MB', 'GB'. Defaults to 'MB' (megabytes).

        Returns:
            Union[int, float]: The size of the file in bytes or the specified unit.
        """
        if unit not in BYTE_UNITS:
            raise ValueError("Invalid unit. Must be one of 'B', 'KB', 'MB', 'GB'.")
        file = Path(file_path)
        size: int = file.stat().st_size
        return size / BYTE_UNITS[unit]

    @staticmethod
    @overload
    def guess_file_extension(file_path: str, /) -> Optional[Type]:
        """
        Guesses the file extension of a file based on its contents using the `filetype` library.

        Args:
            file_path (str): The path to the file.

        Returns:
            An instance of the `filetype` library's `Type` class representing the guessed file type, or None if the file type could not be guessed.
        """
        ...

    @staticmethod
    @overload
    def guess_file_extension(*, data: bytes) -> Optional[Type]:
        """
        Guesses the file extension of a byteobject based on its contents using the `filetype` library.

        Args:
            data (bytes): The byteobject to guess the file extension of.

        Returns:
            An instance of the `filetype` library's `Type` class representing the guessed file type, or None if the file type could not be guessed.
        """
        ...

    @staticmethod
    def guess_file_extension(
        file_path: Optional[str] = None, *, data: Optional[bytes] = None
    ) -> Optional[Type]:
        """
        Guesses the file extension of a file or byteobject based on its contents using the `filetype` library.

        Args:
            file_path (Optional[str], optional): The path to the file. Defaults to None.
            data (Optional[bytes], optional): The byteobject to guess the file extension of. Defaults to None.

        Returns:
            An instance of the `filetype` library's `Type` class representing the guessed file type, or None if the file type could not be guessed.

        Raises:
            ValueError: If neither a file path nor data is provided.
        """
        if file_path is None and data is None:
            raise ValueError("Either a file path or data must be provided.")
        if file_path is not None:
            return guess(file_path)
        return guess(obj=data)

    @staticmethod
    def _convert_string_to_bytes(string: str, /) -> bytes:
        """
        Converts a string to bytes.

        Args:
            string (str): The string to convert.

        Returns:
            bytes: The string converted to bytes.
        """
        return string.encode()

    @staticmethod
    def _convert_bytes_to_string(data: bytes, /) -> str:
        """
        Converts bytes to a string.

        Args:
            data (bytes): The bytes to convert.

        Returns:
            str: The bytes converted to a string.
        """
        return data.decode()

    @staticmethod
    def _encode_string_to_base64(string: str, /) -> str:
        """
        Converts a string to base64.

        Args:
            string (str): The string to convert.

        Returns:
            str: The string converted to base64.
        """
        return b64encode(s=string.encode()).decode()

    @staticmethod
    def _encode_bytes_to_base64(data: bytes, /) -> str:
        """
        Converts bytes to base64.

        Args:
            data (bytes): The bytes to convert.

        Returns:
            str: The bytes converted to base64.
        """
        return b64encode(s=data).decode()

    @staticmethod
    def encode_to_json(data: Any, /) -> str:
        """
        Converts data to a JSON string.

        Args:
            data (Any): The data to convert.

        Returns:
            str: The data converted to a JSON string.
        """
        return dumps(obj=data)

    @staticmethod
    def decode_from_json(data: str, /) -> Any:
        """
        Converts a JSON string to data.

        Args:
            data (str): The JSON string to convert.

        Returns:
            Any: The JSON string converted to data.
        """
        return loads(s=data)
