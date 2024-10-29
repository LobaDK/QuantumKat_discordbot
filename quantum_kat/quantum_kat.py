import asyncio
import hikari
import lightbulb  # Used for plugins (similar to cogs in discord.py)
import arc  # Used for slash commands and type hints
from os import name, environ

from quantum_kat.lib.utility import get_field_from_1password
from quantum_kat import quantum_kat_logger

if name != "nt":
    import uvloop

    asyncio.set_event_loop_policy(policy=uvloop.EventLoopPolicy())

token_type: str = environ.get("TOKEN_TYPE", default="Main")
references: str = (
    f"op://Programming and IT security/QuantumKat Discord bot/{token_type} token"
)

try:
    bot = hikari.GatewayBot(token=get_field_from_1password(reference=references))
except Exception:
    quantum_kat_logger.exception(msg="Failed to create instance of GatewayBot.")
    exit(code=1)
