from subprocess import STDOUT, check_output
from shutil import which
from typing import Tuple
from os import environ
from arc import GatewayClient
from hikari import GatewayBot


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
    if which(cmd="op") is None:
        raise EnvironmentError("The 1Password CLI is not installed. Please install it.")
    token: str = (
        check_output(args=["op", "read", reference], stderr=STDOUT)
        .decode(encoding="utf-8")
        .strip()
    )
    return token


def create_bot() -> Tuple[GatewayBot, GatewayClient]:
    """
    Creates and configures a GatewayBot and a GatewayEnabledClient.

    The function retrieves the token type from the environment variables, constructs a reference
    to fetch the token from 1Password, and initializes a GatewayBot with the retrieved token.
    It then creates a GatewayEnabledClient using the bot and sets the default enabled guilds.

    Returns:
        Tuple[GatewayBot, GatewayEnabledClient]: A tuple containing the
        initialized GatewayBot (Hikari) and GatewayEnabledClient (Lightbulb) instances.
    """
    token_type: str = environ.get("TOKEN_TYPE", default="Main")
    references: str = (
        f"op://Programming and IT security/QuantumKat Discord bot/{token_type} token"
    )

    quantum_bot = GatewayBot(token=get_field_from_1password(reference=references))

    arc_client = GatewayClient(
        app=quantum_bot, default_enabled_guilds=[665680289510588447]
    )

    return quantum_bot, arc_client
