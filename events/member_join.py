# import discord

def member_join(bot):
    @bot.event
    async def on_member_join(member):
        return