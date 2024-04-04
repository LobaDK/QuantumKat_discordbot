import logging
import sqlite3
import os
import shutil
import discord
from discord.ext import commands

"""
This module contains helper classes for logging, database operations, Discord-related operations, and miscellaneous utility functions.
"""


class LogHelper:
    """
    A helper class for logging operations.

    This class provides methods to check if a logger exists, create a logger with a file handler and a stream handler,
    and create file and stream handlers with specified log levels.

    Attributes:
        None

    Methods:
        logger_exists(logger_name): Checks if a logger with the given name exists.
        create_logger(logger_name, log_file, file_log_level, stream_log_level): Creates a logger with the given name and log file.
    """

    def logger_exists(self, logger_name: str) -> bool:
        """
        Checks if a logger with the given name exists.

        Args:
            logger_name (str): The name of the logger to check.

        Returns:
            bool: True if a logger with the given name exists, False otherwise.
        """
        return logger_name in logging.Logger.manager.loggerDict

    def create_logger(
        self,
        logger_name: str,
        log_file: str,
        file_log_level=logging.INFO,
        stream_log_level=logging.ERROR,
    ) -> logging.Logger:
        """
        Creates a logger with the given name and log file.

        Helper function to create, configure, and return a logger with the given name and log file.
        The logger will have a file handler and a stream handler attached to it.
        If the logger already exists, it will be returned without any changes.

        Args:
            logger_name (str): The name of the logger to create.
            log_file (str): The path to the log file to use.
            file_log_level (int, optional): The log level for the file handler. Defaults to logging.INFO.
            stream_log_level (int, optional): The log level for the stream handler. Defaults to logging.ERROR.

        Returns:
            logging.Logger: The created logger.
        """
        if self.logger_exists(logger_name):
            return logging.getLogger(logger_name)

        logger = logging.getLogger(logger_name)
        logger.setLevel(logging.DEBUG)
        file_handler = self._create_file_handler(log_file, file_log_level)
        logger.addHandler(file_handler)

        stream_handler = self._create_stream_handler(stream_log_level)
        logger.addHandler(stream_handler)

        return logger

    def _create_file_handler(self, log_file: str, level: int) -> logging.FileHandler:
        """
        Creates a logging FileHandler with the specified log file and level.

        Args:
            log_file (str): The path and name of the log file to create.

        Returns:
            logging.FileHandler: The file handler object.

        """
        handler = logging.FileHandler(
            filename=log_file,
            encoding="utf-8",
            mode="a",
        )
        date_format = "%Y-%m-%d %H:%M:%S"
        formatter = logging.Formatter(
            "[{asctime}] [{levelname:<8}] {name}: {message}",
            datefmt=date_format,
            style="{",
        )
        handler.setFormatter(formatter)
        handler.setLevel(level)
        return handler

    def _create_stream_handler(self, level: int) -> logging.StreamHandler:
        """
        Creates a logging StreamHandler with the specified log level.

        Returns:
            logging.StreamHandler: The created StreamHandler object.

        """
        handler = logging.StreamHandler()
        date_format = "%Y-%m-%d %H:%M:%S"
        formatter = logging.Formatter(
            "[{asctime}] [{levelname:<8}] {name}: {message}",
            datefmt=date_format,
            style="{",
        )
        handler.setFormatter(formatter)
        handler.setLevel(level)
        return handler


class DBHelper:
    """
    A helper class for SQLite database operations.

    This class provides methods to create tables, read data, insert data, update data, and delete data in an SQLite database.

    Attributes:
        conn (sqlite3.Connection): The SQLite database connection object.
        logger (logging.Logger): The logger object for logging database operations.

    Methods:
        create_table(table_name, columns): Create a table with the given name and columns.
        read_table(table_name, columns, condition): Read data from the table with the given name and columns.
        insert_into_table(table_name, values): Insert values into the table with the given name.
        update_rows(table_name, values, condition): Update rows in the table with the given values and condition.
        delete_rows(table_name, condition): Delete rows from the table with the given condition.
    """

    def __init__(
        self,
        conn: sqlite3.Connection,
        logger=LogHelper().create_logger("DBHelper", "logs/db.log"),
    ):
        """
        DBHelper constructor.

        Args:
            conn (sqlite3.Connection): The SQLite database connection object.
            logger (logging.Logger, optional): The logger object for logging database operations. Defaults to a new logger.
        """
        self.conn = conn
        self.logger = logger

    def create_table(self, table_name: str, columns: tuple):
        """
        Create a table with the given name and columns if it does not already exist.

        Args:
            table_name (str): The name of the table to create.
            columns (tuple): The columns of the table in the format (column1, column2, ...).
        """
        columns_str = ", ".join(columns)
        query = f"CREATE TABLE IF NOT EXISTS {table_name} ({columns_str})"
        self.logger.info(f"Creating table {table_name} with columns {columns}")
        self.conn.execute(query)
        self.conn.commit()

    def read_table(self, table_name: str, columns: tuple, condition: str = "") -> list:
        """
        Read data from the table with the given name and columns.

        Args:
            table_name (str): The name of the table to read from.
            columns (tuple): The columns to read from the table.
            condition (str, optional): The condition to filter the rows. Defaults to "".

        Returns:
            list: A list of rows that match the condition.
        """
        columns_str = ", ".join(columns)
        query = f"SELECT {columns_str} FROM {table_name}"
        if condition:
            query += f" WHERE {condition}"
        self.logger.info(f"Reading data from table {table_name} with columns {columns}")
        cursor = self.conn.execute(query)
        rows = cursor.fetchall()
        return rows

    def insert_into_table(self, table_name: str, columns: tuple, values: tuple):
        """
        Insert values into the table with the given name.

        Args:
            table_name (str): The name of the table to insert into.
            columns (tuple): The columns to insert the values into.
            values (tuple): The values to insert into the table.
        """
        placeholders = ", ".join(["?" for _ in values])
        columns = ", ".join(columns)
        query = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"
        self.logger.info(f"Inserting values into table {table_name}: {values}")
        self.conn.execute(query, values)
        self.conn.commit()

    def update_rows(self, table_name: str, values: dict, condition: str):
        """
        Update rows in the table with the given values and condition.

        Args:
            table_name (str): The name of the table to update.
            values (dict): A dictionary of column-value pairs to update.
            condition (str): The condition to filter the rows to update.
        """
        set_values = ", ".join([f"{key} = ?" for key in values.keys()])
        query = f"UPDATE {table_name} SET {set_values} WHERE {condition}"
        self.logger.info(
            f"Updating table {table_name} with values {values} where {condition}"
        )
        self.conn.execute(query, list(values.values()))
        self.conn.commit()

    def delete_rows(self, table_name: str, condition: str):
        """
        Delete rows from the table with the given condition.

        Args:
            table_name (str): The name of the table to delete from.
            condition (str): The condition to filter the rows to delete.
        """
        query = f"DELETE FROM {table_name} WHERE {condition}"
        self.logger.info(f"Deleting rows from table {table_name} where {condition}")
        self.conn.execute(query)
        self.conn.commit()


class DiscordHelper:
    """
    A helper class for Discord-related operations.

    This class provides various methods to check different conditions related to Discord contexts and users.

    Attributes:
        None

    Methods:
        is_dm(ctx): Checks if the given context is a direct message (DM).
        is_bot_owner(ctx): Checks if the author of the given context is the owner of the bot.
        is_guild_owner(ctx): Checks if the author of the given context is the owner of the server.
        is_admin(ctx): Checks if the author of the given context has administrator permissions in the guild.
        is_mod(ctx): Checks if the author of the command has moderator permissions.
        is_privileged_user(ctx): Checks if the user is a privileged user.
        first_load_cogs(bot, cog_dir): Loads initial extensions (cogs) for the bot.
        user_in_guild(user, guild): Checks if a user is a member of a guild.
    """

    def is_dm(self, ctx: commands.Context) -> bool:
        """
        Checks if the given context is a direct message (DM).

        Args:
            ctx (discord.ext.commands.Context): The context object representing the command invocation.

        Returns:
            bool: True if the context is a DM, False otherwise.
        """
        return ctx.guild is None

    def is_bot_owner(self, ctx: commands.Context) -> bool:
        """
        Checks if the author of the given context is the owner of the bot.

        Args:
            ctx (discord.ext.commands.Context): The context object representing the command invocation.

        Returns:
            bool: True if the author is the owner of the bot, False otherwise.
        """
        return ctx.author.id in ctx.bot.owner_ids

    def is_guild_owner(self, ctx: commands.Context) -> bool:
        """
        Checks if the author of the given context is the owner of the server.

        Args:
            ctx (discord.ext.commands.Context): The context object representing the command invocation.

        Returns:
            bool: True if the author is the owner of the server, False otherwise.
        """
        return ctx.author.id == ctx.guild.owner_id

    def is_admin(self, ctx: commands.Context) -> bool:
        """
        Checks if the author of the given context has administrator permissions in the guild.

        Args:
            ctx (discord.ext.commands.Context): The context object representing the command invocation.

        Returns:
            bool: True if the author has administrator permissions, False otherwise.
        """
        return ctx.author.guild_permissions.administrator

    def is_mod(self, ctx: commands.Context) -> bool:
        """
        Checks if the author of the command has moderator permissions.

        Args:
            ctx (discord.ext.commands.Context): The context object representing the command invocation.

        Returns:
            bool: True if the author has moderator permissions, False otherwise.
        """
        # Since there is no official "moderator" role, we can instead check for some common moderator-only permissions.
        mod_perms = [
            "kick_members",
            "ban_members",
            "manage_messages",
            "manage_channels",
        ]
        return any([getattr(ctx.author.guild_permissions, perm) for perm in mod_perms])

    def is_privileged_user(self, ctx: commands.Context) -> bool:
        """
        Checks if the user is a privileged user.

        A privileged user is defined as a bot owner, guild owner, administrator, or moderator.

        Args:
            ctx: The context object representing the current command invocation.

        Returns:
            True if the user is a privileged user, False otherwise.
        """
        return (
            self.is_bot_owner(ctx)
            or self.is_guild_owner(ctx)
            or self.is_admin(ctx)
            or self.is_mod(ctx)
        )

    async def first_load_cogs(
        self, bot: commands.Bot, cog_dir: str, logger: logging.Logger
    ):
        """
        Loads initial extensions (cogs) for the bot.

        This method iterates over the files in the specified `cog_dir` directory and loads the valid Python files
        as extensions for the bot.

        Args:
            bot: The bot instance.
            cog_dir (str): The directory path where the cogs are located.

        Returns:
            None
        """
        initial_extensions = []
        for cog in os.listdir(cog_dir):
            if cog.endswith(".py"):
                logger.info(f"Loading cog: {cog}")
                initial_extensions.append(f"cogs.{os.path.splitext(cog)[0]}")

        for extension in initial_extensions:
            await bot.load_extension(extension)

    def user_in_guild(self, user: discord.User, guild: discord.Guild) -> bool:
        """
        Checks if a user is a member of a guild.

        Args:
            user (discord.User): The user object to check.
            guild (discord.Guild): The guild object to check.

        Returns:
            bool: True if the user is a member of the guild, False otherwise.
        """
        return guild.get_member(user.id) is not None


class MiscHelper:
    """
    A helper class that provides miscellaneous utility functions.

    attributes:
        None

    methods:
        is_installed(executable): Checks if the specified executable is installed on the system.
        remaining_time(seconds): Converts the given number of seconds into a formatted string representing the remaining time.
    """

    def is_installed(self, executable: str) -> bool:
        """
        Checks if the specified executable is installed on the system.

        Args:
            executable (str): The name of the executable to check.

        Returns:
            bool: True if the executable is installed, False otherwise.
        """
        return shutil.which(executable) is not None

    def remaining_time(self, seconds: int) -> str:
        """
        Converts the given number of seconds into a formatted string representing the remaining time.

        Args:
            seconds (int): The number of seconds.

        Returns:
            str: A formatted string representing the remaining time in the format "MM:SS".
        """
        minutes, seconds = divmod(seconds, 60)
        return f"{int(minutes):02d}:{int(seconds):02d}"
