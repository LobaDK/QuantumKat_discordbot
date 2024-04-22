from random import choice
import discord

from textwrap import dedent
from discord.ext import commands
from helpers import LogHelper
from sqlalchemy.exc import SQLAlchemyError

from decorators import requires_tos_acceptance
from sql import crud, schemas
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
    @requires_tos_acceptance
    async def tos(self, ctx: commands.Context):
        return

    @commands.command()
    @requires_tos_acceptance
    async def test(self, ctx: commands.Context):
        await ctx.send("*Meows*")

    @commands.is_owner()
    @commands.group()
    async def user(self, ctx: commands.Context):
        if ctx.invoked_subcommand is None:
            await ctx.send("Invalid user command passed...")
            return

    @user.group()
    async def bot(self, ctx: commands.Context):
        if ctx.invoked_subcommand is None:
            await ctx.send("Invalid bot command passed...")
            return

    @bot.command()
    async def ban(self, ctx: commands.Context, user: discord.User):
        try:
            if not await crud.check_user_exists(
                AsyncSessionLocal, schemas.User.Get(user_id=user.id)
            ):
                await crud.add_user(
                    AsyncSessionLocal,
                    schemas.User.Add(
                        user_id=user.id,
                        username=user.display_name,
                        is_banned=True,
                    ),
                )
            else:
                await crud.edit_user_ban(
                    AsyncSessionLocal,
                    schemas.User.SetBan(user_id=user.id, is_banned=True),
                )
            await ctx.reply(
                f"{user.display_name} has been banned from using the bot.",
                silent=True,
            )
        except SQLAlchemyError:
            self.logger.error("Failed to add user to DB", exc_info=True)
            await ctx.reply("Database error. Please try again later.", silent=True)
            return

    @bot.command()
    async def unban(self, ctx: commands.Context, user: discord.User):
        try:
            if not await crud.check_user_exists(
                AsyncSessionLocal, schemas.User.Get(user_id=user.id)
            ):
                await ctx.reply(
                    f"{user.display_name} is not in the database and cannot be unbanned.",
                    silent=True,
                )
                return
            else:
                await crud.edit_user_ban(
                    AsyncSessionLocal,
                    schemas.User.SetBan(user_id=user.id, is_banned=False),
                )
            await ctx.reply(
                f"{user.display_name} has been unbanned from using the bot.",
                silent=True,
            )
        except SQLAlchemyError:
            self.logger.error("Failed to add user to DB", exc_info=True)
            await ctx.reply("Database error. Please try again later.", silent=True)
            return

    @user.command()
    async def whois(self, ctx: commands.Context, user: discord.User):
        message = dedent(
            f"""
            User ID: {user.id}
            Username: {user.display_name}
            Is bot: {user.bot}
            Created at: {user.created_at}
            """
        )
        if not self.bot.discord_helper.is_dm(
            ctx
        ) and self.bot.discord_helper.user_in_guild(user, ctx.guild):
            member = ctx.guild.get_member(user.id)
            if member is None:
                member = await ctx.guild.fetch_member(user.id)
            message += f"Joined at: {member.joined_at}"

        await ctx.send(message)

    print("Started Control!")


async def setup(bot: commands.Bot):
    await bot.add_cog(Control(bot))
