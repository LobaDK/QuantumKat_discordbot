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


class ToSView(discord.ui.View):
    def __init__(self, ctx: commands.Context):
        super().__init__(timeout=TIMEOUT_IN_SECONDS)
        self.value = None
        self.ctx = ctx

    async def disable_buttons(self):
        for item in self.children:
            item.disabled = True

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
        await self.disable_buttons()
        await self.message.edit(view=self)
        await self.message.edit(
            content=f"{self.message.content}\n\nTimed out waiting for user response. Please try again.",
        )
        self.value = False
        self.stop()

    @discord.ui.button(label="Yes", style=discord.ButtonStyle.green)
    async def confirm(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        await self.disable_buttons()
        await self.message.edit(view=self)
        await interaction.response.defer()
        self.value = True
        self.stop()

    @discord.ui.button(label="No", style=discord.ButtonStyle.red)
    async def declined(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        await self.disable_buttons()
        await self.message.edit(view=self)
        await interaction.response.defer()
        self.value = False
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
            view = ToSView(ctx)
            view.message = await ctx.send(
                dedent(
                    f"""
                    This command needs to store the following basic data to function:

                    - Your Discord username and user ID

                    Furthermore, the following commands store additional data when used:

                    - `?chat`|`?sharedchat`: Stores the message you send to the bot, the bot's response, and whether the chat is shared with other users.

                    I do not store normal chat messages.

                    By clicking "Yes", you agree to the above terms and can use ?`{ctx.invoked_with}`. By clicking "No", you will not be able to use ?`{ctx.invoked_with}`. You can change your decision at any time by running the `?tos` command or a command that requires ToS acceptance.
                    """
                ),
                view=view,
            )
            await view.wait()
            if view.value is None:
                return
            if view.value:
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
                    await crud.update_user(
                        database.AsyncSessionLocal,
                        schemas.User.SetTos(user_id=ctx.author.id, agreed_to_tos=True),
                    )
                return await func(*args, **kwargs)
            else:
                return

    return wrapper


def timeit(func):
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
