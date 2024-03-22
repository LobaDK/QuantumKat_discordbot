from random import randint, choice
from discord import Game, User, TextChannel, DMChannel
from discord.ext import commands, tasks
from num2words import num2words
import logging
import threading

ONE_HOUR_IN_MILLISECONDS = 3_600_000


class Activity(commands.Cog):
    def __init__(self, bot: commands.Bot):

        self.bot = bot

        self.db_conn = bot.db_conn

        if "discord.Activity" in logging.Logger.manager.loggerDict:
            self.logger = logging.getLogger("discord.Activity")
        else:
            self.logger = logging.getLogger("discord.Activity")
            self.logger.setLevel(logging.INFO)
            handler = logging.FileHandler(
                filename="logs/activity.log", encoding="utf-8", mode="a"
            )
            date_format = "%Y-%m-%d %H:%M:%S"
            formatter = logging.Formatter(
                "[{asctime}] [{levelname:<8}] {name}: {message}",
                datefmt=date_format,
                style="{",
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)

        self.hissList = ["Hissing", "Hissed"]

        self.purgeList = ["Purrging", "Purrged"]

        self.purrList = ["Purring", "Purred"]

        self.vibrateList = ["Vibrating", "Vibrated", "Fluctuating", "Fluctuated"]

        self.nounList = [
            "a chair",
            "a table",
            "a vase",
            "a long-lost credit card",
            "some strangers phone",
            "a stranger",
            "an error",
            "a bucket",
            "a bucket of milk",
            "redacted",
            "a cat",
            "a quantum cat",
            "an alien from the 7th dimension",
            "a blackhole",
            "a random star",
            "a random planet",
            "Earth",
            "the void",
        ]

        self.locationList = ["dimension", "universe", "timeline", "reality"]

        self.messages = [
            "{hiss} in the {ordinal} {location}",
            "{purr} in the {ordinal} {location}",
            "{hiss} at {noun} in the {ordinal} {location}",
            "{purr} at {noun} in the {ordinal} {location}",
            "{vibrate} at {purrHz}hz in the {ordinal} {location}",
            "{purr} at {purrHz}hz in the {ordinal} {location}",
            "{purge} {noun} in the {ordinal} {location}",
            ("Segfault in... ErrorIt?656E64\t\trebooting faulty" "... rF7_Q>~bTV"),
            ("69 74 77 61 73 6e 27 74 73 75 70 70 6f 73 65 64 74 " "6f 65 6e 64"),
        ]

        self.logger.info("Starting Activity!")
        self.change_activity.start()

    # command splitter for easier reading and navigating

    def cog_unload(self):
        self.logger.info("Stopping Activity!")
        self.change_activity.cancel()

    async def remind_user(
        self,
        user: User,
        channel: TextChannel | DMChannel,
        reminder_message: str,
    ) -> None:
        if isinstance(channel, DMChannel):
            await channel.send(reminder_message)
        elif isinstance(channel, TextChannel):
            await channel.send(f"{user.mention}, {reminder_message}")

    async def start_reminder(
        self,
        user: User,
        channel: TextChannel | DMChannel,
        reminder_id: int,
        reminder_message: str,
        reminder_time: int,
    ) -> None:
        self.logger.info(
            f"Reminder {reminder_id} is scheduled for {reminder_time}ms from now."
        )
        threading.Timer(
            reminder_time / 1000,
            self.remind_user,
            args=(user, channel, reminder_message),
        ).start()
        self.db_conn.execute(
            """UPDATE reminders SET is_in_queue = 1 WHERE id = ?""",
            (reminder_id,),
        )
        self.db_conn.commit()

    async def check_reminder(self, reminder):
        reminder_time = reminder[8]
        is_in_queue = reminder[9]
        if reminder_time <= ONE_HOUR_IN_MILLISECONDS and not is_in_queue:
            user_id = reminder[1]
            server_id = reminder[3]
            channel_id = reminder[5]
            server = self.bot.get_guild(server_id)
            channel = server.get_channel(channel_id)
            user = await self.bot.fetch_user(user_id)
            reminder_message = reminder[7]
            reminder_id = reminder[0]
            await self.start_reminder(
                user, channel, reminder_id, reminder_message, reminder_time
            )

    @tasks.loop(hours=1, count=None, reconnect=True)
    async def reminder_listener(self):
        reminders = self.db_conn.execute(
            """SELECT * FROM reminders WHERE is_in_queue = 0"""
        ).fetchall()

        for reminder in reminders:
            self.check_reminder(reminder)

    @reminder_listener.before_loop
    async def before_reminder_listener(self):
        self.logger.info("Starting Reminder listener...")
        await self.bot.wait_until_ready()
        self.logger.info("Reminder listener started!")

    # command splitter for easier reading and navigating

    @tasks.loop(minutes=randint(30, 180), count=None, reconnect=True)
    async def change_activity(self):
        interval = randint(10, 180)
        self.logger.info(f"Changing activity interval to: {interval} minutes")
        self.change_activity.change_interval(minutes=(interval))

        purrHz = randint(1, 100_000)
        ordinal = num2words(randint(0, 10_000), to="ordinal_num")

        presence = Game(
            name=choice(self.messages).format(
                hiss=choice(self.hissList),
                purge=choice(self.purgeList),
                purr=choice(self.purrList),
                vibrate=choice(self.vibrateList),
                noun=choice(self.nounList),
                location=choice(self.locationList),
                purrHz=purrHz,
                ordinal=ordinal,
            )
        )

        self.logger.info(f"Changing activity to: {presence.name}")
        await self.bot.change_presence(activity=presence)

    # command splitter for easier reading and navigating

    @change_activity.before_loop
    async def before_change_activity(self):
        self.logger.info("Starting Activity loop...")
        await self.bot.wait_until_ready()
        self.logger.info("Activity loop started!")

    # command splitter for easier reading and navigating

    @commands.command(
        aliases=["activitystop", "astop"],
        brief="(Bot owner only) Stops the displayed activity.",
        description=(
            "Stops the loop that displays a random " "activity under the bot."
        ),
    )
    @commands.is_owner()
    async def ActivityStop(self, ctx: commands.Context):
        if self.change_activity.is_running():
            self.change_activity.cancel()
            await ctx.message.add_reaction("👌")
        else:
            await ctx.reply("Activity is not running!", silent=True)

    # command splitter for easier reading and navigating

    @commands.command(
        aliases=[
            "activityrestart",
            "arestart",
            "ActivityRefresh",
            "activityrefresh",
            "arefresh",
        ],
        brief=("(Bot owner only) Restarts/Refreshes the " "displayed activity."),
        description=(
            "Restarts/Refreshes the loop that displays "
            "a random activity under the bot."
        ),
    )
    @commands.is_owner()
    async def ActivityRestart(self, ctx: commands.Context):
        self.change_activity.restart()
        await ctx.message.add_reaction("👌")

    # command splitter for easier reading and navigating

    @commands.command(
        aliases=["activitystart", "astart"],
        brief=("(Bot owner only) Starts displaying a random " "activity."),
        description=(
            "Starts the loop that displays a random "
            "activity under the bot. A random interval "
            "between 30 to 180 minutes is chosen each "
            "time it loops itself."
        ),
    )
    @commands.is_owner()
    async def ActivityStart(self, ctx: commands.Context):
        if not self.change_activity.is_running():
            self.change_activity.start()
            await ctx.message.add_reaction("👌")
        else:
            await ctx.reply("Activity is already running!", silent=True)


# command splitter for easier reading and navigating


async def setup(bot):
    await bot.add_cog(Activity(bot))
