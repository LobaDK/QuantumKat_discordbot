from re import compile
from os import rename

async def RequantizeCommand(self, ctx, current_filename, new_filename):
    if current_filename and new_filename:

        data_dir = self.aaaa_dir
        
        #allow only alphanumeric, underscores, a single dot and at least one alphanumeric after the dot
        allowed = compile('^[\w]*(\.){1,}[\w]{1,}$')
        if not '/' in current_filename and allowed.match(current_filename) and allowed.match(new_filename):
            await ctx.send('Attempting to requantize data...')
            
            try:
                rename(f'{data_dir}{current_filename}', f'{data_dir}{new_filename}')
            
            except FileNotFoundError:
                await ctx.send('Error! Data does not exist')
            
            except FileExistsError:
                await ctx.send('Error! Cannot requantize, data already exists')
            
            except Exception as e:
                print('{}: {}'.format(type(e).__name__, e))
                await ctx.send('Critical error! Check logs for info')
            await ctx.send('Success!')

        else:
            await ctx.send('Only alphanumeric and a dot allowed. Extension required. Syntax is:\n```name.extension```')
    else:
        await ctx.send('Command requires 2 arguments:\n```?requantize <current.name> <new.name>```')