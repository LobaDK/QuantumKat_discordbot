import random
from num2words import num2words

import requests
from bs4 import BeautifulSoup
from discord.ext import commands

class Field(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def arpr(self, ctx, url):
        links = []
        for _ in range(ctx.message.content.split(" ")[0].count("r")):
            response = requests.get(url)
            soup = BeautifulSoup(response.text, 'lxml')
            link = soup.find('body')
            links.append(url.replace('botrandom', '') + link.get_text().replace('./', ''))
        await ctx.send('\n'.join(links))

    @commands.command(aliases=['arr','arrr','arrrr','arrrrr'])
    async def ar(self, ctx):
        url = 'https://aaaa.lobadk.com/botrandom'
        await self.arpr(ctx, url)
        

    @commands.command(aliases=['or', 'orr','orrr','orrrr','orrrrr'])
    async def pr(self, ctx):
        url = 'https://possum.lobadk.com/botrandom'
        await self.arpr(ctx, url)

    @commands.command(aliases=['pæt','pets','pæts'])
    async def pet(self, ctx, *, arg=""):
        quantum_amount = random.randint(1,20)
        if quantum_amount == 1:
            verb = 'time'
        else:
            verb = 'times'
        
        pets = 'pe' + 't' * quantum_amount + 's'
        
        if not arg:
            await ctx.send(f'Superpositions {quantum_amount} {verb} around {ctx.author.mention} and {pets}')
            return
        
        mention = f'<@{self.bot.user.id}>'
        if mention in arg:
            quantumspan = random.randint(0,100)
            quantummode = random.choices(['purr','frequency','quantumloop'], k=1, weights=[10,10,2])[0]
            if quantummode == 'purr':
                await ctx.send(f'Quantum purrs across {quantumspan} {random.choices(["dimension","universe","reality","timeline","dimension, universe, realitie and timeline"], weights=[100,100,100,100,1], k=1)[0] if quantumspan == 1 else random.choices(["dimensions","universes","realities","timelines","dimensions, universes, realities and timelines"], weights=[100,100,100,100,1], k=1)[0]}')
            elif quantummode == 'frequency':
                await ctx.send(f'Quantum vibrates at {random.randint(1,100000)}hz')
            elif quantummode == 'quantumloop':
                petloop = ""
                for _ in range(0,random.randint(8,40)):
                    petloop = petloop + random.choice(['pet','pat','petting'])
                await ctx.send(f'Quantum Loop pet initiated trying to pet self! {petloop}')
            return
        else:
            await ctx.send(f'Superpositions {quantum_amount} {verb} around {arg} and {pets}')
            return

    @commands.command(aliases=['hugs'])
    async def hug(self, ctx, *, arg=""):
        quantum_amount = random.randint(1,20)
        if quantum_amount == 1:
            verb = 'time'
        else:
            verb = 'times'
        quantumspan = random.randint(0,100)

        hugs = 'hu' + 'g' * quantum_amount + 's'

        if not arg:
            await ctx.send(f'Superpositions {quantum_amount} {verb} around {arg} and {hugs}')
            return

        mention = f'<@{self.bot.user.id}>'
        if mention in arg:
            quantummode = random.choice(['purr','frequency'])
            if quantummode == 'purr':
                await ctx.send(f'Quantum purrs and entangles {ctx.author.mention} to the {num2words(quantumspan, to="ordinal_num")} {random.choice(["dimension","universe","reality","timeline"])}')
            elif quantummode == 'frequency':
                await ctx.send(f'Quantum vibrates at {random.randint(1,100000)}hz, teleporting {random.choice(["a chair","a table","a vase","a long-lost creditcard","some strangers phone","a stranger","an error","a bucket","a bucket of milk","redacted","a cat","a quantum cat","an alien from the 7th dimension","a blackhole","a random star","a random planet"])} from the {num2words(quantumspan, to="ordinal_num")} {random.choice(["dimension","universe","reality","timeline"])}')
        else:
            await ctx.send(f'Superpositions {quantum_amount} {verb} around {arg} and {hugs}')
            return
    
    @commands.command(aliases=['quantumpæt','qpet','qpæt','quantumpæts','quantumpets','qpets','qpæts'])
    async def quantumpet(self, ctx, *, arg=""):
        mention = f'<@{self.bot.user.id}>'
        quantum_amount = random.randint(100,1000)
        qpets = 'pe' + 't' * int(str(quantum_amount)[:2]) + 's'
        if not arg:
            await ctx.send(f'Superpositions {quantum_amount} times across all timelines, dimensions, universes and realities, and {qpets} {ctx.author.mention}')
            return
        elif mention in arg:
            quantumpetloop = ""
            for _ in range(0,random.randint(8,40)):
                quantumpetloop = quantumpetloop + random.choice(['Quantum petting the','QuantumKat','QuantumKatting the','Quantum pet'])
            await ctx.send(f'{quantumpetloop}... Instability detected, sucessfully terminated the {random.choice(["dimension","universe","reality","timeline","chair","table","error","object","redacted","corruptcorruptcorruptcorrupt","corrupt","future","past","presence","instability","stability","..."])}!')
            return
        else:
            await ctx.send(f'Superpositions {quantum_amount} times across all timelines, dimensions, universes and realities, and {qpets} {arg}')
            return

    @commands.command(aliases=['quantumhøg','qhug','qhøg','quantumhøgs','quantumhugs','qhugs','qhøgs'])
    async def quantumhug(self, ctx, *, arg=""):
        mention = f'<@{self.bot.user.id}>'
        quantum_amount = random.randint(100,1000)
        qhugs = 'hu' + 'g' * int(str(quantum_amount)[:2]) + 's'
        if not arg:
            await ctx.send(f'Superpositions {quantum_amount} times across all timelines, dimensions, universes and realities, and {qhugs} {ctx.author.mention}')
            return
        elif mention in arg:
            quantumhugloop = ""
            for _ in range(0,random.randint(8,40)):
                quantumhugloop = quantumhugloop + random.choice(['Quantum hugging the','QuantumKat','QuantumKatting the','Quantum hug'])
            await ctx.send(f'{quantumhugloop}... Instability detected, sucessfully terminated the {random.choice(["dimension","universe","reality","timeline","chair","table","error","object","redacted","corruptcorruptcorruptcorrupt","corrupt","future","past","presence","instability","stability","..."])}!')
            return
        else:
            await ctx.send(f'Superpositions {quantum_amount} times across all timelines, dimensions, universes and realities, and {qhugs} {arg}')
            return
    
    @commands.command(aliases=['rockpaperscissor'])
    async def rps(self, ctx, *, arg=""):
        substring = ['rock','rocks','paper','papers','scissor','scissors','✂️','🪨','🧻']
        if any(_ in arg.lower() for _ in substring):
            whowin = random.choices(['I win!','You win!'], k=1, weights=[100,5])[0]
            if whowin == 'I win!':
                whowin = whowin + " You do know I'm a quantum kat, right?"
            await ctx.send(f'{whowin}')
        else:
            await ctx.send('Rock, paper or scissors required')

    @commands.command()
    async def aaaasearch(self, ctx, arg=""):
        if arg >= 4:
            response = requests.get(f'https://aaaa.lobadk.com/?search={arg}')
            soup = BeautifulSoup(response.text, 'lxml')
            links = []

            for link in soup.find_all('a'):
                temp = link.get('href')
                if temp.startswith('http') or temp.startswith(',') or temp.startswith('.'):
                    continue
                links.append(temp)

            ctx.send(' '.join(links))
        else:
            ctx.send('Search too short! A minimum of 4 characters are required')
def setup(bot):
    bot.add_cog(Field(bot))
