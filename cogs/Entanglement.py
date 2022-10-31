import asyncio
from logging import exception
import os
import random
import re

from discord.ext import commands
from num2words import num2words


class Entanglement(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    initial_extensions = []
    for cog in os.listdir('./cogs'):
        if cog.endswith('.py'):
            initial_extensions.append(f'{cog[:-3]}')
    
    @commands.command(brief="(Bot owner only) Stops the bot.", description="Stops and disconnects the bot. Supports no arguments.")
    @commands.is_owner()
    async def observe(self, ctx):
        await ctx.send("QuantumKat's superposition has collapsed!")
        await self.bot.close()
    
    @commands.command(aliases=['stabilize', 'restart', 'reload', 'reboot'], brief="(Bot owner only) Reloads cogs/extensions.", description="Reloads the specified cogs/extensions. Requires at least one argument, and supports an arbitrary amount of arguments. Special character `*` can be used to reload all.")
    @commands.is_owner()
    async def stabilise(self, ctx, *, module : str=''):
        if module:
            location = random.choice(['reality','universe','dimension','timeline'])
            if module == '*':
                await ctx.send('Quantum instability detected across... <error>. Purrging!')
                for extension in self.initial_extensions:
                    try:
                        await self.bot.reload_extension(f'cogs.{extension}')
                        await ctx.send(f'Purging {extension}!')
                    except commands.ExtensionNotLoaded as e:
                        print('{}: {}'.format(type(e).__name__, e))
                        await ctx.send(f'{extension} is not running, or could not be found')
                    except commands.ExtensionNotFound as e:
                        print('{}: {}'.format(type(e).__name__, e))
                        await ctx.send(f'{extension} could not be found!')
                    except commands.NoEntryPointError as e:
                        print('{}: {}'.format(type(e).__name__, e))
                        await ctx.send(f'successfully loaded {extension}, but no setup was found!')
            else:
                cogs = module.split()
                for cog in cogs:
                    if cog[0].islower:
                        cog = cog.replace(cog[0], cog[0].upper(), 1)
                        try:
                            await self.bot.reload_extension(f'cogs.{cog}')
                            if len(cogs) == 1:
                                await ctx.send(f'Superposition irregularity detected in Quantum {cog}! Successfully entangled to the {num2words(random.randint(1,1000), to="ordinal_num")} {location}!')
                            else:
                                await ctx.send(f'Purrging {cog}!')
                        except commands.ExtensionNotFound as e:
                            print('{}: {}'.format(type(e).__name__, e))
                            await ctx.send(f'{cog} could not be found!')
                        except commands.ExtensionNotLoaded as e:
                            print('{}: {}'.format(type(e).__name__, e))
                            await ctx.send(f'{cog} is not running, or could not be found!')
                        except commands.NoEntryPointError as e:
                            print('{}: {}'.format(type(e).__name__, e))
                            await ctx.send(f'successfully loaded {cog}, but no setup was found!')
    
    @commands.command(aliases=['load', 'start'], brief="(Bot owner only) Starts/Loads a cog/extension.", description="Starts/Loads the specified cogs/extensions. Requires at least one argument, and supports an arbitrary amount of arguments.")
    @commands.is_owner()
    async def entangle(self, ctx, *, module : str=''):
        if module:
            cogs = module.split()
            for cog in cogs:
                if cog[0].islower:
                    cog = cog.replace(cog[0], cog[0].upper(), 1)
                    try:
                        await self.bot.load_extension(f'cogs.{cog}')
                        await ctx.send(f'Successfully entangled to {cog}')
                    except commands.ExtensionNotFound as e:
                        print('{}: {}'.format(type(e).__name__, e))
                        await ctx.send(f'{cog} could not be found!')
                    except commands.ExtensionAlreadyLoaded as e:
                        print('{}: {}'.format(type(e).__name__, e))
                        await ctx.send(f'{cog} is already loaded!')
                    except commands.NoEntryPointError as e:
                        print('{}: {}'.format(type(e).__name__, e))
                        await ctx.send(f'successfully loaded {cog}, but no setup was found!')
                    except commands.ExtensionFailed as e:
                        print('{}: {}'.format(type(e).__name__, e))
                        await ctx.send(f'Loading {cog} failed due to an error!')

    @commands.command(aliases=['unload', 'stop'], brief="(Bot owner only) Stops/Unloads a cog/extension.", description="Stops/Unloads the specified cogs/extensions. Requires at least one argument, and supports an arbitrary amount of arguments.")
    @commands.is_owner()
    async def unentangle(self, ctx, *, module : str=''):
        if module:
            cogs = module.split()
            for cog in cogs:
                if cog[0].islower:
                    cog = cog.replace(cog[0], cog[0].upper(), 1)
                    try:
                        await self.bot.unload_extension(f'cogs.{cog}')
                        await ctx.send(f'Successfully unentangled from {cog}')
                    except commands.ExtensionNotFound as e:
                        print('{}: {}'.format(type(e).__name__, e))
                        await ctx.send(f'{cog} could not be found!')
                    except commands.ExtensionNotLoaded as e:
                        print('{}: {}'.format(type(e).__name__, e))
                        await ctx.send(f'{cog} not running, or could not be found!')

    @commands.command(aliases=['quantise'], brief="(Bot owner only) Downloads a file to aaaa.lobadk.com.", description="Downloads the specified file to the root directory of aaaa.lobadk.com, for easier file adding. Requires at least 2 arguments, and supports 3 arguments. The first argument is the file URL, the second is the filename to be used, the third (optional) is `YT` to indicate yt-lp should be used to download the file (YouTub or Twitter for example). If a file extension is detected, it will automatically be used, otherwise it needs to be specified in the filename. Supports links with disabled embeds, by `<>`.")
    @commands.is_owner()
    async def quantize(self, ctx, arg2="", arg3="", arg1=""):
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
                    
                    except Exception as e:
                        print('{}: {}'.format(type(e).__name__, e))
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

                    except Exception as e:
                        print('{}: {}'.format(type(e).__name__, e))
                        await ctx.send('Error, quantization tunnel collapsed unexpectedly!')
                        
            else:
                await ctx.send('Command requires 2 arguments:\n```?quantize <URL> <filename>``` or ```?quantize <URL> <filename> YT``` to use yt-dlp to download it')

    @commands.command(aliases=['requantise'], brief="(Bot owner only) Rename a file on aaaa.lobadk.com.", description="Renames the specified file. Requires and supports 2 arguments. Only alphanumeric, underscores and a single dot allowed, and at least one character must appear after the dot when chosing a new name.")
    @commands.is_owner()
    async def requantize(self, ctx, arg1='', arg2=''):
        if arg1 and arg2:
            allowed = re.compile('^[\w]*(\.){1,}[\w]{1,}$') #allow only alphanumeric, underscores, a single dot and at least one alphanumeric after the dot
            if not '/' in arg1 and allowed.match(arg2):
                await ctx.send('Attempting to requantize data...')
                try:
                    os.rename(f'/var/www/aaaa/{arg1}', f'/var/www/aaaa/{arg2}')
                    await ctx.send('Success!')
                except FileNotFoundError:
                    await ctx.send('Error! Data does not exist')
                except FileExistsError:
                    await ctx.send('Error! Cannot requantize, data already exists')
                except Exception as e:
                    print('{}: {}'.format(type(e).__name__, e))
                    await ctx.send('Critical error! Check logs for info')
            else:
                await ctx.send('Only alphanumeric and a dot allowed. Extension required. Syntax is:\n```name.extension```')
        else:
            await ctx.send('Command requires 2 arguments:\n```?requantize <current.name> <new.name>```')

    @commands.command(brief="(Bot owner only) Runs git commands in the bots directory.", description="Run any git command by passing along the arguments specified. Mainly used for updating the bot or swapping versions, but there is no limit.")
    @commands.is_owner()
    async def git(self, ctx, *, arg1):
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
                    
                except Exception as e:
                    print('{}: {}'.format(type(e).__name__, e))
                    await ctx.send('Error running command')

    @commands.command(brief="(Bot owner only) Fetches new updates and reloads all cogs/extensions.", description="Fetches the newest version by running `git pull` and then reloads the cogs/extensions if successful.")
    @commands.is_owner()
    async def update(self, ctx):
        try:
            process = await asyncio.create_subprocess_shell('git pull', stderr=asyncio.subprocess.PIPE, stdout=asyncio.subprocess.PIPE)
            stderr, stdout = await process.communicate()
            stdout = stdout.decode()
            stdout = stdout.replace("b'","")
            stdout = stdout.replace("\\n'","")
            stderr = stderr.decode()
            stderr = stderr.replace("b'","")
            stderr = stderr.replace("\\n'","")
            if 'Already up to date' in stderr or 'Already up-to-date' in stderr:
                await ctx.send(stderr)
            elif stderr:
                await ctx.send(stderr)
                await asyncio.sleep(2)
                for extension in self.initial_extensions:
                    try:
                        await self.bot.reload_extension(f'cogs.{extension}')
                        await ctx.send(f'Purging {extension}!')
                    except commands.ExtensionNotLoaded as e:
                        print('{}: {}'.format(type(e).__name__, e))
                        await ctx.send(f'{extension} is not running, or could not be found')
                    except commands.ExtensionNotFound as e:
                        print('{}: {}'.format(type(e).__name__, e))
                        await ctx.send(f'{extension} could not be found!')
                    except commands.NoEntryPointError as e:
                        print('{}: {}'.format(type(e).__name__, e))
                        await ctx.send(f'successfully loaded {extension}, but no setup was found!')
            elif stdout:
                await ctx.send(stdout)
            
        except Exception as e:
            print('{}: {}'.format(type(e).__name__, e))
            await ctx.send('Error running command')

    print('Started Entanglement!')
async def setup(bot):
    await bot.add_cog(Entanglement(bot))
