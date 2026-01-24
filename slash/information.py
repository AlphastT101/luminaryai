import time
import datetime
from discord.ext import commands
from discord.ui import View, Button
from bot_utilities.help_embed import *
from bot_utilities.owner_utils import *
from bot_utilities.about_embed import *
from bot_utilities.credits_ranking import CreditsRanking
from bot_utilities.credits_cache import CreditsCache
from bot_utilities.embed_utils import create_embed, create_error_embed, create_success_embed, create_warning_embed, create_processing_embed
from discord import app_commands, Interaction

class InformationSlash(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name='userinfo', description="View information about a user")
    @app_commands.guild_only()
    @app_commands.describe(user="Select a user.")
    async def user(self, interaction: Interaction, user: discord.Member = None):
        if await check_blist(interaction, self.bot.db): return
        await interaction.response.defer(ephemeral=False)

        if user is None:user = interaction.user
        roles = [role.mention for role in user.roles if role != interaction.guild.default_role]
        roles_string = ", ".join(roles) if roles else "No roles"

        permissions = interaction.channel.permissions_for(user)
        permissions_string = ", ".join([perm.replace('_', ' ').title() for perm, value in permissions if value])

        embed = create_embed(
            title=f"Username: {user}",
            description=(
                f"UserID: `{user.id}`\n"
                f"Joined the server: <t:{int(user.joined_at.timestamp())}:R>\n"
                f"Joined Discord: <t:{int(user.created_at.timestamp())}:R>\n\n"
                "**User's Roles:**\n"
                f"{roles_string}\n\n"
                "**Channel Permissions:**\n"
                f"{permissions_string}"
            )
        )
        embed.set_thumbnail(url=user.avatar.url)
        await interaction.followup.send(embed=embed)


    @app_commands.command(name='support', description="Shows support server invite link")
    @app_commands.guild_only()
    async def support(self, interaction: discord.Interaction):
        if await check_blist(interaction, self.bot.db): return
        await interaction.response.defer(ephemeral=False)
        await interaction.followup.send(embed=create_embed(description="**Support server:** [here](https://discord.com/invite/hmMBe8YyJ4)"))

    @app_commands.command(name='owner', description="Shows bot owner")
    @app_commands.guild_only()
    async def owner(self, interaction: discord.Interaction):
        if await check_blist(interaction, self.bot.db): return
        await interaction.response.defer(ephemeral=False)
        await interaction.followup.send(embed=create_embed(description="My owner is [AlphasT101](https://me.lumixcore.com)"))

    @app_commands.command(name="ping", description="See bot ping")
    @app_commands.guild_only()
    async def check(self, interaction: discord.Interaction):
        if await check_blist(interaction, self.bot.db): return
        await interaction.response.defer(ephemeral=False)
        await interaction.followup.send(embed=create_embed(description=f"**Latency:** `{round(self.bot.latency * 1000)}ms`"))

    @app_commands.command(name="uptime", description="Shows bot uptime")
    @app_commands.guild_only()
    async def uptime(self, interaction: discord.Interaction):
        if await check_blist(interaction, self.bot.db): return
        await interaction.response.defer(ephemeral=False)
        uptime = str(datetime.timedelta(seconds=int(round(time.time() - self.bot.start_time))))
        await interaction.followup.send(embed=create_embed(description=f"**Uptime:** `{uptime}`"))

    @app_commands.command(name="about", description="about the bot")
    @app_commands.guild_only()
    async def about(self, interaction: discord.Interaction):
        if await check_blist(interaction, self.bot.db): return
        await interaction.response.defer(ephemeral=False)
        about = await about_embed(self.bot.start_time, self.bot)
        owner = self.bot.get_user(1026388699203772477)
        about.set_author(name="alphast101", icon_url=owner.avatar.url)
        await interaction.followup.send(embed=about, file=discord.File("images/ai.png", filename="ai.png"))


    @app_commands.command(name="help", description="Help/command list")
    @app_commands.guild_only()
    async def help(self, interaction: discord.Interaction):
        if await check_blist(interaction, self.bot.db): return
        await interaction.response.defer(ephemeral=False)

        help_view = View()
        help_view.add_item(help_select)

        help_embbed.set_thumbnail(url=self.bot.user.avatar)
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

    @app_commands.command(name='leaderboard', description="View the credits leaderboard")
    @app_commands.guild_only()
    async def leaderboard(self, interaction: Interaction):
        if await check_blist(interaction, self.bot.db): 
            return
        await interaction.response.defer(ephemeral=False)
        
        try:
            # Get the global cache instance
            cache = CreditsCache()
            
            # Initialize cache if not already done
            if not cache.credits_ranking:
                api_key = getattr(self.bot, 'panel_api_key', None) or "your_api_key_here"
                cache.initialize(api_key)
            
            # Get cached data
            cached_users = cache.get_cached_users()
            time_since_update = cache.get_time_since_update()
            
            if not cached_users:
                # If no cache exists, trigger an update
                await cache.update_cache()
                cached_users = cache.get_cached_users()
                time_since_update = cache.get_time_since_update()
            
            # Create leaderboard view with cached data
            leaderboard_view = cache.create_leaderboard_view(interaction.user.id)
            
            # Create initial embed with update time
            embed = leaderboard_view.create_embed()
            
            # Add last update info to the embed
            if time_since_update < 60:
                update_text = f"Last updated {time_since_update} seconds ago"
            else:
                minutes = time_since_update // 60
                seconds = time_since_update % 60
                if minutes == 1:
                    update_text = f"Last updated 1 minute ago"
                else:
                    update_text = f"Last updated {minutes} minutes ago"
                if seconds > 0:
                    update_text += f" {seconds} seconds ago"
            
            embed.description = f"{embed.description}\n\n📊 {update_text}"
            
            # Send message with view
            message = await interaction.followup.send(embed=embed, view=leaderboard_view)
            leaderboard_view.message = message
            
        except Exception as e:
            await interaction.followup.send(
                embed=create_error_embed(
                    title="Error",
                    description=f"Failed to fetch leaderboard: {str(e)}"
                )
            )

async def setup(bot):
    await bot.add_cog(InformationSlash(bot))