
import discord
from discord.ui import Button
from discord.ext import commands
from bot_utilities.owner_utils import *
from bot_utilities.about_embed import about_embed
from bot_utilities.help_embed import *
import datetime
import time

def bot_slash(bot,start_time, mongodb):

    ##### check #######
    @bot.tree.command(name="status", description="Check bot status")
    @commands.guild_only()
    async def check(interaction: discord.Interaction):
        if await check_blist(interaction, mongodb): return
        await interaction.response.send_message("bot is online")

    @bot.tree.command(name="uptime", description="Shows bot uptime")
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def uptime(interaction: discord.Interaction):
        if await check_blist(interaction, mongodb): return
        await interaction.response.defer(ephemeral=False)
        current_time = time.time()
        difference = int(round(current_time - start_time))
        uptime_duration = datetime.timedelta(seconds=difference)

        embed = discord.Embed(colour=0xc8dc6c)
        embed.add_field(name="LuminaryAI - Uptime", value=str(uptime_duration))
        await interaction.followup.send(embed=embed)

    ############## about ##################
    @bot.tree.command(name="about", description="about the bot")
    @commands.guild_only()
    async def about(interaction: discord.Interaction):
        if await check_blist(interaction, mongodb): return
        await interaction.response.defer(ephemeral=False)
        about = await about_embed(start_time, bot)
        owner = bot.get_user(1026388699203772477)
        about.set_author(name="alphast101", icon_url=owner.avatar.url)
        await interaction.followup.send(embed=about, file=discord.File("images/ai.png", filename="ai.png"))

    ##### help #######
    @bot.tree.command(name="help", description="Help/command list")
    @commands.guild_only()
    async def help(interaction: discord.Interaction):
        if await check_blist(interaction, mongodb): return
        await interaction.response.defer(ephemeral=False)

        help_view = View()
        help_view.add_item(help_select)

        help_embbed.set_thumbnail(url=bot.user.avatar)
        help_msg = await interaction.followup.send(embed=help_embbed, view=help_view)
        # Pagination buttons
        buttons = [
            Button(label="Previous", style=discord.ButtonStyle.primary, custom_id='Previous'),
            Button(label="Next", style=discord.ButtonStyle.primary, custom_id='Next')
        ]

        help_view.add_item(buttons[0])
        help_view.add_item(buttons[1])

        # Variables to track current state
        current_page = 0
        current_commands = information_commannds
        embed = embed_info

        async def help_callback(interaction):
            nonlocal current_page, current_commands, embed

            if help_select.values[0] == "Information":
                current_commands = information_commannds
                embed = embed_info
            elif help_select.values[0] == "AI":
                current_commands = ai_commands
                embed = embed_ai
            elif help_select.values[0] == "Fun":
                current_commands = fun_commands
                embed = embed_fun
            elif help_select.values[0] == "Moderation":
                current_commands = moderation_commands
                embed = embed_moderation
            elif help_select.values[0] == "Automod":
                current_commands = automod_commands
                embed = embed_automod
            elif help_select.values[0] == "Admin":
                current_commands = admin_commands
                embed = embed_admin
            elif help_select.values[0] == "Music":
                current_commands = music_commands
                embed = embed_music

            current_page = 0  # Reset to the first page
            embed = get_chunk(embed, current_commands, current_page * 5)
            await interaction.response.defer()
            await help_msg.edit(embed=embed, view=help_view)

        help_select.callback = help_callback

        # Callback for the buttons
        async def button_callback(interaction):
            nonlocal current_page, current_commands, embed


            if interaction.data["custom_id"] == "Previous":
                current_page = max(current_page - 1, 0)
            elif interaction.data["custom_id"] == "Next":
                current_page = min(current_page + 1, (len(current_commands) - 1) // 5)

            embed = get_chunk(embed, current_commands, current_page * 5)
            await interaction.response.defer()
            await help_msg.edit(embed=embed, view=help_view)

        for button in buttons:
            button.callback = button_callback