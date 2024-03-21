from random import choice
import logging

from discord.ext import commands


class Control(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.locations = ["universe", "reality", "dimension", "timeline"]

        if "discord.Control" in logging.Logger.manager.loggerDict:
            self.logger = logging.getLogger("discord.Control")
        else:
            self.logger = logging.getLogger("discord.Control")
            self.logger.setLevel(logging.INFO)
            handler = logging.FileHandler(
                filename="logs/control.log", encoding="utf-8", mode="a"
            )
            date_format = "%Y-%m-%d %H:%M:%S"
            formatter = logging.Formatter(
                "[{asctime}] [{levelname:<8}] {name}: {message}",
                datefmt=date_format,
                style="{",
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)

    async def get_permissions(self, guild) -> list[str]:
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
    async def ServerOwnerList(self, ctx):
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
    async def LeaveServer(self, ctx, Server_ID=""):
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
    async def Leave(self, ctx):
        if ctx.guild is not None:
            application = await self.bot.application_info()
            if (
                ctx.author.id == ctx.guild.owner.id
                or ctx.author.id == application.owner.id
                or ctx.author.guild_permissions.administrator
                or ctx.author.guild_permissions.moderate_members
            ):
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
    async def ListPermissions(self, ctx, Server_ID=""):
        guild = None
        # If Server_ID is provided and the command was used in DM's
        if Server_ID and ctx.guild is None:
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
        elif ctx.guild is not None and not Server_ID:
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
    async def test(self, ctx):
        await ctx.send("*Meows*")

    print("Started Control!")


async def setup(bot):
    await bot.add_cog(Control(bot))
