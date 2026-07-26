from discord.ext import commands

from bot.utils.ai import create_and_send_embed, search_image
from bot.utils.blacklist import check_blist_msg
from bot.utils.embeds import create_error_embed, create_processing_embed


class Ai(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="search")
    @commands.cooldown(1, 1, commands.BucketType.user)
    async def search(self, ctx, *, query: str = None):
        if await check_blist_msg(ctx, self.bot.db):
            return
        if query is None:
            await ctx.reply(
                embed=create_error_embed(description="Please enter your query."),
                mention_author=False,
            )
            return

        message = await ctx.reply(
            embed=create_processing_embed(description="Please wait while I process your request."),
            mention_author=False,
        )

        image_urls = await search_image(query)
        if not image_urls:
            await message.edit(embed=create_error_embed(description="No valid images found."))
            return

        await create_and_send_embed(query, image_urls, message, ctx)


async def setup(bot):
    await bot.add_cog(Ai(bot))
