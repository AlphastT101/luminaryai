import discord
from discord.ext import commands
from bot_utilities.ai_utils import search_image, create_and_send_embed

class Ai(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="search")
    @commands.cooldown(1, 1, commands.BucketType.user)
    async def search(self, ctx, *, query: str = None):
        if query is None:
            await ctx.reply(embed=discord.Embed(description="Please enter your query."), mention_author=False)

        message = await ctx.reply(embed=discord.Embed(description="Please wait while I process your request."), mention_author=False)

        image_urls = search_image(query)
        if not image_urls:
            await message.edit(embed=discord.Embed(description="No valid images found."))
            return

        await create_and_send_embed(query, image_urls, message, ctx)

async def setup(bot):
    await bot.add_cog(Ai(bot))