from asyncio import run
from datetime import datetime
from os import environ
from random import choice, randint
from sys import exit

from helpers import LogHelper, MiscHelper, DiscordHelper, DBHelper
import sqlite3
from pathlib import Path
from discord import Intents, __version__
from discord.ext import commands
from dotenv import load_dotenv
from num2words import num2words
from os import mkdir
from threading import Thread
import pubapi

from sql import models
from sql.database import engine


async def init_models():
    async with engine.begin() as conn:
        await conn.run_sync(models.Base.metadata.create_all)


run(init_models())

try:
    mkdir("logs")
except FileExistsError:
    pass

log_helper = LogHelper()
misc_helper = MiscHelper()
discord_helper = DiscordHelper()

logger = log_helper.create_logger("QuantumKat", "logs/QuantumKat.log")

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
intents = Intents.default()
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

bot.db_conn = sqlite3.connect("quantumkat.db")
bot.db_helper = DBHelper(bot.db_conn, logger)
bot.log_helper = log_helper
bot.misc_helper = misc_helper
bot.discord_helper = discord_helper
try:
    bot.db_helper.create_table(
        "chat",
        (
            "id INTEGER PRIMARY KEY AUTOINCREMENT",
            "user_id INTEGER NOT NULL",
            "user_name TEXT NOT NULL",
            "server_id INTEGER NOT NULL",
            "server_name TEXT NOT NULL",
            "user_message TEXT NOT NULL",
            "assistant_message TEXT NOT NULL",
            "shared_chat INTEGER NOT NULL DEFAULT 0",
        ),
    )
    bot.db_helper.create_table(
        "authenticated_servers",
        (
            "id INTEGER PRIMARY KEY AUTOINCREMENT",
            "server_id INTEGER NOT NULL",
            "server_name TEXT NOT NULL",
            "authenticated_by_id INTEGER NOT NULL",
            "authenticated_by_name TEXT NOT NULL",
            "is_authenticated INTEGER NOT NULL DEFAULT 0",
        ),
    )
except sqlite3.Error:
    logger.error("Error creating tables.", exc_info=True)
    exit(1)


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
        authenticated_server_ids = bot.db_conn.execute(
            "SELECT server_id FROM authenticated_servers WHERE is_authenticated = 1"
        ).fetchall()
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


@bot.event
async def on_ready():
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
Discord.py version: {__version__}
\nStarted at {datetime.now()}\n
{bot.user} has appeared from the {num2words(randint(1,1000),
    to="ordinal_num")} {choice(quantum)}!"""
    logger.info(message)
    print(message)

    bot.add_check(is_authenticated)
    bot.add_check(is_reboot_scheduled)

    Thread(target=pubapi.start_api).start()


run(setup(bot))
