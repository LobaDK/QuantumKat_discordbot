from random import choice

from discord.ext import commands
from Fields.aaaaCountCommand import aaaaCountCommand
from Fields.aaaaSearchCommand import aaaaSearchCommand
from Fields.aCommand import aCommand
from Fields.ArPrCommand import arpr
from Fields.ArSearchCommand import ArSearchCommand
from Fields.HugCommand import HugCommand
from Fields.PetCommand import PetCommand
from Fields.PingCommand import PingCommand
from Fields.QuantumBallCommand import QuantumBallCommand
from Fields.QuantumHugCommnd import QuantumHugCommand
from Fields.QuantumPetCommand import QuantumPetCommand
from Fields.RPSCommand import RPSCommand


class Field(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        #Open the file and load each joke per line into a list
        jokefile = open('./files/quantumjokes.txt', 'r')
        self.jokes = [joke for joke in jokefile.readlines() if joke.strip()]
        jokefile.close()

###################################################################################################### command splitter for easier reading and navigating

    @commands.command(aliases=['arr','arrr','arrrr','arrrrr'], brief='Returns a random file from aaaa.lobadk.com.', description="Takes no arguments, but up to 5 r' can be appended, each fetching another random file from aaaa.lobadk.com.")
    async def ar(self, ctx):
        url = 'https://aaaa.lobadk.com/botrandom'
        await arpr(ctx, url)
        
######################################################################################################

    @commands.command(aliases=['or', 'orr','orrr','orrrr','orrrrr'], brief='Returns a random file from possum.lobadk.com.', description="Takes no arguments, but up to 5 r' can be appended, each fetching another random file from possum.lobadk.com.")
    async def pr(self, ctx):
        url = 'https://possum.lobadk.com/botrandom'
        await arpr(ctx, url)

######################################################################################################

    @commands.command(aliases=['pæt','pets','pæts'], brief='Pets another user, the bot or themselves a random amount.', description='Supports one argument, being whatever or whoever the user wants to pet. If no argument is included, the bot pets the user who ran the command. Does between a 1 and 20 long pet.')
    async def pet(self, ctx, *, optional_user_or_object=""):
        await PetCommand(self, ctx, optional_user_or_object)

######################################################################################################

    @commands.command(aliases=['hugs'], brief='Hugs another user, the bot or themselves a random amount.', description='Supports one argument, being whatever or whoever the user wants to hug. If no argument is included, the bot hugs the user who ran the command. Does between a 1 and 20 long hug.')
    async def hug(self, ctx, *, optional_user_or_object=""):
        await HugCommand(self, ctx, optional_user_or_object)

######################################################################################################

    @commands.command(aliases=['quantumpæt','qpet','qpæt','quantumpæts','quantumpets','qpets','qpæts'], brief='Pets another user, the bot or themselves a large random amount.', description='Supports one argument, being whatever or whoever the user wants to pet. If no argument is included, the bot pets the user who ran the command. Does between a 100 and 1000 long pet.')
    async def quantumpet(self, ctx, *, optional_user_or_object=""):
        await QuantumPetCommand(self, ctx, optional_user_or_object)

######################################################################################################

    @commands.command(aliases=['quantumhøg','qhug','qhøg','quantumhøgs','quantumhugs','qhugs','qhøgs'], brief='Hugs another user, the bot or themselves a large random amount.', description='Supports one argument, being whatever or whoever the user wants to hug. If no argument is included, the bot hugs the user who ran the command. Does between a 100 and 1000 long hug.')
    async def quantumhug(self, ctx, *, optional_user_or_object=""):
        await QuantumHugCommand(self, ctx, optional_user_or_object)

######################################################################################################

    @commands.command(aliases=['rockpaperscissor'], brief='Rock, Paper, Scissors game.', description='A Rock, Paper, Scissors game. Supports one argument, being the chosen gesture. Emote is also supported. Is not rigged.')
    async def rps(self, ctx, *, item=""):
        await RPSCommand(self, ctx, item)

######################################################################################################

    @commands.command(aliases=['as','asearch'], brief='aaaa search function.', description='Searches aaaa with the given argument and returns the results. Only takes one, and limited to a minimum of two characters, being alphanumeric as well as a dot.')
    async def aaaasearch(self, ctx, search_keyword=""):
        await aaaaSearchCommand(self, ctx, search_keyword)

######################################################################################################

    @commands.command(brief='Appends filename to aaaa.lobadk.com.', description='Appends the provided filename to the end of aaaa.lobadk.com/, to quickly link the file. Only alphanumeric characters and a dot is allowed.')
    async def a(self, ctx, filename=""):
        await aCommand(self, ctx, filename)

######################################################################################################

    @commands.command(aliases=['qjoke', 'joke', 'qj'], brief='Fetch a random quantum joke.', description='Fetches a random quantum joke stored in a text file. Supports no arguments.')
    async def quantumjoke(self, ctx):
        await ctx.send(choice(self.jokes).strip())

######################################################################################################

    @commands.command(aliases=['ars', 'asr', 'aaaarandomsearch'], brief='Search aaaa.lobadk.com and return a random result.', description='Queries aaaa.lobadk.com with the provided search, and returns a random file from it. Supports one argument')
    async def arsearch(self, ctx, search_keyword=""):
        await ArSearchCommand(self, ctx, search_keyword)

######################################################################################################

    @commands.command(aliases=['pong'], brief="Test if the bot works, and it's latency.", description="Tests if the bot is seeing the command as well as capable of responding. Supports one, but not required, argument, as 'latency'. If latency argument is used, tests and displays the one-way latency from your home, to Discord, and then to the bot (with a multiplication of 2 to simulate round-trip), as well as the round-trip latency between the bot and Discord.")
    async def ping(self, ctx, ping_mode=""):
        await PingCommand(self, ctx, ping_mode)

######################################################################################################

    @commands.command(aliases=['acount', 'countaaaa', 'counta'], brief='Counts the images and videos stored on aaaa.lobadk.com.', description="Counts the amount of images and videos that are stored on aaaa.lobadk.com, excluding any unrelated files, as well as folders.")
    async def aaaacount(self, ctx):
        await aaaaCountCommand(self, ctx)

######################################################################################################

    @commands.command(aliases=['quantumball', 'qball'], brief='standard 8ball replies, but with some quantum mixed.', description='Uses the standard 8ball replies, but with some quantum related replies or addition to the messages. Accepts no arguments.')
    async def QuantumBall(self, ctx):
        await QuantumBallCommand(self, ctx)

    print('Started Field!')
async def setup(bot):
    await bot.add_cog(Field(bot))
