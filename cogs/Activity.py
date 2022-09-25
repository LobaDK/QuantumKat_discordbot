import random

import discord
from discord.ext import commands, tasks
from num2words import num2words


class Activity(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.index = 0

        hissList = ['Hissing',
                    'Hissed']
        
        purgeList = ['Purrging',
                     'Purrged']

        purrList = ['Purring',
                    'Purred']

        vibrateList = ['Vibrating',
                       'Vibrated']

        nounList = ["a chair",
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
                    "a blackhole","a random star",
                    "a random planet",
                    "Earth"]

        locationList = ['dimension',
                        'universe',
                        'timeline',
                        'reality']

        messages = ['{hiss} in the {ordinal} {location}',
                    '{purr} in the {ordinal} {location}',
                    '{hiss} at {noun} in the {ordinal} {location}',
                    '{purr} at {noun} in the {ordinal} {location}',
                    '{vibrate} at {purrHz}hz in the {ordinal} {location}',
                    '{purr} at {purrHz}hz in the {ordinal} {location}',
                    '{purge} {noun} in the {oridnal} {location}']
            
        self.change_activity.start(hissList, purgeList, purrList, vibrateList, nounList, locationList, messages)

    def cog_unload(self):
        self.change_activity.cancel()

    @tasks.loop(minutes=random.randint(30,180))
    async def change_activity(self, hissList, purgeList, purrList, vibrateList, nounList, locationList, messages):
        print('Activity loop started!')
        self.change_activity.change_interval(minutes=(random.randint(30,360)))

        purrHz = random.randint(1,100000)
        ordinal = num2words(random.randint(0,10000), to='ordinal_num')

        await self.bot.change_presence(activity=discord.Game(name=random.choice(messages).format(hiss=random.choice(hissList),
                                                                                                    purge=random.choice(purgeList),
                                                                                                    purr=random.choice(purrList),
                                                                                                    vibrate=random.choice(vibrateList),
                                                                                                    noun=random.choice(nounList),
                                                                                                    location=random.choice(locationList),
                                                                                                    purrHz=purrHz,
                                                                                                    ordinal=ordinal)))
    
    @change_activity.before_loop
    async def before_change_activity(self):
        print('Starting Activity loop...')
        await self.bot.wait_until_ready()

def setup(bot):
    bot.add_cog(Activity(bot))
