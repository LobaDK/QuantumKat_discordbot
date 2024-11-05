from typing import List, Any
from pathlib import Path
from arc import GatewayClient, AutocompleteData, Context, HookResult

from QuantumKat.quantum_kat import arc_client


async def get_extensions() -> list[Path]:
    return list(Path("quantum_kat", "plugins").rglob(pattern="*.py"))


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
    return ctx.author.id == arc_client.application.owner.id


def is_owner_hook(ctx: Context[Any]) -> HookResult:
    """
    A hook function to check if the context's user is the owner.

    Args:
        ctx (Context[Any]): The context of the command being executed.

    Returns:
        HookResult: A result object indicating whether to abort the operation.
    """
    if not is_owner(ctx=ctx):
        return HookResult(abort=True)
    return HookResult(abort=False)
