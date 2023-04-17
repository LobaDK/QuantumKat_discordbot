from re import compile
from requests import head

async def aCommand(self, ctx, filename):
    if filename:
        allowed = compile('[^\w.\-]')
        if not allowed.match(filename):
            URL = f'https://aaaa.lobadk.com/{filename}'
            if head(URL).status_code == 200:
                await ctx.send(URL)
            else:
                await ctx.send('File not found')
    else:
        await ctx.send('Filename required!\n```?a example.mp4```')