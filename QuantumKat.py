import asyncio
import random
from num2words import num2words

import discord
from discord.ext import commands

client = discord.Client()

async def main():

    with open('./files/token', 'r') as tokenfile:
        token = tokenfile.read().strip()
    

    intents = discord.Intents.all()

    bot = commands.Bot(command_prefix='?', help_command=None, intents=intents)

    asyncio.run(setup(bot))

    async with client:
        await client.start(token)

    @bot.check
    async def globally_block_dms(ctx):
        return ctx.guild is not None

    @bot.event
    async def on_ready():
        quantum = ['reality','universe','dimension','timeline']
        print(f'{bot.user} has appeared from the {num2words(random.randint(1,1000), to="ordinal_num")} {random.choice(quantum)}!')
        #channel = bot.get_channel(873703927621758986)
        #await channel.send(f'QuantumKat has entered a state of superposition in the {num2words(random.randint(1,1000), to="ordinal_num")} {random.choice(quantum)}!')

async def setup(bot):
    initial_extensions = ['cogs.Activity']
    for extension in initial_extensions:
        await bot.load_extension(extension)

asyncio.run(main())