from asyncio import run
from datetime import datetime
from os import environ, listdir
from random import choice, randint
from sys import exit

from discord import Intents, __version__
from discord.ext import commands
from dotenv import load_dotenv
from num2words import num2words
from shutil import which

# If False, will exit if a required program is mising
# Can be set to True for debugging without needing them installed
ignoreMissingExe = False

# Load .env file which contains bot token and my user ID
# and store in OS user environment variables
load_dotenv()

# Get the bot token and my user ID from the environment variables
OWNER_ID = environ.get('OWNER_ID')
TOKEN = environ.get('TOKEN')

# If the bot token or my user ID is not set, exit the program
if OWNER_ID is None:
    print("Error: The OWNER_ID environment variable is not set.")
    exit(1)

if TOKEN is None:
    print("Error: The TOKEN environment variable is not set.")
    exit(1)

# Gives the bot default access as well as access
# to contents of messages and managing members
intents = Intents.default()
intents.message_content = True
intents.members = True

# Sets the bot's command prefix, help command, and
# set it's intents, and adds my ID to owner_ids
bot = commands.Bot(command_prefix='?',
                   help_command=commands.DefaultHelpCommand(
                       sort_commands=False, show_parameter_descriptions=False,
                       width=100), intents=intents, owner_ids=[int(OWNER_ID)])

# Get and add cogs to a list
initial_extensions = []
for cog in listdir('./cogs'):
    if cog.endswith('.py'):
        initial_extensions.append(f'cogs.{cog[:-3]}')


def ffmpegInstalled():
    return which('ffmpeg') is not None


def ffprobeInstalled():
    return which('ffprobe') is not None


def ytdlpInstalled():
    return which('yt-dlp') is not None


async def setup(bot):
    if not ffmpegInstalled():
        if not ignoreMissingExe:
            print('Exiting due to ffmpeg not being found')
            exit()
        else:
            print('No ffmpeg executable found')

    if not ffprobeInstalled():
        if not ignoreMissingExe:
            print('Exiting due to ffprobe not being found')
            exit()
        else:
            print('No ffprobe executable found')

    if not ytdlpInstalled():
        if not ignoreMissingExe:
            print('Exiting due to yt-dlp not being found')
            exit()
        else:
            print('No yt-dlp executable found')

    # Iterate through each cog and start it
    for extension in initial_extensions:
        await bot.load_extension(extension)
    await bot.start(TOKEN, reconnect=True)


@bot.event
async def on_ready():
    bot.appinfo = await bot.application_info()
    quantum = ['reality', 'universe', 'dimension', 'timeline']
    print(f'''
----------info----------
Application ID: {bot.appinfo.id}
Application name: {bot.appinfo.name}
Application owner: {bot.appinfo.owner}
Application owner IDs: {bot.owner_ids}
Latency to Discord: {int(bot.latency * 1000)}ms.
Discord version: {__version__}
\nStarted at {datetime.now()}\n
{bot.user} has appeared from the {num2words(randint(1,1000),
    to="ordinal_num")} {choice(quantum)}!''')

run(setup(bot))
