from typing import Optional, Union, overload
from filetype import guess
from filetype.types import Type

from cogs.utils.classes.base import FileHandlerBase


class FileHandlerWithStringData(FileHandlerBase):
    def __init__(self, data: str, file_path: Optional[str] = None) -> None:
        """
        Initialize the FileHandler object.

        Args:
            data (str): The data to be processed.
            file_path (Optional[str], optional): The "default" file path to be used when reading/writing data. Can be set later using the file_path property. Defaults to None.
        """
        super().__init__(data=data)
        self._file_path: str = file_path

    @property
    def as_bytes(self) -> bytes:
        """
        Converts the data stored in the object to bytes.

        Returns:
            bytes: The data converted to bytes.
        """
        return self._convert_string_to_bytes(self._data)

    @property
    def as_base64(self) -> str:
        """
        Converts the data to a base64 encoded string.

        Returns:
            str: The base64 encoded string representation of the data.
        """
        return self._encode_string_to_base64(self._data)

    @property
    def file_path(self) -> str:
        return self._file_path

    @file_path.setter
    def file_path(self, file_path: str) -> None:
        self._file_path = file_path

    def read(self, file_path: Optional[str] = None) -> str:
        """
        Reads the contents of a file.

        Args:
            file_path (str, optional): The path of the file to read. If not provided, the default file path will be used.

        Returns:
            str: The contents of the file.

        """
        if file_path is None:
            file_path = self._file_path
        return self._read_data_from_file(file_path=file_path)

    def write(self, file_path: Optional[str] = None) -> int:
        """
        Writes the data to a file.

        Args:
            file_path (Optional[str]): The path of the file to write the data to. If not provided, the default file path will be used.

        Returns:
            int: The number of bytes written to the file.
        """
        if file_path is None:
            file_path = self._file_path
        return self._write_data_to_file(data=self._data, file_path=file_path)

    @overload
    def set_data(self, data: str) -> "FileHandlerWithStringData":
        """
        Set the data for the FileHandler object.

        Parameters:
            data (str): The data to be set.

        Returns:
            FileHandlerWithStringData: The updated FileHandler object.

        """
        ...

    @overload
    def set_data(self, data: bytes) -> "FileHandlerWithBytesData":
        """
        Set the data for the FileHandler object.

        Parameters:
        - data (bytes): The data to be set.

        Returns:
        - FileHandlerWithBytesData: The updated FileHandler object.

        """

    def set_data(
        self, data: Union[str, bytes]
    ) -> Union["FileHandlerWithBytesData", "FileHandlerWithStringData"]:
        """
        Sets the data for the file handler.

        Parameters:
            data (Union[str, bytes]): The data to be set. Can be either a string or bytes.

        Returns:
            Union[FileHandlerWithBytesData, FileHandlerWithStringData]: An instance of either FileHandlerWithBytesData or FileHandlerWithStringData, depending on the type of data provided.
        """
        return (
            FileHandlerWithBytesData(data=data)
            if isinstance(data, bytes)
            else FileHandlerWithStringData(data=data)
        )

    def _read_data_from_file(self, file_path: str) -> str:
        with open(file=file_path, mode="r") as file:
            return file.read()

    def _write_data_to_file(self, data: str, file_path: str) -> int:
        with open(file=file_path, mode="w") as file:
            return file.write(data)


class FileHandlerWithBytesData(FileHandlerBase):
    def __init__(self, data: bytes, file_path: Optional[str] = None) -> None:
        """
        Initialize the FileHandler object.

        Args:
            data (bytes): The data to be stored in the FileHandler object.
            file_path (Optional[str], optional): The "default" file path to be used when reading/writing data. Can be set later using the file_path property. Defaults to None.
        """
        super().__init__(data=data)
        self._file_path: str = file_path

    @property
    def as_string(self) -> str:
        """
        Converts the data stored in the object to a string representation.

        Returns:
            str: The string representation of the data.
        """
        return self._convert_bytes_to_string(self._data)

    @property
    def as_base64(self) -> str:
        """
        Converts the data to a base64 encoded string.

        Returns:
            str: The base64 encoded string representation of the data.
        """
        return self._encode_bytes_to_base64(self._data)

    @property
    def file_path(self) -> str:
        return self._file_path

    @file_path.setter
    def file_path(self, file_path: str) -> None:
        self._file_path = file_path

    def read(self, file_path: Optional[str] = None) -> bytes:
        """
        Reads the contents of a file.

        Args:
            file_path (Optional[str]): The path of the file to read. If not provided, the default file path will be used.

        Returns:
            bytes: The contents of the file.

        """
        if file_path is None:
            file_path = self._file_path
        return self._read_data_from_file(file_path=file_path)

    def write(self, file_path: Optional[str] = None) -> int:
        """
        Writes the data to a file.

        Args:
            file_path (Optional[str]): The path of the file to write the data to. If not provided, the default file path will be used.

        Returns:
            int: The number of bytes written to the file.
        """
        if file_path is None:
            file_path = self._file_path
        return self._write_data_to_file(data=self._data, file_path=file_path)

    def guess_extension(self) -> Optional[Type]:
        """
        Guesses the file extension based on the data stored in the object.

        Returns:
            Optional[Type]: The guessed file extension, or None if it cannot be determined.
        """
        return self._guess_file_extension(data=self._data)

    @overload
    def set_data(self, data: str) -> "FileHandlerWithStringData":
        """
        Set the data for the FileHandler object.

        Parameters:
            data (str): The data to be set.

        Returns:
            FileHandlerWithStringData: The updated FileHandler object.

        """
        ...

    @overload
    def set_data(self, data: bytes) -> "FileHandlerWithBytesData":
        """
        Set the data for the FileHandler object.

        Parameters:
        - data (bytes): The data to be set for the FileHandler.

        Returns:
        - FileHandlerWithBytesData: The updated FileHandler object.

        """

    def set_data(
        self, data: Union[str, bytes]
    ) -> Union["FileHandlerWithBytesData", "FileHandlerWithStringData"]:
        return (
            FileHandlerWithBytesData(data=data)
            if isinstance(data, bytes)
            else FileHandlerWithStringData(data=data)
        )

    def _read_data_from_file(self, file_path: str) -> bytes:
        with open(file=file_path, mode="rb") as file:
            return file.read()

    def _write_data_to_file(self, data: bytes, file_path: str) -> int:
        with open(file=file_path, mode="wb") as file:
            return file.write(data)

    def _guess_file_extension(self, data: bytes) -> Optional[Type]:
        return guess(obj=data)
