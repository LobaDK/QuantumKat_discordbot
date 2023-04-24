from asyncio import create_subprocess_shell, subprocess, TimeoutError, sleep
from discord.ext import commands
from os import path, listdir
from discord import Message

from QuantumKats.RebootCommand import RebootCommand

async def UpdateCommand(self, ctx):
    #Attempt to get the current commit HASH before updating
    try:
        process1 = await create_subprocess_shell('git rev-parse --short HEAD', stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except Exception as e:
        print('{}: {}'.format(type(e).__name__, e))
        await ctx.send('Error getting current Git information')
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
        await ctx.send('Error running update')
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
        await ctx.send(stderr2)
    
    elif stderr2:

        #Send the output of Git, which displays whichs files has been updated, and how much
        #Then sleep 2 seconds to allow the text to be sent, and read
        await ctx.send(stderr2)
        await sleep(2)

        #Attempt to get a list of files that changed between the pre-update version, using the previously required HASH, and now
        try:
            process3 = await create_subprocess_shell(f'git diff --name-only {current_version} HEAD', stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        except Exception as e:
            print('{}: {}'.format(type(e).__name__, e))
            await ctx.send('Error running file-change check. Manual reloading required')
            return
        
        #Save the output (filenames) in stdout2
        stderr3, stdout3 = await process3.communicate()

        #Decode and remove "b'" characters
        output = stderr3.decode().replace("b'","")

        #Iterate through each listed file
        if 'QuantumKat.py' in output:
            await ctx.send('Main script updated, reboot?')
            def check(m: Message):  # m = discord.Message.
                return m.author.id == ctx.author.id and m.channel.id == ctx.channel.id and m.content.lower() == 'yes'
            
            try:
                await self.bot.wait_for('message', check=check, timeout=10)
            except TimeoutError:
                await ctx.reply('No valid reply sent within 10 seconds')
            else:
                await RebootCommand(ctx, self.bot)
        
        extensions = []
        for cog in listdir('./cogs'):
            if cog.endswith('.py'):
                extensions.append(f'cogs.{cog[:-3]}')

        for extension in extensions:
            if extension[5:] in output:
                try:
                    await self.bot.reload_extension(extension)
                    await ctx.send(f'Purging updated {path.basename(extension)}!')
                
                except commands.ExtensionNotLoaded as e:
                    print('{}: {}'.format(type(e).__name__, e))
                    await ctx.send(f'{path.basename(extension)} is not running, or could not be found')
                
                except commands.ExtensionNotFound as e:
                    print('{}: {}'.format(type(e).__name__, e))
                    await ctx.send(f'{path.basename(extension)} could not be found!')
                
                except commands.NoEntryPointError as e:
                    print('{}: {}'.format(type(e).__name__, e))
                    await ctx.send(f'successfully loaded {path.basename(extension)}, but no setup was found!')
            
    
    elif stdout2:
        await ctx.send(stdout2)
    