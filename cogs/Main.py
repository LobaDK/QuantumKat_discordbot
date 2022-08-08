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
    async def entangle(self, ctx):
        quantum = ['reality','universe','dimension','timeline']
        await ctx.send(f'Quantum entangles @{ctx.message.mentions[0]} to the {num2words(random.randint(1,1000), to="ordinal_num")} {random.choice(quantum)}')

def setup(bot):
    bot.add_cog(Main(bot))
