import time
import yaml
import signal
import asyncio
import discord
import requests
from discord.ext import commands
from bot_utilities.start_util import *
from pymongo.mongo_client import MongoClient

with open("config.yml", "r") as config_file: config = yaml.safe_load(config_file)

if config['bot']['start_api']:
    import uvicorn
    from api import app

async def run_flask_app_async(asyncio):
    def run_api():
        port = config["api"]["port"]
        uvicorn.run("api:app", host='0.0.0.0', port=port, log_level="warning")
    loop = asyncio.get_running_loop()
    await loop.run_in_executor(None, run_api)

# sp_id, sp_secret = spotify_token(client) Not used for now
activity = discord.Game(name="/help")
intents = discord.Intents.all()
intents.presences = False
bot = commands.AutoShardedBot(
    shard_count=1,
    command_prefix=config["bot"]["prefix"],
    intents=intents,
    activity=activity,
    help_command=None,
    reconnect=False
)
flask_task = None
flask_thread = None
mongodb = config["bot"]["mongodb"]
bot.db = MongoClient(mongodb)
bot_token = start(bot.db)

bot.start_time = time.time()
bot.is_generating = {}

@bot.event
async def on_ready():
    print(f'We have logged in as {bot.user}')

    await bot.load_extension("slash.ai")
    await bot.load_extension("slash.fun")
    await bot.load_extension("slash.information")
    await bot.load_extension("events.on_cmd_error")
    
    print(f"Booted in {time.time() - bot.start_time}s")
    await bot.tree.sync()

    if config['bot']['start_api']:
        global flask_task
        flask_task = asyncio.create_task(run_flask_app_async(asyncio))

    if config['bot']['start_api']:
        await asyncio.sleep(1)
        requests.get(f'http://localhost:{config["api"]["port"]}/create-task')

@bot.event
async def on_guild_join(guild):
    channel = bot.get_channel(1189110778599575592)
    embed = discord.Embed(title="Guild Joined", description=f"The bot has joined the server {guild.name}", color=0x00ff00)
    await channel.send(embed=embed)

@bot.event
async def on_guild_remove(guild):
    channel = bot.get_channel(1189110778599575592)
    embed = discord.Embed(title="Guild Left", description=f"The bot has left the server {guild.name}", color=0xff0000)
    await channel.send(embed=embed)


def handle_shutdown(signal, frame):
    print("Shutdown signal received. Shutting down...")
    loop = asyncio.get_event_loop()
    loop.create_task(shutdown_bot())

async def shutdown_bot():
    try:
        if config['bot']['start_api']: requests.get(f'http://localhost:{config["api"]["port"]}/shutdown')
        await bot.close()
    except Exception as e:
        await bot.close()

signal.signal(signal.SIGINT, handle_shutdown)
signal.signal(signal.SIGTERM, handle_shutdown)
bot.run(bot_token)