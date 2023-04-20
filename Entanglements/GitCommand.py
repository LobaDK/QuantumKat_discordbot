from re import compile
from asyncio import create_subprocess_shell, subprocess

async def GitCommand(self, ctx, git_arguments):
    if git_arguments:

        #Only allow alphanumeric, underscores, hyphens and whitespaces
        allowed = compile('^[\w\s-]*$')
        if allowed.match(git_arguments):

            cmd = f'git {git_arguments}'
            
            try:
                process = await create_subprocess_shell(cmd, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
            except Exception as e:
                print('{}: {}'.format(type(e).__name__, e))
                await ctx.send('Error running command')
                return
                
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