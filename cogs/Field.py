import random
import re
import time
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup
from discord.ext import commands
from num2words import num2words


class Field(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        jokefile = open('./files/quantumjokes.txt', 'r')
        self.jokes = [joke for joke in jokefile.readlines() if joke.strip()]
        jokefile.close()

    async def arpr(self, ctx, url):
        links = []
        for _ in range(ctx.message.content.split(" ")[0].count("r")):
            response = requests.get(url)
            soup = BeautifulSoup(response.text, 'lxml')
            link = soup.find('body')
            links.append(url.replace('botrandom', '') + link.get_text().replace('./', ''))
        await ctx.send('\n'.join(links))

    @commands.command(aliases=['arr','arrr','arrrr','arrrrr'], brief='Returns a random file from aaaa.lobadk.com.', description="Takes no arguments, but up to 5 r' can be appended, each fetching another random file from aaaa.lobadk.com.")
    async def ar(self, ctx):
        url = 'https://aaaa.lobadk.com/botrandom'
        await self.arpr(ctx, url)
        

    @commands.command(aliases=['or', 'orr','orrr','orrrr','orrrrr'], brief='Returns a random file from possum.lobadk.com.', description="Takes no arguments, but up to 5 r' can be appended, each fetching another random file from possum.lobadk.com.")
    async def pr(self, ctx):
        url = 'https://possum.lobadk.com/botrandom'
        await self.arpr(ctx, url)

    @commands.command(aliases=['pæt','pets','pæts'], brief='Pets another user, the bot or themselves a random amount.', description='Supports one argument, being whatever or whoever the user wants to pet. If no argument is included, the bot pets the user who ran the command. Does between a 1 and 20 long pet.')
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
        else:
            await ctx.send(f'Superpositions {quantum_amount} {verb} around {arg} and {pets}')

    @commands.command(aliases=['hugs'], brief='Hugs another user, the bot or themselves a random amount.', description='Supports one argument, being whatever or whoever the user wants to hug. If no argument is included, the bot hugs the user who ran the command. Does between a 1 and 20 long hug.')
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
                await ctx.send(f'Quantum vibrates at {random.randint(1,100000)}hz, teleporting {random.choice(["a chair","a table","a vase","a long-lost creditcard","some strangers phone","a stranger","an error","a bucket","a bucket of milk","||redacted||","a cat","a quantum cat","an alien from the 7th dimension","a blackhole","a random star","a random planet"])} from the {num2words(quantumspan, to="ordinal_num")} {random.choice(["dimension","universe","reality","timeline"])}')
        else:
            await ctx.send(f'Superpositions {quantum_amount} {verb} around {arg} and {hugs}')
    
    @commands.command(aliases=['quantumpæt','qpet','qpæt','quantumpæts','quantumpets','qpets','qpæts'], brief='Pets another user, the bot or themselves a large random amount.', description='Supports one argument, being whatever or whoever the user wants to pet. If no argument is included, the bot pets the user who ran the command. Does between a 100 and 1000 long pet.')
    async def quantumpet(self, ctx, *, arg=""):
        mention = f'<@{self.bot.user.id}>'
        quantum_amount = random.randint(100,1000)
        qpets = 'pe' + 't' * int(str(quantum_amount)[:2]) + 's'
        if not arg:
            await ctx.send(f'Superpositions {quantum_amount} times across all timelines, dimensions, universes and realities, and {qpets} {ctx.author.mention}')
        elif mention in arg:
            quantumpetloop = ""
            for _ in range(0,random.randint(8,40)):
                quantumpetloop = quantumpetloop + random.choice(['Quantum petting the','QuantumKat','QuantumKatting the','Quantum pet'])
            await ctx.send(f'{quantumpetloop}... Instability detected, sucessfully terminated the {random.choice(["dimension","universe","reality","timeline","chair","table","error","object","||redacted||","corruptcorruptcorruptcorrupt","corrupt","future","past","presence","instability","stability","..."])}!')
        else:
            await ctx.send(f'Superpositions {quantum_amount} times across all timelines, dimensions, universes and realities, and {qpets} {arg}')

    @commands.command(aliases=['quantumhøg','qhug','qhøg','quantumhøgs','quantumhugs','qhugs','qhøgs'], brief='Hugs another user, the bot or themselves a large random amount.', description='Supports one argument, being whatever or whoever the user wants to hug. If no argument is included, the bot hugs the user who ran the command. Does between a 100 and 1000 long hug.')
    async def quantumhug(self, ctx, *, arg=""):
        mention = f'<@{self.bot.user.id}>'
        quantum_amount = random.randint(100,1000)
        qhugs = 'hu' + 'g' * int(str(quantum_amount)[:2]) + 's'
        if not arg:
            await ctx.send(f'Superpositions {quantum_amount} times across all timelines, dimensions, universes and realities, and {qhugs} {ctx.author.mention}')
        elif mention in arg:
            quantumhugloop = ""
            for _ in range(0,random.randint(8,40)):
                quantumhugloop = quantumhugloop + random.choice(['Quantum hugging the','QuantumKat','QuantumKatting the','Quantum hug'])
            await ctx.send(f'{quantumhugloop}... Instability detected, sucessfully terminated the {random.choice(["dimension","universe","reality","timeline","chair","table","error","object","||redacted||","corruptcorruptcorruptcorrupt","corrupt","future","past","presence","instability","stability","..."])}!')
        else:
            await ctx.send(f'Superpositions {quantum_amount} times across all timelines, dimensions, universes and realities, and {qhugs} {arg}')
    
    @commands.command(aliases=['rockpaperscissor'], brief='Rock, Paper, Scissors game.', description='A Rock, Paper, Scissors game. Supports one argument, being the chosen gesture. Emote is also supported. Is not rigged.')
    async def rps(self, ctx, *, arg=""):
        substring = ['rock','rocks','paper','papers','scissor','scissors','✂️','🪨','🧻']
        if any(_ in arg.lower() for _ in substring):
            whowin = random.choices(['I win!','You win!'], k=1, weights=[100,5])[0]
            if arg == 'scissor':
                arg = arg + 's'
            elif arg == 'rocks' or arg == 'papers':
                arg = arg[:-1]
            if whowin == 'I win!':
                winItem = {"rock": "paper",
                            "paper": "scissors",
                            "scissors": "rock"}

                await ctx.send(f"{winItem[arg]}. {whowin} You do know I'm a quantum kat, right?")
            else:
                winItem = {"paper": "rock",
                            "scissors": "paper",
                            "rock": "scissors"}
                await ctx.send(f'{winItem[arg]}. {whowin}')
        else:
            await ctx.send('Rock, paper or scissors required')

    @commands.command(aliases=['as','asearch'], brief='aaaa search function.', description='Searches aaaa with the given argument and returns the results. Only takes one, and limited to a minimum of two characters, being alphanumeric as well as a dot.')
    async def aaaasearch(self, ctx, arg=""):
        if len(arg) >= 2:
            allowed = re.compile('^(\.?)[a-zA-Z0-9]+(\.?)$')
            if allowed.match(arg):
                response = requests.get(f'https://aaaa.lobadk.com/?search={arg}')
                soup = BeautifulSoup(response.text, 'lxml')
                links = []

                for link in soup.find_all('a'):
                    temp = link.get('href')
                    if temp.startswith('http') or temp.startswith(',') or temp.startswith('.'):
                        continue
                    links.append(temp)

                if len(links) == 0:
                    await ctx.send('Search returned nothing')
                else:
                    if len(' '.join(links)) > 4000:
                        await ctx.send('Too many results! Try narrowing down the search')
                    else:
                        await ctx.send(' '.join(links))
            else:
                await ctx.send('At least two alphanumeric characters are required, or 1 alphanumeric character and a `.` at the start or end')
        else:
            await ctx.send('Search too short! A minimum of 2 characters are required')
    
    @commands.command(brief='Appends filename to aaaa.lobadk.com.', description='Appends the provided filename to the end of aaaa.lobadk.com/, to quickly link the file. Only alphanumeric characters and a dot is allowed.')
    async def a(self, ctx, arg=""):
        if arg:
            allowed = re.compile('[^\w.\-]')
            if not allowed.match(arg):
                URL = f'https://aaaa.lobadk.com/{arg}'
                if requests.head(URL) == 200:
                    await ctx.send(URL)
                else:
                    await ctx.send('File not found')
        else:
            await ctx.send('Filename required!\n```?a example.mp4```')

    @commands.command(aliases=['qjoke', 'joke', 'qj'], brief='Fetch a random quantum joke.', description='Fetches a random quantum joke stored in a text file. Supports no arguments.')
    async def quantumjoke(self, ctx):
        await ctx.send(random.choice(self.jokes).strip())

    @commands.command(aliases=['ars', 'asr', 'aaaarandomsearch'], brief='Search aaaa.lobadk.com and return a random result.', description='Queries aaaa.lobadk.com with the provided search, and returns a random file from it. Supports one argument')
    async def arsearch(self, ctx, arg=""):
        if arg:
            allowed = re.compile('[^\w.\-]')
            if not allowed.match(arg):
                links = []
                SearchURL = f'https://aaaa.lobadk.com/?search={arg}'
                URL = 'https://aaaa.lobadk.com/'
                response = requests.get(SearchURL)
                soup = BeautifulSoup(response.text, 'lxml')
                for link in soup.find_all('a'):
                    temp = link.get('href')
                    if temp.startswith('http') or temp.startswith(',') or temp.startswith('.'):
                        continue
                    links.append(temp)
                if len(links) == 0:
                    await ctx.send('Search returned empty!')
                else:    
                    await ctx.send(urljoin(URL,random.choice(links)))
            else:
                await ctx.send('Invalid character found in search parameter!')
        else:
            await ctx.send('Search parameter required!\n```?ars example```')

    @commands.command(aliases=['pong'], brief="Test if the bot works, and it's latency.", description="Tests if the bot is seeing the command as well as capable of responding. Supports one, but not required, argument, as 'latency'. If latency argument is used, tests and displays the one-way latency from your home, to Discord, and then to the bot, as well as the round-trip latency between the bot and Discord.")
    async def ping(self, ctx, arg=""):
        LatencyResponses = ['Fiber is fast and all but they really should consider swapping to QuantumCables:tm:.',"You know, I could've quantised *at least* 100x the amount of data in that time.", 'That was a nice nap.', "Do you realize how many times I could've been pet in that amount of time!", 'And so close to beating your alternate-self from another dimension too!', "Let's just not tell your alternate-self from another dimension..."]

        if ctx.message.content.startswith('?ping'):
            pingresponse = 'pong'
        elif ctx.message.content.startswith('?pong'):
            pingresponse = 'ping'
        if arg:
            if arg.lower() == 'latency':
                await ctx.send(f'{pingresponse}! Took {(round(time.time() * 1000) - ctx.message.created_at.timestamp() * 1000)}ms. {random.choice(LatencyResponses)}\nConnection to discord: {round(self.bot.latency * 1000, 2)}ms')
            else:
                await ctx.send("Only 'latency' parameter allowed")
        else:
            await ctx.send(pingresponse)

    print('Started Field!')
async def setup(bot):
    await bot.add_cog(Field(bot))
