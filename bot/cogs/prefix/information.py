import datetime
import time

import discord
from discord.ext import commands
from discord.ui import Button, View

from bot import config
from bot.utils.about import about_embed
from bot.utils.embeds import create_embed
from bot.utils.help import (
    admin_commands,
    ai_commands,
    automod_commands,
    embed_admin,
    embed_ai,
    embed_automod,
    embed_fun,
    embed_info,
    embed_moderation,
    embed_music,
    fun_commands,
    get_chunk,
    help_embed,
    help_select,
    information_commands,
    moderation_commands,
    music_commands,
)


class Information(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="support")
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def support(self, ctx):

        await ctx.reply(
            embed=create_embed(description=f"**Support server:** [here]({config.SUPPORT_SERVER_URL})"),
            mention_author=False,
        )

    @commands.command(name="owner")
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def owner(self, ctx):

        await ctx.reply(
            embed=create_embed(description=f"My owner is [{config.OWNER_NAME}]({config.OWNER_URL})"),
            mention_author=False,
        )

    @commands.command(name="ping")
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def ping(self, ctx):

        await ctx.reply(
            embed=create_embed(description=f"**Latency:** `{round(self.bot.latency * 1000)}ms`"),
            mention_author=False,
        )

    @commands.command(name="uptime")
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def uptime(self, ctx):

        uptime = str(datetime.timedelta(seconds=int(round(time.time() - self.bot.start_time))))
        await ctx.reply(embed=create_embed(description=f"**Uptime:** `{uptime}`"), mention_author=False)

    @commands.command(name="about")
    @commands.cooldown(1, 30, commands.BucketType.user)
    async def about(self, ctx):

        embed = await about_embed(self.bot.start_time, self.bot)
        await ctx.reply(
            embed=embed,
            file=discord.File(str(config.AI_IMAGE_PATH), filename="ai.png"),
            mention_author=False,
        )

    @commands.command(name="userinfo")
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def user(self, ctx, user_mention: discord.Member = None):


        if user_mention is None:
            user_mention = ctx.author

        roles = [role.mention for role in user_mention.roles if role != ctx.guild.default_role]
        roles_string = ", ".join(roles) if roles else "No roles"

        permissions = ctx.channel.permissions_for(user_mention)
        permissions_string = ", ".join([perm.replace("_", " ").title() for perm, value in permissions if value])

        embed = create_embed(
            title=f"Username: {user_mention}",
            description=(
                f"UserID: `{user_mention.id}`\n"
                f"Joined the server: <t:{int(user_mention.joined_at.timestamp())}:R>\n"
                f"Joined Discord: <t:{int(user_mention.created_at.timestamp())}:R>\n\n"
                "**User's Roles:**\n"
                f"{roles_string}\n\n"
                "**Channel Permissions:**\n"
                f"{permissions_string}"
            ),
        )
        if user_mention.avatar:
            embed.set_thumbnail(url=user_mention.avatar.url)
        await ctx.reply(embed=embed, mention_author=False)

    @commands.command(name="help")
    @commands.cooldown(1, 60, commands.BucketType.user)
    async def help_ctx(self, ctx):


        help_view = View()
        help_view.add_item(help_select)

        help_embed.set_thumbnail(url=self.bot.user.avatar)
        help_msg = await ctx.reply(embed=help_embed, view=help_view, mention_author=False)

        buttons = [
            Button(label="Previous", style=discord.ButtonStyle.primary, custom_id="Previous"),
            Button(label="Next", style=discord.ButtonStyle.primary, custom_id="Next"),
        ]

        help_view.add_item(buttons[0])
        help_view.add_item(buttons[1])

        current_page = 0
        current_commands = information_commands
        embed = embed_info

        async def help_callback(interaction):
            nonlocal current_page, current_commands, embed

            if help_select.values[0] == "Information":
                current_commands = information_commands
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

            current_page = 0
            embed = get_chunk(embed, current_commands, current_page * 5)
            await interaction.response.defer()
            await help_msg.edit(embed=embed, view=help_view)

        help_select.callback = help_callback

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


async def setup(bot):
    await bot.add_cog(Information(bot))
