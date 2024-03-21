from asyncio import run
from datetime import datetime
from os import environ, listdir, path
from random import choice, randint
from sys import exit

import sqlite3
import logging
import logging.handlers
from discord import Intents, __version__
from discord.ext import commands
from dotenv import load_dotenv
from num2words import num2words
from shutil import which
from os import mkdir


def is_installed(executable: str) -> bool:
    return which(executable) is not None


try:
    mkdir("logs")
except FileExistsError:
    pass

logger = logging.getLogger("discord.QuantumKat")
logger.setLevel(logging.INFO)

handler = logging.FileHandler(
    filename="logs/quantumkat.log", encoding="utf-8", mode="a"
)

date_format = "%Y-%m-%d %H:%M:%S"
formatter = logging.Formatter(
    "[{asctime}] [{levelname:<8}] {name}: {message}", datefmt=date_format, style="{"
)
handler.setFormatter(formatter)
logger.addHandler(handler)

# If False, will exit if a required program is missing
# Can be set to True for debugging without needing them installed
ignoreMissingExe = False

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

bot.db_conn = sqlite3.connect("quantumkat.db")

# Get and add cogs to a list
initial_extensions = []
for cog in listdir("./cogs"):
    if cog.endswith(".py"):
        logger.info(f"Loading cog: {cog}")
        initial_extensions.append(f"cogs.{path.splitext(cog)[0]}")


async def setup(bot: commands.Bot):
    if not ignoreMissingExe:
        for executable in executables:
            if not is_installed(executable):
                logger.error(f"Error: {executable} is not installed.")
                exit(1)

    # Iterate through each cog and start it
    for extension in initial_extensions:
        await bot.load_extension(extension)
    await bot.start(TOKEN, reconnect=True)


@bot.event
async def on_ready():
    sql = """CREATE TABLE IF NOT EXISTS chat (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    user_name TEXT NOT NULL,
    server_id INTEGER NOT NULL,
    server_name TEXT NOT NULL,
    user_message TEXT NOT NULL,
    assistant_message TEXT NOT NULL,
    shared_chat INTEGER NOT NULL DEFAULT 0
    )"""

    try:
        bot.db_conn.execute(sql)
        bot.db_conn.commit()
    except sqlite3.Error as e:
        logger.error(f"Error creating chat table: {e}")

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


run(setup(bot))
