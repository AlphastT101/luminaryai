import os
import time
import yaml
import signal
import asyncio
import discord
import uvicorn
import requests
from discord.ext import commands, tasks
from pymongo.mongo_client import MongoClient

from slash.ai import ai_slash
from slash.fun import fun_slash
from slash.bot import bot_slash
from slash.moderation import moderation_slash
from slash.information import information_slash

from prefix.ai import ai
from prefix.music import music

from events.on_messages import on_messages
from events.member_join import member_join
from events.on_cmd_error import on_cmd_error

from api import app
from bot_utilities.start_util import *
from bot_utilities.ai_utils import process_queue

def run_api():
    port = int(os.environ.get("PORT", config["flask"]["port"]))
    uvicorn.run("api:app", host='0.0.0.0', port=port, log_level="warning")

async def run_flask_app_async(asyncio):
    loop = asyncio.get_running_loop()
    await loop.run_in_executor(None, run_api)

with open("config.yml", "r") as config_file: config = yaml.safe_load(config_file)
flask_task = None
flask_thread = None
mongodb = config["bot"]["mongodb"]
activity = discord.Game(name="/help")
intents = discord.Intents.all()
intents.presences = False
# sp_id, sp_secret = spotify_token(client) Not used for now
bot = commands.AutoShardedBot(
    shard_count=2,
    command_prefix=config["bot"]["prefix"],
    intents=intents,
    activity=activity,
    help_command=None,
    reconnect=False
)
bot.is_generating = {}
bot.start_time = time.time()
bot.db = MongoClient(mongodb)
bot_token, api = start(bot.db)

music(bot)
ai(bot)

fun_slash(bot, bot.db)
moderation_slash(bot, bot.db)
information_slash(bot, bot.db)
bot_slash(bot, bot.start_time, bot.db)
ai_slash(bot)

on_messages(bot, bot.db)
on_cmd_error(bot)
member_join(bot)


bio = """Smart AI bot packed with features on Discord. Managed and developed by XET. AI Engine by shapes.inc.

Site: https://xet.one
Support: https://discord.gg/hmMBe8YyJ4
API Playground: https://play.xet.one"""

@tasks.loop(seconds=30)
async def update_bio():
    url = "https://discord.com/api/v9/applications/@me"
    headers = {"Authorization": f"Bot {bot_token}"}
    data = {"description": bio}
    requests.patch(url=url, headers=headers, json=data)

@tasks.loop(seconds=300)
async def sync_slash_cmd():
    await bot.tree.sync()

@bot.event
async def on_ready():
    print(f'We have logged in as {bot.user}')

    await bot.load_extension("prefix.moderation")
    await bot.load_extension("prefix.information")
    await bot.load_extension("prefix.owner")
    await bot.load_extension("prefix.fun")

    sync_slash_cmd.start()
    update_bio.start()
    asyncio.create_task(process_queue())

    global flask_task  # Refer to the global variable
    flask_task = asyncio.create_task(run_flask_app_async(asyncio))

    print("API Engine has been started.") 
    print(f"Booted in {time.time() - bot.start_time}s")

    await asyncio.sleep(2)
    requests.get("http://localhost:6750/create-task")

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
    print("Shutdown signal received. Cleaning up...")
    loop = asyncio.get_event_loop()
    loop.create_task(shutdown_bot())

async def shutdown_bot():
    try:
        requests.get("http://localhost:6750/shutdown")
        await bot.close()
    except Exception as e:
        await bot.close()

signal.signal(signal.SIGINT, handle_shutdown)
signal.signal(signal.SIGTERM, handle_shutdown)
bot.run(bot_token)