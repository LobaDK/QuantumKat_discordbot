import arc

from QuantumKat.lib.utility import (
    autocomplete_loaded_extensions_callback,
    autocomplete_unloaded_extensions_callback,
)

plugin = arc.GatewayPlugin("control")

extensions: arc.SlashGroup[arc.GatewayClient] = plugin.include_slash_group(
    name="extensions", description="Manage the bot's extensions."
)


@extensions.include
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
    await ctx.respond(content=f"Loading extension: {extension}")


@extensions.include
@arc.slash_subcommand(name="unload", description="Unload an extension.")
async def unload_extension(
    ctx: arc.GatewayContext,
    extension: arc.Option[
        str,
        arc.StrParams(
            description="The extension to unload",  # noqa: F722
            autocomplete_with=autocomplete_loaded_extensions_callback,
        ),
    ],
) -> None:
    await ctx.respond(content=f"Unloading extension: {extension}")


@extensions.include
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
@arc.slash_subcommand(name="list", description="List available extensions.")
async def list_extensions(ctx: arc.GatewayContext) -> None:
    await ctx.respond(content="Listing available extensions.")


@arc.loader
def loader(client: arc.GatewayClient) -> None:
    client.add_plugin(plugin=plugin)


@arc.unloader
def unloader(client: arc.GatewayClient) -> None:
    client.remove_plugin(plugin=plugin)
