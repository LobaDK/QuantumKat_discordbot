from os import listdir, path
from random import choice
from string import ascii_letters, digits
from typing import Optional, Union, Literal, overload
from base64 import b64encode
from filetype import guess  # type: ignore
from filetype.types import Type  # type: ignore
from pathlib import Path
from json import dumps, loads

UNITS: dict[str, int] = {"B": 1, "KB": 1024, "MB": 1024**2, "GB": 1024**3}


class FileHandler:
    """
    A convenience class that contains file-related methods and properties.

    This class provides various instance and static methods for file and data handling. Most of which are overloaded to help hint their usage.
    When initializing the class, you can provide data as a string or bytes. The data can be set or changed later using the `set_data` method.
    By setting the data, most data-related methods can be used without providing the data as an argument. If no data is set, the data must be provided as an argument.
    The user is expected to handle exceptions raised by the methods and the underlying functions they use.

    Attributes:
        data (Optional[Union[str, bytes]]): The data stored in the instance.

    Properties:
        ```python
        @property
        def as_bytes: bytes:
        @property
        def as_string: str:
        @property
        def as_base64: str:
        ```

    Instance Methods:
        ```python
        def set_data(data: Union[str, bytes]) -> None:
        def size(unit: Optional[str] = None) -> Union[int, float]:
        def guess_extension() -> Optional[Type]:
        def write(file_path: str) -> int:
        ```

    Static Methods:
        ```python
        def read_data(file_path: str, /, mode: Literal["r", "rb"] = "r") -> Union[str, bytes]:
        def write_data(file_path: str, /, data: Union[str, bytes]) -> int:
        def convert_to_bytes(data: str, /) -> bytes:
        def convert_to_string(data: bytes, /) -> str:
        def encode_to_base64(data: Union[str, bytes]) -> str:
        def encode_to_json(data: dict, /) -> str:
        def decode_json(data: str, /) -> dict:
        def generate_random_filename(length: int = 10, *, charset: str = ascii_letters + digits) -> str:
        def exists(file_path: str, /, *, ignore_extension: bool = False, return_extension: bool = False) -> Union[bool, tuple[bool, str]]:
        def list_files_in_directory(directory: str, /) -> list[str]:
        def list_directories_in_directory(directory: str, /) -> list[str]:
        def get_size(file_path: str, /, unit: Optional[str] = None) -> Union[int, float]:
        def guess_file_extension(file_path: Optional[str] = None, *, data: Optional[bytes] = None) -> Optional[Type]:
        ```

    Raises:
        ValueError: If the provided data is not a string or bytes.

    Returns:
        None
    """

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
    def read_data(file_path: str, /, mode: Literal["r"] = "r") -> str:
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
    def read_data(file_path: str, /, mode: Literal["rb"]) -> bytes:
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
    def read_data(
        file_path: str, /, mode: Literal["r", "rb"] = "r"
    ) -> Union[str, bytes]:
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

    @staticmethod
    def convert_to_bytes(data: str, /) -> bytes:
        """
        Converts a string to bytes.

        Args:
            data (str): The string to be converted.

        Returns:
            bytes: The converted bytes.
        """
        return data.encode()

    @property
    def as_bytes(self) -> bytes:
        """
        Returns the instance data as bytes. If the data is already bytes, it is returned as is.

        Returns:
            bytes: The converted bytes.

        Raises:
            ValueError: If no data is set in the instance.

        """
        if self.data is None:
            raise ValueError("No data to convert. No data was set in the instance.")
        if isinstance(self.data, bytes):
            return self.data
        return self.convert_to_bytes(self.data)

    @staticmethod
    def convert_to_string(data: bytes, /) -> str:
        """
        Converts bytes to a string.

        Args:
            data (bytes): The bytes to be converted.

        Returns:
            str: The converted string.
        """
        return data.decode()

    @property
    def as_string(self) -> str:
        """
        Returns the instance data as a string. If the data is already a string, it is returned as is.

        Returns:
            str: The converted string.

        Raises:
            ValueError: If no data is set in the instance.

        """
        if self.data is None:
            raise ValueError("No data to convert. No data was set in the instance.")
        if isinstance(self.data, str):
            return self.data
        return self.convert_to_string(self.data)

    @staticmethod
    @overload
    def encode_to_base64(data: str, /) -> str:
        """
        Encodes a string to base64.

        Args:
            data (str): The string to be encoded.

        Returns:
            str: The base64 encoded string.
        """
        ...

    @staticmethod
    @overload
    def encode_to_base64(data: bytes, /) -> str:
        """
        Encodes bytes to base64.

        Args:
            data (bytes): The bytes to be encoded.

        Returns:
            str: The base64 encoded string.
        """
        ...

    @staticmethod
    def encode_to_base64(data: Union[str, bytes]) -> str:
        """
        Encodes data to base64.

        Args:
            data (Union[str, bytes]): The data to be encoded.

        Returns:
            str: The base64 encoded string.
        """
        if isinstance(data, str):
            return b64encode(data.encode()).decode()
        return b64encode(data).decode()

    @property
    def as_base64(self) -> str:
        """
        Returns the instance data as base64 encoded string.

        Returns:
            str: The base64 encoded string.

        Raises:
            ValueError: If no data is set in the instance.

        """
        if self.data is None:
            raise ValueError("No data to encode. No data was set in the instance.")
        return self.encode_to_base64(self.data)

    @staticmethod
    def encode_to_json(data: dict, /) -> str:
        """
        Encodes a dictionary to a JSON string.

        Args:
            data (dict): The dictionary to be encoded.

        Returns:
            str: The JSON encoded string.
        """
        return dumps(obj=data)

    @staticmethod
    def decode_json(data: str, /) -> dict:
        """
        Decodes a JSON string to a dictionary.

        Args:
            data (str): The JSON string to be decoded.

        Returns:
            dict: The decoded dictionary.
        """
        return loads(s=data)

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
    def get_size(file_path: str, /, unit: Optional[str] = None) -> Union[int, float]:
        """
        Retrieves the size of a file.

        Args:
            file_path (str): The path to the file.
            unit (Optional[str], optional): The unit to return the size in. Must be one of 'B', 'KB', 'MB', 'GB'. Defaults to None.

        Returns:
            Union[int, float]: The size of the file in bytes or the specified unit.
        """
        if unit not in UNITS:
            raise ValueError("Invalid unit. Must be one of 'B', 'KB', 'MB', 'GB'.")
        size: int = path.getsize(filename=file_path)
        return size / UNITS[unit]

    @overload
    def size(self) -> int:
        """
        Retrieves the size of the data stored in the instance.

        Returns:
            int: The size of the data in bytes.

        Raises:
            ValueError: If no data is set in the instance.
        """
        ...

    @overload
    def size(self, unit: str) -> float:
        """
        Retrieves the size of the data stored in the instance.

        Args:
            unit (str): The unit to return the size in. Must be one of 'B', 'KB', 'MB', 'GB'.

        Returns:
            float: The size of the data in the specified unit.

        Raises:
            ValueError: If no data is set in the instance.
        """
        ...

    def size(self, unit: Optional[str] = None) -> Union[int, float]:
        """
        Retrieves the size of the data stored in the instance.

        Args:
            unit (Optional[str], optional): The unit to return the size in. Must be one of 'B', 'KB', 'MB', 'GB'. Defaults to None.

        Returns:
            Union[int, float]: The size of the data in bytes or the specified unit.

        Raises:
            ValueError: If no data is set in the instance.
        """
        if unit not in UNITS:
            raise ValueError("Invalid unit. Must be one of 'B', 'KB', 'MB', 'GB'.")
        if self.data is None:
            raise ValueError(
                "No data to get the size of. No data was set in the instance."
            )
        size: int = len(self.data)
        return size / UNITS[unit]

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

    def guess_extension(self) -> Optional[Type]:
        """
        Guesses the file extension of the data stored in the instance using the `filetype` library.

        If the data is a string, it is encoded to bytes before guessing the extension.

        Returns:
            An instance of the `filetype` library's `Type` class representing the guessed file type, or None if the file type could not be guessed.
        """
        if self.data is None:
            raise ValueError(
                "No data to guess the extension of. No data was set in the instance."
            )
        if isinstance(self.data, str):
            return self.guess_file_extension(data=self.as_bytes)
        return self.guess_file_extension(data=self.data)
