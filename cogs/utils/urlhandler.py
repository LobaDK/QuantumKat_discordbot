from typing import Any, Optional, overload, Union
from requests import head, get, Response, RequestException
from requests.structures import CaseInsensitiveDict

UNITS: dict[str, int] = {"B": 1, "KB": 1024, "MB": 1024**2, "GB": 1024**3}


class FileSizeLimitError(Exception):
    """
    Raised when a file or byte stream exceeds a certain size limit.

    Inherits from base Exception class.
    """

    pass


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
    def __init__(self, *, url: str) -> None:
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
    def __init__(self, *, header: dict) -> None:
        """
        Creates an instance of the URLHandler class.

        Uses the provided header information to expose them as properties for convenience.

        Args:
            header (dict): The header from a URL.
        """
        ...

    def __init__(
        self,
        url: Optional[str] = None,
        header: Union[dict[str, Any], CaseInsensitiveDict, None] = None,
    ) -> None:
        if url and header:
            raise ValueError("Both URL and header cannot be specified.")
        if not url and not header:
            raise ValueError("Either URL or header must be specified.")

        self._url: Optional[str] = None
        self._header: Union[dict[str, Any], CaseInsensitiveDict] = CaseInsensitiveDict()

        if url:
            self._url = url
            try:
                headers: Response = head(url=self._url)
                headers.raise_for_status()
            except RequestException:
                try:
                    # If the header request fails, try using a streamed GET request to get the header
                    headers = get(url=self._url, stream=True)
                    headers.raise_for_status()
                    headers.close()
                except (
                    RequestException
                ) as e:  # If this fails too, assume the file cannot be accessed
                    raise ValueError(
                        f"Could not access the file at {self._url}."
                    ) from e
            self._header.update(headers.headers)
        if header:
            self._header = header

    @property
    def header_file_size(self) -> Optional[int]:
        """
        Returns the size of the file from the 'Content-Length' header.

        If the 'Content-Length' header is not present, returns None.

        Returns:
            int: The size of the file from the 'Content-Length' header, or None if not present.
        """
        try:
            return int(self._header["Content-Length"])
        except KeyError:
            return None

    @property
    def header_mime_type(self) -> Optional[str]:
        """
        Returns the MIME type from the 'Content-Type' header.

        If the 'Content-Type' header is not present, returns None.

        Example:
            'text/html; charset=utf-8' -> 'text/html'

        Returns:
            str: The MIME type from the 'Content-Type' header, or None if not present.
        """
        try:
            return (
                self._header["Content-Type"].split(";")[0]
                if self._header["Content-Type"]
                else None
            )
        except KeyError:
            return None

    @property
    def url(self) -> Optional[str]:
        return self._url

    @url.setter
    def url(self, url: str) -> None:
        self._url = url

    @property
    def header(self) -> Union[dict[str, Any], CaseInsensitiveDict]:
        return self._header

    @header.setter
    def header(self, header: Union[dict[str, Any], CaseInsensitiveDict]) -> None:
        self._header = header

    @overload
    def download(self) -> bytes:
        """
        Downloads the file.

        Returns:
            bytes: The downloaded file.

        Raises:
            ValueError: If the file at the URL cannot be accessed.
        """
        ...

    @overload
    def download(
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

    def download(
        self,
        amount_or_limit: Optional[int] = None,
        unit: Optional[str] = None,
        raise_on_limit: bool = False,
    ) -> bytes:
        if not self._url:
            raise ValueError(
                f"Instance of {self.__class__.__name__} does not have a URL."
            )
        if not amount_or_limit or not unit:
            raise ValueError("Both the amount and unit must be specified.")
        if unit not in UNITS:
            raise ValueError(f"Invalid unit. Choose from {', '.join(UNITS.keys())}.")

        if amount_or_limit:
            calculated_size: int = amount_or_limit * UNITS[unit]

        try:
            with get(url=self._url, stream=True) as response:
                response.raise_for_status()
                if amount_or_limit:
                    data: bytes = b""
                    for chunk in response.iter_content(chunk_size=1024):
                        data += chunk
                        if len(data) >= calculated_size:
                            if raise_on_limit:
                                raise FileSizeLimitError(
                                    f"The file from {self._url} exceeds the specified limit of {amount_or_limit} {unit}."
                                )
                            break
                else:
                    data = response.content
        except RequestException as e:
            raise ValueError(f"Could not access the file at {self._url}.") from e
        return data
