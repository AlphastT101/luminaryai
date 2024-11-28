import discord
import aiohttp
# import datetime
from discord.ext import commands
from bot_utilities.ai_utils import *
from bot_utilities.owner_utils import *

def ai(bot, member_histories_msg, is_generating):

    # @bot.command(name='activate')
    # @commands.cooldown(1, 10, commands.BucketType.user)
    # async def start(ctx):
    #     channel_id = ctx.channel.id

    #     if ctx.author.guild_permissions.administrator or ctx.author.id == 1026388699203772477:
    #         insert_result = await insertdb("ai-channels",channel_id, mongodb)
    #         if insert_result == "success":
    #             await ctx.send(embed=Embed(description="Success, now I'll respond to **all messages** in this channel.", color=discord.Colour.green()))
    #         elif insert_result == "already set":
    #             await ctx.send(embed=Embed(description=":x: **Error**, this channel is already activated.", colour=discord.Colour.red()))
    #     else:
    #         await ctx.send(embed=Embed(description="**You don't have permission to use this comamnd.**", color=discord.Color.red()),)


    # @bot.command(name='deactivate')
    # @commands.cooldown(1, 10, commands.BucketType.user)
    # async def stop(ctx):

    #     channel_id = ctx.channel.id

    #     if ctx.author.guild_permissions.administrator or ctx.author.id == 1026388699203772477:
    #         delete_result = await deletedb("ai-channels", channel_id, mongodb)

    #         if delete_result == "success":
    #             await ctx.send(embed=Embed(description="**Successfully disabled this channel.**", color=discord.Color.green()),)
    #         elif delete_result == "not found":
    #             await ctx.send(embed=Embed(description=":x: **Error**, this channel isn't activated.", colour=discord.Colour.red()))
    #     else:
    #         await ctx.send(embed=Embed(description="**You don't have permission to use this comamnd.**", color=discord.Color.red()),)


    # @bot.command(name='ask')
    # @commands.cooldown(1, 80, commands.BucketType.user)
    # async def answer_command(ctx, *, args: str = None):
    #     if args is None:
    #         await embed(ctx, "LuminaryAI - Error", "Please enter your question.", color=0x99ccff)
    #         return
    #     # Get or create member-specific history
    #     member_id = str(ctx.author.id)  # Using member ID as the key
    #     history = member_histories_msg.get(member_id, [])

    #     answer_embed = discord.Embed(
    #         title="LuminaryAI - Loading",
    #         description="Please wait while I process your request.",
    #         color=0x99ccff,
    #         timestamp=datetime.datetime.now(datetime.timezone.utc)
    #     )
    #     answer_embed.set_footer(text="This may take a few moments", icon_url=bot.user.avatar.url)
    #     answer = await ctx.reply(embed=answer_embed)

    #     user_input = args
    #     generated_message, updated_history = await generate_response_cmd(ctx, user_input, history)
    #     member_histories_msg[member_id] = updated_history


    #     answer_generated = discord.Embed(
    #         title="LuminaryAI - Response",
    #         description=generated_message,
    #         color=0x99ccff,
    #         timestamp=datetime.datetime.now(datetime.timezone.utc)
    #     )
    #     answer_generated.set_footer(text="Thanks for using LuminaryAI!", icon_url=bot.user.avatar.url)
    #     await answer.edit(embed=answer_generated)


    @bot.command(name="imagine")
    async def imagine(ctx, *, prompt: str = None):
        if is_generating.get(ctx.author.id):
            await ctx.send("> **You're already generating an image!**")
            return

        if prompt is None:
            await ctx.send("> **Please enter your prompt.**")
            return

        is_generating[ctx.author.id] = True
        req = await ctx.reply("> **Please wait while I process your request.**")
        link = await image_generate("flux", prompt, "1024x1024")

        try:
            embed = discord.Embed(
                title="LuminaryAI - Image Generation",
                description=f"Requested by: `{ctx.author}`\nPrompt: `{prompt}`\nModel: `Flux`\n\nModel is selected `Flux` by default in prefix commands, if you want to choose a specific model, please use the `/imagine` command!",
                color=discord.Color.blue()
            )
            embed.set_footer(icon_url=bot.user.avatar.url, text="Thanks for using LuminaryAI!")
            embed.set_image(url=link)
            await req.edit(content="", embed=embed)
            is_generating[ctx.author.id] = False
        except Exception as e:
            req.edit(content="> **❌ Ouch! something went wrong.**")


    @bot.command(name='poli')
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def imagine_m2_command(ctx, *, prompt: str = None):
        if prompt is None:
            await ctx.reply("**Please enter your prompt!**", delete_after=3)
            return

        delete_msg = await ctx.send("> **⌚Please wait while I process your request.**")
        async with aiohttp.ClientSession() as session:
            send_embed = discord.Embed(
                title="LuminaryAI - Image generation",
                description=f"Requested by: `{ctx.author}`\nPrompt: `{prompt}`.",
                color=0x99ccff,
                timestamp=ctx.message.created_at
            )
            send_embed.set_footer(icon_url=bot.user.avatar.url, text="Thanks for using LuminaryAI!")
            image = await poly_image_gen(session, prompt)
            file=discord.File(image, 'generated_image.png')
            send_embed.set_image(url=f'attachment://generated_image.png')
            await delete_msg.delete()
            await ctx.reply(content="", embed=send_embed, file=file)


    @bot.command(name="search")
    @commands.cooldown(1, 1, commands.BucketType.user)
    async def search(ctx, *, query: str = None):
        if query is None:
            await embed(ctx, "LuminaryAI - Web search", "Please enter your prompt", color=0x99ccff)
            return

        wait = discord.Embed(
            title="LuminaryAI - loading",
            description="Please wait while I process your request.",
            timestamp=ctx.message.created_at,
            color=0x99ccff,
        )
        wait.set_footer(text=f"Thanks for using {bot.user}!", icon_url=bot.user.avatar.url)
        file_web_search = discord.File('images/web_search.png', filename='web_search.png')
        wait.set_thumbnail(url='attachment://web_search.png')
        wait_message = await ctx.send(embed=wait, file=file_web_search)

        # Get image URLs from the search query
        image_urls = search_image(query)
        if not image_urls:
            await wait_message.delete()
            await ctx.send("> ❌ **Aww, no results found!**")
            return

        await create_and_send_embed(query, bot, ctx, image_urls)
        await wait_message.delete()