from asyncio import create_subprocess_shell, create_subprocess_exec, subprocess
from json import loads
from os import execl, listdir, remove, rename, stat, path
from random import choice, randint
from string import ascii_letters, digits
from sys import argv, executable
from asyncio import sleep as asyncsleep
from shlex import quote
from re import compile
from pathlib import Path
from requests import get
from inspect import Parameter
import shutil
from datetime import datetime

from alembic import command
from alembic.script import ScriptDirectory
from alembic.config import Config
from alembic.util.exc import CommandError
from sqlalchemy.exc import OperationalError

import mimetypes
import magic
import discord
import ast
import astunparse
from discord.ext import commands
from num2words import num2words
from psutil import cpu_percent, disk_usage, virtual_memory

from sql.database import AsyncSessionLocal
from sql import crud, schemas

from QuantumKat import log_helper, misc_helper


class Entanglements(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

        self.logger = log_helper.create_logger(
            log_helper.TimedRotatingFileAndStreamHandler(
                logger_name="Entanglements",
                log_file="logs/entanglements/Entanglements.log",
            )
        )

        self.alembic_cfg = Config("./alembic.ini")

    initial_extensions = []
    for cog in listdir("./cogs"):
        if cog.endswith(".py"):
            initial_extensions.append(f"{cog[:-3]}")

    aaaa_dir = "/var/www/aaaa/"
    aaaa_domain = "https://aaaa.lobadk.com/"
    possum_dir = "/var/www/possum/"
    possum_domain = "https://possum.lobadk.com/"

    characters = f"{ascii_letters}{digits}"

    def database_backup(self):
        date = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        backup_file = f"backup_{date}.db"
        if not Path("backups").exists():
            Path("backups").mkdir()
        files = [file for file in listdir("backups") if path.isfile(f"backups/{file}")]
        if len(files) > 5:
            # Remove the oldest backup
            oldest_backup = Path(
                min(Path("backups").glob("*.db"), key=lambda x: x.stat().st_birthtime)
            )
            oldest_backup.unlink()
        shutil.copy("quantumkat.db", f"backups/{backup_file}")

    def get_file_by_partial_name(self, directory: str, partial_name: str) -> str:
        """
        Returns the full file name from the given partial name.

        Parameters:
        - partial_name (str): The partial name of the file.

        Returns:
        - str: The full file name.
        """
        for file in listdir(directory):
            if partial_name in file:
                return file

    def extract_function_code(self, filename, function_name):
        with open(filename, "r") as source:
            tree = ast.parse(source.read())

        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name == function_name:
                return astunparse.unparse(node.body)

    async def get_mime_type(self, mime_type: str) -> str:
        """
        Returns the file extension corresponding to the given MIME type.

        Parameters:
        - mime_type (str): The MIME type for which to determine the file extension.

        Returns:
        - str: The file extension corresponding to the given MIME type.
        """
        return mimetypes.guess_extension(mime_type)

    async def get_file_type(self, ctx: commands.Context, filename: str) -> str:
        """
        Retrieves the file type of a given filename.

        Parameters:
        - ctx (commands.Context): The context of the command.
        - filename (str): The name of the file.

        Returns:
        - str: The file extension of the given file.
        """
        mime = magic.Magic(mime=True)
        try:
            mime_type = mime.from_file(filename)
        except OSError as e:
            await ctx.reply(f"Error getting file type: {e}", silent=True)
            self.logger.error("Error getting file type", exc_info=True)
            return None
        file_extension = await self.get_mime_type(mime_type)
        return file_extension

    async def parameter_kind_to_string(self, parameter: Parameter) -> str:
        """
        Converts the parameter kind to a string representation.

        Args:
            parameter (Parameter): The parameter to convert.

        Returns:
            str: The string representation of the parameter kind.
        """
        parameter_kind = parameter.kind.name
        parameter_kind_string = parameter_kind.replace("_", " ").capitalize()
        return parameter_kind_string

    async def getvideometadata(self, data_dir: str, filename: str) -> dict:
        arg2 = (
            "ffprobe -v quiet -show_streams -select_streams v:0 -of json "
            f'{quote(f"{data_dir}{filename}.mp4")}'
        )

        #  Attempt to run command with above args
        stream = await create_subprocess_shell(
            arg2, stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
        stdout, _ = await stream.communicate()
        await stream.wait()

        # Load the "streams" key, which holds all the metadata information
        return loads(stdout)["streams"][0]

    async def decreaseesolution(self, video_metadata: dict) -> tuple[int, int]:
        # Attempt to parse, divide, and save the video's width
        # and height in int, to remove any decimal points
        frame_width = int(video_metadata["coded_width"] / 1.5)
        frame_height = int(video_metadata["coded_height"] / 1.5)

        return frame_width, frame_height

    async def decreasebitrate(
        self,
        ctx: commands.Context,
        video_duration: int,
        bitrate_decrease: int,
        attempts: int,
        data_dir: str,
        filename: str,
        frame_width: int,
        frame_height: int,
    ) -> tuple[int, int]:
        # calculate the average bitrate required to reach around 50MB's
        # by multiplying 50 by 8192 (convert megabits to kilobits)
        # dividing that by the video length, and subtracting the audio bitrate
        # Audio bitrate is hardcoded for now.
        bitrate = (50 * 8192) / video_duration - 192 - bitrate_decrease

        # Transcode original video into an h264 stream, with an average
        # bitrate calculated from the above code, and scale the video to
        # the new resolution.
        # In the future, a check should be made whether the video has audio
        # or not, either by checking if there's an audio stream
        # or the audio stream's bitrate
        # (I don't know how Youtube handles muted videos)
        arg4 = (
            f"ffmpeg -y -i {data_dir}{filename}.mp4 -c:v libx264 -c:a aac "
            f"-b:v {str(int(bitrate))}k -b:a 192k -movflags +faststart "
            f"-vf scale={frame_width}:{frame_height} "
            f'-f mp4 {quote(f"{data_dir}{filename}.tmp")}'
        )

        try:
            process3 = await create_subprocess_shell(arg4)
            await process3.wait()
        except Exception as e:
            self.logger.error(f"{type(e).__name__}: {e}")
            await ctx.reply(
                ("Error transcoding resized with " "average bitrate video!"),
                silent=True,
            )
            return

        # Increase attempts by 1
        attempts += 1
        # Increase by 100 kilobits
        # to decrease the average bitrate by 100 kilobits
        bitrate_decrease += 100

        return attempts, bitrate

    async def generatefilename(self) -> str:
        return "".join(choice(self.characters) for _ in range(8))

    # command splitter for easier reading and navigating

    @commands.command(
        brief="(Bot owner only) Stops the bot.",
        description=("Stops and disconnects the bot. " "Supports no arguments."),
    )
    @commands.is_owner()
    async def observe(self, ctx: commands.Context):
        await ctx.reply("QuantumKat's superposition has collapsed!", silent=True)
        await self.bot.close()

    # command splitter for easier reading and navigating

    @commands.command(
        aliases=["stabilize", "restart", "reload"],
        brief="(Bot owner only) Reloads cogs/extensions.",
        description="Reloads the specified cogs/extensions. "
        "Requires at least one argument, and "
        "supports an arbitrary amount of arguments. "
        "Special character '*' can be used "
        "to reload all.",
    )
    @commands.is_owner()
    async def stabilise(self, ctx: commands.Context, *, module: str = ""):
        if module:
            location = choice(["reality", "universe", "dimension", "timeline"])
            if module == "*":
                msg = await ctx.reply(
                    ("Quantum instability detected across..." " <error>. Purrging!"),
                    silent=True,
                )
                for extension in self.initial_extensions:
                    try:
                        await self.bot.reload_extension(f"cogs.{extension}")
                        msg = await msg.edit(
                            content=f"{msg.content}\nPurging {extension}!"
                        )
                    except commands.ExtensionNotLoaded as e:
                        self.logger.error(f"{type(e).__name__}: {e}")
                        await ctx.send(
                            (f"{extension} is not running, " "or could not be found")
                        )
                    except commands.ExtensionNotFound as e:
                        self.logger.error(f"{type(e).__name__}: {e}")
                        await ctx.send(f"{extension} could not be found!")
                    except commands.NoEntryPointError as e:
                        self.logger.error(f"{type(e).__name__}: {e}")
                        await ctx.send(
                            (
                                f"successfully loaded {extension}, "
                                "but no setup was found!"
                            )
                        )
            else:
                cogs = module.split()
                for cog in cogs:
                    if cog[0].islower():
                        cog = cog.replace(cog[0], cog[0].upper(), 1)
                    try:
                        await self.bot.reload_extension(f"cogs.{cog}")
                        if len(cogs) == 1:
                            await ctx.reply(
                                (
                                    f"Superposition irregularity "
                                    f"detected in Quantum {cog}! "
                                    f"Successfully entangled to the "
                                    f'{(num2words(randint(1, 1000), to="ordinal_num"))} {location}!'
                                ),
                                silent=True,
                            )
                        else:
                            await ctx.reply(f"Purrging {cog}!", silent=True)
                    except commands.ExtensionNotFound as e:
                        self.logger.error(f"{type(e).__name__}: {e}")
                        await ctx.reply(f"{cog} could not be found!", silent=True)
                    except commands.ExtensionNotLoaded as e:
                        self.logger.error(f"{type(e).__name__}: {e}")
                        await ctx.reply(
                            (f"{cog} is not running, " "or could not be found!"),
                            silent=True,
                        )
                    except commands.NoEntryPointError as e:
                        self.logger.error(f"{type(e).__name__}: {e}")
                        await ctx.reply(
                            (f"successfully loaded {cog}, " "but no setup was found!"),
                            silent=True,
                        )

    # command splitter for easier reading and navigating

    @commands.command(
        aliases=["load", "start"],
        brief="(Bot owner only) Starts/Loads a cog/extension.",
        description=(
            "Starts/Loads the specified cogs/extensions"
            ".Requires at least one argument, and "
            "supports an arbitrary amount of "
            "arguments."
        ),
    )
    @commands.is_owner()
    async def entangle(self, ctx: commands.Context, *, module: str = ""):
        if module:
            cogs = module.split()
            for cog in cogs:
                if cog[0].islower():
                    cog = cog.replace(cog[0], cog[0].upper(), 1)
                try:
                    await self.bot.load_extension(f"cogs.{cog}")
                    await ctx.reply(f"Successfully entangled to {cog}", silent=True)
                except commands.ExtensionNotFound as e:
                    self.logger.error(f"{type(e).__name__}: {e}")
                    await ctx.reply(f"{cog} could not be found!", silent=True)
                except commands.ExtensionAlreadyLoaded as e:
                    self.logger.error(f"{type(e).__name__}: {e}")
                    await ctx.reply(f"{cog} is already loaded!", silent=True)
                except commands.NoEntryPointError as e:
                    self.logger.error(f"{type(e).__name__}: {e}")
                    await ctx.reply(
                        (f"successfully loaded {cog}, " "but no setup was found!"),
                        silent=True,
                    )
                except commands.ExtensionFailed as e:
                    self.logger.error(f"{type(e).__name__}: {e}")
                    await ctx.reply(
                        f"Loading {cog} failed due to an unknown error!", silent=True
                    )

    # command splitter for easier reading and navigating

    @commands.command(
        aliases=["unload", "stop"],
        brief="(Bot owner only) Stops/Unloads a cog/extension.",
        description=(
            "Stops/Unloads the specified cogs/"
            "extensions. Requires at least one "
            "argument, and supports an arbitrary "
            "amount of arguments."
        ),
    )
    @commands.is_owner()
    async def unentangle(self, ctx: commands.Context, *, module: str = ""):
        if module:
            cogs = module.split()
            for cog in cogs:
                if cog[0].islower():
                    cog = cog.replace(cog[0], cog[0].upper(), 1)
                try:
                    await self.bot.unload_extension(f"cogs.{cog}")
                    await ctx.reply(f"Successfully unentangled from {cog}", silent=True)
                except commands.ExtensionNotFound as e:
                    self.logger.error(f"{type(e).__name__}: {e}")
                    await ctx.reply(f"{cog} could not be found!", silent=True)
                except commands.ExtensionNotLoaded as e:
                    self.logger.error(f"{type(e).__name__}: {e}")
                    await ctx.reply(
                        (f"{cog} not running, or could not be " "found!"), silent=True
                    )

    # command splitter for easier reading and navigating

    @commands.command(
        aliases=["quantise"],
        brief=("(Bot owner only) Downloads a file to aaaa/" "possum.lobadk.com."),
        description=(
            "Downloads the specified file to the root "
            "directory of aaaa.lobadk.com or possum."
            "lobadk.com, for easier file adding. "
            "Requires at least 3 arguments, and "
            "supports 4 arguments. The first argument "
            "is the file URL, the second is the "
            "filename to be used, with a special 'rand'"
            " parameter that produces a random 8 "
            "character long base62 filename, the third "
            "is the location, specified with 'aaaa' or "
            "'possum', the fourth (optional) is 'YT' to"
            " indicate yt-lp should be used to download"
            " the file (YouTub or Twitter for example)."
            " If a file extension is detected, it will "
            "automatically be used, otherwise it needs "
            "to be specified in the filename. Supports "
            "links that have had their embeds disabled with '<>'."
        ),
    )
    @commands.is_owner()
    async def quantize(
        self,
        ctx: commands.Context,
        URL: str = "",
        filename: str = "",
        location: str = "",
        mode: str = "",
    ):
        oldfilename = filename

        # Check if user has given all required inputs
        if URL and filename and location and mode:

            # Check and set the correct download location
            if location.casefold() == "aaaa":
                data_dir = self.aaaa_dir
                data_domain = self.aaaa_domain

            elif location.casefold() == ("possum" or "opossum"):
                data_dir = self.possum_dir
                data_domain = self.possum_domain

            # If an incorrect location is given
            else:
                await ctx.reply(
                    ("Only `aaaa` and `possum` are valid " "parameters!"), silent=True
                )
                return

        # If a required input is missing
        else:
            await ctx.reply(
                "Command requires 4 arguments:\n```?quantize "
                "<URL> <filename|rand> <aaaa|possum> <mode>```",
                silent=True,
            )
            return

        msg = await ctx.reply("Creating quantum tunnel... ", silent=True)

        # If filename is 'rand' generate a random 8-character base62 filename
        if oldfilename.casefold() == "rand":
            filename = await self.generatefilename()

        # Strip greater-than and less-than symbols
        # if they've been used to disable embeds
        if URL.startswith("<") or URL.endswith(">"):
            URL = URL.replace("<", "")
            URL = URL.replace(">", "")

        msg = await msg.edit(content=f"{msg.content} Tunnel created!")

        # If mode is 'normal' i.e. normal downloads
        if mode.casefold() == "normal":

            while True:

                # If the filename already exists
                if Path(data_dir, filename).exists():

                    # If the old filename is not 'rand' and thus not supposed to be randomly generated
                    if not oldfilename.casefold() == "rand":
                        await ctx.reply(
                            "Filename already exists, consider using a different name",
                            silent=True,
                        )
                        return

                    # Regenerate random filename
                    else:
                        filename = await self.generatefilename()
                        continue

                # Request and write file data
                with open(f"{Path(data_dir, filename)}", "wb") as quantizer:
                    msg = await msg.edit(content=f"{msg.content} Retrieving {filename}")

                    response = get(URL, stream=True)

                    if not response.ok:
                        self.logger.error(
                            f"Error connecting to server! {response.status_code}"
                        )
                        await ctx.reply(
                            f"Error connecting to server! {response.status_code}"
                        )
                        return

                    for block in response.iter_content(1024):
                        if not block:
                            break

                        quantizer.write(block)

                if not Path(filename).suffix:
                    file_extension = await self.get_file_type(
                        ctx, str(Path(data_dir, filename))
                    )
                    if not file_extension:
                        return
                    msg = await msg.edit(
                        content=f"{msg.content} \nFile extension detected: {file_extension}"
                    )
                    rename(
                        f"{Path(data_dir, filename)}",
                        f"{Path(data_dir, filename)}{file_extension}",
                    )
                    filename = f"{filename}{file_extension}"
                await msg.edit(
                    content=f"{msg.content} \nSuccess! Data quantized to {data_domain}{filename}",
                    suppress=True,
                )
                return

        # If mode is 'yt' i.e. requires yt-dlp
        elif mode.casefold() == "yt":

            # If the URL is a link to a YouTube playlist and not a video.
            # Since links to videos IN playlists contain '&list=' instead
            # we can still allow those by using the --no-playlist flag in yt-dlp
            if "playlist?list" in URL:
                await ctx.reply("Playlists are not supported", silent=True)
                return

            # Downloads the best (up to 720p) MP4 video and m4a audio, and then combines them
            # Or a single video with audio included (up to 720p), if that's the best option
            arg = f'yt-dlp -f "bv[ext=mp4][height<=720]+ba[ext=m4a]/b[ext=mp4][height<=720]" {quote(URL)} --no-playlist -o {quote(f"{data_dir}{filename}.%(ext)s")}'

            msg = await msg.edit(content=f"{msg.content} Retrieving {filename}")

            # Make the bot show as 'typing' in the channel while it is downloading the video
            async with ctx.typing():
                # Attempt to run command with above args
                try:
                    process = await create_subprocess_shell(
                        arg, stdout=subprocess.PIPE, stderr=subprocess.PIPE
                    )
                    await process.wait()
                    stdout, stderr = await process.communicate()

                except Exception as e:
                    self.logger.error(f"{type(e).__name__}: {e}")
                    await ctx.reply(
                        "Error, quantization tunnel collapsed unexpectedly!",
                        silent=False,
                    )
                    return

                # yt-dlp sometimes outputs non-fatal errors or warnings
                # making it unreliable for canceling the process.
                # Instead we're supplying the error for verbosity.
                # TODO: Test and figure out the warning and error messages
                # it can return, for better process handling
                if stderr:
                    await ctx.reply(stderr.decode(), silent=True)

                # If a file with the same name already exists
                # yt-dlp returns this string in it's output
                # which we can use to handle duplicates
                if "has already been downloaded" in stdout.decode():
                    await msg.reply(
                        "Filename already exists, consider using a different name",
                        silent=True,
                    )
                    return

                # Reaching this part assumes that everything went well.
                # Improvements and research could be made
                # But I am too lazy, tired and stressed
                elif stdout:

                    # Check if the downloaded file is above 50MB's
                    if (
                        int(
                            stat(quote(f"{data_dir}{filename}.mp4")).st_size
                            / (1024 * 1024)
                        )
                        > 50
                    ):
                        msg = await msg.edit(
                            content=f"{msg.content} \nDataset exceeded recommended limit! Crunching some bits... this might take a ***bit***"
                        )

                        # We wanna try and lower the resolution first by 1.5
                        # as that should hurt quality and viewability in
                        # Discord embeds the least

                        # Gets the video metadata from custom function
                        try:
                            video_metadata = await self.getvideometadata(
                                data_dir, filename
                            )
                        except Exception as e:
                            self.logger.error(f"{type(e).__name__}: {e}")
                            await ctx.reply(
                                "Error getting video metadata!", silent=True
                            )
                            return

                        # Get new frame sizes from custom function
                        try:
                            frame_width, frame_height = await self.decreaseesolution(
                                video_metadata
                            )
                        except Exception as e:
                            self.logger.error(f"{type(e).__name__}: {e}")
                            await ctx.reply(
                                "Error parsing video resolution, manual conversion required!",
                                silent=True,
                            )
                            return

                        # Transcode the video into an h264 stream with a CRF of 30
                        # and downscale the video to the new resolution.
                        # Currently audio is encoded regardless if it's there or not
                        # so in the future we should check if audio is actually present.
                        arg3 = f'ffmpeg -y -i {quote(f"{data_dir}{filename}.mp4")} -c:v libx264 -c:a aac -crf 30 -b:v 0 -b:a 192k -movflags +faststart -vf scale={frame_width}:{frame_height} -f mp4 {quote(f"{data_dir}{filename}.tmp")}'

                        # Attempt to run command with above args
                        try:
                            process2 = await create_subprocess_shell(arg3)
                            await process2.wait()
                        except Exception as e:
                            self.logger.error(f"{type(e).__name__}: {e}")
                            await ctx.reply(
                                "Error transcoding resized video!", silent=True
                            )
                            return

                        # If the returncode is 0, i.e. no errors happened
                        if process2.returncode == 0:
                            # Check if the new lower-resolution version is under 50MB's.
                            # As a last resort, if the file is still above 50MB's
                            # it will enter a loop where it attempts x amount of times
                            # and decreases the bitrate each time until it is under

                            # Attempt to parse, convert from string, to float, to int, and save the video duration
                            # 100% accuracy down to the exact millisecond isn't required, so we just get the whole number instead
                            try:
                                video_duration = int(float(video_metadata["duration"]))
                            except Exception as e:
                                self.logger.error(f"{type(e).__name__}: {e}")
                                await ctx.reply(
                                    "Error parsing video duration, manual conversion required!",
                                    silent=True,
                                )
                                return

                            bitrate_decrease = 0
                            attempts = 0
                            while (
                                int(
                                    stat(f"{data_dir}{filename}.tmp").st_size
                                    / (1024 * 1024)
                                )
                                > 50
                                or attempts >= 15
                            ):
                                attempts, bitrate = await self.decreasebitrate(
                                    ctx,
                                    video_duration,
                                    bitrate_decrease,
                                    attempts,
                                    data_dir,
                                    filename,
                                    frame_width,
                                    frame_height,
                                )

                            # Attempt to delete the original video, and then rename the transcoded .tmp video to .mp4
                            try:
                                remove(f"{data_dir}{filename}.mp4")
                                rename(
                                    f"{data_dir}{filename}.tmp",
                                    f"{data_dir}{filename}.mp4",
                                )
                            except Exception as e:
                                self.logger.error(f"{type(e).__name__}: {e}")
                                await ctx.reply(
                                    "Error moving/removing file!", silent=True
                                )
                                return

                            # If the bitrate option was reached, this would be at least 1
                            # Otherwise if it's 0, it means it never attempted to transcode with a variable bitrate
                            if attempts == 0:
                                message = f"\nSuccess! Data quantized and bit-crunched to {data_domain}{filename}.mp4\nResized to {frame_width}:{frame_height}"
                            else:
                                message = f"\nSuccess! Data quantized and bit-crunched to {data_domain}{filename}.mp4\nUsing {bitrate}k/s and Resized to {frame_width}:{frame_height} with {attempts} attempt(s)"

                            await msg.edit(
                                content=f"{msg.content}{message}", suppress=True
                            )

                        # Else statement for the process returncode, from the initial ffmpeg command
                        else:
                            await ctx.reply(
                                "Non-0 exit status code detected!", silent=True
                            )

                    # If the file is under 50MB's
                    else:
                        await msg.edit(
                            content=f"{msg.content}\nSuccess! Data quantized to {data_domain}{filename}.mp4",
                            suppress=True,
                        )

                else:
                    ctx.reply("No output detected in yt-dlp!", silent=True)
                    return

        # If mode is not 'normal' or 'yt'
        else:
            await ctx.reply("Only 'normal'|'yt' are valid download modes!", silent=True)
            return

    # command splitter for easier reading and navigating

    @commands.command(
        aliases=["requantise"],
        brief="(Bot owner only) Rename a file on aaaa.lobadk.com.",
        description="Renames the specified file. Requires and supports 2 arguments. Only alphanumeric, underscores and a single dot allowed, and at least one character must appear after the dot when choosing a new name.",
    )
    @commands.is_owner()
    async def requantize(
        self, ctx: commands.Context, current_filename: str = "", new_filename: str = ""
    ):
        if current_filename and new_filename:

            data_dir = self.aaaa_dir

            # allow only alphanumeric, underscores, a single dot and at least one alphanumeric after the dot
            allowed = compile(r"^[\w]*(\.){1,}[\w]{1,}$")
            if (
                "/" not in current_filename
                and allowed.match(current_filename)
                and allowed.match(new_filename)
            ):
                msg = await ctx.reply("Attempting to requantize data...", silent=True)

                try:
                    rename(f"{data_dir}{current_filename}", f"{data_dir}{new_filename}")

                except FileNotFoundError:
                    await msg.edit(content=f"{msg.content}\nError! Data does not exist")
                    return

                except FileExistsError:
                    await msg.edit(
                        content=f"{msg.content}\nError! Cannot requantize, data already exists"
                    )
                    return

                except Exception as e:
                    self.logger.error(f"{type(e).__name__}: {e}")
                    await ctx.reply("Critical error! Check logs for info", silent=True)
                    return

                await msg.edit(content=f"{msg.content}\nSuccess!")

            else:
                await ctx.reply(
                    "Only alphanumeric and a dot allowed. Extension required. Syntax is:\n```name.extension```",
                    silent=True,
                )
        else:
            await ctx.reply(
                "Command requires 2 arguments:\n```?requantize <current.name> <new.name>```",
                silent=True,
            )

    # command splitter for easier reading and navigating

    @commands.group(
        brief="(Bot owner only) Git commands.",
        description="Command group for Git commands.",
    )
    @commands.is_owner()
    async def git(self, ctx: commands.Context):
        if ctx.invoked_subcommand is None:
            await ctx.reply("Invalid git command passed...", silent=True)

    @git.command(
        brief="(Bot owner only) Pulls the latest changes from the repository.",
        description="Pulls the latest changes from the repository.",
    )
    async def pull(self, ctx: commands.Context):
        process = await create_subprocess_shell(
            "git pull", stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
        stdout, stderr = await process.communicate()

        if stderr:
            await ctx.reply(stderr.decode(), silent=True)
        else:
            await ctx.reply(stdout.decode(), silent=True)

    @git.command(
        brief="(Bot owner only) Shows the status of the current branch.",
        description="Shows the status of the current branch.",
    )
    async def status(self, ctx: commands.Context):
        process = await create_subprocess_shell(
            "git status", stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
        stdout, stderr = await process.communicate()

        if stderr:
            await ctx.reply(stderr.decode(), silent=True)
        else:
            await ctx.reply(stdout.decode(), silent=True)

    @git.command(
        brief="(Bot owner only) Swaps to a different branch. Requires a branch name.",
        description="Swaps to a different branch. Requires a branch name.",
    )
    async def checkout(self, ctx: commands.Context, branch: str = ""):
        if not branch:
            await ctx.reply("You must specify a branch name!", silent=True)
            return
        process = await create_subprocess_exec(
            "git",
            "checkout",
            branch,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        stdout, stderr = await process.communicate()

        if stderr:
            await ctx.reply(stderr.decode(), silent=True)
        else:
            await ctx.reply(stdout.decode(), silent=True)

    @git.command(
        brief="(Bot owner only) A minimalistic git-branch command. Requires an option.",
        description="A minimalistic git-branch command. Has two options: 'delete' and 'list'. 'delete' requires a branch name.",
    )
    async def branch(self, ctx: commands.Context, option: str = "", branch: str = ""):
        if not option:
            await ctx.reply("You must specify an option!", silent=True)
            return
        if option.casefold() == "delete":
            if not branch:
                await ctx.reply("You must specify a branch name!", silent=True)
                return
            process = await create_subprocess_exec(
                "git",
                "branch",
                "-d",
                branch,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            stdout, stderr = await process.communicate()

            if stderr:
                await ctx.reply(stderr.decode(), silent=True)
            else:
                await ctx.reply(stdout.decode(), silent=True)

        elif option.casefold() == "list":
            process = await create_subprocess_exec(
                "git",
                "branch",
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            stdout, stderr = await process.communicate()

            if stderr:
                await ctx.reply(stderr.decode(), silent=True)
            else:
                await ctx.reply(stdout.decode(), silent=True)

        else:
            await ctx.reply("Invalid option!", silent=True)

    # command splitter for easier reading and navigating

    @commands.command(
        brief="(Bot owner only) Fetches new updates and reloads all changed/updated cogs/extensions.",
        description="Fetches the newest version by running 'git pull' and then reloads the cogs/extensions if successful. If the bot's main script has been updated, it will ask if you want to reboot the bot. If any dependencies have been updated, it will automatically update them.",
    )
    @commands.is_owner()
    async def update(self, ctx: commands.Context):
        # Attempt to get the current commit HASH before updating
        try:
            process1 = await create_subprocess_shell(
                "git rev-parse --short HEAD",
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
        except Exception as e:
            self.logger.error(f"{type(e).__name__}: {e}")
            await ctx.reply("Error getting current Git information", silent=True)
            return

        stderr1, stdout1 = await process1.communicate()

        current_version = stderr1.decode().replace("\n", "")

        process2 = await create_subprocess_shell(
            "git pull", stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )

        # DO NOT CHANGE ORDER
        # Git's output seems to be reversed, and most information gets piped to STDERR instead for some reason
        # STDOUT may also sometimes contain either the data, or some other random data, or part of the whole output, from STDERR
        # "Already up to date" is piped to STDOUT, but output from file changes when doing "git pull" for example
        # Are outputted to STDERR instead, hence why it is also reversed here
        stderr2, stdout2 = await process2.communicate()

        # For some reason after decoding Git's output stream, "b'" and "\\n'" shows up everywhere in the output
        # This removes any of them, cleaning up the output
        stdout2 = stdout2.decode()
        stdout2 = stdout2.replace("b'", "")
        stdout2 = stdout2.replace("\\n'", "")
        stdout2 = stdout2.replace("\n'", "")
        stderr2 = stderr2.decode()
        stderr2 = stderr2.replace("b'", "")
        stderr2 = stderr2.replace("\\n'", "")
        stderr2 = stderr2.replace("\n'", "")

        # For some reason Git on Windows returns the string without hyphens, while Linux returns it with hyphens
        if "Already up to date" in stderr2 or "Already up-to-date" in stderr2:
            await ctx.reply(stderr2, silent=True)

        elif stderr2:

            # Send the output of Git, which displays which files has been updated, and how much
            # Then sleep 2 seconds to allow the text to be sent, and read
            msg = await ctx.reply(stderr2, silent=True)
            await asyncsleep(2)

            # Attempt to get a list of files that changed between the pre-update version, using the previously required HASH, and now
            try:
                process3 = await create_subprocess_shell(
                    f"git diff --name-only {current_version} HEAD",
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                )
            except Exception as e:
                self.logger.error(f"{type(e).__name__}: {e}")
                await msg.edit(
                    content=f"{msg.content}\nError running file-change check. Manual reloading required"
                )
                return

            # Save the output (filenames) in stderr3
            stderr3, stdout3 = await process3.communicate()

            #  Decode and remove "b'" characters
            output = stderr3.decode().replace("b'", "")

            reboot = False

            if "requirements.txt" in output:
                msg = await msg.edit(
                    content=f"{msg.content}\nPossible dependency changes detected. Updating from requirements.txt..."
                )
                try:
                    proc = await create_subprocess_shell(
                        "pip install -r requirements.txt",
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                    )
                    await proc.wait()
                    msg = await msg.edit(content=f"{msg.content} Done!")
                    reboot = True
                except Exception as e:
                    self.logger.error(f"{type(e).__name__}: {e}")
                    msg = await msg.edit(
                        content=f"{msg.content} Error updating from requirements.txt."
                    )

            if "sql/models.py" in output:
                msg = await msg.edit(
                    content=f"{msg.content}\nDatabase schema changes detected. Updating..."
                )

                try:
                    await ctx.invoke(
                        self.bot.get_command("db revision"), "Automatic update"
                    )
                    await ctx.invoke(self.bot.get_command("db upgrade"), "head")
                except Exception:
                    self.logger.error(
                        "Database schema update/migration failed", exc_info=True
                    )
                    msg = await msg.edit(
                        content=f"{msg.content} Error updating database schema."
                    )
                else:
                    msg = await msg.edit(
                        content=f"{msg.content} Database schema updated!"
                    )
                    reboot = True

            if "QuantumKat.py" in output and not reboot:
                msg = await msg.edit(
                    content=f"{msg.content}\nMain script updated, reboot?"
                )

                def check(m: discord.Message):
                    return (
                        m.author.id == ctx.author.id
                        and m.channel.id == ctx.channel.id
                        and m.content.casefold() == "yes"
                    )

                try:
                    await self.bot.wait_for("message", check=check, timeout=10)
                except TimeoutError:
                    msg = await msg.edit(content=f"{msg.content}\nNot rebooting...")
                else:
                    reboot = True

            if reboot:
                await ctx.invoke(self.bot.get_command("reboot"))

            extensions = []
            for cog in listdir("./cogs"):
                if cog.endswith(".py"):
                    extensions.append(f"cogs.{cog[:-3]}")

            for extension in extensions:
                if extension[5:] in output:
                    try:
                        await self.bot.reload_extension(extension)
                        msg = await msg.edit(
                            content=f"{msg.content}\nPurging updated {extension[5:]}!"
                        )

                    except commands.ExtensionNotLoaded as e:
                        self.logger.error(f"{type(e).__name__}: {e}")
                        msg = await msg.edit(
                            content=f"{msg.content}\n{extension[5:]} is not running, or could not be found"
                        )

                    except commands.ExtensionNotFound as e:
                        self.logger.error(f"{type(e).__name__}: {e}")
                        msg = await msg.edit(
                            content=f"{msg.content}\n{extension[5:]} could not be found!"
                        )

                    except commands.NoEntryPointError as e:
                        self.logger.error(f"{type(e).__name__}: {e}")
                        msg = await msg.edit(
                            content=f"{msg.content}\nsuccessfully loaded {extension[5:]}, but no setup was found!"
                        )

        elif stdout2:
            await ctx.reply(stdout2, silent=True)

    # command splitter for easier reading and navigating

    @commands.command(
        aliases=["dequantize"],
        brief="(Bot owner only) Delete the specified file.",
        description="Attempts to delete the specified file. Supports and requires 2 arguments, being the filename, and location (aaaa|possum).",
    )
    @commands.is_owner()
    async def dequantise(
        self, ctx: commands.Context, filename: str = "", location: str = ""
    ):
        if filename and location:

            data_dir = ""

            if location.casefold() == "aaaa":
                data_dir = self.aaaa_dir

            elif location.casefold() == "possum":
                data_dir = self.possum_dir

            else:
                await ctx.reply(
                    "Only `aaaa` and `possum` are valid parameters!", silent=True
                )
                return

            # allow only alphanumeric, underscores, a single dot and at least one alphanumeric after the dot
            allowed = compile(r"^[\w]*(\.){1,}[\w]{1,}$")
            if allowed.match(filename):

                try:
                    remove(f"{data_dir}{filename}")

                except FileNotFoundError:
                    await ctx.reply(
                        "Dataset not found. Did you spell it correctly?", silent=True
                    )
                    return

                except Exception as e:
                    self.logger.error(f"{type(e).__name__}: {e}")
                    await ctx.reply("Error dequantising dataset!", silent=True)
                    return

                await ctx.reply(
                    f"Successfully dequantised and purged {filename}!", silent=True
                )

            else:
                await ctx.reply(
                    "Only alphanumeric and a dot allowed. Extension required. Syntax is:\n```?dequantise name.extension aaaa|possum```",
                    silent=True,
                )

        else:
            await ctx.reply(
                "Filename and location required!\n`?dequantise|dequantize <filename> aaaa|possum`",
                silent=True,
            )

    # command splitter for easier reading and navigating

    @commands.command(
        brief="(Bot owner only) Displays some basic system usage information."
    )
    @commands.is_owner()
    async def serverstatus(self, ctx: commands.Context):
        await ctx.reply(
            f"""
Current CPU Usage: {cpu_percent(1)}%
RAM: {int(virtual_memory().used / 1024 / 1024)}MB / {int(virtual_memory().total / 1024 / 1024)}MB | {virtual_memory().percent}%
Primary disk: {int(disk_usage('/').used / 1024 / 1024 / 1000)}GB / {int(disk_usage('/').total / 1024 / 1024 / 1000)}GB | {disk_usage('/').percent}%
""",
            silent=True,
        )

    # command splitter for easier reading and navigating

    @commands.command(
        brief="(Bot owner only) Restarts the main script and all extensions.",
        description="Restarts the main script and all extensions. Useful for when the main script has been updated.",
    )
    @commands.is_owner()
    async def reboot(self, ctx: commands.Context):
        self.bot.reboot_scheduled = True
        msg = await ctx.send("Shutting down extensions and rebooting...")
        await asyncsleep(10)
        await crud.set_reboot(
            AsyncSessionLocal,
            schemas.Bot.SetReboot(
                is_reboot_scheduled=True,
                reboot_time=datetime.now(),
                message_location=(
                    msg.id,
                    msg.channel.id,
                    msg.guild.id if msg.guild else 0,
                ),
            ),
        )
        for cog in listdir("./cogs"):
            if cog.endswith(".py"):
                try:
                    await self.bot.unload_extension(f"cogs.{cog[:-3]}")
                except commands.ExtensionNotLoaded:
                    continue

        # Note: This doesn't really work on Windows.
        execl(executable, executable, *argv)

    # command splitter for easier reading and navigating

    @commands.command()
    async def version(self, ctx: commands.Context):
        version = misc_helper.get_git_commit_count()
        # Turn the version number into a dot-separated string to make it look a little fancier.
        version = ".".join(str(version))
        await ctx.reply(f"Current version: {version}", silent=True)

    @commands.is_owner()
    @commands.group()
    async def db(self, ctx: commands.Context):
        """
        Command group used for database management.
        """
        if ctx.invoked_subcommand is None:
            await ctx.send_help(ctx.command)

    @db.command()
    async def revision(self, ctx: commands.Context, message: str):
        """
        Create a database revision using Alembic.

        Args:
            message (str): The message for the revision.
        """
        try:
            command.revision(self.alembic_cfg, message, autogenerate=True)
        except CommandError as e:
            self.logger.error("Database revision failed", exc_info=True)
            await ctx.reply(f"Database revision failed: {e}", silent=True)
        except Exception:
            self.logger.error("Database revision failed", exc_info=True)
            await ctx.reply("Database revision failed!", silent=True)
        else:
            await ctx.reply("Revision created!", silent=True)

    @db.command(aliases=["update"])
    async def upgrade(self, ctx: commands.Context, revision: str = "+1"):
        """
        Upgrades the database using Alembic.

        Parameters:
        - revision (str): The revision to upgrade to. Defaults to "+1" which upgrades to the next revision.
        """
        self.database_backup()
        try:
            command.upgrade(self.alembic_cfg, revision)
        except CommandError as e:
            self.logger.error("Database upgrade failed", exc_info=True)
            await ctx.reply(f"Database upgrade failed: {e}", silent=True)
        except Exception:
            self.logger.error("Database upgrade failed", exc_info=True)
            await ctx.reply("Database upgrade failed!", silent=True)
        else:
            await ctx.reply("Database upgraded!", silent=True)

    @db.command(aliases=["revert"])
    async def downgrade(self, ctx: commands.Context, revision: str = "-1"):
        """
        Downgrades the database using Alembic.

        Parameters:
        - revision (str): The revision to downgrade to. Defaults to "-1" which represents the previous revision.
        """
        self.database_backup()
        try:
            command.downgrade(self.alembic_cfg, revision)
        except CommandError as e:
            self.logger.error("Database downgrade failed", exc_info=True)
            await ctx.reply(f"Database downgrade failed: {e}", silent=True)
        except Exception:
            self.logger.error("Database downgrade failed", exc_info=True)
            await ctx.reply("Database downgrade failed!", silent=True)
        else:
            await ctx.reply("Database downgraded!", silent=True)

    @db.command()
    async def history(self, ctx: commands.Context):
        """
        Retrieves the migration history and displays it in the channel.
        """
        try:
            current_revision = await crud.get_current_revision(AsyncSessionLocal)
        except OperationalError as e:
            self.logger.error("Failed to get current revision", exc_info=True)
            await ctx.reply(f"Failed to get current revision: {e}", silent=True)
            return
        try:
            script_dir = ScriptDirectory.from_config(self.alembic_cfg)
            revisions = script_dir.walk_revisions()
            history = []
            for revision in revisions:
                history.append(
                    f"{revision.revision} {revision.doc or 'No message'} {'<- Current' if revision.revision == current_revision else ''}".strip()
                )
            await ctx.reply("\n".join(history), silent=True)
        except Exception:
            self.logger.error("Failed to get migration history", exc_info=True)
            await ctx.reply("Failed to get migration history", silent=True)

    @db.command()
    async def migrate(self, ctx: commands.Context, message: str):
        """
        Runs both the revision and upgrade commands in one go.

        Parameters:
        - message (str): The message to be passed to the migration command.
        """
        await ctx.invoke(self.bot.get_command("db revision"), message)
        await ctx.invoke(self.bot.get_command("db upgrade"), "head")

    @db.command(aliases=["inspect"])
    async def inspect_revision(self, ctx: commands.Context, revision_id: str):
        """
        Inspects a specific revision in the database.

        Parameters:
        - revision_id (str): The revision to inspect.
        """
        directory = "./alembic/versions"
        filename = self.get_file_by_partial_name(directory, revision_id)
        filename = Path(directory, filename)
        upgrade_code = self.extract_function_code(filename, "upgrade")
        downgrade_code = self.extract_function_code(filename, "downgrade")
        try:
            script_dir = ScriptDirectory.from_config(self.alembic_cfg)
            revision = script_dir.get_revision(revision_id)
            await ctx.reply(
                f"Revision: {revision.revision}\nMessage: {revision.doc or 'No message'}\nUpgrade:\n```{upgrade_code}```\nDowngrade:\n```{downgrade_code}```",
                silent=True,
            )
        except CommandError as e:
            self.logger.error("Failed to inspect revision", exc_info=True)
            await ctx.reply(f"Failed to inspect revision: {e}", silent=True)
        except Exception:
            self.logger.error("Failed to inspect revision", exc_info=True)
            await ctx.reply("Failed to inspect revision", silent=True)

    @db.command()
    async def current(self, ctx: commands.Context):
        """
        Displays the current database revision.
        """
        current_revision = await crud.get_current_revision(AsyncSessionLocal)
        await ctx.reply(f"Current database revision: {current_revision}", silent=True)

    print("Started Entanglements!")


async def setup(bot: commands.Bot):
    await bot.add_cog(Entanglements(bot))
