import random

import discord
from discord.ext import commands, tasks
from num2words import num2words


class Activity(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.index = 0
        self.change_activity.start()

    def cog_unload(self):
        self.change_activity.cancel()

    @tasks.loop(minutes=random.randint(30,360))
    async def change_activity(self):
        self.change_activity.change_interval(minutes=(random.randint(30,360)))
        action = random.choice(['Purring','Purred', 'Hissing', 'Hissed', 'Vibrating', 'Vibrated', 'Purrging', 'Purrged'])
        prefix_location = num2words(random.randint(0,10000), to='ordinal_num')
        suffix_location = random.choice(['dimension','universe','timeline','universe'])
        if action == 'Purring' or action == 'Purred':
            await self.bot.change_presence(activity=discord.Game(name=f'{action} in the {prefix_location} {suffix_location}'))
        elif action == 'Hissing' or action == 'Hissed':
            action_suffix = random.choice(["a chair","a table","a vase","a long-lost creditcard","some strangers phone","a stranger","an error","a bucket","a bucket of milk","redacted","a cat","a quantum cat","an alien from the 7th dimension","a blackhole","a random star","a random planet", "Earth"])
            await self.bot.change_presence(activity=discord.Game(name=f'{action} at {action_suffix} in the {prefix_location} {suffix_location}'))
        elif action == 'Vibrating' or action == 'Vibrated':
            action_suffix = random.randint(1,100000)
            await self.bot.change_presence(activity=discord.Game(name=f'{action} at {action_suffix}hz in the {prefix_location} {suffix_location}'))
        elif action == 'Purrging' or action == 'Purrged':
            action_suffix = random.choice(["a chair","a table","a vase","a long-lost creditcard","some strangers phone","a stranger","an error","a bucket","a bucket of milk","redacted","a cat","a quantum cat","an alien from the 7th dimension","a blackhole","a random star","a random planet", "Earth"])
            await self.bot.change_presence(activity=discord.Game(name=f'{action} {action_suffix} in the {prefix_location} {suffix_location}'))

def setup(bot):
    bot.add_cog(Activity(bot))
