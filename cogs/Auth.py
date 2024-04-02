from discord.ext import commands, tasks
import asyncio


class Auth(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.db_conn = bot.db_conn
        self.authenticated_server_ids = []
        self.denied_server_ids = []
        self.update_auth.start()

    async def is_privileged_user(self, ctx: commands.Context) -> bool:
        return (
            ctx.author.guild_permissions.administrator
            or ctx.author.guild_permissions.manage_guild
            or ctx.author.id == ctx.guild.owner_id
            or ctx.author.id == self.bot.owner_ids[0]
        )

    @tasks.loop(seconds=10, count=None, reconnect=True)
    async def update_auth(self) -> None:
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

    @commands.command(aliases=["requestauth", "auth"])
    @commands.cooldown(1, 300, commands.BucketType.guild)
    async def request_auth(self, ctx: commands.Context) -> None:
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
        if not self.is_privileged_user(ctx):
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
                "INSERT INTO authenticated_servers (server_id, server_name, authenticated_by_id, authenticated_by_name, is_authenticated) VALUES (?, ?, ?, ?, 1)",
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

    @commands.command()
    async def deauth(
        self, ctx: commands.Context, server_id_or_name: int | str = ""
    ) -> None:
        """
        Deauthenticates a server.

        Parameters:
        - ctx (commands.Context): The context object representing the invocation of the command.
        - server_id_or_name (int | str): Optional. The ID or name of the server to deauthenticate.

        Returns:
        None
        """
        if server_id_or_name:
            if ctx.author.id != self.bot.owner_ids[0]:
                await ctx.send("You must be the bot owner to deauthenticate a server.")
                return
            server = self.db_conn.execute(
                "SELECT * FROM authenticated_servers WHERE server_id = ? OR server_name = ?",
                (server_id_or_name, server_id_or_name),
            ).fetchone()
            if server is None:
                await ctx.send("Server not found.")
                return
            self.db_conn.execute(
                "DELETE FROM authenticated_servers WHERE server_id = ? OR server_name = ?",
                (server_id_or_name, server_id_or_name),
            )
            self.db_conn.commit()
            await ctx.send(
                f"Deauthenticated server `{server[2]}` with ID `{server[1]}`."
            )
        elif ctx.guild is None:
            await ctx.send("This command must be used in a server.")
            return
        elif await self.is_privileged_user(ctx):
            self.db_conn.execute(
                "DELETE FROM authenticated_servers WHERE server_id = ?",
                (ctx.guild.id,),
            )
            self.db_conn.commit()
            await ctx.send("This server has been deauthenticated.")
        else:
            await ctx.send(
                "You must be a server admin/moderator, owner or the bot owner to deauthenticate this server."
            )

    print("Started Auth!")


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Auth(bot))
