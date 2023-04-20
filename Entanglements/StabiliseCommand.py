from random import choice, randint
from discord.ext import commands
from num2words import num2words


async def StabiliseCommand(self, ctx, module):
    if module:
        location = choice(['reality','universe','dimension','timeline'])
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
                            await ctx.send(f'Superposition irregularity detected in Quantum {cog}! Successfully entangled to the {num2words(randint(1,1000), to="ordinal_num")} {location}!')
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
