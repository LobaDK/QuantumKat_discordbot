from discord.ext import commands
import random
from num2words import num2words

class Entanglement(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command()
    async def observe(self, ctx):
        if ctx.author.id == 429406165903081472:
            await ctx.send("QuantumKat's superposition has collapsed!")
            await self.bot.close()
    
    @commands.command()
    async def stabilise(self, ctx, module : str):
        if ctx.author.id == 429406165903081472:
            location = random.choice(['reality','universe','dimension','timeline'])
            if module == 'cogs.Entanglement' or module == 'Entanglement':
                await ctx.send(f'Superposition irregularity detected in Quantum Entanglement! Attempting to quantum entangle to another {location}...')
            if module == 'cogs.Field' or module == 'Field':
                await ctx.send(f'Superposition irregularity detected in Quantum Field! Attempting to quantum entangle to another {location}...')
            if module == 'cogs.Tunnel' or module == 'Tunnel':
                await ctx.send(f'Superposition irregularity detected in Quantum Tunnel! Attempting to quantum entangle to another {location}...')
            try:
                if "cogs." not in module:
                    module = "cogs." + module
                self.bot.reload_extension(module)
                await ctx.send(f'Successfully entangled to the {num2words(random.randint(1,1000), to="ordinal_num")} {location}!')
            except Exception as e:
                print('{}: {}'.format(type(e).__name__, e))
                await ctx.send('Error, possible timeline paradox detected! Please try again')
        else:
            await ctx.send(f"I'm sorry {ctx.author.mention}. I'm afraid I can't do that.")
    
    @commands.command()
    async def entangle(self, ctx, module : str):
        if ctx.author.id == 429406165903081472:
            try:
                if "cogs." not in module:
                    module = "cogs." + module
                self.bot.load_extension(module)
                await ctx.send(f'Successfully entangled to {module.replace("cogs.","")}')
            except Exception as e:
                print('{}: {}'.format(type(e).__name__, e))
                await ctx.send('https://aaaa.lobadk.com/aitrash.mp4')
        else:
            await ctx.send(f"I'm sorry {ctx.author.mention}. I'm afraid I can't do that.")

    @commands.command()
    async def unentangle(self, ctx, module : str):
        if ctx.author.id == 429406165903081472:
            try:
                if "cogs." not in module:
                    module = "cogs." + module
                self.bot.unload_extension(module)
                await ctx.send(f'Successfully unentangled from {module.replace("cogs.","")}')
            except Exception as e:
                print('{}: {}'.format(type(e).__name__, e))
                await ctx.send('https://aaaa.lobadk.com/aitrash.mp4')
        else:
            await ctx.send(f"I'm sorry {ctx.author.mention}. I'm afraid I can't do that.")

def setup(bot):
    bot.add_cog(Entanglement(bot))