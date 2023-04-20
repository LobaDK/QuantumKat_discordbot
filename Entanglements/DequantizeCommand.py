from re import compile
from os import remove

async def DequantizeCommand(self, ctx, filename, location):
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
                    await ctx.send('Dataset not found. Did you spell it correctly?')
                
                except Exception as e:
                    print('{}: {}'.format(type(e).__name__, e))
                    await ctx.send('Error dequantising dataset!')
            
                await ctx.send(f'Successfully dequantised and purged {filename}!')
                
            else:
                await ctx.send('Only alphanumeric and a dot allowed. Extension required. Syntax is:\n```?dequantise name.extension aaaa|possum```')
        
        else:
            await ctx.send('Only `aaaa` and `possum` are valid parameters!')
    
    else:
        await ctx.send('Filename and location required!\n`?dequantise|dequantize <filename> aaaa|possum`')