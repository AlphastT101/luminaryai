import discord
from discord import app_commands
from discord.ext import commands
from bot_utilities.owner_utils import *
from bot_utilities.ai_utils import vision
from bot_utilities.ai_utils import *
from bot_utilities.api_utils import check_user, insert_token, delete_token

def ai_slash(bot, mongodb, member_histories_msg, is_generating):

    # @bot.tree.command(name="activate", description="Activate AI responses in a channel.")
    # @commands.guild_only()
    # @app_commands.describe(channel="Select the channel you want to activate the AI in(optional).")
    # async def activate_slash(interaction: discord.Interaction, channel: discord.TextChannel = None):
    #     if await check_blist(interaction, mongodb): return
    #     await interaction.response.defer(ephemeral=False)
    #     if channel is None: channel = interaction.channel
    #     channel_id = channel.id

    #     if interaction.user.guild_permissions.administrator or interaction.user.id == 1026388699203772477:
    #         insert_result = await insertdb("ai-channels",channel_id, mongodb)
    #         if insert_result == "success":
    #             await interaction.followup.send(embed=Embed(description="Success, now I'll respond to **all messages** in that channel.", color=discord.Colour.green()))
    #         elif insert_result == "already set":
    #             await interaction.followup.send(embed=Embed(description=":x: **Error**, that channel is already activated.", colour=discord.Colour.red()))
    #     else:
    #         await interaction.followup.send(embed=Embed(description="**You don't have permission to use this comamnd.**", color=discord.Color.red()),)
    
    
    # @commands.guild_only()
    # @bot.tree.command(name="deactivate", description="Deactivate AI responses in a channel")
    # @app_commands.describe(channel="Select the channel you want to activate the AI in(optional).")
    # async def deactivate_slash(interaction: discord.Interaction, channel: discord.TextChannel = None):
    #     if await check_blist(interaction, mongodb): return
    #     await interaction.response.defer(ephemeral=False)
    #     if channel is None: channel = interaction.channel
    #     channel_id = channel.id

    #     if interaction.user.guild_permissions.administrator or interaction.user.id == 1026388699203772477:
    #         delete_result = await deletedb("ai-channels", channel_id, mongodb)

    #         if delete_result == "success":
    #             await interaction.followup.send(embed=Embed(description="**✅ Successfully **disabled** that channel.**", color=discord.Color.green()),)
    #         elif delete_result == "not found":
    #             await interaction.followup.send(embed=Embed(description="❌ **Error**, that channel isn't activated.", colour=discord.Colour.red()))
    #     else:
    #         await interaction.followup.send(embed=Embed(description="**❌ You don't have permission to use this comamnd.**", color=discord.Color.red()),)

    @bot.tree.command(name="vision", description="Vision an image")
    @commands.guild_only()
    @app_commands.describe(message="Enter your message.")
    @app_commands.describe(image_link="Enter the image link.")
    async def vision_command(interaction: discord.Interaction, message: str, image_link: str):
        if await check_blist(interaction, mongodb): return
        await interaction.response.defer(ephemeral=False)
        response = await vision(message, image_link)

        response_embed = discord.Embed(
            title="LuminaryAI - vision",
            description=response,
            color=discord.Color.green() if response != "Ouch! Something went wrong!" else discord.Color.red()
        )

        response_embed.set_footer(text="Reply from LuminaryAI Image Vision. LuminaryAI does not guarantee the accuracy of the response provided. The Vision model is currently in **beta**")
        await interaction.followup.send(embed=response_embed)
    

    @bot.tree.command(name="ask", description="Ask LuminaryAI a question!")
    @commands.guild_only()
    @app_commands.describe(prompt="The question you want to ask LuminaryAI")
    async def ask(interaction: discord.Interaction, prompt: str):
        if await check_blist(interaction, mongodb): return
        await interaction.response.defer(ephemeral=False)

        if prompt is None:
            await interaction.followup.send(embed=discord.Embed(description="**❌ Please include your prompt!**"))
            return

        member_id = str(interaction.user.id)
        history = member_histories_msg.get(member_id, [])

        answer_embed = discord.Embed(
            title="LuminaryAI - Loading",
            description="Please wait while I process your request.",
            color=0x99ccff,
        )
        answer_embed.set_footer(text="This may take a few moments", icon_url=bot.user.avatar.url)
        answer = await interaction.followup.send(embed=answer_embed)

        generated_message, updated_history = await generate_response_slash(interaction, prompt, history)
        member_histories_msg[member_id] = updated_history

        answer_generated = discord.Embed(
            title="LuminaryAI - Response",
            description=generated_message,
            color=0x99ccff,
        )
        answer_generated.set_footer(text="Thanks for using LuminaryAI!", icon_url=bot.user.avatar.url)
        await answer.edit(embed=answer_generated)


    @bot.tree.command(name="imagine", description="Imagine an image using LuminaryAI")
    @commands.guild_only()
    @app_commands.describe(prompt="Enter the prompt for the image to generate.")
    async def imagine_pla(interaction: discord.Interaction, prompt: str):
        if await check_blist(interaction, mongodb): return
        await interaction.response.defer(ephemeral=False)

        if is_generating.get(interaction.user.id):
            await interaction.followup.send("> **You're already generating an image!**")
            return
        if prompt is None:
            await interaction.followup.send("> **Please enter your prompt.**")
            return

        is_generating[interaction.user.id] = True
        req = await interaction.followup.send("> **Please wait while I process your request.**")

        guild = bot.get_guild(1253765266115133442)
        category = discord.utils.get(guild.categories, name="dalle3")
        exists = discord.utils.get(guild.text_channels, name=str(interaction.user.id))
        if exists: await exists.delete()
        channel = await guild.create_text_channel(str(interaction.user.id), category=category)
        sendapi = bot.get_channel(1254053747227889785)
        await sendapi.send(f"a!reqapi {interaction.user.id} {channel.id} 1 {prompt}")

        def check(m):
            if m.content == "uhh can u say that again?":
                return False
            return m.content.startswith("https://files.shapes.inc/") and m.channel.id == channel.id

        try:
            msg = await bot.wait_for('message', check=check, timeout=120)
            if not msg:
                await req.edit("> **❌ Excepted a link from the API, recived a string instead.")
            embed = discord.Embed(
                title="LuminaryAI - Image Generation",
                description=f"Requested by: `{interaction.user}`\nPrompt: `{prompt}`",
                color=discord.Color.blue()
            )
            embed.set_footer(icon_url=bot.user.avatar.url, text="Thanks for using LuminaryAI!")
            embed.set_image(url=msg.content)
            await req.edit(content="", embed=embed)
        except asyncio.TimeoutError:
            await req.edit(content="> **❌ Request timed out. Please try again later.**")
        finally:
            is_generating[interaction.user.id] = False
            await channel.delete()


    @bot.tree.command(name='poli', description="Generate images using Polinations.ai")
    @commands.guild_only()
    @app_commands.describe(prompt="Enter the prompt for the image to generate.")
    async def poli_gen(interaction: discord.Interaction, prompt: str):
        if await check_blist(interaction, mongodb): return
        await interaction.response.defer(ephemeral=False)
        delete_msg = await interaction.followup.send("> **⌚Please wait while I process your request.**")
        async with aiohttp.ClientSession() as session:
            send_embed = discord.Embed(
                title="LuminaryAI - Image generation",
                description=f"Requested by: `{interaction.user}`\nPrompt: `{prompt}`.",
                color=0x99ccff,
            )
            send_embed.set_footer(icon_url=bot.user.avatar.url, text="Thanks for using LuminaryAI!")
            image = await poly_image_gen(session, prompt)
            file=discord.File(image, 'generated_image.png')
            send_embed.set_image(url=f'attachment://generated_image.png')
            await delete_msg.delete()
            await interaction.followup.send(content="", embed=send_embed, file=file)

    @bot.tree.command(name="search", description="Seaech the web for images and texts!")
    @commands.guild_only()
    @app_commands.describe(prompt="Enter prompt for the web to search!")
    async def search(interaction: discord.Interaction, prompt: str):
        if await check_blist(interaction, mongodb): return
        await interaction.response.defer(ephemeral=False)
        image_urls = search_image(prompt)
        await create_and_send_embed(prompt, bot, interaction, image_urls)


    @bot.tree.command(name="generate-api-key", description="Generate an API key for LuminaryAI")
    @commands.guild_only()
    async def create_api(interaction: discord.Interaction):
        if await check_blist(interaction, mongodb): return
        await interaction.response.defer(ephemeral=True)
        check = await check_user(mongodb, interaction.user.id)
    
        if check:
            await interaction.followup.send("> ❌ **You already have an API token! You can generate only one API token.**")
            return
        
        token = await insert_token(mongodb, interaction.user.id)
        await interaction.followup.send(f"> ✅ **API token is generated successfully. Do not share this key with anyone, even they are from LuminaryAI!**\n* **Join our support server for help on how to use the API Key.**\n* **API token:**\n```bash\n{token}```\n")


    @bot.tree.command(name="delete-api-key", description="Delete Your API key for LuminaryAI")
    @commands.guild_only()
    async def delete_api(interaction: discord.Interaction):
        if await check_blist(interaction, mongodb): return
        await interaction.response.defer(ephemeral=False)
        check = await check_user(mongodb, interaction.user.id)
    
        if check:
            deleted = await delete_token(mongodb, interaction.user.id)
            if deleted:
                await interaction.followup.send("> ✅ **API token is deleted successfully**")
            else:
                await interaction.followup.send("> ❌ **Failed to delete API token**")
        else: await interaction.followup.send("> ❌ **You don't have an API key!**")
        