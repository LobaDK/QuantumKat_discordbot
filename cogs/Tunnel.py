from traceback import print_exception
from datetime import datetime

from discord.ext import commands
from discord import Client
from helpers import LogHelper


class Tunnel(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

        self.logger = bot.log_helper.create_logger(
            LogHelper.TimedRotatingFileAndStreamHandler(
                logger_name="Tunnel", log_file="logs/tunnel/Tunnel.log"
            )
        )

    @commands.Cog.listener()
    async def on_command_error(
        self, ctx: commands.Context, error: commands.CommandError
    ):
        if hasattr(ctx.command, "on_error"):
            return

        cog = ctx.cog
        if cog:
            if cog._get_overridden_method(cog.cog_command_error) is not None:
                return

        ignored_errors = (
            commands.CommandNotFound,
            commands.CheckFailure,
            commands.UnexpectedQuoteError,
            commands.InvalidEndOfQuotedStringError,
            commands.CommandOnCooldown,
            commands.MissingRequiredArgument,
            commands.MemberNotFound,
            commands.UserNotFound,
        )

        error = getattr(error, "original", error)

        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(
                f"Missing required argument: {error.param.name}. Please check your command and try again."
            )

        if isinstance(error, (commands.MemberNotFound, commands.UserNotFound)):
            await ctx.send("User not found. Please check your command and try again.")

        if isinstance(error, (commands.NotOwner, commands.PrivateMessageOnly)):
            await ctx.send(
                f"I'm sorry {ctx.author.mention}. I'm afraid I can't do that."
            )
        if isinstance(error, commands.CommandOnCooldown):
            minutes, seconds = divmod(error.retry_after, 60)
            minutes = int(minutes)
            seconds = int(seconds)
            try:
                await ctx.send(
                    f"Command on cooldown. Please wait {minutes:02d}:{seconds:02d} before trying again."
                )
            except Exception:
                self.logger.error(
                    "Exception ocurred while sending cooldown message.", exc_info=True
                )
        if isinstance(error, ignored_errors):
            return

        else:
            trace = type(error), error, error.__traceback__

            self.logger.error(
                f"Exception caused in command: {ctx.command}User: {ctx.author}, {ctx.author.id} Message ID: {ctx.message.id} Time: {datetime.now()}"
            )

            print_exception(type(error), error, error.__traceback__)

            owner = Client.get_user(self.bot, self.bot.owner_ids[0])
            await owner.send(
                f"Exception caused in command: {ctx.command}\nUser: {ctx.author}, {ctx.author.id}\nMessage ID: {ctx.message.id}\nTime: {datetime.now()}\n\n{trace}"
            )

    @commands.Cog.listener()
    async def on_command_completion(self, ctx: commands.Context):
        self.logger.info(
            f"Command {ctx.command} completed by {ctx.author}, {ctx.author.id} Message ID: {ctx.message.id} Time: {datetime.now()}"
        )

    print("Started Tunnel!")


async def setup(bot: commands.Bot):
    await bot.add_cog(Tunnel(bot))
