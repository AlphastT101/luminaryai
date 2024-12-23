import io
import os
import bs4
import cv2
import PIL
import time
import yaml
import signal
import random
import aiohttp
import asyncio
import discord
import uvicorn
import datetime
import requests
import imagehash
import numpy as np
from openai import AsyncOpenAI
from discord.ui import View, Button
from discord.ext import commands, tasks
from pymongo.mongo_client import MongoClient

from slash.fun import fun_slash
from slash.moderation import moderation_slash

from events.on_messages import on_messages
from events.member_join import member_join
from events.on_cmd_error import on_cmd_error

from api import app

from bot_utilities.start_util import *
from bot_utilities.about_embed import about_embed
from bot_utilities.owner_utils import check_blist
from bot_utilities.ai_utils import image_generate, poly_image_gen, search_image, create_and_send_embed

with open("config.yml", "r") as config_file: config = yaml.safe_load(config_file)
def run_api():
    port = int(os.environ.get("PORT", config["api"]["port"]))
    uvicorn.run("api:app", host='0.0.0.0', port=port, log_level="warning")

async def run_flask_app_async(asyncio):
    loop = asyncio.get_running_loop()
    await loop.run_in_executor(None, run_api)

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
flask_task = None
flask_thread = None
mongodb = config["bot"]["mongodb"]
bot.db = MongoClient(mongodb)
bot_token, openr_api_token = start(bot.db)

bot.modules_io = io
bot.modules_np = np
bot.modules_cv2 = cv2
bot.modules_bs4 = bs4
bot.modules_PIL = PIL
bot.modules_time = time
bot.modules_view = View
bot.modules_random = random
bot.modules_button = Button
bot.modules_aiohttp = aiohttp
bot.modules_datetime = datetime
bot.modules_requests = requests
bot.modules_imagehash = imagehash

bot.about_embedd = about_embed
bot.start_time = time.time()
bot.is_generating = {}

bot.func_imgen = image_generate
bot.func_searchimg = search_image
bot.func_checkblist = check_blist
bot.func_poly_imgen = poly_image_gen
bot.func_cse = create_and_send_embed

bot.openai_client = AsyncOpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=openr_api_token,
)
bot.xet_client = AsyncOpenAI(
    base_url = f'http://localhost:{config["api"]["port"]}/v1',
    api_key="aner123!",
)

fun_slash(bot, bot.db)
moderation_slash(bot, bot.db)

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
    await bot.load_extension("prefix.music")
    await bot.load_extension("prefix.owner")
    await bot.load_extension("prefix.fun")
    await bot.load_extension("prefix.ai")

    await bot.load_extension("slash.ai")
    await bot.load_extension("slash.information")

    sync_slash_cmd.start()
    update_bio.start()

    global flask_task
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
    print("Shutdown signal received. Shutting down...")
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