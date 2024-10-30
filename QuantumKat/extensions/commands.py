import arc

plugin = arc.GatewayPlugin("commands")


@plugin.include
@arc.slash_command(name="ping", description="Check if the bot is alive.")
async def ping_command(ctx: arc.GatewayContext) -> None:
    await ctx.respond(content="Pong!")


@arc.loader
def loader(client: arc.GatewayClient) -> None:
    client.add_plugin(plugin=plugin)


@arc.unloader
def unloader(client: arc.GatewayClient) -> None:
    client.remove_plugin(plugin=plugin)
