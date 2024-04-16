from random import choice
import discord
from textwrap import dedent

from discord.ext import commands
from helpers import LogHelper

from sql import schemas, crud
from sql.database import AsyncSessionLocal

TIMEOUT_IN_SECONDS = 60


class ViewTest(discord.ui.View):
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


class Control(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.locations = ["universe", "reality", "dimension", "timeline"]

        self.logger = bot.log_helper.create_logger(
            LogHelper.TimedRotatingFileAndStreamHandler(
                logger_name="Control", log_file="logs/control/Control.log"
            )
        )

    async def get_permissions(self, guild: discord.Guild) -> list[str]:
        permissions = []
        for permission in guild.me.guild_permissions:
            if permission[1] is True:
                permissions.append(permission[0])
        return permissions

    @commands.command(
        aliases=["serverownerlist", "SOL"],
        brief=(
            "(Bot owner only, limited to DM's) Fetches a "
            "list of servers the bot is in."
        ),
        description=(
            "Fetches a list of servers the bot is in, "
            "including the ID of the server, the owner "
            "username and the ID of the owner. "
            "Supports no arguments. Limited to bot "
            "owner, and DM's for privacy."
        ),
    )
    @commands.is_owner()
    @commands.dm_only()
    async def ServerOwnerList(self, ctx: commands.Context):
        # TODO: Remove discriminator since Discord phased it out
        servers_and_owners = []
        for guild in self.bot.guilds:
            servers_and_owners.append(
                (
                    f"Server: {guild.name} "
                    f"with ID: {guild.id}, "
                    f"owned by: {guild.owner.display_name}"
                    f"#{guild.owner.discriminator} "
                    f"with ID: {guild.owner.id}"
                )
            )
        await ctx.send("\n".join(servers_and_owners))

    @commands.command(
        aliases=["leaveserver"],
        brief="(Bot owner only) Leaves a server.",
        description=(
            "Leaves the ID-specified server. ID can be "
            "acquired from the ServerOwnerList "
            "command. Only bot owner can do this. "
            "Supports and requires a single argument."
        ),
    )
    @commands.is_owner()
    @commands.dm_only()
    async def LeaveServer(self, ctx: commands.Context, Server_ID: str = ""):
        if Server_ID:
            if Server_ID.isnumeric():
                guild = self.bot.get_guild(int(Server_ID))
                if guild is not None:
                    try:
                        await guild.leave()
                        await ctx.send(f"Left {guild}")
                    except Exception as e:
                        await ctx.send(e)
                        self.logger.error(f"{type(e).__name__}: {e}")
                else:
                    await ctx.send(
                        (
                            "Server does not exist or the bot is not "
                            "in it, did you enter the correct ID?"
                        )
                    )
            else:
                await ctx.send("Server ID can only be a number!")
        else:
            await ctx.send("Server ID required!")

    @commands.command(
        aliases=["leave"],
        brief=(
            "(Bot owner, server owner and admin/mods only) " "Leave current server."
        ),
        description=(
            "Leaves the server the message was sent "
            "from. Only server and bot owner, and mods "
            "can do this. Supports no arguments."
        ),
    )
    async def Leave(self, ctx: commands.Context):
        if not self.bot.discord_helper.is_dm(ctx):
            if self.bot.discord_helper.is_privileged_user(ctx):
                await ctx.send(f"*Poofs to another {choice(self.locations)}*")
                await ctx.guild.leave()
            else:
                await ctx.send(("Only server and bot owner, and mods can use " "this!"))
        else:
            await ctx.send("Command only works in a server")

    @commands.is_owner()
    @commands.command(
        aliases=["LP"],
        brief=("(Bot owner only) Lists permissions given to the " "bot."),
        description=(
            "Lists the permissions given to the bot. "
            "If no server ID is provided, it will show "
            "the permissions from the server the "
            "command was used in. Supports a single "
            "optional argument as the server ID."
        ),
    )
    async def ListPermissions(self, ctx: commands.Context, Server_ID: str = ""):
        guild = None
        # If Server_ID is provided and the command was used in DM's
        if Server_ID and self.bot.discord_helper.is_dm(ctx):
            if Server_ID.isnumeric():
                # Get a guild object of the server from it's ID
                guild = self.bot.get_guild(int(Server_ID))

                # We can only get the guild object if the bot is in the server
                # so if it is None, it either does not exist or the bot is not in it
                if guild is None:
                    await ctx.send(
                        (
                            "Server does not exist or the bot is not "
                            "in it, did you enter the correct ID?"
                        )
                    )
                    return
            else:
                await ctx.send("Server ID can only be a number!")
                return

        # If Server_ID is not provided and the command was used in a server
        elif not self.bot.discord_helper.is_dm(ctx) and not Server_ID:
            guild = ctx.guild
        else:
            await ctx.send(
                (
                    "Syntax is:\n```?ListPermissions optional"
                    "<Server ID>```\nServer ID may only be provided "
                    "in DM's"
                )
            )
            return

        permissions = await self.get_permissions(guild)
        await ctx.send(
            f"I have the following permissions in {guild.name}:\n"
            + "\n".join(permissions)
        )

    @commands.command()
    async def tos(self, ctx: commands.Context):
        user = await crud.get_user(AsyncSessionLocal, ctx.author.id)
        if user is not None and user.agreed_to_tos:
            await ctx.send("You have already agreed to the ToS!")
            return
        view = ViewTest(ctx)
        view.message = await ctx.send(
            dedent(
                """\
            Hello! In order for certain commands to work properly, I need to store your Discord username and ID in my database. Alongside this, I also log all errors and my commands for debugging purposes.
            Logs are stored for approximately 7 days before being deleted.
            The following commands store additional information in the database:

            - `?chat` and `?sharedchat` stores the chat history between you and me. This can be viewed with `?chatview`, and cleared with `?chatclear`.

            I do not store or log normal chat messages.

            Abuse of the bot and its commands will result in a ban from using it.
            Do you agree to this?
            """,
            ),
            view=view,
        )
        await view.wait()
        if view.value is True:
            try:
                if not await crud.check_user_exists(AsyncSessionLocal, ctx.author.id):
                    await crud.add_user(
                        AsyncSessionLocal,
                        schemas.UserAdd(
                            user_id=ctx.author.id,
                            username=ctx.author.name,
                            agreed_to_tos=1,
                        ),
                    )
                else:
                    await crud.edit_user_tos(AsyncSessionLocal, ctx.author.id, 1)
            except Exception:
                self.logger.error("Error adding user to database", exc_info=True)
                await ctx.reply(
                    "An error occurred. Please try again later and contact the bot owner if it continues.",
                    silent=True,
                )
                return
        elif view.value is False:
            await ctx.reply(
                "You must agree to the terms of service to use the bot.", silent=True
            )

    @commands.command()
    async def test(self, ctx: commands.Context):
        await ctx.send("*Meows*")

    print("Started Control!")


async def setup(bot: commands.Bot):
    await bot.add_cog(Control(bot))
