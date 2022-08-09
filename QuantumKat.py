import random
from num2words import num2words

import discord
from discord.ext import commands

with open('./files/token', 'r') as tokenfile:
    token = tokenfile.read().strip()

initial_extensions = ['cogs.Field','cogs.Entanglement']
def setup(bot):
    for extension in initial_extensions:
        bot.load_extension(extension)

intents = discord.Intents.default()

bot = commands.Bot(command_prefix='?', help_command=None, intents=intents)

@bot.check
async def globally_block_dms(ctx):
    return ctx.guild is not None

@bot.event
async def on_ready():
    quantum = ['reality','universe','dimension','timeline']
    print(f'{bot.user} has appeared from the {num2words(random.randint(1,1000), to="ordinal_num")} {random.choice(quantum)}!')
    channel = bot.get_channel(873703927621758986)
    await channel.send(f'QuantumKat has entered a state of superposition in the {num2words(random.randint(1,1000), to="ordinal_num")} {random.choice(quantum)}!')

setup(bot)
bot.run(token)
