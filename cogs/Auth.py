from discord.ext import commands, tasks
import discord
import asyncio


class Auth(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.db_conn = bot.db_conn
        self.authenticated_server_ids = []
        self.denied_server_ids = []
        self.check_auth.start()

    @tasks.loop(seconds=10, count=None, reconnect=True)
    async def check_auth(self) -> None:
        """
        Periodically checks the authentication status of servers.

        Retrieves the list of authenticated servers and denied servers from the database.
        Updates the `authenticated_server_ids` and `denied_server_ids` attributes accordingly.
        """
        authenticated_servers = self.db_conn.execute(
            "SELECT * FROM authenticated_servers WHERE is_authenticated = 1"
        ).fetchall()
        denied_servers = self.db_conn.execute(
            "SELECT * FROM authenticated_servers WHERE is_authenticated = 0"
        ).fetchall()
        self.authenticated_server_ids = [server[1] for server in authenticated_servers]
        self.denied_server_ids = [server[1] for server in denied_servers]

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message) -> None:
        """
        Handles the event when a command is invoked.

        Parameters:
        - message (discord.Message): The message object representing the command invocation.

        Returns:
        - None

        Raises:
        - None
        """
        if not message.author.bot:
            if message.content.startswith(self.bot.command_prefix):
                if message.guild.id not in self.authenticated_server_ids:
                    await message.reply(
                        "This server is not authenticated to use this bot. Please run `?auth` to authenticate this server.",
                        silent=True,
                    )
                    return
                else:
                    await self.bot.process_commands(message)

    @commands.command()
    async def auth(self, ctx: commands.Context) -> None:
        """
        Authenticates a server by sending a request to the bot owner for approval.

        Parameters:
        - ctx (commands.Context): The context object representing the command invocation.

        Returns:
        None
        """
        if ctx.guild.id in self.authenticated_server_ids:
            await ctx.send("This server is already authenticated.")
            return
        if ctx.guild.id in self.denied_server_ids:
            await ctx.send(
                "This server has been denied authentication. Please contact the bot owner for more information."
            )
            return
        if (
            not ctx.author.guild_permissions.administrator
            and not ctx.author.guild_permissions.manage_guild
            and not ctx.author.id == ctx.guild.owner_id
            and not ctx.author.id == self.bot.owner_ids[0]
        ):
            await ctx.send(
                "You must be a server admin/moderator, owner or the bot owner to request authentication."
            )
            return
        bot_owner = self.bot.get_user(self.bot.owner_ids[0])
        dm_msg = await bot_owner.send(
            f"Server `{ctx.guild.name}` with ID `{ctx.guild.id}` is requesting authentication from `{ctx.author.name}` with ID `{ctx.author.id}`."
        )
        server_msg = await ctx.send(
            "Request sent. Awaiting approval... This may take up to 5 minutes."
        )

        def check(m):
            return (
                m.author == bot_owner
                and m.channel == dm_msg.channel
                and m.content.lower() in ["yes", "no"]
            )

        async def wait_for_response():
            return await self.bot.wait_for("message", check=check)

        async def update_server_msg():
            for remaining in range(300, 0, -10):
                minutes, seconds = divmod(remaining, 60)
                await server_msg.edit(
                    content=f"{server_msg.content}\nTime remaining: {minutes:02d}:{seconds:02d}"
                )
                await asyncio.sleep(10)

        response_task = asyncio.create_task(wait_for_response())
        update_task = asyncio.create_task(update_server_msg())

        done, pending = await asyncio.wait(
            [response_task, update_task], return_when=asyncio.FIRST_COMPLETED
        )

        for task in pending:
            task.cancel()

        if response_task in done:
            response = response_task.result()
            if response.content.lower() == "no":
                await server_msg.edit(
                    content=f"{server_msg.content}\nRequest denied. If you believe this is a mistake, please contact the bot owner."
                )
                self.db_conn.execute(
                    "INSERT INTO authenticated_servers (server_id, server_name, authenticated_by_id, authenticated_by_name, is_authenticated) VALUES (?, ?, ?, ?, 0)",
                    (ctx.guild.id, ctx.guild.name, ctx.author.id, ctx.author.name),
                )
                self.db_conn.commit()
                return
            self.db_conn.execute(
                "INSERT INTO authenticated_servers (server_id, server_name, authenticated_by_id, authenticated_by_name) VALUES (?, ?, ?, ?)",
                (ctx.guild.id, ctx.guild.name, ctx.author.id, ctx.author.name),
            )
            self.db_conn.commit()
            await server_msg.edit(
                content=f"{server_msg.content}\nRequest approved. This server is now authenticated. You may need to wait a few seconds for the changes to take effect."
            )
        else:
            await server_msg.edit(
                content=f"{server_msg.content}\nRequest timed out. Please try again later."
            )

    print("Started Auth!")


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Auth(bot))
