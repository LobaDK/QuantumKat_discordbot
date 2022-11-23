import random
import re
import time
import glob
import ntplib
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup
from discord.ext import commands
from num2words import num2words


class Field(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        #Open the file and load each joke per line into a list
        jokefile = open('./files/quantumjokes.txt', 'r')
        self.jokes = [joke for joke in jokefile.readlines() if joke.strip()]
        jokefile.close()

###################################################################################################### command splitter for easier reading and navigating

    async def arpr(self, ctx, url):
        links = []
        for _ in range(ctx.message.content.split(" ")[0].count("r")):
            response = requests.get(url)
            soup = BeautifulSoup(response.text, 'lxml')
            link = soup.find('body')
            links.append(url.replace('botrandom', '') + link.get_text().replace('./', ''))
        await ctx.send('\n'.join(links))

######################################################################################################

    @commands.command(aliases=['arr','arrr','arrrr','arrrrr'], brief='Returns a random file from aaaa.lobadk.com.', description="Takes no arguments, but up to 5 r' can be appended, each fetching another random file from aaaa.lobadk.com.")
    async def ar(self, ctx):
        url = 'https://aaaa.lobadk.com/botrandom'
        await self.arpr(ctx, url)
        
######################################################################################################

    @commands.command(aliases=['or', 'orr','orrr','orrrr','orrrrr'], brief='Returns a random file from possum.lobadk.com.', description="Takes no arguments, but up to 5 r' can be appended, each fetching another random file from possum.lobadk.com.")
    async def pr(self, ctx):
        url = 'https://possum.lobadk.com/botrandom'
        await self.arpr(ctx, url)

######################################################################################################

    @commands.command(aliases=['pæt','pets','pæts'], brief='Pets another user, the bot or themselves a random amount.', description='Supports one argument, being whatever or whoever the user wants to pet. If no argument is included, the bot pets the user who ran the command. Does between a 1 and 20 long pet.')
    async def pet(self, ctx, *, optional_user_or_object=""):
        quantum_amount = random.randint(1,20)
        if quantum_amount == 1:
            verb = 'time'
        else:
            verb = 'times'
        
        pets = 'pe' + 't' * quantum_amount + 's'
        
        if not optional_user_or_object:
            await ctx.send(f'Superpositions {quantum_amount} {verb} around {ctx.author.mention} and {pets}')
            return
        
        mention = f'<@{self.bot.user.id}>'
        if mention in optional_user_or_object:
            quantumspan = random.randint(0,100)
            quantummode = random.choices(['purr','frequency','quantumloop'], k=1, weights=[10,10,2])[0]
            if quantummode == 'purr':
                await ctx.send(f'Quantum purrs across {quantumspan} {random.choices(["dimension","universe","reality","timeline","dimension, universe, realitie and timeline"], weights=[100,100,100,100,1], k=1)[0] if quantumspan == 1 else random.choices(["dimensions","universes","realities","timelines","dimensions, universes, realities and timelines"], weights=[100,100,100,100,1], k=1)[0]}')
            elif quantummode == 'frequency':
                await ctx.send(f'Quantum vibrates at {random.randint(1,100_000)}hz')
            elif quantummode == 'quantumloop':
                petloop = ""
                for _ in range(0,random.randint(8,40)):
                    petloop = petloop + random.choice(['pet','pat','petting', 'patting'])
                await ctx.send(f'Quantum Loop pet initiated trying to pet self! {petloop}')
        else:
            await ctx.send(f'Superpositions {quantum_amount} {verb} around {optional_user_or_object} and {pets}')

######################################################################################################

    @commands.command(aliases=['hugs'], brief='Hugs another user, the bot or themselves a random amount.', description='Supports one argument, being whatever or whoever the user wants to hug. If no argument is included, the bot hugs the user who ran the command. Does between a 1 and 20 long hug.')
    async def hug(self, ctx, *, optional_user_or_object=""):
        quantum_amount = random.randint(1,20)
        if quantum_amount == 1:
            verb = 'time'
        else:
            verb = 'times'
        quantumspan = random.randint(0,100)

        hugs = 'hu' + 'g' * quantum_amount + 's'

        if not optional_user_or_object:
            await ctx.send(f'Superpositions {quantum_amount} {verb} around {optional_user_or_object} and {hugs}')
            return

        mention = f'<@{self.bot.user.id}>'
        if mention in optional_user_or_object:
            quantummode = random.choice(['purr','frequency'])
            if quantummode == 'purr':
                await ctx.send(f'Quantum purrs and entangles {ctx.author.mention} to the {num2words(quantumspan, to="ordinal_num")} {random.choice(["dimension","universe","reality","timeline"])}')
            elif quantummode == 'frequency':
                await ctx.send(f'Quantum vibrates at {random.randint(1,100_000)}hz, teleporting {random.choice(["a chair","a table","a vase","a long-lost creditcard","some strangers phone","a stranger","an error","a bucket","a bucket of milk","||redacted||","a cat","a quantum cat","an alien from the 7th dimension","a blackhole","a random star","a random planet"])} from the {num2words(quantumspan, to="ordinal_num")} {random.choice(["dimension","universe","reality","timeline"])}')
        else:
            await ctx.send(f'Superpositions {quantum_amount} {verb} around {optional_user_or_object} and {hugs}')

######################################################################################################

    @commands.command(aliases=['quantumpæt','qpet','qpæt','quantumpæts','quantumpets','qpets','qpæts'], brief='Pets another user, the bot or themselves a large random amount.', description='Supports one argument, being whatever or whoever the user wants to pet. If no argument is included, the bot pets the user who ran the command. Does between a 100 and 1000 long pet.')
    async def quantumpet(self, ctx, *, optional_user_or_object=""):
        mention = f'<@{self.bot.user.id}>'
        quantum_amount = random.randint(100,1000)
        qpets = 'pe' + 't' * int(str(quantum_amount)[:2]) + 's'
        if not optional_user_or_object:
            await ctx.send(f'Superpositions {quantum_amount} times across all timelines, dimensions, universes and realities, and {qpets} {ctx.author.mention}')
        elif mention in optional_user_or_object:
            quantumpetloop = ""
            for _ in range(0,random.randint(8,40)):
                quantumpetloop = quantumpetloop + random.choice(['Quantum petting the','QuantumKat','QuantumKatting the','Quantum pet'])
            await ctx.send(f'{quantumpetloop}... Instability detected, sucessfully terminated the {random.choice(["dimension","universe","reality","timeline","chair","table","error","object","||redacted||","corruptcorruptcorruptcorrupt","corrupt","future","past","presence","instability","stability","..."])}!')
        else:
            await ctx.send(f'Superpositions {quantum_amount} times across all timelines, dimensions, universes and realities, and {qpets} {optional_user_or_object}')

######################################################################################################

    @commands.command(aliases=['quantumhøg','qhug','qhøg','quantumhøgs','quantumhugs','qhugs','qhøgs'], brief='Hugs another user, the bot or themselves a large random amount.', description='Supports one argument, being whatever or whoever the user wants to hug. If no argument is included, the bot hugs the user who ran the command. Does between a 100 and 1000 long hug.')
    async def quantumhug(self, ctx, *, optional_user_or_object=""):
        mention = f'<@{self.bot.user.id}>'
        quantum_amount = random.randint(100,1000)
        qhugs = 'hu' + 'g' * int(str(quantum_amount)[:2]) + 's'
        if not optional_user_or_object:
            await ctx.send(f'Superpositions {quantum_amount} times across all timelines, dimensions, universes and realities, and {qhugs} {ctx.author.mention}')
        elif mention in optional_user_or_object:
            quantumhugloop = ""
            for _ in range(0,random.randint(8,40)):
                quantumhugloop = quantumhugloop + random.choice(['Quantum hugging the','QuantumKat','QuantumKatting the','Quantum hug'])
            await ctx.send(f'{quantumhugloop}... Instability detected, sucessfully terminated the {random.choice(["dimension","universe","reality","timeline","chair","table","error","object","||redacted||","corruptcorruptcorruptcorrupt","corrupt","future","past","presence","instability","stability","..."])}!')
        else:
            await ctx.send(f'Superpositions {quantum_amount} times across all timelines, dimensions, universes and realities, and {qhugs} {optional_user_or_object}')

######################################################################################################

    @commands.command(aliases=['rockpaperscissor'], brief='Rock, Paper, Scissors game.', description='A Rock, Paper, Scissors game. Supports one argument, being the chosen gesture. Emote is also supported. Is not rigged.')
    async def rps(self, ctx, *, item=""):
        substring = ['rock','rocks','paper','papers','scissor','scissors','✂️','🪨','🧻']
        if any(_ in item.lower() for _ in substring):
            whowin = random.choices(['I win!','You win!'], k=1, weights=[100,5])[0]
            if item == 'scissor':
                item = item + 's'
            elif item == 'rocks' or item == 'papers':
                item = item[:-1]
            if whowin == 'I win!':
                winItem = {"rock": "paper",
                            "paper": "scissors",
                            "scissors": "rock"}

                await ctx.send(f"{winItem[item]}. {whowin} You do know I'm a quantum kat, right?")
            else:
                winItem = {"paper": "rock",
                            "scissors": "paper",
                            "rock": "scissors"}
                await ctx.send(f'{winItem[item]}. {whowin}')
        else:
            await ctx.send('Rock, paper or scissors required')

######################################################################################################

    @commands.command(aliases=['as','asearch'], brief='aaaa search function.', description='Searches aaaa with the given argument and returns the results. Only takes one, and limited to a minimum of two characters, being alphanumeric as well as a dot.')
    async def aaaasearch(self, ctx, search_keyword=""):
        if len(search_keyword) >= 2:
            allowed = re.compile('^(\.?)[a-zA-Z0-9]+(\.?)$')
            if allowed.match(search_keyword):
                response = requests.get(f'https://aaaa.lobadk.com/?search={search_keyword}')
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

######################################################################################################

    @commands.command(brief='Appends filename to aaaa.lobadk.com.', description='Appends the provided filename to the end of aaaa.lobadk.com/, to quickly link the file. Only alphanumeric characters and a dot is allowed.')
    async def a(self, ctx, filename=""):
        if filename:
            allowed = re.compile('[^\w.\-]')
            if not allowed.match(filename):
                URL = f'https://aaaa.lobadk.com/{filename}'
                if requests.head(URL).status_code == 200:
                    await ctx.send(URL)
                else:
                    await ctx.send('File not found')
        else:
            await ctx.send('Filename required!\n```?a example.mp4```')

######################################################################################################

    @commands.command(aliases=['qjoke', 'joke', 'qj'], brief='Fetch a random quantum joke.', description='Fetches a random quantum joke stored in a text file. Supports no arguments.')
    async def quantumjoke(self, ctx):
        await ctx.send(random.choice(self.jokes).strip())

######################################################################################################

    @commands.command(aliases=['ars', 'asr', 'aaaarandomsearch'], brief='Search aaaa.lobadk.com and return a random result.', description='Queries aaaa.lobadk.com with the provided search, and returns a random file from it. Supports one argument')
    async def arsearch(self, ctx, search_keyword=""):
        if search_keyword:
            allowed = re.compile('[^\w.\-]')
            if not allowed.match(search_keyword):
                links = []
                SearchURL = f'https://aaaa.lobadk.com/?search={search_keyword}'
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

######################################################################################################

    @commands.command(aliases=['pong'], brief="Test if the bot works, and it's latency.", description="Tests if the bot is seeing the command as well as capable of responding. Supports one, but not required, argument, as 'latency'. If latency argument is used, tests and displays the one-way latency from your home, to Discord, and then to the bot (with a multiplication of 2 to simulate round-trip), as well as the round-trip latency between the bot and Discord.")
    async def ping(self, ctx, ping_mode=""):
        LatencyResponses = ['Fiber is fast and all but they really should consider swapping to QuantumCables:tm:.',"You know, I could've quantised *at least* 100x the amount of data in that time.", 'That was a nice nap.', "Do you realize how many times I could've been pet in that amount of time!", 'And so close to beating your alternate-self from another dimension too!', "Let's just not tell your alternate-self from another dimension..."]

        if ctx.message.content.startswith('?ping'):
            pingresponse = 'pong'
        
        elif ctx.message.content.startswith('?pong'):
            pingresponse = 'ping'
        
        if ping_mode:
            if ping_mode.lower() == 'latency':
                
                #Get current local time on the machine clock and multiply by 1000 to get milliseconds
                local_time_in_ms = (round(time.time() * 1000))

                #Get the time the message was sent in milliseconds by multiplying by 1000
                message_timestamp = (round(ctx.message.created_at.timestamp() * 1000))

                #Get latency in milliseconds by subtracting the current time, with the time the message was sent
                latency = local_time_in_ms - message_timestamp

                #If the latency is negative i.e. system clock is behind the real world by more than the latency
                #Get a rough estimate of the latency instead, by taking the offset, turning it into milliseconds, and adding it to the latency
                if latency < 0:
                    c = ntplib.NTPClient()
                    response = c.request('pool.ntp.org', version=3)
                    offset = round(response.offset * 1000)
                    latency += offset
                    await ctx.send(f'A negative latency value was detected. Used pool.ntp.org to attempt to correct, with a {round(offset)}ms offset.')


                await ctx.send(f'{pingresponse}! Took {latency * 2}ms. {random.choice(LatencyResponses)}\nConnection to discord: {round(self.bot.latency * 1000)}ms')
            else:
                await ctx.send("Only 'latency' parameter allowed")
        else:
            await ctx.send(pingresponse)

######################################################################################################

    @commands.command(aliases=['acount', 'countaaaa', 'counta'], brief='Counts the images and videos stored on aaaa.lobadk.com.', description="Counts the amount of images and videos that are stored on aaaa.lobadk.com, excluding any unrelated files, as well as folders.")
    async def aaaacount(self, ctx):
        extensions = ['*.gif', '*.jpeg', '*.jpg', '*.mov', '*.mp3', '*.mp4', '*.png', '*.webm', '*.webp']
        all_files = []
        for extension in extensions:
            current_extension = glob.glob(f'/var/www/aaaa/{extension}')
            all_files += current_extension
        await ctx.send(f'There are currently {len(all_files)} quantised datasets.')

######################################################################################################

    @commands.command(aliases=['quantumball', 'qball'], brief='standard 8ball replies, but with some quantum mixed.', description='Uses the standard 8ball replies, but with some quantum related replies or addition to the messages. Accepts no arguments.')
    async def QuantumBall(self, ctx):
        affirmative_answers_list = ['It is certain.', 'It is decidedly so.', 'Without a doubt.', 'Yes definitely.', 'You may rely on it.', 'As I see it, yes.', 'Most likely.', 'Outlook good.', 'Yes.', 'Signs point to yes.']
        non_committal_answers_list = ['Reply hazy, try again.', 'Ask again later.', 'Better not tell you now.', 'Cannot predict now.', 'Concentrate and ask again.']
        negative_answers_list = ["Don't count on it.", 'My reply is no.', 'My sources say no.', 'Outlook not so good.', 'Very doubtful.']
        reason_list = ['Quantum tunnel unexpectedly collapsed!', 'Entanglement lost!', 'Was that vase always broken?', 'Error', '||redacted||', 'Universal instability detected!']
        quantumball_messages_list = ['{amount} {location} agrees or already happened in. {affirmative_answer}', '{reason}. {non_committal_answer}', 'No related parallel universe, dimension, timeline or reality detected! {negative_answer}']

        amount = random.randint(100, 100_000)

        await ctx.send(random.choices(quantumball_messages_list, k=1, weights=[10, 5, 5])[0].format(amount=amount, location=random.choice(['realities','universes','dimensions','timelines']), affirmative_answer=random.choice(affirmative_answers_list), reason=random.choice(reason_list), non_committal_answer=random.choice(non_committal_answers_list), negative_answer=random.choice(negative_answers_list)))

    print('Started Field!')
async def setup(bot):
    await bot.add_cog(Field(bot))
