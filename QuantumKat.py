from asyncio import run
from datetime import datetime
from os import environ, listdir
from random import choice, randint
from sys import exit

from discord import Intents
from discord.ext import commands
from dotenv import load_dotenv
from num2words import num2words
from shutil import which

from QuantumKats.RebootCommand import RebootCommand
from functions.getCogs import getCogs

# If False, will exit if a required program is mising
# Can be to True for debugging without needing them installed
ignoreMissingExe = False

# Load .env file which contains bot token and my user ID
# and store in OS user environment variables
load_dotenv()

# Gives the bot default access as well as access
# to contents of messages and managing members
intents = Intents.default()
intents.message_content = True
intents.members = True

# Gives bot command prefix, enable built-in help command
# set it's intents, and add my ID to owner_ids
bot = commands.Bot(command_prefix='?', help_command=commands.DefaultHelpCommand(sort_commands=False, show_parameter_descriptions=False, width=100), intents=intents, owner_ids=[int(environ.get('OWNER_ID'))])

# Get and add cogs to a list
initial_extensions = getCogs()

def ffmpegInstalled():
    return which('ffmpeg') is not None

def ytdlpInstalled():
    return which('yt-dlp') is not None

def wgetInstalled():
    return which('wget') is not None

async def setup(bot):
    if not ffmpegInstalled():
        if not ignoreMissingExe:
            print('Exiting due to ffmpeg not being found')
            exit()
        else:
            print('No ffmpeg executable found')

    if not ytdlpInstalled():
        if not ignoreMissingExe:
            print('Exiting due to yt-dlp not being found')
            exit()
        else:
            print('No yt-dlp executable found')

    if not wgetInstalled():
        if not ignoreMissingExe:
            print('Exiting due to wget not being found')
            exit()
        else:
            print('No wget executable found')
    
    # Iterate through each cog and start it
    for extension in initial_extensions:
        await bot.load_extension(extension)
    await bot.start(environ.get('TOKEN'))

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
\nStarted at {datetime.now()}\n
{bot.user} has appeared from the {num2words(randint(1,1000), to="ordinal_num")} {choice(quantum)}!
    ''')
    #channel = bot.get_channel(873703927621758986)
    #await channel.send(f'QuantumKat has entered a state of superposition in the {num2words(random.randint(1,1000), to="ordinal_num")} {random.choice(quantum)}!')

#Uses os.execl to replace the running script with a new version. 
#Useful if an update has changed parts of the main file, which
#otherwise would require a manual restart from an SSH connection
@bot.listen('on_message')
async def listen_for_reboot(message):
    if message.content == '?reboot':
        if message.author.id in bot.owner_ids:
            await RebootCommand(message, bot)

run(setup(bot))
