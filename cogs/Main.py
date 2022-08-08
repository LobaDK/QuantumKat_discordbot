import random
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup
from discord.ext import commands


class Main(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        @commands.command()
        async def ar(self, ctx):
            if ctx.content.startswith("ar"):
                randomurl('https://aaaa.lobadk.com/', ctx)
            elif ctx.content.startswith("or"):
                randomurl('https://possum.lobadk.com/', ctx)
        def randomurl(url, ctx):
            links = []
            reponse = requests.get(url)
            soup = BeautifulSoup(reponse.text, 'lxml')
            for link in soup.find_all('a'):
                temp = link.get('href')
                if temp.startswith('http') or temp.startswith(',') or temp.startswith('.'):
                    continue
                links.append(temp)
            ctx.send(urljoin(url,random.choice(links)))
def setup(bot):
    bot.add_cog(Main(bot))
