from typing import List, Any
from pathlib import Path
from arc import GatewayClient, AutocompleteData, Context

from QuantumKat.quantum_kat import arc_client


async def get_extensions() -> list[Path]:
    return list(Path("QuantumKat", "extensions").rglob(pattern="*.py"))


async def autocomplete_loaded_extensions_callback(
    data: AutocompleteData[GatewayClient, str]
) -> List[str]:
    return [
        extension
        for extension in arc_client.plugins.keys()
        if data.focused_value in extension
    ]


async def autocomplete_unloaded_extensions_callback(
    data: AutocompleteData[GatewayClient, str]
) -> List[str]:
    return [
        extension.stem
        for extension in await get_extensions()
        if extension.stem not in arc_client.plugins.keys()
        and data.focused_value in extension.stem
    ]


async def autocomplete_available_extensions_callback(
    data: AutocompleteData[GatewayClient, str]
) -> List[str]:
    return [extension.stem for extension in await get_extensions()]


def is_owner(ctx: Context[Any]) -> bool:
    """
    Checks if the user invoking the command is the owner of the bot.

    Args:
        ctx (Context): The context of the command invocation.

    Returns:
        bool: True if the user is the owner of the bot, False otherwise.
    """
    return ctx.author.id in arc_client.owner_ids
