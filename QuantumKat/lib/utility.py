from subprocess import check_output, STDOUT
from shutil import which
from typing import List, Tuple
from pathlib import Path
from os import environ
from hikari import GatewayBot
from arc import GatewayClient, AutocompleteData, Context

from QuantumKat import loaded_extensions, owner_ids


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


async def get_extensions() -> list[Path]:
    return list(Path("quantum_kat", "plugins").rglob(pattern="*.py"))


async def autocomplete_loaded_extensions_callback(
    data: AutocompleteData[GatewayClient, str]
) -> List[str]:
    return loaded_extensions


async def autocomplete_unloaded_extensions_callback(
    data: AutocompleteData[GatewayClient, str]
) -> List[str]:
    return [
        extension.stem
        for extension in await get_extensions()
        if extension.stem not in loaded_extensions
    ]


async def autocomplete_available_extensions_callback(
    data: AutocompleteData[GatewayClient, str]
) -> List[str]:
    return [extension.stem for extension in await get_extensions()]


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


def is_owner(ctx: Context) -> bool:
    """
    Checks if the user invoking the command is the owner of the bot.

    Args:
        ctx (Context): The context of the command invocation.

    Returns:
        bool: True if the user is the owner of the bot, False otherwise.
    """
    return ctx.author.id in owner_ids
