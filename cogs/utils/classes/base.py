from abc import ABC, abstractmethod
from typing import Any, LiteralString, overload, Union, Literal
from random import choice
from string import ascii_letters, digits
from pathlib import Path
from requests.structures import (
    CaseInsensitiveDict,
)  # Why re-invent the wheel when you can borrow it ;).


BYTE_UNITS = CaseInsensitiveDict(
    data={"B": 1, "KB": 1024, "MB": 1024**2, "GB": 1024**3}
)
CHARSET: LiteralString = ascii_letters + digits


class FileHandlerBase(ABC):
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
