from discord.ext import commands

async def Entanglecommand(self, ctx, module):
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