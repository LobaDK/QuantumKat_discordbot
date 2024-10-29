from subprocess import check_output, STDOUT
from shutil import which


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
