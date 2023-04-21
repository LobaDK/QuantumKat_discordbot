from os import execl, listdir
from sys import executable, argv
from discord.ext import commands

async def RebootCommand(message, bot):
    await message.channel.send('Shutting down extensions and rebooting...')   
    for cog in listdir('./cogs'):
        if cog.endswith('.py'):
            try:
                await bot.unload_extension(cog)
            except commands.ExtensionNotLoaded:
                continue
    
    execl(executable, executable, * argv)