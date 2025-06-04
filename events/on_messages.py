from discord.ext import commands
from bot_utilities.ai_utils import gentext

class MessageHandler(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.guild is None or message.author.bot: return

        collection = self.bot.db['bot']['activated_channels']
        if not collection.find_one({"id": message.channel.id}): return

        async with message.channel.typing():
            if message.author.id not in self.bot.history: self.bot.history[message.author.id] = []

            history = self.bot.history[message.author.id]
            history.append({"role": "user", "content": message.content})

            try:
                response = await gentext(history)
                history.append({"role": "assistant", "content": response})

                max_len = 2000
                parts = [response[i:i + max_len] for i in range(0, len(response), max_len)]

                for part in parts:
                    await message.reply(part)
        
            except Exception as e:
                await message.reply("Something went wrong while generating a response.")
                print(f"[gentext error] {e}")

async def setup(bot):
    await bot.add_cog(MessageHandler(bot))