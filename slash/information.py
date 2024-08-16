import discord
from discord import app_commands
from discord.ext import commands
from bot_utilities.owner_utils import *

def information_slash(bot, mongodb):

    @bot.tree.command(name='userinfo', description="View information about a user")
    @commands.guild_only()
    @app_commands.describe(user="Select a user.")
    async def user(interaction: discord.Interaction, user: discord.Member = None):

        if await check_blist(interaction, mongodb): return
        await interaction.response.defer(ephemeral=False)

        if user is None:
            user = interaction.user

        roles = [role.mention for role in user.roles if role != interaction.guild.default_role]
        roles_string = ", ".join(roles) if roles else "No roles"

        permissions = interaction.channel.permissions_for(user)
        permissions_string = ", ".join([perm.replace('_', ' ').title() for perm, value in permissions if value])

        embed = discord.Embed(
            title=f"Username: {user}",
            description=(
                f"UserID: `{user.id}`\n"
                f"Joined the server: <t:{int(user.joined_at.timestamp())}:R>\n"
                f"Joined Discord: <t:{int(user.created_at.timestamp())}:R>\n\n"
                "**User's Roles:**\n"
                f"{roles_string}\n\n"
                "**Channel Permissions:**\n"
                f"{permissions_string}"
            ),
            color=0x99ccff
        )

        embed.set_thumbnail(url=user.avatar.url)
        await interaction.followup.send(embed=embed)


    @bot.tree.command(name='support', description="Shows support server invite link")
    async def support(interaction: discord.Interaction):
        if await check_blist(interaction, mongodb): return
        await interaction.response.send_message("> **Support server invite link:** [here](https://discord.com/invite/hmMBe8YyJ4)")

    @bot.tree.command(name='owner', description="Shows bot owner")
    async def owner(interaction: discord.Interaction):
        if await check_blist(interaction, mongodb): return
        await interaction.response.send_message("> **My owner is:** [AlphasT101](https://alphast101.netlify.app)")