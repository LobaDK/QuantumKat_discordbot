from glob import glob
from random import choice, choices, randint, sample
from time import time
from urllib.parse import urljoin
from urllib import parse
from pathlib import Path
from asyncio import create_subprocess_shell, subprocess

from discord.ext import commands
from ntplib import NTPClient
from num2words import num2words
from re import compile


class Fields(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        self.aURL = 'https://aaaa.lobadk.com/'
        self.a_folder = '/var/www/aaaa/'
        self.pURL = 'https://possum.lobadk.com/'
        self.p_folder = '/var/www/possum/'

        self.extensions = ('jpg', 'jpeg', 'png', 'webp', 'mp4', 'gif', 'mov', 'mp3', 'webm')

        #Open the file and load each joke per line into a list
        jokefile = open('./files/quantumjokes.txt', 'r')
        self.jokes = [joke for joke in jokefile.readlines() if joke.strip()]
        jokefile.close()

    async def arpr(self, ctx, url, folder):
        files = await self.getfiles(url, folder)
        links = sample(files, k=ctx.message.content.split(" ")[0].count("r"))
        await ctx.reply('\n'.join(links), silent=True)

    async def getfiles(self, url, folder):
        files = []
        for file in glob(f'{folder}*'):
            if file.endswith(self.extensions):
                files.append(parse.urljoin(url, str(Path(file).name)))
        
        return files

    async def searchfiles(self, search_keyword):
        files = []
        p = await create_subprocess_shell(f'find {self.a_folder} -maxdepth 1 -type f -iname "*{search_keyword}*"', stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        await p.wait()
        stdout, stderr = await p.communicate()
        for file in stdout.decode().split('\n'):
            if file.endswith(self.extensions):
                files.append(str(Path(file).name))
        
        return files

######################################################################################################

    @commands.command(aliases=['arr','arrr','arrrr','arrrrr'], brief='Returns a random file from aaaa.lobadk.com.', description="Takes no arguments, but up to 5 r' can be appended, each fetching another random file from aaaa.lobadk.com.")
    async def ar(self, ctx):
        await self.arpr(ctx, self.aURL, self.a_folder)
        
######################################################################################################

    @commands.command(aliases=['or', 'orr','orrr','orrrr','orrrrr'], brief='Returns a random file from possum.lobadk.com.', description="Takes no arguments, but up to 5 r' can be appended, each fetching another random file from possum.lobadk.com.")
    async def pr(self, ctx):
        await self.arpr(ctx, self.pURL, self.p_folder)

######################################################################################################

    @commands.command(aliases=['pæt','pets','pæts'], brief='Pets another user, the bot or themselves a random amount.', description='Supports one argument, being whatever or whoever the user wants to pet. If no argument is included, the bot pets the user who ran the command. Does between a 1 and 20 long pet.')
    async def pet(self, ctx, *, optional_user_or_object=""):
        quantum_amount = randint(1,20)
        if quantum_amount == 1:
            verb = 'time'
        else:
            verb = 'times'

        pets = 'pe' + ('t' * quantum_amount) + 's'

        if not optional_user_or_object:
            await ctx.send(f'Superpositions {quantum_amount} {verb} around {ctx.author.mention} and {pets}')
            return
        
        mention = f'<@{self.bot.user.id}>'
        if mention in optional_user_or_object:
            async def quantumpurr(self, ctx):
                quantumspan = randint(0,100)
                await ctx.send(f'Quantum purrs across {quantumspan} {choices(["dimension","universe","reality","timeline","dimension, universe, realitie and timeline"], weights=[100,100,100,100,1], k=1)[0] if quantumspan == 1 else choices(["dimensions","universes","realities","timelines","dimensions, universes, realities and timelines"], weights=[100,100,100,100,1], k=1)[0]}')
            
            async def quantumfrequency(self, ctx):
                await ctx.send(f'Quantum vibrates at {randint(1,100_000)}hz')

            async def quantumloop(self, ctx):
                petloop = ''.join(choices(['pet', 'pat', 'petting', 'patting'], k=randint(8, 40)))
                await ctx.send(f'Quantum Loop pet initiated trying to pet self! {petloop}')
                    
            await choices([quantumpurr, quantumfrequency, quantumloop], k=1, weights=[10,10,2])[0](self, ctx)
        
        else:
            await ctx.send(f'Superpositions {quantum_amount} {verb} around {optional_user_or_object} and {pets}', silent=True)

######################################################################################################

    @commands.command(aliases=['hugs'], brief='Hugs another user, the bot or themselves a random amount.', description='Supports one argument, being whatever or whoever the user wants to hug. If no argument is included, the bot hugs the user who ran the command. Does between a 1 and 20 long hug.')
    async def hug(self, ctx, *, optional_user_or_object=""):
        quantum_amount = randint(1,20)
        if quantum_amount == 1:
            verb = 'time'
        else:
            verb = 'times'
        quantumspan = randint(0,100)

        hugs = 'hu' + ('g' * quantum_amount) + 's'

        if not optional_user_or_object:
            await ctx.send(f'Superpositions {quantum_amount} {verb} around {ctx.author.mention} and {hugs}')
            return

        mention = f'<@{self.bot.user.id}>'
        if mention in optional_user_or_object:
            quantummode = choice(['purr','frequency'])
            if quantummode == 'purr':
                await ctx.send(f'Quantum purrs and entangles {ctx.author.mention} to the {num2words(quantumspan, to="ordinal_num")} {choice(["dimension","universe","reality","timeline"])}')
            elif quantummode == 'frequency':
                await ctx.send(f'Quantum vibrates at {randint(1,100_000)}hz, teleporting {choice(["a chair","a table","a vase","a long-lost creditcard","some strangers phone","a stranger","an error","a bucket","a bucket of milk","||redacted||","a cat","a quantum cat","an alien from the 7th dimension","a blackhole","a random star","a random planet"])} from the {num2words(quantumspan, to="ordinal_num")} {choice(["dimension","universe","reality","timeline"])}')
        else:
            await ctx.send(f'Superpositions {quantum_amount} {verb} around {optional_user_or_object} and {hugs}', silent=True)

######################################################################################################

    @commands.command(aliases=['quantumpæt','qpet','qpæt','quantumpæts','quantumpets','qpets','qpæts'], brief='Pets another user, the bot or themselves a large random amount.', description='Supports one argument, being whatever or whoever the user wants to pet. If no argument is included, the bot pets the user who ran the command. Does between a 100 and 1000 long pet.')
    async def quantumpet(self, ctx, *, optional_user_or_object=""):
        mention = f'<@{self.bot.user.id}>'
        quantum_amount = randint(100,1000)
        qpets = 'pe' + ('t' * int(str(quantum_amount)[:2])) + 's'
        if not optional_user_or_object:
            await ctx.send(f'Superpositions {quantum_amount} times across all timelines, dimensions, universes and realities, and {qpets} {ctx.author.mention}')
        elif mention in optional_user_or_object:
            quantumpetloop = ''.join(choices(['Quantum petting the', 'QuantumKat', 'QuantumKatting the', 'Quantum pet'], k=randint(8, 40)))
            await ctx.send(f'{quantumpetloop}... Instability detected, sucessfully terminated the {choice(["dimension","universe","reality","timeline","chair","table","error","object","||redacted||","corruptcorruptcorruptcorrupt","corrupt","future","past","presence","instability","stability","..."])}!')
        else:
            await ctx.send(f'Superpositions {quantum_amount} times across all timelines, dimensions, universes and realities, and {qpets} {optional_user_or_object}', silent=True)

######################################################################################################

    @commands.command(aliases=['quantumhøg','qhug','qhøg','quantumhøgs','quantumhugs','qhugs','qhøgs'], brief='Hugs another user, the bot or themselves a large random amount.', description='Supports one argument, being whatever or whoever the user wants to hug. If no argument is included, the bot hugs the user who ran the command. Does between a 100 and 1000 long hug.')
    async def quantumhug(self, ctx, *, optional_user_or_object=""):
        mention = f'<@{self.bot.user.id}>'
        quantum_amount = randint(100,1000)
        qhugs = 'hu' + ('g' * int(str(quantum_amount)[:2])) + 's'
        if not optional_user_or_object:
            await ctx.send(f'Superpositions {quantum_amount} times across all timelines, dimensions, universes and realities, and {qhugs} {ctx.author.mention}')
        elif mention in optional_user_or_object:
            quantumhugloop = ''.join(choices(['Quantum hugging the', 'QuantumKat', 'QuantumKatting the', 'Quantum hug'], k=randint(8, 40)))
            await ctx.send(f'{quantumhugloop}... Instability detected, sucessfully terminated the {choice(["dimension","universe","reality","timeline","chair","table","error","object","||redacted||","corruptcorruptcorruptcorrupt","corrupt","future","past","presence","instability","stability","..."])}!')
        else:
            await ctx.send(f'Superpositions {quantum_amount} times across all timelines, dimensions, universes and realities, and {qhugs} {optional_user_or_object}', silent=True)

######################################################################################################

    @commands.command(aliases=['rockpaperscissor'], brief='Rock, Paper, Scissors game.', description='A Rock, Paper, Scissors game. Supports one argument, being the chosen gesture. Emote is also supported. Is not rigged.')
    async def rps(self, ctx, *, item=""):
        substring = ['rock','rocks','paper','papers','scissor','scissors','✂️','🪨','🧻']
        item = item.lower()
        if any(_ in item for _ in substring):
            whowin = choices(['I win!','You win!'], k=1, weights=[100,5])[0]
            if item == 'scissor':
                item = f'{item}s'
            elif item == 'rocks' or item == 'papers':
                item = item[:-1]
            if whowin == 'I win!':
                winItem = {"rock": "paper",
                            "paper": "scissors",
                            "scissors": "rock"}

                await ctx.reply(f"{winItem[item]}. {whowin} You do know I'm a quantum kat, right?", silent=True)
            else:
                winItem = {"paper": "rock",
                            "scissors": "paper",
                            "rock": "scissors"}
                await ctx.reply(f'{winItem[item]}. {whowin}', silent=True)
        else:
            await ctx.reply('Rock, paper or scissors required', silent=True)

######################################################################################################

    @commands.command(aliases=['as','asearch'], brief='aaaa search function.', description='Searches aaaa with the given argument and returns the results. Only takes one, and limited to a minimum of two characters, being alphanumeric as well as a dot.')
    async def aaaasearch(self, ctx, search_keyword=""):
        if len(search_keyword) >= 2:
            allowed = compile('^(\.?)[a-zA-Z0-9]+(\.?)$')
            if allowed.match(search_keyword):

                files = await self.searchfiles(search_keyword)

                if len(files) == 0:
                    await ctx.reply('Search returned nothing', silent=True)
                else:
                    if len(' '.join(files)) >= 4000:
                        await ctx.reply('Too many results! Try narrowing down the search', silent=True)
                    else:
                        await ctx.reply(' '.join(files), silent=True)
            else:
                await ctx.reply('At least two alphanumeric characters are required, or 1 alphanumeric character and a `.` at the start or end', silent=True)
        else:
            await ctx.reply('Search too short! A minimum of 2 characters are required', silent=True)

######################################################################################################

    @commands.command(brief='Appends filename to aaaa.lobadk.com.', description='Appends the provided filename to the end of aaaa.lobadk.com/, to quickly link the file. Only alphanumeric characters and a dot is allowed.')
    async def a(self, ctx, filename=""):
        if filename:
            allowed = compile('[^\w.\-]')
            if not allowed.match(filename):

                links = await self.searchfiles(filename)

                if len(links) == 1:
                    await ctx.reply(urljoin(self.aURL, links[0]))
                
                else:
                    if len(links) == 0:
                        await ctx.reply('File not found', silent=True)
                    else:
                        await ctx.reply(f'Found {len(links)} files. Please be more precise!')
        else:
            await ctx.reply('At least a partial filename is required!\n```?a example```', silent=True)

######################################################################################################

    @commands.command(aliases=['qjoke', 'joke', 'qj'], brief='Fetch a random quantum joke.', description='Fetches a random quantum joke stored in a text file. Supports no arguments.')
    async def quantumjoke(self, ctx):
        await ctx.reply(choice(self.jokes).strip(), silent=True)

######################################################################################################

    @commands.command(aliases=['ars', 'asr', 'aaaarandomsearch'], brief='Search aaaa.lobadk.com and return a random result.', description='Queries aaaa.lobadk.com with the provided search, and returns a random file from it. Supports one argument')
    async def arsearch(self, ctx, search_keyword=""):
        if search_keyword:
            allowed = compile('[^\w.\-]')
            if not allowed.match(search_keyword):
                
                links = await self.searchfiles(search_keyword)
                
                if len(links) == 0:
                    await ctx.reply('Search returned empty!', silent=True)
                else:    
                    await ctx.reply(urljoin(self.aURL, choice(links)), silent=True)
            else:
                await ctx.reply('Invalid character found in search parameter!', silent=True)
        else:
            await ctx.reply('Search parameter required!\n```?ars example```', silent=True)

######################################################################################################

    @commands.command(aliases=['pong'], brief="Test if the bot works, and it's latency.", description="Tests if the bot is seeing the command as well as capable of responding. Supports one, but not required, argument, as 'latency'. If latency argument is used, tests and displays the one-way latency from your home, to Discord, and then to the bot (with a multiplication of 2 to simulate round-trip), as well as the round-trip latency between the bot and Discord.")
    async def ping(self, ctx, ping_mode=""):
        LatencyResponses = ['Fiber is fast and all but they really should consider swapping to QuantumCables:tm:.',"You know, I could've quantised *at least* 100x the amount of data in that time.", 'That was a nice nap.', "Do you realize how many times I could've been pet in that amount of time!", 'And so close to beating your alternate-self from another dimension too!', "Let's just not tell your alternate-self from another dimension..."]

        if ctx.message.content.startswith('?ping'):
            pingresponse = 'pong'
        
        elif ctx.message.content.startswith('?pong'):
            pingresponse = 'ping'
        
        if ping_mode:
            if ping_mode.casefold() == 'latency':
                
                #Get current local time on the machine clock and multiply by 1000 to get milliseconds
                local_time_in_ms = (round(time() * 1000))

                #Get the time the message was sent in milliseconds by multiplying by 1000
                message_timestamp = (round(ctx.message.created_at.timestamp() * 1000))

                #Get latency in milliseconds by subtracting the current time, with the time the message was sent
                latency = local_time_in_ms - message_timestamp

                #If the latency is negative i.e. system clock is behind the real world by more than the latency
                #Get a rough estimate of the latency instead, by taking the offset, turning it into milliseconds, and adding it to the latency
                if latency < 0:
                    c = NTPClient()
                    response = c.request('pool.ntp.org', version=3)
                    offset = round(response.offset * 1000)
                    latency += offset
                    await ctx.reply(f'A negative latency value was detected. Used pool.ntp.org to attempt to correct, with a {round(offset)}ms offset.', silent=True)


                await ctx.reply(f'{pingresponse}! Took {latency * 2}ms. {choice(LatencyResponses)}\nConnection to discord: {round(self.bot.latency * 1000)}ms', silent=True)
            else:
                await ctx.reply("Only 'latency' parameter allowed", silent=True)
        else:
            await ctx.reply(pingresponse, silent=True)

######################################################################################################

    @commands.command(aliases=['acount', 'countaaaa', 'counta'], brief='Counts the images and videos stored on aaaa.lobadk.com.', description="Counts the amount of images and videos that are stored on aaaa.lobadk.com, excluding any unrelated files, as well as folders.")
    async def aaaacount(self, ctx):
        all_files = await self.getfiles(self.aURL, self.a_folder)
        await ctx.reply(f'There are currently {len(all_files)} quantised datasets.', silent=True)


######################################################################################################

    @commands.command(aliases=['quantumball', 'qball'], brief='standard 8ball replies, but with some quantum mixed.', description='Uses the standard 8ball replies, but with some quantum related replies or addition to the messages. Accepts no arguments.')
    async def QuantumBall(self, ctx):
        affirmative_answers_list = ['It is certain.', 'It is decidedly so.', 'Without a doubt.', 'Yes definitely.', 'You may rely on it.', 'As I see it, yes.', 'Most likely.', 'Outlook good.', 'Yes.', 'Signs point to yes.']
        non_committal_answers_list = ['Reply hazy, try again.', 'Ask again later.', 'Better not tell you now.', 'Cannot predict now.', 'Concentrate and ask again.']
        negative_answers_list = ["Don't count on it.", 'My reply is no.', 'My sources say no.', 'Outlook not so good.', 'Very doubtful.']
        reason_list = ['Quantum tunnel unexpectedly collapsed!', 'Entanglement lost!', 'Was that vase always broken?', 'Error', '||redacted||', 'Universal instability detected!']
        quantumball_messages_list = ['{amount} {location} agrees or already happened in. {affirmative_answer}', '{reason}. {non_committal_answer}', 'No related parallel universe, dimension, timeline or reality detected! {negative_answer}']

        amount = randint(100, 100_000)

        await ctx.reply(choices(quantumball_messages_list, k=1, weights=[10, 5, 5])[0].format(amount=amount, location=choice(['realities','universes','dimensions','timelines']), affirmative_answer=choice(affirmative_answers_list), reason=choice(reason_list), non_committal_answer=choice(non_committal_answers_list), negative_answer=choice(negative_answers_list)), silent=True)

    print('Started Fields!')
async def setup(bot):
    await bot.add_cog(Fields(bot))
