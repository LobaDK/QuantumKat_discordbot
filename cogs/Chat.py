from openai import AsyncOpenAI as OpenAI, OpenAIError
import logging
import tiktoken
import os

from discord.ext import commands


class Chat(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        self.db_conn = bot.db_conn

        self.logger = logging.getLogger('discord.Chat')
        self.logger.setLevel(logging.INFO)
        handler = logging.FileHandler(filename='logs/chat.log', encoding='utf-8', mode='w')
        date_format = '%Y-%m-%d %H:%M:%S'
        formatter = logging.Formatter('[{asctime}] [{levelname:<8}] {name}: {message}', datefmt=date_format, style='{')
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)

        # Set the model encoding for tiktoken
        self.encoding = tiktoken.encoding_for_model('gpt-3.5-turbo')
        # Set the system message for ChatGPT. This controls the personality of the bot and how it responds.
        self.system_message = "You are QuantumKat, a cybernetic cat with void-like black fur. You have the intelligence of a human and can talk. You can teleport to any point in time or location between dimensions, realities, universes and timelines. while your past is unknown and you have no knowledge of how you came to existence, you know you have to use these powers to monitor and keep them all safe, however, you are still young and don't quite know how to do it correctly, as well as being clumsy, often resulting in you appearing in an incorrect location or doing the wrong thing. You are quite sarcastic. You are allowed to have opinions on things."
        # Attempt to get the OpenAI API key from the environment variables
        if os.environ.get('OPENAI_API_KEY'):
            self.FOUND_API_KEY = True
            self.openai = OpenAI(api_key=os.environ.get('OPENAI_API_KEY'))
        else:
            self.FOUND_API_KEY = False
            self.logger.error("OpenAI API key not found. Chat commands will not work.")

    def calculate_tokens(self, user_message: str) -> int:
        """
        Calculates the number of tokens in a given user message.

        Parameters:
        - user_message (str): The user message to calculate tokens for.

        Returns:
        - int: The number of tokens in the user message.
        """
        messages = [user_message, self.system_message]
        tokens = 0
        for message in messages:
            tokens += len(self.encoding.encode(message))
        return tokens

    def database_add(self, ctx: commands.Context, user_message: str, assistant_message: str):
        """
        Adds a conversation pair to the database.

        Parameters:
        - ctx (commands.Context): The context of the command.
        - user_message (str): The user message to add to the database.
        - assistant_message (str): The assistant message to add to the database.

        Returns:
        - None
        """
        user_id = ctx.author.id
        user_name = ctx.author.name
        sql = "INSERT INTO chat (user_id, user_name, user_message, assistant_message) VALUES (?, ?, ?, ?)"
        params = (user_id, user_name, user_message, assistant_message)
        self.db_conn.execute(sql, params)

    def database_read(self, ctx: commands.Context):
        """
        Retrieves the user and assistant messages from the database for a specific user.

        Args:
            ctx (commands.Context): The context object representing the invocation context of the command.

        Returns:
            list: A list of dictionaries containing the user and assistant messages.
                    Each dictionary has two keys: 'role' (either 'user' or 'assistant') and 'content' (the message content).
        """
        user_id = ctx.author.id
        sql = "SELECT user_message, assistant_message FROM chat WHERE user_id = ? ORDER BY id DESC LIMIT 10"
        params = (user_id,)
        rows = self.db_conn.execute(sql, params).fetchall()
        messages = []
        for user_message, assistant_message in rows:
            messages.append({"role": "user", "content": user_message})
            messages.append({"role": "assistant", "content": assistant_message})
        return messages

    @commands.command(aliases=['chat', 'talk'], brief='Talk to QuantumKat.', description='Talk to QuantumKat using the OpenAI API/ChatGPT.')
    async def Chat(self, ctx: commands.Context, *, user_message=""):
        if self.FOUND_API_KEY is True:
            if user_message:
                tokens = self.calculate_tokens(user_message)
                if not tokens > 256:
                    command = ctx.invoked_with
                    user_message = ctx.message.clean_content.split(f"{self.bot.command_prefix}{command}", 1)[1].strip()
                    for member in ctx.message.mentions:
                        user_message = user_message.replace(member.mention, member.display_name)
                    self.logger.info(f'User {ctx.author.name} ({ctx.author.id}) initiated chat command with message: {user_message}, using {tokens} tokens.')
                    conversation_history = self.database_read(ctx)
                    async with ctx.typing():
                        try:
                            # Create a conversation with the system message first
                            # Then inject the 10 most recent conversation pairs
                            # Then add the user's message
                            messages = [
                                {
                                    "role": "system",
                                    "content": self.system_message
                                },
                                *conversation_history,
                                {
                                    "role": "user",
                                    "content": user_message
                                }
                            ]

                            response = await self.openai.chat.completions.create(
                                model="gpt-3.5-turbo",
                                messages=messages,
                                temperature=1,
                                max_tokens=512,
                                top_p=1,
                                frequency_penalty=0,
                                presence_penalty=0
                            )
                            chat_response = response.choices[0].message.content

                            self.database_add(ctx, user_message, chat_response)

                            self.logger.info(f'Chat response: {chat_response}, using {response.usage.total_tokens} tokens in total.')
                            await ctx.send(chat_response)
                        except OpenAIError as e:
                            self.logger.error(f'HTTP status code: {e.http_status}, Error message: {e}')
                            await ctx.send(f"OpenAI returned an error with the status code {e.http_status}. Please try again later.")
                else:
                    await ctx.send(f"Message is too long! Your message is {tokens} tokens long, but the maximum is 256 tokens.")
            else:
                await ctx.send("Message cannot be empty! I may be smart, but I'm not a mind reader!")
        else:
            await ctx.send("OpenAI API key not found. Chat commands will not work.")

    print("Started Chat!")


async def setup(bot):
    await bot.add_cog(Chat(bot))
