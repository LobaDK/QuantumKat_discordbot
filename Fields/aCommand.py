from re import compile
from requests import head

async def aCommand(self, ctx, filename):
    if filename:
        allowed = compile('[^\w.\-]')
        if not allowed.match(filename):
            URL = f'https://aaaa.lobadk.com/{filename}'
            if head(URL).status_code == 200:
                await ctx.reply(URL)
            else:
                await ctx.reply('File not found')
    else:
        await ctx.reply('Filename required!\n```?a example.mp4```')