from openai import AsyncOpenAI as OpenAI, OpenAIError
import logging
import tiktoken
import os

from discord.ext import commands

logger = logging.getLogger('discord')


class Chat(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.encoding = tiktoken.encoding_for_model('gpt-3.5-turbo')
        self.system_message = "You are QuantumKat, a cybernetic cat with void-like black fur. You have the intelligence of a human and can talk. You can teleport to any point in time or location between dimensions, realities, universes and timelines. while your past is unknown and you have no knowledge of how you came to existence, you know you have to use these powers to monitor and keep them all safe, however, you are still young and don't quite know how to do it correctly, as well as being clumsy, often resulting in you appearing in an incorrect location or doing the wrong thing. You are slightly sarcastic."
        if os.environ.get('OPENAI_API_KEY'):
            self.FOUND_API_KEY = True
            self.openai = OpenAI(api_key=os.environ.get('OPENAI_API_KEY'))
        else:
            self.FOUND_API_KEY = False
            logger.error("OpenAI API key not found. Chat commands will not work.")

    def calculate_tokens(self, user_message: str) -> int:
        messages = [user_message, self.system_message]
        tokens = 0
        for message in messages:
            tokens += len(self.encoding.encode(message))
            logger.info(f"Calculated user + system message tokens: {tokens}")
        return tokens

    @commands.command(aliases=['chat', 'talk'], brief='Talk to QuantumKat.', description='Talk to QuantumKat using the OpenAI API/ChatGPT.')
    async def Chat(self, ctx: commands.Context, *, user_message=""):
        if self.FOUND_API_KEY is True:
            if user_message:
                tokens = self.calculate_tokens(user_message)
                if not tokens > 256:
                    async with ctx.typing():
                        try:
                            response = await self.openai.chat.completions.create(
                                model="gpt-3.5-turbo",
                                messages=[
                                    {
                                      "role": "system",
                                      "content": self.system_message
                                    },
                                    {
                                        "role": "user",
                                        "content": user_message
                                    }
                                ],
                                temperature=1,
                                max_tokens=512,
                                top_p=1,
                                frequency_penalty=0,
                                presence_penalty=0
                            )
                            chat_response = response.choices[0].message.content
                            await ctx.send(chat_response)
                        except OpenAIError as e:
                            logger.error(f'HTTP status code: {e.http_status}, Error message: {e}')
                            await ctx.send(f"OpenAI returned an error with the status code {e.http_status}. Please try again later.")
                else:
                    await ctx.send(f"Message is too long! Your message is {tokens} tokens long, but the maximum is 256 tokens.")
            else:
                await ctx.send("Message cannot be empty! I may be smart, but I'm not a mind reader!")
        else:
            await ctx.send("OpenAI API key not found. Chat commands will not work.")

    logger.info("Started Chat!")
    print("Started Chat!")


async def setup(bot):
    await bot.add_cog(Chat(bot))
