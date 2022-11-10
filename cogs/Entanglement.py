import asyncio
import string
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

###################################################################################################### command splitter for easier reading and navigating
    
    @commands.command(brief="(Bot owner only) Stops the bot.", description="Stops and disconnects the bot. Supports no arguments.")
    @commands.is_owner()
    async def observe(self, ctx):
        await ctx.send("QuantumKat's superposition has collapsed!")
        await self.bot.close()

######################################################################################################

    @commands.command(aliases=['stabilize', 'restart', 'reload', 'reboot'], brief="(Bot owner only) Reloads cogs/extensions.", description="Reloads the specified cogs/extensions. Requires at least one argument, and supports an arbitrary amount of arguments. Special character '*' can be used to reload all.")
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

######################################################################################################

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

######################################################################################################

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

######################################################################################################

    @commands.command(aliases=['quantise'], brief="(Bot owner only) Downloads a file to aaaa/possum.lobadk.com.", description="Downloads the specified file to the root directory of aaaa.lobadk.com or possum.lobadk.com, for easier file adding. Requires at least 3 arguments, and supports 4 arguments. The first argument is the file URL, the second is the filename to be used, with a special 'rand' parameter that produces a random 8 character long base62 filename, the third is the location, specified with 'aaaa' or 'possum', the fourth (optional) is 'YT' to indicate yt-lp should be used to download the file (YouTub or Twitter for example). If a file extension is detected, it will automatically be used, otherwise it needs to be specified in the filename. Supports links with disabled embeds, by '<>'.")
    @commands.is_owner()
    async def quantize(self, ctx, URL="", filename="", location="", mode=""):
        characters = string.ascii_letters + string.digits
        if URL and filename:
            if filename.lower() == 'rand':
                filename = "".join(random.choice(characters) for _ in range(8))
            if URL.startswith('<') or URL.endswith('>'):
                URL = URL.replace('<','')
                URL = URL.replace('>','')
            if mode.upper() == 'YT' and not location.lower() == 'possum':
                if "&list=" in URL or "playlist" in URL:
                    await ctx.send('Playlists not supported')
                    return
                try:
                    arg = f'yt-dlp -f bv[ext=mp4]+ba[ext=m4a]/b[ext=mp4] "{URL}" -o "/var/www/aaaa/{filename}.%(ext)s"'
                    await ctx.send('Creating quantum tunnel... Tunnel created! Quantizing data...')
                    process = await asyncio.create_subprocess_shell(arg, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
                    await process.wait()
                    stdout, stderr = await process.communicate()
                    if stderr:
                        await ctx.send(stderr.decode())
                    if 'has already been downloaded' in stdout.decode():
                        await ctx.send('Filename already exists, consider using a different name')
                        return
                    elif stdout:
                        if int(os.stat(f'/var/www/aaaa/{filename}.mp4').st_size / (1024 * 1024)) > 50:
                            await ctx.send('Dataset exceeded recommended limit! Crunching some bits... this might take a *bit*')
                            try:
                                arg2 = f'ffmpeg -n -i /var/www/aaaa/{filename}.mp4 -c:v libx264 -c:a aac -crf 30 -b:v 0 -b:a 192k -movflags +faststart -f mp4 /var/www/aaaa/{filename}.tmp'
                                process2 = await asyncio.create_subprocess_exec(arg2)
                                await process2.wait()
                                if process2.returncode() == 0:
                                    try:
                                        os.rename(f'/var/www/aaaa/{filename}.mp4', f'/var/www/aaaa/{filename}.old')
                                        os.rename(f'/var/www/aaaa/{filename}.tmp', f'/var/www/aaaa/{filename}.mp4')
                                        os.remove(f'/var/www/aaaa/{filename}.old')
                                        #Precautions to avoid loss of original file in case of error
                                        await ctx.send(f'Success! Data quantized and bit-crunched to https://aaaa.lobadk.com/{filename}.mp4')
                                    except Exception as e:
                                        print('{}: {}'.format(type(e).__name__, e))
                                        await ctx.send('Error shifting the dataset!')
                                else:
                                    await ctx.send('Unknown error running utility!')
                            except Exception as e:
                                print('{}: {}'.format(type(e).__name__, e))
                                await ctx.send('Dataset bit error!')
                        else:
                            await ctx.send(f'Success! Data quantized to https://aaaa.lobadk.com/{filename}.mp4')

                
                except Exception as e:
                    print('{}: {}'.format(type(e).__name__, e))
                    await ctx.send('Error, quantization tunnel collapsed unexpectedly!')
                    return

            elif mode.upper() == 'YT' and location.lower() == 'possum':
                await ctx.send('Oppossum location not allowed with YT download mode!')

            elif location.lower() == 'aaaa' or location.lower() == 'possum':
                try:
                    await ctx.send('Creating quantum tunnel... Tunnel created! Quantizing data...')
                    while True:
                        if os.path.splitext(URL)[1]:
                            filename = filename + os.path.splitext(URL)[1].lower()
                        if location.lower() == 'aaaa':
                            root = 'https://aaaa.lobadk.com/'
                            arg = f'wget -nc -O /var/www/aaaa/{filename} {URL}'
                        elif location.lower() == 'possum':
                            root = 'https://possum.lobadk.com/'
                            arg = f'wget -nc -O /var/www/possum/{filename} {URL}'
                        process = await asyncio.create_subprocess_shell(arg, stderr=asyncio.subprocess.PIPE)
                        stdout, stderr = await process.communicate()
                        if 'already there; not retrieving' in stderr.decode():
                            if not filename.lower() == 'rand':
                                await ctx.send('Filename already exists, consider using a different name')
                                return
                            else:
                                filename = "".join(random.choice(characters) for _ in range(8))
                                continue
                        else:
                            await ctx.send(f'Success! Data quantized to <{root}{filename}>')
                            return

                except Exception as e:
                    print('{}: {}'.format(type(e).__name__, e))
                    await ctx.send('Error, quantization tunnel collapsed unexpectedly!')
            
            else:
                await ctx.send('Only `aaaa` and `possum` are valid parameters!')
                    
        else:
            await ctx.send('Command requires 3 arguments:\n```?quantize <URL> <filename> <aaaa|possum>``` or ```?quantize <URL> <filename> <aaaa|possum> YT``` to use yt-dlp to download it')

######################################################################################################

    @commands.command(aliases=['requantise'], brief="(Bot owner only) Rename a file on aaaa.lobadk.com.", description="Renames the specified file. Requires and supports 2 arguments. Only alphanumeric, underscores and a single dot allowed, and at least one character must appear after the dot when chosing a new name.")
    @commands.is_owner()
    async def requantize(self, ctx, current_filename='', new_filename=''):
        if current_filename and new_filename:
            allowed = re.compile('^[\w]*(\.){1,}[\w]{1,}$') #allow only alphanumeric, underscores, a single dot and at least one alphanumeric after the dot
            if not '/' in current_filename and allowed.match(new_filename):
                await ctx.send('Attempting to requantize data...')
                try:
                    os.rename(f'/var/www/aaaa/{current_filename}', f'/var/www/aaaa/{new_filename}')
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

######################################################################################################

    @commands.command(brief="(Bot owner only) Runs git commands in the bots directory.", description="Run any git command by passing along the arguments specified. Mainly used for updating the bot or swapping versions, but there is no limit.")
    @commands.is_owner()
    async def git(self, ctx, *, git_arguments):
        if git_arguments:
            allowed = re.compile('^[\w\s-]*$')
            if allowed.match(git_arguments):
                cmd = f'git {git_arguments}'
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

######################################################################################################

    @commands.command(brief="(Bot owner only) Fetches new updates and reloads all cogs/extensions.", description="Fetches the newest version by running 'git pull' and then reloads the cogs/extensions if successful.")
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

######################################################################################################

    @commands.command(aliases=['dequantize'], brief='(Bot owner only) Delete the specified file.', description='Attempts to delete the specified file. Supports and requires 2 arguments, being the filename, and location (aaaa|possum).')
    @commands.is_owner()
    async def dequantise(self, ctx, filename="", location=""):
        if filename and location:
            allowed = re.compile('^[\w]*(\.){1,}[\w]{1,}$') #allow only alphanumeric, underscores, a single dot and at least one alphanumeric after the dot
            if allowed.match(filename):
                try:
                    await ctx.send(f'Dequantising and purging {filename}...')
                    if location.lower() == 'aaaa':
                        os.remove(f'/var/www/aaaa/{filename}')
                    elif location.lower() == 'possum':
                        os.remove(f'/var/www/possum/{filename}')
                    else:
                        await ctx.send('Only `aaaa` and `possum` are valid locations!')
                        return
                    await ctx.send('Success!')
                except FileNotFoundError:
                    await ctx.send('Dataset not found. Did you spell it correctly?')
                except:
                    await ctx.send('Error dequantising dataset!')
            else:
                await ctx.send('Only alphanumeric and a dot allowed. Extension required. Syntax is:\n```?dequantise name.extension aaaa|possum```')


    print('Started Entanglement!')
async def setup(bot):
    await bot.add_cog(Entanglement(bot))
