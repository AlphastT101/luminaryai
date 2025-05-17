from discord.ext import commands
from bot_utilities.owner_utils import check_blist_msg

class MessageHandler(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.guild is None or message.author == self.bot.user:
            return

        ctx = await self.bot.get_context(message)
        if ctx.valid and ctx.command is not None:
            if not await check_blist_msg(message, self.bot.db):
                await self.bot.process_commands(message)

async def setup(bot):
    await bot.add_cog(MessageHandler(bot))