import asyncio
import hikari
from os import name
from pathlib import Path

from shared.utility import create_bot
from QuantumKat import quantum_kat_logger

if name != "nt":
    import uvloop

    quantum_kat_logger.debug(
        msg="System appears to be running on a non-Windows OS, using uvloop as the event loop policy."
    )
    asyncio.set_event_loop_policy(policy=uvloop.EventLoopPolicy())


quantum_bot, arc_client = create_bot()


@quantum_bot.listen(hikari.StartingEvent)
async def on_starting(_: hikari.StartingEvent) -> None:
    arc_client.load_extensions_from(dir_path=Path("QuantumKat", "extensions"))


@quantum_bot.listen(hikari.StoppingEvent)
async def on_stopping(_: hikari.StoppingEvent) -> None:
    pass
