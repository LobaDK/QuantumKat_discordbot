from requests import get
from bs4 import BeautifulSoup
from re import compile

async def aaaaSearchCommand(self, ctx, search_keyword):
    if len(search_keyword) >= 2:
        allowed = compile('^(\.?)[a-zA-Z0-9]+(\.?)$')
        if allowed.match(search_keyword):
            response = get(f'https://aaaa.lobadk.com/?search={search_keyword}')
            soup = BeautifulSoup(response.text, 'lxml')
            links = []

            for link in soup.find_all('a'):
                temp = link.get('href')
                if temp.startswith('http') or temp.startswith(',') or temp.startswith('.'):
                    continue
                links.append(temp)

            if len(links) == 0:
                await ctx.send('Search returned nothing')
            else:
                if len(' '.join(links)) > 4000:
                    await ctx.send('Too many results! Try narrowing down the search')
                else:
                    await ctx.send(' '.join(links))
        else:
            await ctx.send('At least two alphanumeric characters are required, or 1 alphanumeric character and a `.` at the start or end')
    else:
        await ctx.send('Search too short! A minimum of 2 characters are required')