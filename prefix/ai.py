import discord
from discord.ext import commands

class Ai(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="imagine")
    async def imagine(self, ctx, *, prompt: str = None):
        if self.bot.is_generating.get(ctx.author.id):
            await ctx.send("> **You're already generating an image!**")
            return

        if prompt is None:
            await ctx.send("> **Please enter your prompt.**")
            return

        self.bot.is_generating[ctx.author.id] = True
        req = await ctx.reply("> **Please wait while I process your request.**")
        link = await self.bot.func_imgen("flux-dev", prompt, "1024x1024", self.bot)

        try:
            embed = discord.Embed(
                title="LuminaryAI - Image Generation",
                description=f"Requested by: `{ctx.author}`\nPrompt: `{prompt}`\nModel: `Flux-Dev`\n\nModel is selected `Flux-Dev` by default in prefix commands, if you want to choose a specific model, please use the `/imagine` command!",
                color=discord.Color.blue()
            )
            embed.set_footer(icon_url=self.bot.user.avatar.url, text="Thanks for using LuminaryAI!")
            embed.set_image(url=link)
            await req.edit(content="", embed=embed)
            self.bot.is_generating[ctx.author.id] = False
        except Exception as e:
            self.bot.is_generating[ctx.author.id] = False
            req.edit(content="> **❌ Ouch! something went wrong.**")

    @commands.command(name='poli')
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def imagine_m2_command(self, ctx, *, prompt: str = None):
        if prompt is None:
            await ctx.reply("**Please enter your prompt!**", delete_after=3)
            return

        delete_msg = await ctx.send("> **⌚Please wait while I process your request.**")
        async with self.bot.modules_aiohttp.ClientSession() as session:
            send_embed = discord.Embed(
                title="LuminaryAI - Image generation",
                description=f"Requested by: `{ctx.author}`\nPrompt: `{prompt}`.",
                color=0x99ccff,
                timestamp=ctx.message.created_at
            )
            send_embed.set_footer(icon_url=self.bot.user.avatar.url, text="Thanks for using LuminaryAI!")
            image = await self.bot.func_poly_imgen(session, prompt, self.bot)

            file=discord.File(image, 'generated_image.png')
            send_embed.set_image(url=f'attachment://generated_image.png')
            await delete_msg.delete()
            await ctx.reply(content="", embed=send_embed, file=file)
        await session.close()

    @commands.command(name="search")
    @commands.cooldown(1, 1, commands.BucketType.user)
    async def search(self, ctx, *, query: str = None):
        if query is None:
            await embed(ctx, "LuminaryAI - Web search", "Please enter your prompt", color=0x99ccff)
            return

        wait = discord.Embed(
            title="LuminaryAI - loading",
            description="Please wait while I process your request.",
            timestamp=ctx.message.created_at,
            color=0x99ccff,
        )
        wait.set_footer(text=f"Thanks for using {self.bot.user}.", icon_url=self.bot.user.avatar.url)
        file_web_search = discord.File('images/web_search.png', filename='web_search.png')
        wait.set_thumbnail(url='attachment://web_search.png')
        wait_message = await ctx.send(embed=wait, file=file_web_search)

        image_urls = self.bot.func_searchimg(query, self.bot)
        if not image_urls:
            await wait_message.delete()
            await ctx.send("> ❌ **Aww, no results found!**")
            return

        await self.bot.func_cse(self.bot.modules_discord, query, ctx, image_urls, self.bot)
        await wait_message.delete()

async def setup(bot):
    await bot.add_cog(Ai(bot))