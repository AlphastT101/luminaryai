import time
start_time = time.time()

import os
import yaml
import asyncio
import discord
import requests
from discord.ext import commands, tasks
from pymongo.mongo_client import MongoClient

# Slash commands import
from slash.ai import ai_slash
from slash.fun import fun_slash
from slash.bot import bot_slash
from slash.information import information_slash
from slash.moderation import moderation_slash

# Prefix commands import
from prefix.ai import ai
from prefix.fun import fun
from prefix.bot import bbot
from prefix.music import music
from prefix.moderation import moderation
from prefix.information import information

# Events import
from events.on_messages import on_messages
from events.member_join import member_join
from events.on_cmd_error import on_cmd_error

# API import
from api import app
from bot_utilities.start_util import *
from bot_utilities.ai_utils import process_queue

def run_api():
    port = int(os.environ.get("PORT", config["flask"]["port"]))
    import uvicorn
    uvicorn.run("api:app", host='0.0.0.0', port=port, log_level="warning")

async def run_flask_app_async():
    loop = asyncio.get_running_loop()
    await loop.run_in_executor(None, run_api)  # This will run run_flask_app in a separate thread

with open("config.yml", "r") as config_file: config = yaml.safe_load(config_file)
mongodb = config["bot"]["mongodb"]
client = MongoClient(mongodb)
bot_token, api = start(client)
# sp_id, sp_secret = spotify_token(client) Not used for now

is_generating = {}
member_histories_msg = {}
flask_thread = None
intents = discord.Intents.all()
intents.presences = False
activity = discord.Game(name="/help")
bot = commands.AutoShardedBot(
    shard_count=2,
    command_prefix=config["bot"]["prefix"],
    intents=intents, activity=activity,
    help_command=None,
    reconnect=False
)


fun(bot)
moderation(bot)
information(bot)
bbot(bot, start_time, client)
music(bot)
ai(bot, member_histories_msg, is_generating)

fun_slash(bot, client)
moderation_slash(bot, client)
information_slash(bot, client)
bot_slash(bot, start_time, client)
ai_slash(bot, client, member_histories_msg, is_generating)

on_cmd_error(bot)
member_join(bot)

@bot.command(name="cmd")
async def cmdd(ctx):
    if ctx.author.id == 1026388699203772477: await ctx.send("\n".join(cmd_list))

cmd_list = []
for command in bot.commands:
    cmd_prefix = "ai." + command.name
    cmd_list.append(cmd_prefix)

on_messages(bot, cmd_list, member_histories_msg, client)
@tasks.loop(seconds=300)
async def sync_slash_cmd():
    await bot.tree.sync()

bio = """Smart AI bot packed with features on Discord. Managed and developed by XET. AI Engine by shapes.inc

Site: https://xet.one
Support: https://discord.gg/hmMBe8YyJ4
API Playground: https://play.xet.one"""

@tasks.loop(seconds=30)
async def update_bio():
    url = "https://discord.com/api/v9/applications/@me"
    headers = {"Authorization": f"Bot {bot_token}"}
    data = {"description": bio}
    requests.patch(url=url, headers=headers, json=data)

@bot.event
async def on_ready():
    os.system('cls' if os.name == 'nt' else 'clear')
    print(f'We have logged in as {bot.user}')
    print(f"\033[1;38;5;46mCurrent model: {config['bot']['text_model']}\033[0m")
    client.admin.command('ping')
    print("Pinged your deployment. You are successfully connected to MongoDB!")
    sync_slash_cmd.start()
    update_bio.start()
    asyncio.create_task(process_queue())

    asyncio.create_task(run_flask_app_async())

    print("API Engine has been started!")
    await bot.tree.sync()
    print("Slash commands synced!")
    print(f'Shard count: {bot.shard_count}')
    time_difference = time.time() - start_time
    print(f"Booted in {time_difference}s")

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



try: bot.run(bot_token)
except KeyboardInterrupt: exit(0)