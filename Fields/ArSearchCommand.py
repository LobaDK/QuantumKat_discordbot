from re import compile
from requests import get
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from random import choice

async def ArSearchCommand(self, ctx, search_keyword):
    if search_keyword:
        allowed = compile('[^\w.\-]')
        if not allowed.match(search_keyword):
            links = []
            SearchURL = f'https://aaaa.lobadk.com/?search={search_keyword}'
            URL = 'https://aaaa.lobadk.com/'
            response = get(SearchURL)
            soup = BeautifulSoup(response.text, 'lxml')
            for link in soup.find_all('a'):
                temp = link.get('href')
                if temp.startswith('http') or temp.startswith(',') or temp.startswith('.'):
                    continue
                links.append(temp)
            if len(links) == 0:
                await ctx.send('Search returned empty!')
            else:    
                await ctx.send(urljoin(URL, choice(links)))
        else:
            await ctx.send('Invalid character found in search parameter!')
    else:
        await ctx.send('Search parameter required!\n```?ars example```')