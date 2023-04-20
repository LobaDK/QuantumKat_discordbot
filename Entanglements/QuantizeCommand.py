from string import ascii_letters, digits
from random import choice
from asyncio import create_subprocess_shell, subprocess
from os import stat, remove, rename, path
from json import loads

async def QuantizeCommand(self, ctx, URL, filename, location, mode):
    #Make a characters variable that combines lower- and uppercase letters, as well as numbers.
    #Used to generate a random filename, if specified
    characters = ascii_letters + digits
    if URL and filename and location:
        
        if location.lower() == 'aaaa':
            data_dir = self.aaaa_dir
            data_domain = self.aaaa_domain
        
        elif location.lower()== 'possum':
            data_dir = self.possum_dir
            data_domain = self.possum_domain

        else:
            await ctx.send('Only `aaaa` and `possum` are valid parameters!')
            return
            
        #If the filename is 'rand' generate a random 8-character long base62 filename using the previously created 'characters' variable
        if filename.lower() == 'rand':
            filename = "".join(choice(characters) for _ in range(8))
        
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
                    process = await create_subprocess_shell(arg, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
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
                    if int(stat(f'{data_dir}{filename}.mp4').st_size / (1024 * 1024)) > 50:
                        await ctx.reply('Dataset exceeded recommended limit! Crunching some bits... this might take a ***bit***')
                        #Try and first lower the resolution of the original video by 1.5 e.g. 1080p turns into 720p. 
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
                            await ctx.reply('Error getting video metadata!')
                            return

                        #Load the "streams" key, which holds all the metadata information
                        video_metadata = loads(self.stdout)['streams'][0]
                        
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
                            self.process2 = await create_subprocess_shell(arg3)
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
                            while int(stat(f'{data_dir}{filename}.tmp').st_size / (1024 * 1024)) > 50:
                                
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
                                arg4 = f'ffmpeg -y -i {data_dir}{filename}.mp4 -c:v libx264 -c:a aac -b:v {str(int(bitrate))}k -b:a 192k -movflags +faststart -vf scale={self.frame_width}:{self.frame_height} -f mp4 {data_dir}{filename}.tmp'
                            
                                try:
                                    self.process3 = await create_subprocess_shell(arg4)
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
                                remove(f'{data_dir}{filename}.mp4')
                                rename(f'{data_dir}{filename}.tmp', f'{data_dir}{filename}.mp4')
                            
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

        #Else statement if mode is not equals YT
        else:
            await ctx.send('Creating quantum tunnel... Tunnel created! Quantizing data...')
            while True:

                #If URL contains a file extension at the end, and the filename does not, split and add the extension to the filename
                if path.splitext(URL)[1] and not path.splitext(filename)[1]:
                    filename = filename + path.splitext(URL)[1].lower()
                
                elif path.splitext(filename)[1]:
                    pass

                else:
                    await ctx.send('No file extension was found for the file!')
                    return
                
                arg = f'wget -nc -O {data_dir}{filename} {URL}'
                
                try:
                    process = await create_subprocess_shell(arg, stderr=subprocess.PIPE)
                
                except Exception as e:
                    print('{}: {}'.format(type(e).__name__, e))
                    await ctx.send('Error, quantization tunnel collapsed unexpectedly!')
                    return

                stdout, stderr = await process.communicate()

                #If the file already exist, either notify the user, or if they chose a random filename, loop back to the start and try again with a new one
                if 'already there; not retrieving' in stderr.decode():
                    
                    if not filename.lower() == 'rand':
                        await ctx.send('Filename already exists, consider using a different name')
                        return
                    
                    else:
                        filename = "".join(choice(characters) for _ in range(8))
                        continue
                else:
                    await ctx.send(f'Success! Data quantized to <{data_domain}{filename}>')
                    break
    
    
    #Else statement if the URL, filename or location variables are empty
    else:
        await ctx.send('Command requires 3 arguments:\n```?quantize <URL> <filename> <aaaa|possum>``` or ```?quantize <URL> <filename> <aaaa|possum> YT``` to use yt-dlp to download it')