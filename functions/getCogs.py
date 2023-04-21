from os import listdir

def getCogs():
    extensions = []
    for cog in listdir('./cogs'):
        if cog.endswith('.py'):
            extensions.append(f'cogs.{cog[:-3]}')
    return extensions