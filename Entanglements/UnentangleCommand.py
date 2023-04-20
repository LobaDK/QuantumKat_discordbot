from discord.ext import commands

async def UnentangleCommand(self, ctx, module):
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