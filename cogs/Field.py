import random
from urllib.parse import urljoin
from num2words import num2words

import requests
from bs4 import BeautifulSoup
from discord.ext import commands


class Field(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def ar(self, ctx):
        url = 'https://aaaa.lobadk.com/'
        links = []
        reponse = requests.get(url)
        soup = BeautifulSoup(reponse.text, 'lxml')
        for link in soup.find_all('a'):
            temp = link.get('href')
            if temp.startswith('http') or temp.startswith(',') or temp.startswith('.'):
                continue
            links.append(temp)
        await ctx.send(urljoin(url,random.choice(links)))

    @commands.command()
    async def pr(self, ctx):
        url = 'https://possum.lobadk.com/'
        links = []
        reponse = requests.get(url)
        soup = BeautifulSoup(reponse.text, 'lxml')
        for link in soup.find_all('a'):
            temp = link.get('href')
            if temp.startswith('http') or temp.startswith(',') or temp.startswith('.'):
                continue
            links.append(temp)
        await ctx.send(urljoin(url,random.choice(links)))

    @commands.command()
    async def pet(self, ctx, *, arg=""):
        verb = random.choice(["petted","pets"])
        if verb == 'petted':
            quantumtime = (f'{random.randint(1,150)} years, {random.randint(0,12)} months, {random.randint(0,31)} days and {random.randint(0,24)} hours ago')
        elif verb == 'pets':
            present = random.choices(['now','future'], k=1, weights=[1,10])[0]
            if present == 'now':
                quantumtime = ('in present time')
            elif present == 'future':
                quantumtime = (f'{random.randint(1,150)} years, {random.randint(0,12)} months, {random.randint(0,31)} days and {random.randint(0,24)} hours into the future')
        
        if not arg:
            await ctx.send(f'Quantum {verb} {ctx.author.mention} {quantumtime}')
            return
        
        mention = f'<@{self.bot.user.id}>'
        if mention in arg:
            quantumspan = random.randint(0,100)
            quantummode = random.choices(['purr','frequency','quantumloop'], k=1, weights=[10,10,2])[0]
            if quantummode == 'purr':
                await ctx.send(f'Quantum purrs across {quantumspan} {random.choices(["dimension","universe","reality","timeline","dimension, universe, realitie and timeline"], weights=[100,100,100,100,1], k=1)[0] if quantumspan == 1 else random.choices(["dimensions","universes","realities","timelines","dimensions, universes, realities and timelines"], weights=[100,100,100,100,1], k=1)[0]}')
            elif quantummode == 'frequency':
                await ctx.send(f'Quantum vibrates at a frequency of {random.randint(1,100000)}hz')
            elif quantummode == 'quantumloop':
                petloop = ""
                for n in range(0,random.randint(8,40)):
                    petloop = petloop + random.choice(['pet','pat','petting'])
                await ctx.send(f'Quantum Loop pet initiated trying to pet self! {petloop}')
            return
        else:
            await ctx.send(f'Quantum {verb} {arg} {quantumtime}')
            return

    @commands.command()
    async def hug(self, ctx, *, arg=""):
        verb = random.choice(["hugged","hugs"])
        quantum_direction = random.choice(["left","right","behind","front"])
        quantumspan = random.randint(0,100)
        if quantum_direction == 'left' or quantum_direction == 'right':
            direction_prefix = 'from the '
        elif quantum_direction == 'front':
            direction_prefix = 'from the '
        elif quantum_direction == 'behind':
            direction_prefix = 'from '

        else:
            direction_prefix = NULL
        if verb == 'hugged':
            quantum_time = (f'{random.randint(1,1000)} years, {random.randint(0,12)} months, {random.randint(0,31)} days and {random.randint(0,24)} hours ago')
        elif verb == 'hugs':
            present = random.choices(['now','future'], k=1, weights=[1,10])[0]
            if present == 'now':
                quantum_time = ('in present time')
            elif present == 'future':
                quantum_time = (f'{random.randint(1,1000)} years, {random.randint(0,12)} months, {random.randint(0,31)} days and {random.randint(0,24)} hours into the future')
        if not arg:
            await ctx.send(f'Superpositions to {ctx.author.mention}, and {verb} {quantum_time} {direction_prefix + quantum_direction}')
            return

        mention = f'<@{self.bot.user.id}>'
        if mention in arg:
            quantummode = random.choice(['purr','frequency'])
            if quantummode == 'purr':
                await ctx.send(f'Quantum purrs and entangles {ctx.author.mention} to the {num2words(quantumspan, to="ordinal_num")} {random.choice(["dimension","universe","reality","timeline"])}')
            elif quantummode == 'frequency':
                await ctx.send(f'Quantum vibrates at {random.randint(1,100000)}hz, teleporting {random.choice(["a chair","a table","a vase","a long-lost creditcard","some strangers phone","a stranger","an error","a bucket","a bucket of milk","redacted","a cat","a quantum cat","an alien from the 7th dimension","a blackhole","a random star","a random planet"])} from the {num2words(quantumspan, to="ordinal_num")} {random.choice(["dimension","universe","reality","timeline"])}')
        else:
            await ctx.send(f'Superpositions to {arg}, and {verb} {quantum_time} {direction_prefix + quantum_direction}')
            return
def setup(bot):
    bot.add_cog(Field(bot))
