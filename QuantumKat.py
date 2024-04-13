from asyncio import run
from datetime import datetime
from os import environ
from random import choice, randint
from sys import exit

from helpers import LogHelper, MiscHelper, DiscordHelper
from pathlib import Path
import discord
from discord.ext import commands
from dotenv import load_dotenv
from num2words import num2words
from threading import Thread
import pubapi
import textwrap

from sql import models, schemas
from sql.database import engine, AsyncSessionLocal
from sql import crud

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


async def init_models():
    async with engine.begin() as conn:
        # For testing purposes, drop all tables
        await conn.run_sync(models.Base.metadata.drop_all)
        await conn.run_sync(models.Base.metadata.create_all)


run(init_models())

log_helper = LogHelper()
misc_helper = MiscHelper()
discord_helper = DiscordHelper()

logger = log_helper.create_logger(
    log_helper.TimedRotatingFileAndStreamHandler(
        logger_name="QuantumKat", log_file="logs/quantumkat/QuantumKat.log"
    )
)

# If False, will exit if a required program is missing
# Can be set to True for debugging without needing them installed
ignoreMissingExe = True

# List of required executables
executables = ["ffmpeg", "ffprobe", "youtube-dl"]

# Load .env file which contains bot token and my user ID
# and store in OS user environment variables
load_dotenv()

# Get the bot token and my user ID from the environment variables
OWNER_ID = environ.get("OWNER_ID")
TOKEN = environ.get("TOKEN")

# If the bot token or my user ID is not set, exit the program
if OWNER_ID is None or OWNER_ID == "":
    logger.error("Error: The OWNER_ID environment variable is not set or is empty.")
    exit(1)

if TOKEN is None or TOKEN == "":
    logger.error("Error: The TOKEN environment variable is not set or is empty.")
    exit(1)

# Gives the bot default access as well as access
# to contents of messages and managing members
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

# Sets the bot's command prefix, help command, intents, and adds my ID to owner_ids
bot = commands.Bot(
    command_prefix="?",
    help_command=commands.DefaultHelpCommand(
        sort_commands=False, show_parameter_descriptions=False, width=100
    ),
    intents=intents,
    owner_ids=[int(OWNER_ID)],
)

bot.reboot_scheduled = False

bot.log_helper = log_helper
bot.misc_helper = misc_helper
bot.discord_helper = discord_helper


async def setup(bot: commands.Bot):
    if not ignoreMissingExe:
        for executable in executables:
            if not bot.misc_helper.is_installed(executable):
                logger.error(f"Error: {executable} is not installed.")
                exit(1)

    await bot.discord_helper.first_load_cogs(bot, "./cogs", logger)
    await bot.start(TOKEN, reconnect=True)


async def is_authenticated(ctx: commands.Context) -> bool:
    if not ctx.message.content.startswith(f"{bot.command_prefix}auth"):
        authenticated_server_ids = await crud.get_authenticated_servers(
            AsyncSessionLocal
        )
        authenticated_server_ids = [server[0] for server in authenticated_server_ids]
        if bot.discord_helper.is_dm(ctx):
            # If the command is run in a DM, check if the user is in an authenticated server
            for guild in bot.guilds:
                if guild.id in authenticated_server_ids:
                    if bot.discord_helper.user_in_guild(ctx.author, guild):
                        return True
            await ctx.send(
                "You need to be in an at least one authenticated server to interact with me in DMs."
            )
            return False
        if ctx.guild.id in authenticated_server_ids:
            return True
        else:
            await ctx.send(
                "This server is not authenticated. Please run the `?auth` command to authenticate this server."
            )
            return False
    return True


async def is_reboot_scheduled(ctx: commands.Context) -> bool:
    if bot.reboot_scheduled:
        await ctx.reply(
            "A reboot has been scheduled. Commands are disabled until the reboot is complete.",
            silent=True,
        )
        return False
    return True


# Check before any command to ensure the user is in the database.
# A little excessive to check on each command, but for privacy reasons
#   I wanna give the user the option to opt out of the database by not using the bot.
# TODO: Ask the user if they agree to be in the database. Maybe also add a command to opt out?
#   Should the command remove the user from the database or just set a flag?
async def ensure_user_in_db(ctx: commands.Context) -> None:
    if not await crud.check_user_exists(AsyncSessionLocal, ctx.author.id):
        view = ViewTest(ctx)
        view.message = await ctx.send(
            textwrap.dedent(
                """\
            Hello! Looks like this is your first time interacting with me. In order for certain commands to work properly, I need to store your Discord username and ID in my database. Alongside this, I also log all errors and my commands for debugging purposes.
            Logs are stored for approximately 7 days before being deleted.
            The following commands store additional information in the database:

            - `?chat` and `?sharedchat` stores the chat history between you and me.

            I do not store or log normal chat messages.
            Do you agree to this?
            """,
            ),
            view=view,
            ephemeral=True,
        )
        await view.wait()
        if view.value:
            try:
                await crud.add_user(
                    AsyncSessionLocal,
                    schemas.UserAdd(user_id=ctx.author.id, username=ctx.author.name),
                )
            except Exception:
                logger.error("Error adding user to database", exc_info=True)
                await ctx.reply(
                    "An error occurred. Please try again later and contact the bot owner if it continues.",
                    silent=True,
                )
                return False
        else:
            return False
    return True


# Triggered whenever the bot joins a server. We use this to add the server to the database.
@bot.event
async def on_guild_join(guild):
    await crud.add_server(
        AsyncSessionLocal,
        schemas.ServerAdd(server_id=guild.id, server_name=guild.name),
    )


@bot.event
async def on_ready():
    # Add all servers the bot is in to the database on startup in case the bot was added while offline
    for guild in bot.guilds:
        if not await crud.check_server_exists(AsyncSessionLocal, guild.id):
            await crud.add_server(
                AsyncSessionLocal,
                schemas.ServerAdd(server_id=guild.id, server_name=guild.name),
            )
    # Check if the bot was rebooted and edit the message to indicate it was successful
    # TODO: Use the database instead? Also, it edits the message even if the bot was not rebooted
    if Path("rebooted").exists():
        with open("rebooted", "r") as f:
            IDs = f.read()
        # Order: message ID, channel ID, guild ID
        IDs = IDs.split("\n")
        try:
            channel = bot.get_channel(int(IDs[1]))
            if channel is None:
                channel = await bot.fetch_channel(int(IDs[1]))
            message = await channel.fetch_message(int(IDs[0]))
        except Exception:
            logger.error("Error fetching message to edit", exc_info=True)
        if message:
            try:
                await message.edit(content=f"{message.content} Rebooted successfully!")
            except Exception:
                logger.error("Error editing message", exc_info=True)
        else:
            # if the message is not found, instead send a message to the bot owner
            await bot.get_user(int(OWNER_ID)).send("Rebooted successfully!")
        Path("rebooted").unlink()

    bot.appinfo = await bot.application_info()
    quantum = ["reality", "universe", "dimension", "timeline"]
    message = f"""
----------info----------
Application ID: {bot.appinfo.id}
Application name: {bot.appinfo.name}
Application owner: {bot.appinfo.owner}
Application owner IDs: {bot.owner_ids}
Latency to Discord: {int(bot.latency * 1000)}ms.
Discord.py version: {discord.__version__}
\nStarted at {datetime.now()}\n
{bot.user} has appeared from the {num2words(randint(1, 1000),
    to="ordinal_num")} {choice(quantum)}!"""
    logger.info(message)
    print(message)

    bot.add_check(is_reboot_scheduled)
    bot.add_check(ensure_user_in_db)
    bot.add_check(is_authenticated)

    Thread(target=pubapi.start_api).start()


run(setup(bot))
