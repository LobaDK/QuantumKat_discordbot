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
                    await ctx.reply('Dataset not found. Did you spell it correctly?')
                
                except Exception as e:
                    print('{}: {}'.format(type(e).__name__, e))
                    await ctx.reply('Error dequantising dataset!')
            
                await ctx.reply(f'Successfully dequantised and purged {filename}!')
                
            else:
                await ctx.reply('Only alphanumeric and a dot allowed. Extension required. Syntax is:\n```?dequantise name.extension aaaa|possum```')
        
        else:
            await ctx.reply('Only `aaaa` and `possum` are valid parameters!')
    
    else:
        await ctx.reply('Filename and location required!\n`?dequantise|dequantize <filename> aaaa|possum`')