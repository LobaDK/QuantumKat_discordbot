import arc
from typing import Optional, List
from os import execl, name
from sys import executable, argv

from QuantumKat.lib.utility import (
    autocomplete_loaded_extensions_callback,
    autocomplete_unloaded_extensions_callback,
)
from QuantumKat.quantum_kat import arc_client

plugin = arc.GatewayPlugin("control")

extensions: arc.SlashGroup[arc.GatewayClient] = plugin.include_slash_group(
    name="extensions", description="Manage the bot's extensions."
)


@extensions.include
@arc.with_hook(hook=arc.owner_only)
@arc.slash_subcommand(name="load", description="Load an extension.")
async def load_extension(
    ctx: arc.GatewayContext,
    extension: arc.Option[
        str,
        arc.StrParams(
            description="The extension to load",  # noqa: F722
            autocomplete_with=autocomplete_unloaded_extensions_callback,
        ),
    ],
) -> None:
    arc_client.load_extension(path=f"QuantumKat.extensions.{extension}")
    await ctx.respond(content=f"Loaded extension: {extension}")


@extensions.include
@arc.with_hook(hook=arc.owner_only)
@arc.slash_subcommand(name="unload", description="Unload an extension.")
async def unload_extension(
    ctx: arc.GatewayContext,
    extension: arc.Option[
        Optional[str],
        arc.StrParams(
            description="The extension to unload",  # noqa: F722
            autocomplete_with=autocomplete_loaded_extensions_callback,
        ),
    ] = None,
    extensions: arc.Option[
        Optional[str],
        arc.StrParams(
            description="A comma separated list of extensions to unload",  # noqa: F722
        ),
    ] = None,
) -> None:
    if extension is None and extensions is None:
        await ctx.respond(content="Please specify an extension to unload.")
        return

    _extensions: List[str] = []

    if extension and extensions:
        _extensions = [extension.strip() for extension in extensions.split(sep=",")]
        _extensions.append(extension)
    elif extension:
        _extensions.append(extension)
    elif extensions:
        _extensions = [extension.strip() for extension in extensions.split(sep=",")]

    for _extension in _extensions:
        arc_client.unload_extension(path=f"QuantumKat.extensions.{_extension}")

    await ctx.respond(content=f"Unloaded extension(s): {', '.join(_extensions)}")


@extensions.include
@arc.with_hook(hook=arc.owner_only)
@arc.slash_subcommand(name="reload", description="Reload an extension.")
async def reload_extension(
    ctx: arc.GatewayContext,
    extension: arc.Option[
        str,
        arc.StrParams(
            description="The extension to reload",  # noqa: F722
            autocomplete_with=autocomplete_loaded_extensions_callback,
        ),
    ],
) -> None:
    await ctx.respond(content=f"Reloading extension: {extension}")


@extensions.include
@arc.with_hook(hook=arc.owner_only)
@arc.slash_subcommand(name="list", description="List available extensions.")
async def list_extensions(ctx: arc.GatewayContext) -> None:
    await ctx.respond(content="Listing available extensions.")


@plugin.include
@arc.with_hook(hook=arc.owner_only)
@arc.slash_command(name="restart", description="Restart the bot.")
async def restart_command(ctx: arc.GatewayContext) -> None:
    # execl is not supported on Windows
    if name == "nt":
        await ctx.respond(content="Restart is not supported on Windows.")
        return

    await ctx.respond(content="Restarting the bot.")
    execl(executable, executable, *argv)


@arc.loader
def loader(client: arc.GatewayClient) -> None:
    client.add_plugin(plugin=plugin)


@arc.unloader
def unloader(client: arc.GatewayClient) -> None:
    client.remove_plugin(plugin=plugin)
