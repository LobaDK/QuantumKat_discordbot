from urllib.parse import urljoin
import requests
import random
from bs4 import BeautifulSoup
import discord  

with open('./files/token', 'r') as tokenfile:
    token = tokenfile.read().strip()

client = discord.Client()

@client.event
async def on_ready():
    print(f'{client.user} has connected to Discord!')

@client.event
async def on_message(message):
    if message.author == client.user:
        return
    if message.content.startswith("?ar") or message.content.startswith("?or"):
        links = []
        if message.content.startswith("?ar"):
                url = 'https://aaaa.lobadk.com/'
        elif message.content.startswith("?or"):
                url = 'https://possum.lobadk.com/'
        reponse = requests.get(url)
        soup = BeautifulSoup(reponse.text, 'lxml')
        for link in soup.find_all('a'):
            temp = link.get('href')
            if temp.startswith('http') or temp.startswith(',') or temp.startswith('.'):
                continue
            links.append(temp)
        await message.channel.send(urljoin(url,random.choice(links)))

client.run(token)
