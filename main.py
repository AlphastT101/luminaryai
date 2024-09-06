import discord
from discord.ext import commands, tasks
import os
from pymongo.mongo_client import MongoClient
import yaml
import asyncio
import threading
import time, requests

from slash.ai import ai_slash
from slash.fun import fun_slash
from slash.bot import bot_slash
from slash.information import information_slash
from slash.moderation import moderation_slash

from prefix.ai import ai
from prefix.fun import fun
from prefix.bot import bbot
from prefix.music import music
from prefix.moderation import moderation
from prefix.information import information

from events.on_messages import on_messages
from events.member_join import member_join
from events.on_cmd_error import on_cmd_error

from api import app
from bot_utilities.start_util import *
from bot_utilities.ai_utils import process_queue

def run_flask_app():
    port = int(os.environ.get("PORT", config["flask"]["port"]))
    app.run(host='0.0.0.0', port=port, debug=False)


with open("config.yml", "r") as config_file: config = yaml.safe_load(config_file)
mongodb = config["bot"]["mongodb"]
client = MongoClient(mongodb)
bot_token, api = start(client)
sp_id, sp_secret = spotify_token(client)

is_generating = {}
flask_thread = None
member_histories_msg = {}
start_time = time.time()
intents = discord.Intents.all()
intents.presences = False
activity = discord.Game(name="/help")
bot = commands.Bot(command_prefix=config["bot"]["prefix"], intents=intents, activity=activity, help_command=None, reconnect=False)


fun(bot)
moderation(bot)
information(bot)
bbot(bot, start_time, client)
music(bot, sp_id, sp_secret)
ai(bot, member_histories_msg, client, is_generating)

fun_slash(bot, client)
moderation_slash(bot, client)
information_slash(bot, client)
bot_slash(bot, start_time, client)
ai_slash(bot, client, member_histories_msg, is_generating)


on_cmd_error(bot)
member_join(bot)

@bot.command(name="cmd")
async def cmdd(ctx):
    if ctx.author.id == 1026388699203772477:
        await ctx.send("\n".join(cmd_list))
    else:
        return

cmd_list = []
for command in bot.commands:
    cmd_prefix = "ai." + command.name
    cmd_list.append(cmd_prefix)

on_messages(bot, cmd_list, member_histories_msg, client)

@tasks.loop(seconds=300) # keep the slash commands synced
async def sync_slash_cmd():
    await bot.tree.sync()

bio = """
Smart AI bot packed with features on Discord.

Site: https://luminaryai.netlify.app
Support: https://discord.gg/hmMBe8YyJ4
TOS: https://luminaryai.netlify.app/tos"""

@tasks.loop(seconds=30)
async def update_bio():
    url = "https://discord.com/api/v9/applications/@me"
    headers = {"Authorization": f"Bot {bot_token}"}
    data = {"description": bio}
    response = requests.patch(url=url, headers=headers, json=data)

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

    # Run Flask app in a separate thread
    flask_thread = threading.Thread(target=run_flask_app, daemon=True)
    flask_thread.start()
    
    print("API Engine has been started!")
    await bot.tree.sync()
    print("Slash commands synced!")

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