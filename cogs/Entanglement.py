import asyncio
import os
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
    
    @commands.command(aliases=['stabilize'])
    async def stabilise(self, ctx, module : str):
        if ctx.author.id == 429406165903081472:
            location = random.choice(['reality','universe','dimension','timeline'])
            if module == '*':
                await ctx.send('Quantum instability detected across... <error>. Purrging!')
                initial_extensions = ['cogs.Field','cogs.Entanglement','cogs.Tunnel', 'cogs.Activity']
                try:
                    for extension in initial_extensions:
                        await ctx.send(f'Purging {extension.replace("cogs.","")}!')
                        self.bot.reload_extension(extension)
                    return
                except Exception as e:
                    print('{}: {}'.format(type(e).__name__, e))
                    await ctx.send('Error, possible timeline paradox detected! Please try again')
                    return

            await ctx.send(f'Superposition irregularity detected in Quantum {module}! Attempting to quantum entangle to another {location}...')
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

    @commands.command(aliases=['quantise'])
    async def quantize(self, ctx, arg2="", arg3="", arg1=""):
        if ctx.author.id == 429406165903081472:
            if arg2 and arg3:
                if arg2.startswith('<') and arg2.endswith('>'):
                    arg2 = arg2.replace('<','')
                    arg2 = arg2.replace('>','')
                if arg1 == 'YT':
                    if "&list=" in arg2 or "playlist" in arg2:
                        await ctx.send('Playlists not supported')
                        return
                    await ctx.send('Creating quantum tunnel...')
                    try:
                        arg = f'yt-dlp -f ba+bv/b "{arg2}" -o "/var/www/aaaa/{arg3}.%(ext)s"'
                        await ctx.send('Tunnel created! Quantizing data...')
                        process = await asyncio.create_subprocess_shell(arg, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
                        stdout, stderr = await process.communicate()
                        if stderr:
                            await ctx.send(stderr.decode())
                        if 'has already been downloaded' in stdout.decode():
                            await ctx.send('Filename already exists, consider using a different name')
                            return
                        elif stdout:
                            await ctx.send(f'Success! Data quantized to {arg3}.mp4')
                    
                    except:
                        await ctx.send('Error, quantization tunnel collapsed unexpectedly!')
                        return

                else:
                    await ctx.send('Creating quantum tunnel...')
                    try:
                        await ctx.send('Tunnel created! Quantizing data...')
                        if os.path.splitext(arg2)[1]:
                            arg3 = arg3 + os.path.splitext(arg2)[1].lower()
                        arg = f'wget -nc -O /var/www/aaaa/{arg3} {arg2}'
                        process = await asyncio.create_subprocess_shell(arg, stderr=asyncio.subprocess.PIPE)
                        stdout, stderr = await process.communicate()
                        if 'already there; not retrieving' in stderr.decode():
                            await ctx.send('Filename already exists, consider using a different name')
                            return
                        else:
                            await ctx.send(f'Success! Data quantized to {arg3}')

                    except:
                        await ctx.send('Error, quantization tunnel collapsed unexpectedly!')
                        
            else:
                await ctx.send('Command requires 2 arguments:\n```?quantize <URL> <filename>``` \nor ```?quantize <URL> <filename> YT``` to use yt-dlp to download it')
    
    @commands.command()
    async def git(self, ctx, *, arg1):
        if ctx.author.id == 429406165903081472:
            if arg1:
                cmd = f'git {arg1}'
                try:
                    process = await asyncio.create_subprocess_shell(cmd, stderr=asyncio.subprocess.PIPE, stdout=asyncio.subprocess.PIPE)
                    stderr, stdout = await process.communicate()
                    stdout = stdout.decode()
                    stdout = stdout.replace("b'","")
                    stdout = stdout.replace("\\n'","")
                    stderr = stderr.decode()
                    stderr = stderr.replace("b'","")
                    stderr = stderr.replace("\\n'","")
                    if stderr:
                        await ctx.send(stderr)
                    elif stdout:
                        await ctx.send(stdout)
                    else:
                        await ctx.message.add_reaction('👍')
                    
                except:
                    await ctx.send('Error running command')
def setup(bot):
    bot.add_cog(Entanglement(bot))