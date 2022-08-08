import random
from urllib.parse import urljoin
from num2words import num2words

import requests
from bs4 import BeautifulSoup
from discord.ext import commands


class Main(commands.Cog):
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
    async def entangle(self, ctx, *, arg):
        await ctx.send(f'Quantum entangles {arg} to the {num2words(random.randint(1,1000), to="ordinal_num")} {random.choice(["reality","universe","dimension","timeline"])}')

    @commands.command()
    async def pet(self, ctx, *, arg):
        mention = f'<@{self.bot.user.id}>'
        if mention in arg:
            quantummode = random.choice(['purr','frequency'])
            if quantummode == 'purr':
                await ctx.send(f'Quantum purrs across {random.randint(2,100)} {random.choices(["dimensions","universes","realities","timelines","dimensions, universes, realities and timelines"], weights=[100,100,100,100,1], k=1)[0]}')
            elif quantummode == 'frequency':
                await ctx.send(f'Quantum vibrates at a frequency of {random.randint(1,69400)}')
            return
        verb = random.choice(["petted","pets"])
        if verb == 'petted':
            quantumtime = (f'{random.randint(1,24)} hours, {random.randint(0,31)} days, {random.randint(0,12)} months and {random.randint(0,150)} years ago')
        elif verb == 'pets':
            present = random.choice(['now','future'])
            if present == 'now':
                quantumtime = ('in present time')
            elif present == 'future':
                quantumtime = (f'{random.randint(1,24)} hour(s), {random.randint(0,31)} days, {random.randint(0,12)} months and {random.randint(0,150)} years into the future')
        await ctx.send(f'Quantum {verb} {arg} {quantumtime}')

def setup(bot):
    bot.add_cog(Main(bot))
