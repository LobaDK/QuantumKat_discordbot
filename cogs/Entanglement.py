from asyncio import create_subprocess_shell, subprocess
from json import loads
from os import execl, listdir, path, remove, rename, stat
from random import choice, randint
from string import ascii_letters, digits
from sys import argv, executable
from asyncio import sleep as asyncsleep

from discord import Message
from discord.ext import commands
from num2words import num2words
from psutil import cpu_percent, disk_usage, virtual_memory


class Entanglements(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    initial_extensions = []
    for cog in listdir('./cogs'):
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
        await ctx.reply("QuantumKat's superposition has collapsed!", silent=True)
        await self.bot.close()

######################################################################################################

    @commands.command(aliases=['stabilize', 'restart', 'reload'], brief="(Bot owner only) Reloads cogs/extensions.", description="Reloads the specified cogs/extensions. Requires at least one argument, and supports an arbitrary amount of arguments. Special character '*' can be used to reload all.")
    @commands.is_owner()
    async def stabilise(self, ctx, *, module : str=''):
        if module:
            location = choice(['reality','universe','dimension','timeline'])
            if module == '*':
                msg = await ctx.reply('Quantum instability detected across... <error>. Purrging!', silent=True)
                for extension in self.initial_extensions:
                    try:
                        await self.bot.reload_extension(f'cogs.{extension}')
                        msg = await msg.edit(content=msg.content + f'\nPurging {extension}!')
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
                                await ctx.reply(f'Superposition irregularity detected in Quantum {cog}! Successfully entangled to the {num2words(randint(1,1000), to="ordinal_num")} {location}!', silent=True)
                            else:
                                await ctx.reply(f'Purrging {cog}!', silent=True)
                        except commands.ExtensionNotFound as e:
                            print('{}: {}'.format(type(e).__name__, e))
                            await ctx.reply(f'{cog} could not be found!', silent=True)
                        except commands.ExtensionNotLoaded as e:
                            print('{}: {}'.format(type(e).__name__, e))
                            await ctx.reply(f'{cog} is not running, or could not be found!', silent=True)
                        except commands.NoEntryPointError as e:
                            print('{}: {}'.format(type(e).__name__, e))
                            await ctx.reply(f'successfully loaded {cog}, but no setup was found!', silent=True)

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
                        await ctx.reply(f'Successfully entangled to {cog}', silent=True)
                    except commands.ExtensionNotFound as e:
                        print('{}: {}'.format(type(e).__name__, e))
                        await ctx.reply(f'{cog} could not be found!', silent=True)
                    except commands.ExtensionAlreadyLoaded as e:
                        print('{}: {}'.format(type(e).__name__, e))
                        await ctx.reply(f'{cog} is already loaded!', silent=True)
                    except commands.NoEntryPointError as e:
                        print('{}: {}'.format(type(e).__name__, e))
                        await ctx.reply(f'successfully loaded {cog}, but no setup was found!', silent=True)
                    except commands.ExtensionFailed as e:
                        print('{}: {}'.format(type(e).__name__, e))
                        await ctx.reply(f'Loading {cog} failed due to an error!', silent=True)

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
                        await ctx.reply(f'Successfully unentangled from {cog}', silent=True)
                    except commands.ExtensionNotFound as e:
                        print('{}: {}'.format(type(e).__name__, e))
                        await ctx.reply(f'{cog} could not be found!', silent=True)
                    except commands.ExtensionNotLoaded as e:
                        print('{}: {}'.format(type(e).__name__, e))
                        await ctx.reply(f'{cog} not running, or could not be found!', silent=True)

######################################################################################################

    @commands.command(aliases=['quantise'], brief="(Bot owner only) Downloads a file to aaaa/possum.lobadk.com.", description="Downloads the specified file to the root directory of aaaa.lobadk.com or possum.lobadk.com, for easier file adding. Requires at least 3 arguments, and supports 4 arguments. The first argument is the file URL, the second is the filename to be used, with a special 'rand' parameter that produces a random 8 character long base62 filename, the third is the location, specified with 'aaaa' or 'possum', the fourth (optional) is 'YT' to indicate yt-lp should be used to download the file (YouTub or Twitter for example). If a file extension is detected, it will automatically be used, otherwise it needs to be specified in the filename. Supports links with disabled embeds, by '<>'.")
    @commands.is_owner()
    async def quantize(self, ctx, URL="", filename="", location="", mode=""):
        #Make a characters variable that combines lower- and uppercase letters, as well as numbers.
        #Used to generate a random filename, if specified
        characters = ascii_letters + digits
        if URL and filename and location:
            
            if location.lower() == 'aaaa':
                data_dir = self.aaaa_dir
                data_domain = self.aaaa_domain
            
            elif location.lower() == 'possum':
                data_dir = self.possum_dir
                data_domain = self.possum_domain

            else:
                await ctx.reply('Only `aaaa` and `possum` are valid parameters!', silent=True)
                return
                
            #If the filename is 'rand' generate a random 8-character long base62 filename using the previously created 'characters' variable
            if filename.lower() == 'rand':
                filename = "".join(choice(characters) for _ in range(8))
            
            #Discord disabled embed detection for the URL
            #Strips all greater-than and less-than symbols from the URL string
            #Allows the user to supply a URL without making it embed
            if URL.startswith('<') or URL.endswith('>'):
                URL = URL.replace('<', '')
                URL = URL.replace('>', '')

            if mode.upper() == 'YT':
                
                #Disallow playlists
                if not "&list=" in URL and not "playlist" in URL:
                
                    #Download the best (up to 720p) MP4 video and m4a audio, and then combines them
                    #Or a single video with audio included (up to 720p), if that's the best option
                    arg = f'yt-dlp -f bv[ext=mp4]["height<=720"]+ba[ext=m4a]/b[ext=mp4]["height<=720"] "{URL}" -o "{data_dir}{filename}.%(ext)s"'
                    async with ctx.typing():
                        msg = await ctx.reply('Creating quantum tunnel... Tunnel created! Quantizing data...', silent=True)
                        
                        #Attempt to run command with above args
                        try:
                            process = await create_subprocess_shell(arg, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                            await process.wait()
                            stdout, stderr = await process.communicate()

                        except Exception as e:
                            print('{}: {}'.format(type(e).__name__, e))
                            await ctx.reply('Error, quantization tunnel collapsed unexpectedly!', silent=False)
                            return
                        
                        #yt-dlp can sometimes output non-fatal errors to stderr
                        #Rather than use it to cancel the process if anything is found
                        #simply print the output
                        #To-do: Figure out which kind of fatal messages it can return, and attempt to look for/parse them
                        if stderr:
                            await ctx.reply(stderr.decode(), silent=True)

                        #If a file with the same name already exists, yt-dlp returns this string somewhere in it's output
                        if 'has already been downloaded' in stdout.decode():
                            await msg.edit(content=msg.content + '\nFilename already exists, consider using a different name')
                            return
                        
                        #If this piece of code is reached, it's assumed that everything went well.
                        #This could definitely be improved, but I'm already losing my sanity
                        elif stdout:

                            #If the downloaded video file is larger than 50MB's
                            if int(stat(f'{data_dir}{filename}.mp4').st_size / (1024 * 1024)) > 50:
                                msg = await msg.edit(content=msg.content + '\nDataset exceeded recommended limit! Crunching some bits... this might take a ***bit***')
                                #Try and first lower the resolution of the original video by 1.5 e.g. 720p turns into 480. 
                                #For Discord embeds, this doesn't hurt viewability much, if at all
                                
                                #Get JSON output of the first video stream's metadata. Youtube only allows a single video stream, so this should always work
                                arg2 = f'ffprobe -v quiet -show_streams -select_streams v:0 -of json {data_dir}{filename}.mp4'
                                
                                #Attempt to run command with above args
                                try:
                                    self.stream = await create_subprocess_shell(arg2, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                                    self.stdout, self.stderr = await self.stream.communicate()
                                    await self.stream.wait()
                                except Exception as e:
                                    print('{}: {}'.format(type(e).__name__, e))
                                    await ctx.reply('Error getting video metadata!', silent=True)
                                    return

                                #Load the "streams" key, which holds all the metadata information
                                video_metadata = loads(self.stdout)['streams'][0]
                                
                                #Attempt to parse, divide, and save the video's width and height in int, to remove any decimal points
                                try:
                                    self.frame_width = int(video_metadata['coded_width'] / 1.5)
                                    self.frame_height = int(video_metadata['coded_height'] / 1.5)
                                except Exception as e:
                                    print('{}: {}'.format(type(e).__name__, e))
                                    await ctx.reply('Error parsing video resolution, manual conversion required!', silent=True)
                                    return

                                #Transcode original video into an h264 stream, with a reasonable CRF value of 30, and scale the video to the new resolution.
                                #In the future, a check should be made whether the video has audio or not, either by checking if there's an audio stream
                                #or the audio stream's bitrate (I don't know how Youtube handles muted videos)
                                arg3 = f'ffmpeg -y -i {data_dir}{filename}.mp4 -c:v libx264 -c:a aac -crf 30 -b:v 0 -b:a 192k -movflags +faststart -vf scale={self.frame_width}:{self.frame_height} -f mp4 {data_dir}{filename}.tmp'
                                
                                #Attempt to run command with above args
                                try:
                                    self.process2 = await create_subprocess_shell(arg3)
                                    await self.process2.wait()
                                except Exception as e:
                                    print('{}: {}'.format(type(e).__name__, e))
                                    await ctx.reply('Error transcoding resized video!', silent=True)
                                    return

                                #If the returncode is 0, i.e. no errors happened
                                if self.process2.returncode == 0:
                                    
                                    #Check if the new lower-resolution version is under 50MB's.
                                    #as a last resort, If not, enter an endless loop and keep trying a lower bitrate until one works
                                    bitrate_decrease = 0
                                    attempts = 0
                                    while int(stat(f'{data_dir}{filename}.tmp').st_size / (1024 * 1024)) > 50:
                                        
                                        #Attempt to parse, convert from string, to float, to int, and save the video duration
                                        #100% accuracy down to the exact millisecond isn't required, so we just get the whole number instead
                                        try:
                                            video_duration = int(float(video_duration['duration']))
                                        except Exception as e:
                                            print('{}: {}'.format(type(e).__name__, e))
                                            await ctx.reply('Error parsing video duration, manual conversion required!', silent=True)
                                            return
                                    
                                        #calculate the average bitrate required to reach around 50MB's
                                        #by multiplying 50 by 8192 (convert megabits to kilobits) 
                                        #dividing that by the video length, and subtracting the audio bitrate
                                        #Audio bitrate is hardcoded for now.
                                        bitrate = (50 * 8192) / video_duration - 192 - bitrate_decrease

                                        #Transcode original video into an h264 stream, with an average bitrate calculated from the above code, and scale the video to the new resolution
                                        #In the future, a check should be made whether the video has audio or not, either by checking if there's an audio stream
                                        #or the audio stream's bitrate (I don't know how Youtube handles muted videos)
                                        arg4 = f'ffmpeg -y -i {data_dir}{filename}.mp4 -c:v libx264 -c:a aac -b:v {str(int(bitrate))}k -b:a 192k -movflags +faststart -vf scale={self.frame_width}:{self.frame_height} -f mp4 {data_dir}{filename}.tmp'
                                    
                                        try:
                                            self.process3 = await create_subprocess_shell(arg4)
                                            await self.process3.wait()
                                        except Exception as e:
                                            print('{}: {}'.format(type(e).__name__, e))
                                            await ctx.reply('Error transcoding resized with average bitrate video!', silent=True)
                                            return

                                        #Increase attemps by 1
                                        attempts += 1
                                        #Increase by 100 kilobits, to decrease the average bitrate by 100 kilotbits
                                        bitrate_decrease += 100
                                    
                                    #Attempt to delete the original video, and then rename the transcoded .tmp video to .mp4
                                    try:
                                        remove(f'{data_dir}{filename}.mp4')
                                        rename(f'{data_dir}{filename}.tmp', f'{data_dir}{filename}.mp4')
                                    
                                    except Exception as e:
                                        print('{}: {}'.format(type(e).__name__, e))
                                        await ctx.reply('Error moving/removing file!', silent=True)
                                        return
                                    
                                    #If the bitrate option was reached, this would be at least 1
                                    #Otherwise if it's 0, it means it never attempted to transcode with a variable bitrate
                                    if attempts == 0:
                                        message = f'\nSuccess! Data quantized and bit-crunched to <{data_domain}{filename}.mp4>\nResized to {self.frame_width}:{self.frame_height}'
                                    else:
                                        message = f'\nSuccess! Data quantized and bit-crunched to <{data_domain}{filename}.mp4>\nUsing {bitrate}k/s and Resized to {self.frame_width}:{self.frame_height} with {attempts} attemp(s)'

                                    await msg.edit(content=msg.content + message)

                                #Else statement for the process returncode, from the initial ffmpeg command
                                else:
                                    await ctx.reply('Non-0 exit status code detected!', silent=True)
                            
                            #Else statement if file was under 50MB's        
                            else:
                                await msg.edit(content=msg.content + f'\nSuccess! Data quantized to <{data_domain}{filename}.mp4>')

                #Else statement if the URL is a Youtube playlist
                else:
                    await ctx.reply('Playlists not supported', silent=True)

            #Else statement if mode is not equals YT
            else:
                msg = await ctx.reply('Creating quantum tunnel... Tunnel created! Quantizing data...', silent=True)
                while True:

                    #If URL contains a file extension at the end, and the filename does not, split and add the extension to the filename
                    if path.splitext(URL)[1] and not path.splitext(filename)[1]:
                        filename = filename + path.splitext(URL)[1].lower()
                    
                    elif path.splitext(filename)[1]:
                        pass

                    else:
                        await msg.edit(content=msg.content + '\nNo file extension was found for the file!')
                        return
                    
                    arg = f'wget -nc -O {data_dir}{filename} {URL}'
                    
                    try:
                        process = await create_subprocess_shell(arg, stderr=subprocess.PIPE)
                    
                    except Exception as e:
                        print('{}: {}'.format(type(e).__name__, e))
                        await ctx.reply('Error, quantization tunnel collapsed unexpectedly!', silent=True)
                        return

                    stdout, stderr = await process.communicate()

                    #If the file already exist, either notify the user, or if they chose a random filename, loop back to the start and try again with a new one
                    if 'already there; not retrieving' in stderr.decode():
                        
                        if not filename.lower() == 'rand':
                            await msg.edit(content=msg.content + '\nFilename already exists, consider using a different name')
                            return
                        
                        else:
                            filename = "".join(choice(characters) for _ in range(8))
                            continue
                    else:
                        await msg.edit(content=msg.content + f'\nSuccess! Data quantized to <{data_domain}{filename}>')
                        break
        
        
        #Else statement if the URL, filename or location variables are empty
        else:
            await ctx.reply('Command requires 3 arguments:\n```?quantize <URL> <filename> <aaaa|possum>``` or ```?quantize <URL> <filename> <aaaa|possum> YT``` to use yt-dlp to download it', silent=True)

######################################################################################################

    @commands.command(aliases=['requantise'], brief="(Bot owner only) Rename a file on aaaa.lobadk.com.", description="Renames the specified file. Requires and supports 2 arguments. Only alphanumeric, underscores and a single dot allowed, and at least one character must appear after the dot when chosing a new name.")
    @commands.is_owner()
    async def requantize(self, ctx, current_filename='', new_filename=''):
        if current_filename and new_filename:

            data_dir = self.aaaa_dir
            
            #allow only alphanumeric, underscores, a single dot and at least one alphanumeric after the dot
            allowed = compile('^[\w]*(\.){1,}[\w]{1,}$')
            if not '/' in current_filename and allowed.match(current_filename) and allowed.match(new_filename):
                await ctx.reply('Attempting to requantize data...', silent=True)
                
                try:
                    rename(f'{data_dir}{current_filename}', f'{data_dir}{new_filename}')
                
                except FileNotFoundError:
                    await ctx.reply('Error! Data does not exist', silent=True)
                
                except FileExistsError:
                    await ctx.reply('Error! Cannot requantize, data already exists', silent=True)
                
                except Exception as e:
                    print('{}: {}'.format(type(e).__name__, e))
                    await ctx.reply('Critical error! Check logs for info', silent=True)
                await ctx.reply('Success!', silent=True)

            else:
                await ctx.reply('Only alphanumeric and a dot allowed. Extension required. Syntax is:\n```name.extension```', silent=True)
        else:
            await ctx.reply('Command requires 2 arguments:\n```?requantize <current.name> <new.name>```', silent=True)

######################################################################################################

    @commands.command(brief="(Bot owner only) Runs git commands in the bots directory.", description="Run any git command by passing along the arguments specified. Mainly used for updating the bot or swapping versions, but there is no limit.")
    @commands.is_owner()
    async def git(self, ctx, *, git_arguments):
        if git_arguments:

            #Only allow alphanumeric, underscores, hyphens and whitespaces
            allowed = compile('^[\w\s-]*$')
            if allowed.match(git_arguments):

                cmd = f'git {git_arguments}'
                
                try:
                    process = await create_subprocess_shell(cmd, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
                except Exception as e:
                    print('{}: {}'.format(type(e).__name__, e))
                    await ctx.reply('Error running command', silent=True)
                    return
                    
                stderr, stdout = await process.communicate()
                stdout = stdout.decode()
                stdout = stdout.replace("b'","")
                stdout = stdout.replace("\\n'","")
                stderr = stderr.decode()
                stderr = stderr.replace("b'","")
                stderr = stderr.replace("\\n'","")
                
                if stderr:
                    await ctx.reply(stderr, silent=True)
                
                elif stdout:
                    await ctx.reply(stdout, silent=True)
                
                else:
                    await ctx.message.add_reaction('👍')

######################################################################################################

    @commands.command(brief="(Bot owner only) Fetches new updates and reloads all changed/updated cogs/extensions.", description="Fetches the newest version by running 'git pull' and then reloads the cogs/extensions if successful.")
    @commands.is_owner()
    async def update(self, ctx):
        #Attempt to get the current commit HASH before updating
        try:
            process1 = await create_subprocess_shell('git rev-parse --short HEAD', stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        except Exception as e:
            print('{}: {}'.format(type(e).__name__, e))
            await ctx.reply('Error getting current Git information', silent=True)
            return

        stderr1, stdout1 = await process1.communicate()

        current_version = stderr1.decode().replace('\n', '')

        try:
            process2 = await create_subprocess_shell('git pull', stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            
            #DO NOT CHANGE ORDER
            #Git's output seems to be reversed, and most information gets piped to STDERR instead for some reason
            #STDOUT may also sometimes contain either the data, or some other random data, or part of the whole output, from STDERR
            #"Aready up to date" is piped to STDUT, but output from file changes when doing "git pull" for example
            #Are outputted to STDERR instead, hence why it is also reversed here
            stderr2, stdout2 = await process2.communicate()
        
        except Exception as e:
            print('{}: {}'.format(type(e).__name__, e))
            await ctx.reply('Error running update', silent=True)
            return

        #For some reason after decoding Git's output stream, "b'" and "\\n'" shows up everywhere in the output
        #This removes any of them, cleaning up the output Test
        stdout2 = stdout2.decode()
        stdout2 = stdout2.replace("b'","")
        stdout2 = stdout2.replace("\\n'","")
        stdout2 = stdout2.replace("\n'","")
        stderr2 = stderr2.decode()
        stderr2 = stderr2.replace("b'","")
        stderr2 = stderr2.replace("\\n'","")
        stderr2 = stderr2.replace("\n'","")

        #For some reason Git on Windows returns the string without hyphens, while Linux returns it with hyphens
        if 'Already up to date' in stderr2 or 'Already up-to-date' in stderr2:
            await ctx.reply(stderr2, silent=True)
        
        elif stderr2:

            #Send the output of Git, which displays whichs files has been updated, and how much
            #Then sleep 2 seconds to allow the text to be sent, and read
            msg = await ctx.reply(stderr2, silent=True)
            await asyncsleep(2)

            #Attempt to get a list of files that changed between the pre-update version, using the previously required HASH, and now
            try:
                process3 = await create_subprocess_shell(f'git diff --name-only {current_version} HEAD', stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            except Exception as e:
                print('{}: {}'.format(type(e).__name__, e))
                await msg.edit(content=msg.content + '\nError running file-change check. Manual reloading required')
                return
            
            #Save the output (filenames) in stdout2
            stderr3, stdout3 = await process3.communicate()

            #Decode and remove "b'" characters
            output = stderr3.decode().replace("b'","")

            #Iterate through each listed file
            if 'QuantumKat.py' in output:
                msg = await msg.edit(content=msg.content + '\nMain script updated, reboot?')
                def check(m: Message):  # m = discord.Message.
                    return m.author.id == ctx.author.id and m.channel.id == ctx.channel.id and m.content.lower() == 'yes'
                
                try:
                    await self.bot.wait_for('message', check=check, timeout=10)
                except TimeoutError:
                    msg = await msg.edit(content=msg.content + '\nNot rebooting...')
                else:
                    await ctx.invoke(self.bot.get_command('reboot'))
            
            extensions = []
            for cog in listdir('./cogs'):
                if cog.endswith('.py'):
                    extensions.append(f'cogs.{cog[:-3]}')

            for extension in extensions:
                if extension[5:] in output:
                    try:
                        await self.bot.reload_extension(extension)
                        msg = await msg.edit(content=msg.content + f'\nPurging updated {path.basename(extension[5:])}!')
                    
                    except commands.ExtensionNotLoaded as e:
                        print('{}: {}'.format(type(e).__name__, e))
                        await msg.edit(content=msg.content + f'\n{path.basename(extension[5:])} is not running, or could not be found')
                    
                    except commands.ExtensionNotFound as e:
                        print('{}: {}'.format(type(e).__name__, e))
                        await msg.edit(content=msg.content + f'\n{path.basename(extension[5:])} could not be found!')
                    
                    except commands.NoEntryPointError as e:
                        print('{}: {}'.format(type(e).__name__, e))
                        await msg.edit(content=msg.content + f'\nsuccessfully loaded {path.basename(extension[5:])}, but no setup was found!')
                
        
        elif stdout2:
            await ctx.reply(stdout2, silent=True)

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
                allowed = compile('^[\w]*(\.){1,}[\w]{1,}$')
                if allowed.match(filename):

                    try:
                        remove(f'/var/www/{data_dir}/{filename}')
                    
                    except FileNotFoundError:
                        await ctx.reply('Dataset not found. Did you spell it correctly?', silent=True)
                    
                    except Exception as e:
                        print('{}: {}'.format(type(e).__name__, e))
                        await ctx.reply('Error dequantising dataset!', silent=True)
                
                    await ctx.reply(f'Successfully dequantised and purged {filename}!', silent=True)
                    
                else:
                    await ctx.reply('Only alphanumeric and a dot allowed. Extension required. Syntax is:\n```?dequantise name.extension aaaa|possum```', silent=True)
            
            else:
                await ctx.reply('Only `aaaa` and `possum` are valid parameters!', silent=True)

        else:
            await ctx.reply('Filename and location required!\n`?dequantise|dequantize <filename> aaaa|possum`', silent=True)

######################################################################################################

    @commands.command()
    @commands.is_owner()
    async def status(self, ctx):
        await ctx.reply(f'''
Current CPU Usage: {cpu_percent(1)}%
RAM: {int(virtual_memory().used / 1024 / 1024)}MB / {int(virtual_memory().total / 1024 / 1024)}MB | {virtual_memory().percent}%
Primary disk: {int(disk_usage('/').used / 1024 / 1024 / 1000)}GB / {int(disk_usage('/').total / 1024 / 1024 / 1000)}GB | {disk_usage('/').percent}%
''', silent=True)

######################################################################################################

    @commands.command()
    @commands.is_owner()
    async def reboot(self, ctx):
        await ctx.send('Shutting down extensions and rebooting...')   
        for cog in listdir('./cogs'):
            if cog.endswith('.py'):
                try:
                    await self.bot.unload_extension(f'cogs.{cog[:-3]}')
                except commands.ExtensionNotLoaded:
                    continue
        
        execl(executable, executable, * argv)

######################################################################################################

    print('Started Entanglements!')
async def setup(bot):
    await bot.add_cog(Entanglements(bot))
