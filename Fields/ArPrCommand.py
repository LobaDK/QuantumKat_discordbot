from requests import get
from bs4 import BeautifulSoup, MarkupResemblesLocatorWarning
import warnings

warnings.filterwarnings("ignore", category=MarkupResemblesLocatorWarning)

async def arpr(ctx, url):
    links = []
    for _ in range(ctx.message.content.split(" ")[0].count("r")):
        response = get(url)
        soup = BeautifulSoup(response.text, 'lxml')
        link = soup.find('body')
        links.append(url.replace('botrandom', '') + link.get_text().replace('./', ''))
    await ctx.send('\n'.join(links))