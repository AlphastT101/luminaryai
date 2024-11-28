# import discord
# from discord.ext import commands
from bot_utilities.owner_utils import *

def member_join(bot):
    @bot.event
    async def on_member_join(member):
        return