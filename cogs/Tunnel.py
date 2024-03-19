from traceback import print_exception
from datetime import datetime

from discord.ext import commands
from discord import Client

import logging


class Tunnel(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.logger = logging.getLogger('discord.Tunnel')
        self.logger.setLevel(logging.INFO)
        handler = logging.FileHandler(filename='logs/tunnel.log', encoding='utf-8', mode='a')
        date_format = '%Y-%m-%d %H:%M:%S'
        formatter = logging.Formatter('[{asctime}] [{levelname:<8}] {name}: {message}', datefmt=date_format, style='{')
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if hasattr(ctx.command, 'on_error'):
            return

        cog = ctx.cog
        if cog:
            if cog._get_overridden_method(cog.cog_command_error) is not None:
                return

        ignored_errors = (commands.CommandNotFound, commands.CheckFailure, commands.UnexpectedQuoteError, commands.InvalidEndOfQuotedStringError)

        error = getattr(error, 'original', error)

        if isinstance(error, (commands.NotOwner, commands.PrivateMessageOnly)):
            await ctx.send(f"I'm sorry {ctx.author.mention}. I'm afraid I can't do that.")
        if isinstance(error, ignored_errors):
            return

        else:
            trace = type(error), error, error.__traceback__

            self.logger.error(f'Exception caused in command: {ctx.command}User: {ctx.author}, {ctx.author.id} Message ID: {ctx.message.id} Time: {datetime.now()}')

            print_exception(type(error), error, error.__traceback__)

            owner = Client.get_user(self.bot, self.bot.owner_ids[0])
            await owner.send(f'Exception caused in command: {ctx.command}\nUser: {ctx.author}, {ctx.author.id}\nMessage ID: {ctx.message.id}\nTime: {datetime.now()}\n\n{trace}')

    @commands.Cog.listener()
    async def on_command_completion(self, ctx):
        self.logger.info(f'Command {ctx.command} completed by {ctx.author}, {ctx.author.id} Message ID: {ctx.message.id} Time: {datetime.now()}')

    print('Started Tunnel!')


async def setup(bot):
    await bot.add_cog(Tunnel(bot))
