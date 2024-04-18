import time
from helpers import LogHelper
from logging import DEBUG
import discord
from discord.ext import commands
from functools import wraps
from textwrap import dedent

from sql import database
from sql import crud, schemas

TIMEOUT_IN_SECONDS = 60


class ToSAgreementView(discord.ui.View):
    def __init__(self, ctx: commands.Context):
        super().__init__(timeout=TIMEOUT_IN_SECONDS)
        self.value = None
        self.ctx: commands.Context = ctx
        self.message: discord.Message = None

    async def interaction_check(
        self, interaction: discord.Interaction[discord.Client]
    ) -> bool:
        if interaction.user.id != self.ctx.author.id:
            await interaction.response.send_message(
                "You can't interact with this message.", ephemeral=True
            )
            return False
        return True

    async def on_timeout(self) -> None:
        await self.message.delete()
        await self.ctx.reply(
            "You took too long to respond. Please run the command again.",
            silent=True,
        )
        self.value = False
        self.stop()

    @discord.ui.button(label="Yes", style=discord.ButtonStyle.green)
    async def confirm(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        await interaction.response.defer()
        await self.message.delete()
        self.value = True
        self.stop()

    @discord.ui.button(label="No", style=discord.ButtonStyle.red)
    async def declined(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        await interaction.response.defer()
        await self.message.delete()
        self.value = False
        self.stop()


class ToSChangeView(discord.ui.View):
    def __init__(self, ctx: commands.Context):
        super().__init__(timeout=TIMEOUT_IN_SECONDS)
        self.value = 0
        self.ctx: commands.Context = ctx
        self.message: discord.Message = None

    async def interaction_check(
        self, interaction: discord.Interaction[discord.Client]
    ) -> bool:
        if interaction.user.id != self.ctx.author.id:
            await interaction.response.send_message(
                "You can't interact with this message.", ephemeral=True
            )
            return False
        return True

    async def on_timeout(self) -> None:
        await self.message.delete()
        await self.ctx.reply(
            "You took too long to respond. Please run the command again.",
            silent=True,
        )
        self.value = False
        self.stop()

    @discord.ui.button(label="Yes", style=discord.ButtonStyle.grey)
    async def confirm(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        await interaction.response.defer()
        await self.message.delete()
        self.value = 1
        self.stop()

    @discord.ui.button(label="Yes, and delete my data", style=discord.ButtonStyle.red)
    async def delete_data(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        await interaction.response.defer()
        await self.message.delete()
        self.value = 2
        self.stop()

    @discord.ui.button(label="No", style=discord.ButtonStyle.green)
    async def declined(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        await interaction.response.defer()
        await self.message.delete()
        self.value = 0
        self.stop()


logger = LogHelper().create_logger(
    LogHelper.TimedRotatingFileAndStreamHandler(
        logger_name="Timer", log_file="logs/timer/Timer.log", file_log_level=DEBUG
    )
)


def requires_tos_acceptance(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        ctx: commands.Context = args[1]
        user = await crud.get_user(
            database.AsyncSessionLocal, schemas.User.Get(user_id=ctx.author.id)
        )
        if user is None or not user.agreed_to_tos:
            invoked_with = (
                f"`?{ctx.invoked_with}`"
                if ctx.command.name != "tos"
                else "additional commands"
            )
            view = ToSAgreementView(ctx)
            view.message = await ctx.send(
                dedent(
                    f"""
                    {'This command' if ctx.command.name != 'tos' else 'Some commands'} needs to store the following basic data to function:

                    - Your Discord username and user ID

                    Furthermore, the following commands store additional data when used:

                    - `?chat`|`?sharedchat`: Stores the message you send to the bot, the bot's response, and whether the chat is shared with other users.

                    I do not store normal chat messages. Abuse of any commands will result in a ban from using the bot.

                    By clicking "Yes", you agree to the above terms and can use {invoked_with}. By clicking "No", you will not be able to use {invoked_with}. You can change your decision at any time by running the `?tos` command or a command that requires ToS acceptance.
                    """
                ),
                view=view,
            )
            await view.wait()
            if view.value is True:
                if user is None:
                    await crud.add_user(
                        database.AsyncSessionLocal,
                        schemas.User.Add(
                            user_id=ctx.author.id,
                            username=ctx.author.name,
                            agreed_to_tos=True,
                        ),
                    )
                else:
                    await crud.edit_user_tos(
                        database.AsyncSessionLocal,
                        schemas.User.SetTos(user_id=ctx.author.id, agreed_to_tos=True),
                    )
                return await func(*args, **kwargs)
            else:
                return
        elif user.agreed_to_tos and ctx.command.name == "tos":
            view = ToSChangeView(ctx)
            view.message = await ctx.send(
                dedent(
                    """
                    You have already agreed to the Terms of Service. Would you like to change your decision and opt out?
                    """
                ),
                view=view,
            )
            await view.wait()
            if view.value == 1:
                await crud.edit_user_tos(
                    database.AsyncSessionLocal,
                    schemas.User.SetTos(user_id=ctx.author.id, agreed_to_tos=False),
                )
                await ctx.reply(
                    "You have opted out of the Terms of Service.", silent=True
                )
            elif view.value == 2:
                await crud.delete_all_user_data(
                    database.AsyncSessionLocal,
                    schemas.User.Delete(user_id=ctx.author.id),
                )
                await ctx.reply(
                    "You have opted out of the Terms of Service and your data has been deleted.",
                    silent=True,
                )
            else:
                return
        else:
            return await func(*args, **kwargs)

    return wrapper


def timeit(func):
    """
    A decorator that measures the execution time of a function.

    Args:
        func: The function to be decorated.

    Returns:
        The decorated function.

    """

    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = func(*args, **kwargs)
        end = time.perf_counter()
        elapsed_time = (end - start) * 1_000_000  # Convert to microseconds
        logger.debug(
            f"CRUD function {func.__name__} took {round(elapsed_time, 5)} microseconds to execute."
        )
        return result

    return wrapper
