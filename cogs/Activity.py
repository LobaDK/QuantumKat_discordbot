import random

import discord
from discord.ext import commands, tasks
from num2words import num2words


class Activity(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        self.hissList = ['Hissing',
                    'Hissed']
        
        self.purgeList = ['Purrging',
                     'Purrged']

        self.purrList = ['Purring',
                    'Purred']

        self.vibrateList = ['Vibrating',
                       'Vibrated',
                       'Fluctuating',
                       'Fluctuated']

        self.nounList = ["a chair",
                    "a table",
                    "a vase",
                    "a long-lost creditcard",
                    "some strangers phone",
                    "a stranger",
                    "an error",
                    "a bucket",
                    "a bucket of milk",
                    "redacted",
                    "a cat",
                    "a quantum cat",
                    "an alien from the 7th dimension",
                    "a blackhole",
                    "a random star",
                    "a random planet",
                    "Earth",
                    'the void']

        self.locationList = ['dimension',
                        'universe',
                        'timeline',
                        'reality']

        self.messages = ['{hiss} in the {ordinal} {location}',
                    '{purr} in the {ordinal} {location}',
                    '{hiss} at {noun} in the {ordinal} {location}',
                    '{purr} at {noun} in the {ordinal} {location}',
                    '{vibrate} at {purrHz}hz in the {ordinal} {location}',
                    '{purr} at {purrHz}hz in the {ordinal} {location}',
                    '{purge} {noun} in the {ordinal} {location}',
                    'Segfault in... ErrorIt?656E64       rebooting faulty... rF7_Q>~bTV',
                    '69 74 77 61 73 6e 27 74 73 75 70 70 6f 73 65 64 74 6f 65 6e 64']
        
        self.change_activity.start()

###################################################################################################### command splitter for easier reading and navigating

    def cog_unload(self):
        self.change_activity.cancel()

######################################################################################################

    @tasks.loop(minutes=random.randint(30,180), count=None, reconnect=True)
    async def change_activity(self):
        self.change_activity.change_interval(minutes=(random.randint(30,180)))

        purrHz = random.randint(1,100_000)
        ordinal = num2words(random.randint(0,10_000), to='ordinal_num')

        await self.bot.change_presence(activity=discord.Game(name=random.choice(self.messages).format(hiss=random.choice(self.hissList),
                                                                                                    purge=random.choice(self.purgeList),
                                                                                                    purr=random.choice(self.purrList),
                                                                                                    vibrate=random.choice(self.vibrateList),
                                                                                                    noun=random.choice(self.nounList),
                                                                                                    location=random.choice(self.locationList),
                                                                                                    purrHz=purrHz,
                                                                                                    ordinal=ordinal)))

######################################################################################################

    @change_activity.before_loop
    async def before_change_activity(self):
        print('Starting Activity loop...')
        await self.bot.wait_until_ready()

######################################################################################################

    @commands.command(aliases=['activitystop', 'astop'], brief='(Bot owner only) Stops the displayed activity.', description='Stops the loop that displays a random activity under the bot.')
    @commands.is_owner()
    async def ActivityStop(self, ctx):
        if self.change_activity.is_running():
            self.change_activity.cancel()
            await ctx.message.add_reaction('👌')
        else:
            await ctx.send('Activity is not running!')

######################################################################################################

    @commands.command(aliases=['activityrestart', 'arestart', 'ActivityRefresh', 'activityrefresh', 'arefresh'], brief='(Bot owner only) Restarts/Refreshes the displayed activity.', description='Restarts/Refreshes the loop that displays a random activity under the bot.')
    @commands.is_owner()
    async def ActivityRestart(self, ctx):
        self.change_activity.restart()
        await ctx.message.add_reaction('👌')

######################################################################################################

    @commands.command(aliases=['activitystart', 'astart'], brief='(Bot owner only) Starts displaying a random activity.', description='Starts the loop that displays a random activity under the bot. A random interval between 30 to 180 minutes is chosen each time it loops itself.')
    @commands.is_owner()
    async def ActivityStart(self, ctx):
        if not self.change_activity.is_running():
            self.change_activity.start()
            await ctx.message.add_reaction('👌')
        else:
            await ctx.send('Activity is already running!')

######################################################################################################

async def setup(bot):
    await bot.add_cog(Activity(bot))
