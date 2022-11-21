import asyncio
import string
import os
import random
import re
import json

from discord.ext import commands
from num2words import num2words


class Entanglement(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    initial_extensions = []
    for cog in os.listdir('./cogs'):
        if cog.endswith('.py'):
            initial_extensions.append(f'{cog[:-3]}')

    aaaa_dir = '/var/www/aaaa/'
    aaaa_domain = 'https://aaaa.lobadk.com/'
    possum_dir = '/var/www/possum/'
    possum_domain = 'https://possum.lobadk.com/'


    

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

        #Make a characters variable that combines lower- and uppercase letters, as well as numbers.
        #Used to generate a random filename, if specified
        characters = string.ascii_letters + string.digits
        if URL and filename and location:
            if location.lower() == 'aaaa':
                data_dir = self.aaaa_dir
                data_domain = self.aaaa_domain
            elif location.lower()== 'possum':
                data_dir = self.possum_dir
                data_domain = self.possum_domain

                #If the filename is 'rand' generate a random 8-character long base62 filename using the previously created 'characters' variable
                if filename.lower() == 'rand':
                    filename = "".join(random.choice(characters) for _ in range(8))
                
                #Discord disabled embed detection for the URL
                #Strips all greater-than and less-than symbols from the URL string
                #Allows the user to supply a URL without making it embed
                if URL.startswith('<') or URL.endswith('>'):
                    URL = URL.replace('<','')
                    URL = URL.replace('>','')

                if mode.upper() == 'YT':
                    
                    #Disallow playlists
                    if not "&list=" in URL and not "playlist" in URL:
                    
                        #Download the best (up to 1080p) MP4 video and m4a audio, and then combines them
                        #Or a single video with audio included (up to 1080p), if that's the best option
                        arg = f'yt-dlp -f bv[ext=mp4]["height<=1080"]+ba[ext=m4a]/b[ext=mp4]["height<=1080"] "{URL}" -o "{data_dir}{filename}.%(ext)s"'
                        
                        await ctx.send('Creating quantum tunnel... Tunnel created! Quantizing data...')
                        
                        #Attempt to run command with above args
                        try:
                            process = await asyncio.create_subprocess_shell(arg, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
                            await process.wait()
                            stdout, stderr = await process.communicate()

                        except Exception as e:
                            print('{}: {}'.format(type(e).__name__, e))
                            await ctx.reply('Error, quantization tunnel collapsed unexpectedly!')
                            return
                        
                        #yt-dlp can sometimes output non-fatal errors to stderr
                        #Rather than use it to cancel the process if anything is found
                        #simply print the output
                        #To-do: Figure out which kind of fatal messages it can return, and attempt to look for/parse them
                        if stderr:
                            await ctx.send(stderr.decode())

                        #If a file with the same name already exists, yt-dlp returns this string somewhere in it's output
                        if 'has already been downloaded' in stdout.decode():
                            await ctx.send('Filename already exists, consider using a different name')
                            return
                        
                        #If this piece of code is reached, it's assumed that everything went well.
                        #This could definitely be improved, but I'm already losing my sanity
                        elif stdout:

                            #If the downloaded video file is larger than 50MB's
                            if int(os.stat(f'{data_dir}{filename}.mp4').st_size / (1024 * 1024)) > 50:
                                await ctx.reply('Dataset exceeded recommended limit! Crunching some bits... this might take a ***bit***')
                                #Try and first lower the resolution of the original video by 1.5 e.g. 1080p turns into 720p. 
                                #For Discord embeds, this doesn't hurt viewability much, if at all
                                
                                #Get JSON output of the first video stream's metadata. Youtube only allows a single video stream, so this should always work
                                arg2 = f'ffprobe -v quiet -show_streams -select_streams v:0 -of json {data_dir}{filename}.mp4'
                                
                                #Attempt to run command with above args
                                try:
                                    self.stream = await asyncio.create_subprocess_shell(arg2, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
                                    self.stdout, self.stderr = await self.stream.communicate()
                                    await self.stream.wait()
                                except Exception as e:
                                    print('{}: {}'.format(type(e).__name__, e))
                                    await ctx.reply('Error getting video metadata!')
                                    return

                                #Load the "streams" key, which holds all the metadata information
                                video_metadata = json.loads(self.stdout)['streams'][0]
                                
                                #Attempt to parse, divide, and save the video's width and height in int, to remove any decimal points
                                try:
                                    self.frame_width = int(video_metadata['coded_width'] / 1.5)
                                    self.frame_height = int(video_metadata['coded_height'] / 1.5)
                                except Exception as e:
                                    print('{}: {}'.format(type(e).__name__, e))
                                    await ctx.reply('Error parsing video resolution, manual conversion required!')
                                    return

                                #Transcode original video into an h264 stream, with a reasonable CRF value of 30, and scale the video to the new resolution.
                                #In the future, a check should be made whether the video has audio or not, either by checking if there's an audio stream
                                #or the audio stream's bitrate (I don't know how Youtube handles muted videos)
                                arg3 = f'ffmpeg -y -i {data_dir}{filename}.mp4 -c:v libx264 -c:a aac -crf 30 -b:v 0 -b:a 192k -movflags +faststart -vf scale={self.frame_width}:{self.frame_height} -f mp4 {data_dir}{filename}.tmp'
                                
                                #Attempt to run command with above args
                                try:
                                    self.process2 = await asyncio.create_subprocess_shell(arg3)
                                    await self.process2.wait()
                                except Exception as e:
                                    print('{}: {}'.format(type(e).__name__, e))
                                    await ctx.reply('Error transcoding resized video!')
                                    return

                                #If the returncode is 0, i.e. no errors happened
                                if self.process2.returncode == 0:
                                    
                                    #Check if the new lower-resolution version is under 50MB's.
                                    #as a last resort, If not, enter an endless loop and keep trying a lower bitrate until one works
                                    bitrate_decrease = 0
                                    attempts = 0
                                    while int(os.stat(f'{data_dir}{filename}.tmp').st_size / (1024 * 1024)) > 50:
                                        
                                        #Attempt to parse, convert from string, to float, to int, and save the video duration
                                        #100% accuracy down to the exact millisecond isn't required, so we just get the whole number instead
                                        try:
                                            video_duration = int(float(video_duration['duration']))
                                        except Exception as e:
                                            print('{}: {}'.format(type(e).__name__, e))
                                            await ctx.reply('Error parsing video duration, manual conversion required!')
                                            return
                                    
                                        #calculate the average bitrate required to reach around 50MB's
                                        #by multiplying 50 by 8192 (convert megabits to kilobits) 
                                        #dividing that by the video length, and subtracting the audio bitrate
                                        #Audio bitrate is hardcoded for now.
                                        bitrate = (50 * 8192) / video_duration - 192 - bitrate_decrease

                                        #Transcode original video into an h264 stream, with an average bitrate calculated from the above code, and scale the video to the new resolution
                                        #In the future, a check should be made whether the video has audio or not, either by checking if there's an audio stream
                                        #or the audio stream's bitrate (I don't know how Youtube handles muted videos)
                                        arg4 = f'ffmpeg -y -i {data_dir}{filename}.mp4 -c:v libx264 -c:a aac -b:v {bitrate}k -b:a 192k -movflags +faststart -vf scale={self.frame_width}:{self.frame_height} -f mp4 {data_dir}{filename}.tmp'
                                    
                                        try:
                                            self.process3 = await asyncio.create_subprocess_shell(arg4)
                                            await self.process3.wait()
                                        except Exception as e:
                                            print('{}: {}'.format(type(e).__name__, e))
                                            await ctx.reply('Error transcoding resized with average bitrate video!')
                                            return

                                        #Increase attemps by 1
                                        attempts += 1
                                        #Increase by 100 kilobits, to decrease the average bitrate by 100 kilotbits
                                        bitrate_decrease += 100
                                    
                                    #Attempt to delete the original video, and then rename the transcoded .tmp video to .mp4
                                    try:
                                        os.remove(f'{data_dir}{filename}.mp4')
                                        os.rename(f'{data_dir}{filename}.tmp', f'{data_dir}{filename}.mp4')
                                    
                                    except Exception as e:
                                        print('{}: {}'.format(type(e).__name__, e))
                                        await ctx.reply('Error moving/removing file!')
                                        return
                                    
                                    #If the bitrate option was reached, this would be at least 1
                                    #Otherwise if it's 0, it means it never attempted to transcode with a variable bitrate
                                    if attempts == 0:
                                        await ctx.reply(f'Success! Data quantized and bit-crunched to <{data_domain}{filename}.mp4>\nResized to {self.frame_width}:{self.frame_height}')
                                    else:
                                        await ctx.reply(f'Success! Data quantized and bit-crunched to <{data_domain}{filename}.mp4>\nUsing {bitrate}k/s and Resized to {self.frame_width}:{self.frame_height} with {attempts} attemp(s)')
                                
                                #Else statement for the process returncode, from the initial ffmpeg command
                                else:
                                    await ctx.reply('Non-0 exit status code detected!')
                            
                            #Else statement if file was under 50MB's        
                            else:
                                await ctx.reply(f'Success! Data quantized to <{data_domain}{filename}.mp4>')

                    #Else statement if the URL is a Youtube playlist
                    else:
                        await ctx.send('Playlists not supported')

                else:
                    await ctx.send('Creating quantum tunnel... Tunnel created! Quantizing data...')
                    try:
                        while True:
                            if os.path.splitext(URL)[1]:
                                filename = filename + os.path.splitext(URL)[1].lower()
                            arg = f'wget -nc -O {data_dir}{filename} {URL}'
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
                                await ctx.send(f'Success! Data quantized to <{data_domain}{filename}>')
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
            data_dir = self.aaaa_dir
            allowed = re.compile('^[\w]*(\.){1,}[\w]{1,}$') #allow only alphanumeric, underscores, a single dot and at least one alphanumeric after the dot
            if not '/' in current_filename and allowed.match(new_filename):
                await ctx.send('Attempting to requantize data...')
                try:
                    os.rename(f'{data_dir}{current_filename}', f'{data_dir}{new_filename}')
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
            process = await asyncio.create_subprocess_shell('git pull', stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
            stdout, stderr = await process.communicate()
       
        except Exception as e:
            print('{}: {}'.format(type(e).__name__, e))
            await ctx.send('Error running command')

        #For some reason after decoding Git's output stream, "b'" and "\\n'" shows up everywhere in the output
        #This removes any of them, cleaning up the output
        stdout = stdout.decode()
        stdout = stdout.replace("b'","")
        stdout = stdout.replace("\\n'","")
        stderr = stderr.decode()
        stderr = stderr.replace("b'","")
        stderr = stderr.replace("\\n'","")

        #For some reason Git on Windows returns the string without hyphens, while Linux returns it with hyphens
        if 'Already up to date' in stderr or 'Already up-to-date' in stderr:
            await ctx.send(stderr)
        
        elif stderr:

            #Send the output of Git, which displays whichs files has been updated, and how much
            #Then sleep 2 seconds to allow the text to be sent, and read
            await ctx.send(stderr)
            await asyncio.sleep(2)

            #This command display the filenames of the files the changed between the last and current versions
            process2 = await asyncio.create_subprocess_shell('git diff --name-only HEAD~1 HEAD', stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)

            #Save the output (filenames) in stdout2
            stderr2, stdout2 = await process2.communicate()

            #Each displayed file is on a newline, so split by the newlines to save them as a list
            extensions = stdout2.split('\n')

            #Iterate through each listed files
            for extension in extensions:
                try:
                    await self.bot.reload_extension(f'cogs.{os.path.basename(extension)[:-3]}')
                    await ctx.send(f'Purging updated {extension[:-3]}!')
                
                except commands.ExtensionNotLoaded as e:
                    print('{}: {}'.format(type(e).__name__, e))
                    await ctx.send(f'{extension[:-3]} is not running, or could not be found')
                
                except commands.ExtensionNotFound as e:
                    print('{}: {}'.format(type(e).__name__, e))
                    await ctx.send(f'{extension[:-3]} could not be found!')
                
                except commands.NoEntryPointError as e:
                    print('{}: {}'.format(type(e).__name__, e))
                    await ctx.send(f'successfully loaded {extension[:-3]}, but no setup was found!')
        
        elif stdout:
            await ctx.send(stdout)
        

######################################################################################################

    @commands.command(aliases=['dequantize'], brief='(Bot owner only) Delete the specified file.', description='Attempts to delete the specified file. Supports and requires 2 arguments, being the filename, and location (aaaa|possum).')
    @commands.is_owner()
    async def dequantise(self, ctx, filename="", location=""):
        if filename and location:

            if location.lower() == 'aaaa':
                data_dir = self.aaaa_dir
            elif location.lower() == 'possum':
                data_dir = self.possum_dir

                #allow only alphanumeric, underscores, a single dot and at least one alphanumeric after the dot
                allowed = re.compile('^[\w]*(\.){1,}[\w]{1,}$')
                if allowed.match(filename):

                    try:
                        os.remove(f'/var/www/{data_dir}/{filename}')
                        await ctx.send(f'Successfully dequantised and purged {filename}!')
                    
                    except FileNotFoundError:
                        await ctx.send('Dataset not found. Did you spell it correctly?')
                    
                    except Exception as e:
                        print('{}: {}'.format(type(e).__name__, e))
                        await ctx.send('Error dequantising dataset!')
                
                else:
                    await ctx.send('Only alphanumeric and a dot allowed. Extension required. Syntax is:\n```?dequantise name.extension aaaa|possum```')
            
            else:
                await ctx.send('Only `aaaa` and `possum` are valid parameters!')
        
        else:
            await ctx.send('Filename and location required!\n`?dequantise|dequantize <filename> aaaa|possum`')


    print('Started Entanglement!')
async def setup(bot):
    await bot.add_cog(Entanglement(bot))
