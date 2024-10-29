import asyncio
import hikari
import lightbulb  # Used for plugins (similar to cogs in discord.py)
import arc  # Used for slash commands and type hints
from os import name, environ

from quantum_kat.lib.utility import get_field_from_1password
from quantum_kat import quantum_kat_logger
from quantum_kat import plugins

if name != "nt":
    import uvloop

    asyncio.set_event_loop_policy(policy=uvloop.EventLoopPolicy())


token_type: str = environ.get("TOKEN_TYPE", default="Main")
references: str = (
    f"op://Programming and IT security/QuantumKat Discord bot/{token_type} token"
)

try:
    quantum_bot = hikari.GatewayBot(
        token=get_field_from_1password(reference=references)
    )
except Exception:
    quantum_kat_logger.exception(msg="Failed to create instance of GatewayBot.")
    exit(code=1)

lb_client: lightbulb.GatewayEnabledClient = lightbulb.client_from_app(
    app=quantum_bot, default_enabled_guilds=["665680289510588447"]
)


@quantum_bot.listen(hikari.StartingEvent)
async def on_starting(_: hikari.StartingEvent) -> None:
    await lb_client.load_extensions_from_package(package=plugins)
    await lb_client.start()


@quantum_bot.listen(hikari.StoppingEvent)
async def on_stopping(_: hikari.StoppingEvent) -> None:
    await lb_client.stop()
