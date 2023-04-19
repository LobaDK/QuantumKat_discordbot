from asyncio import run
from datetime import datetime
from os import environ, execl, listdir
from random import choice, randint
from sys import argv, executable

from discord import Intents
from discord.ext import commands
from dotenv import load_dotenv
from num2words import num2words

load_dotenv()

initial_extensions = []
for cog in listdir('./cogs'):
    if cog.endswith('.py'):
        initial_extensions.append(f'cogs.{cog[:-3]}')

async def setup(bot):
    for extension in initial_extensions:
        await bot.load_extension(extension)
    await bot.start(environ.get('TOKEN'))

intents = Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix='?', help_command=commands.DefaultHelpCommand(sort_commands=False, show_parameter_descriptions=False, width=100), intents=intents, owner_ids=[int(environ.get('OWNER_ID'))])

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
        if message.author.id == bot.owner_id[0]:
            if not message.channel.guild == None:
                await message.channel.reply('Shutting down extensions and rebooting...')
            else:
                await message.channel.send('Shutting down extensions and rebooting...')
            
            for cog in initial_extensions:
                try:
                    await bot.unload_extension(cog)
                except commands.ExtensionNotLoaded:
                    continue
            
            execl(executable, executable, * argv)

run(setup(bot))
