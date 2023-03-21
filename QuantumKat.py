import asyncio
import os
import random
from datetime import datetime

import discord
from discord.ext import commands
from num2words import num2words

with open('./files/token', 'r') as tokenfile:
    token = tokenfile.read().strip()

initial_extensions = []
for cog in os.listdir('./cogs'):
    if cog.endswith('.py'):
        initial_extensions.append(f'cogs.{cog[:-3]}')

async def setup(bot):
    for extension in initial_extensions:
        await bot.load_extension(extension)
    await bot.start(token)

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix='?', help_command=commands.DefaultHelpCommand(sort_commands=False, show_parameter_descriptions=False, width=100), intents=intents)

@bot.event
async def on_ready():
    bot.appinfo = await bot.application_info()
    quantum = ['reality', 'universe', 'dimension', 'timeline']
    print(f'''
----------info----------
Application ID: {bot.appinfo.id}
Application name: {bot.appinfo.name}
Application owner: {bot.appinfo.owner}
Latency to Discord: {int(bot.latency * 1000)}ms.
\nStarted at {datetime.now()}\n
{bot.user} has appeared from the {num2words(random.randint(1,1000), to="ordinal_num")} {random.choice(quantum)}!
    ''')
    #channel = bot.get_channel(873703927621758986)
    #await channel.send(f'QuantumKat has entered a state of superposition in the {num2words(random.randint(1,1000), to="ordinal_num")} {random.choice(quantum)}!')

asyncio.run(setup(bot))
