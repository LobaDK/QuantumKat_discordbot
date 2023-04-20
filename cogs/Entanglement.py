import os

from discord.ext import commands
from Entanglements.DequantizeCommand import DequantizeCommand
from Entanglements.EntangleCommand import Entanglecommand
from Entanglements.GitCommand import GitCommand
from Entanglements.QuantizeCommand import QuantizeCommand
from Entanglements.RequantizeCommand import RequantizeCommand

from Entanglements.StabiliseCommand import StabiliseCommand
from Entanglements.StatusCommand import StatusCommand
from Entanglements.UnentangleCommand import UnentangleCommand
from Entanglements.UpdateCommand import UpdateCommand


class Entanglement(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    initial_extensions = []
    for cog in os.listdir('./cogs'):
        if cog.endswith('.py'):
            initial_extensions.append(f'{cog[:-3]}')

    aaaa_dir = '/var/www/aaaa/'
    aaaa_domain = 'https://aaaa.lobadk.com/'
    possum_dir = '/var/www/possum/'
    possum_domain = 'https://possum.lobadk.com/'

###################################################################################################### command splitter for easier reading and navigating
    
    @commands.command(brief="(Bot owner only) Stops the bot.", description="Stops and disconnects the bot. Supports no arguments.")
    @commands.is_owner()
    async def observe(self, ctx):
        await ctx.send("QuantumKat's superposition has collapsed!")
        await self.bot.close()

######################################################################################################

    @commands.command(aliases=['stabilize', 'restart', 'reload'], brief="(Bot owner only) Reloads cogs/extensions.", description="Reloads the specified cogs/extensions. Requires at least one argument, and supports an arbitrary amount of arguments. Special character '*' can be used to reload all.")
    @commands.is_owner()
    async def stabilise(self, ctx, *, module : str=''):
        StabiliseCommand(self, ctx, module)

######################################################################################################

    @commands.command(aliases=['load', 'start'], brief="(Bot owner only) Starts/Loads a cog/extension.", description="Starts/Loads the specified cogs/extensions. Requires at least one argument, and supports an arbitrary amount of arguments.")
    @commands.is_owner()
    async def entangle(self, ctx, *, module : str=''):
        Entanglecommand(self, ctx, module)

######################################################################################################

    @commands.command(aliases=['unload', 'stop'], brief="(Bot owner only) Stops/Unloads a cog/extension.", description="Stops/Unloads the specified cogs/extensions. Requires at least one argument, and supports an arbitrary amount of arguments.")
    @commands.is_owner()
    async def unentangle(self, ctx, *, module : str=''):
        UnentangleCommand(self, ctx, module)

######################################################################################################

    @commands.command(aliases=['quantise'], brief="(Bot owner only) Downloads a file to aaaa/possum.lobadk.com.", description="Downloads the specified file to the root directory of aaaa.lobadk.com or possum.lobadk.com, for easier file adding. Requires at least 3 arguments, and supports 4 arguments. The first argument is the file URL, the second is the filename to be used, with a special 'rand' parameter that produces a random 8 character long base62 filename, the third is the location, specified with 'aaaa' or 'possum', the fourth (optional) is 'YT' to indicate yt-lp should be used to download the file (YouTub or Twitter for example). If a file extension is detected, it will automatically be used, otherwise it needs to be specified in the filename. Supports links with disabled embeds, by '<>'.")
    @commands.is_owner()
    async def quantize(self, ctx, URL="", filename="", location="", mode=""):
        QuantizeCommand(self, ctx, URL, filename, location, mode)

######################################################################################################

    @commands.command(aliases=['requantise'], brief="(Bot owner only) Rename a file on aaaa.lobadk.com.", description="Renames the specified file. Requires and supports 2 arguments. Only alphanumeric, underscores and a single dot allowed, and at least one character must appear after the dot when chosing a new name.")
    @commands.is_owner()
    async def requantize(self, ctx, current_filename='', new_filename=''):
        RequantizeCommand(self, ctx, current_filename, new_filename)

######################################################################################################

    @commands.command(brief="(Bot owner only) Runs git commands in the bots directory.", description="Run any git command by passing along the arguments specified. Mainly used for updating the bot or swapping versions, but there is no limit.")
    @commands.is_owner()
    async def git(self, ctx, *, git_arguments):
        GitCommand(self, ctx, git_arguments)

######################################################################################################

    @commands.command(brief="(Bot owner only) Fetches new updates and reloads all changed/updated cogs/extensions.", description="Fetches the newest version by running 'git pull' and then reloads the cogs/extensions if successful.")
    @commands.is_owner()
    async def update(self, ctx):
        UpdateCommand(self, ctx)

######################################################################################################

    @commands.command(aliases=['dequantize'], brief='(Bot owner only) Delete the specified file.', description='Attempts to delete the specified file. Supports and requires 2 arguments, being the filename, and location (aaaa|possum).')
    @commands.is_owner()
    async def dequantise(self, ctx, filename="", location=""):
        DequantizeCommand(self, ctx, filename, location)

######################################################################################################

    @commands.command()
    @commands.is_owner()
    async def status(self, ctx):
        StatusCommand(self, ctx)

######################################################################################################

    print('Started Entanglement!')
async def setup(bot):
    await bot.add_cog(Entanglement(bot))
