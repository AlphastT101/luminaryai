import signal
import time

import discord
from discord.ext import commands
from pymongo.mongo_client import MongoClient

from bot import config

if not config.DISCORD_TOKEN:
    raise SystemExit("DISCORD_TOKEN is missing. Copy .env.example to .env and fill in your values.")

activity = discord.Game(name="/help" if config.ENABLE_SLASH_COMMANDS else f"{config.BOT_PREFIX}help")
intents = discord.Intents.all()
intents.presences = False

bot = commands.AutoShardedBot(
    shard_count=config.SHARD_COUNT,
    command_prefix=config.BOT_PREFIX,
    intents=intents,
    activity=activity,
    help_command=None,
    reconnect=False,
)

bot.db = MongoClient(config.MONGODB_URI)
bot.poli_token = config.POLLINATIONS_TOKEN
bot.start_time = time.time()
bot.is_generating = {}
bot.history = {}


@bot.event
async def on_ready():
    print(f"We have logged in as {bot.user}")

    if config.ENABLE_PREFIX_COMMANDS:
        await bot.load_extension("bot.cogs.prefix.owner")
        await bot.load_extension("bot.cogs.prefix.ai")
        await bot.load_extension("bot.cogs.prefix.fun")
        await bot.load_extension("bot.cogs.prefix.information")

    if config.ENABLE_SLASH_COMMANDS:
        await bot.load_extension("bot.cogs.slash.ai")
        await bot.load_extension("bot.cogs.slash.fun")
        await bot.load_extension("bot.cogs.slash.information")

    await bot.load_extension("bot.events.on_messages")
    await bot.load_extension("bot.events.on_cmd_error")
    await bot.load_extension("bot.events.on_member_join")

    print(f"Booted in {time.time() - bot.start_time}s")
    if config.ENABLE_SLASH_COMMANDS:
        await bot.tree.sync()


@bot.event
async def on_guild_join(guild):
    if not config.GUILD_LOG_CHANNEL_ID:
        return
    channel = bot.get_channel(config.GUILD_LOG_CHANNEL_ID)
    if not channel:
        return
    embed = discord.Embed(
        title="Guild Joined",
        description=f"The bot has joined the server {guild.name}",
        color=config.EMBED_COLOR_SUCCESS,
    )
    await channel.send(embed=embed)


@bot.event
async def on_guild_remove(guild):
    if not config.GUILD_LOG_CHANNEL_ID:
        return
    channel = bot.get_channel(config.GUILD_LOG_CHANNEL_ID)
    if not channel:
        return
    embed = discord.Embed(
        title="Guild Left",
        description=f"The bot has left the server {guild.name}",
        color=config.EMBED_COLOR_ERROR,
    )
    await channel.send(embed=embed)


def handle_shutdown(signum, frame):
    print("Shutdown signal received. Shutting down...")
    import asyncio

    loop = asyncio.get_event_loop()
    loop.create_task(shutdown_bot())


async def shutdown_bot():
    try:
        await bot.close()
    except Exception:
        await bot.close()


signal.signal(signal.SIGINT, handle_shutdown)
signal.signal(signal.SIGTERM, handle_shutdown)
bot.run(config.DISCORD_TOKEN)
