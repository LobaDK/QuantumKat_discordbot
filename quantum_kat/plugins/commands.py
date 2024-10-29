import lightbulb

loader = lightbulb.Loader()


@loader.command()
class ping(lightbulb.SlashCommand, name="ping", description="Ping the bot."):
    @lightbulb.invoke
    async def ping(self, ctx: lightbulb.Context) -> None:
        await ctx.respond(content="Pong!")
