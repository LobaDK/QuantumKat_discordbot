from discord.ext import commands
import random
from num2words import num2words

class Admin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command()
    async def observe(self, ctx):
        if ctx.author.id == 429406165903081472:
            await ctx.send("QuantumKat's superposition has collapsed!")
            await self.bot.close()
    
    @commands.command()
    async def stabilize(self, ctx, module : str):
        if ctx.author.id == 429406165903081472:
            quantum = ['reality','universe','dimension','timeline']
            location = random.choice(quantum)
            try:
                if "cogs." not in module:
                    module = "cogs." + module
                self.bot.reload_extension(module)
                await ctx.send(f'Superposition irregularity detected! Quantum entangling to another {location}...')
                await ctx.send(f'Successfully entangled to the {num2words(random.randint(1,1000), to="ordinal_num")} {location}!')
            except Exception as e:
                print('{}: {}'.format(type(e).__name__, e))
                await ctx.send('https://aaaa.lobadk.com/aitrash.mp4')

def setup(bot):
    bot.add_cog(Admin(bot))