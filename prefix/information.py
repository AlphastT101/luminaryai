import time
import datetime
from discord.ext import commands
from discord.ui import Button, View
from bot_utilities.help_embed import *
from bot_utilities.about_embed import about_embed
from bot_utilities.owner_utils import check_blist_msg

class Information(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='support')
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def support(self, ctx):
        if await check_blist_msg(ctx, self.bot.db): return
        await ctx.reply(embed=discord.Embed(description="**Support server:** [here](https://discord.com/invite/hmMBe8YyJ4)"), mention_author=False)

    @commands.command(name='owner')
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def owner(self, ctx):
        if await check_blist_msg(ctx, self.bot.db): return
        await ctx.reply(embed=discord.Embed(description="My owner is [AlphasT101](https://owner.xet.one)"), mention_author=False)
        
    @commands.command(name="ping")
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def ping(self, ctx):
        if await check_blist_msg(ctx, self.bot.db): return
        await ctx.reply(embed=discord.Embed(description=f"**Latency:** `{round(self.bot.latency * 1000)}ms`"), mention_author=False)

    @commands.command(name="uptime")
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def uptime(self, ctx):
        if await check_blist_msg(ctx, self.bot.db): return
        uptime = str(datetime.timedelta(seconds=int(round(time.time() - self.bot.start_time))))
        await ctx.reply(embed=discord.Embed(description=f"**Uptime:** `{uptime}`"), mention_author=False)

    @commands.command(name='about')
    @commands.cooldown(1, 30, commands.BucketType.user)
    async def about(self, ctx):
        if await check_blist_msg(ctx, self.bot.db): return
        embed = await about_embed(self.bot.start_time, self.bot)
        await ctx.reply(embed=embed, file=discord.File("images/ai.png", filename="ai.png"), mention_author=False)

    @commands.command(name='userinfo')
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def user(self, ctx, user_mention: discord.Member = None):
        if await check_blist_msg(ctx, self.bot.db): return

        if user_mention is None:
            user_mention = ctx.author

        roles = [role.mention for role in user_mention.roles if role != ctx.guild.default_role]
        roles_string = ", ".join(roles) if roles else "No roles"

        permissions = ctx.channel.permissions_for(user_mention)
        permissions_string = ", ".join([perm.replace('_', ' ').title() for perm, value in permissions if value])

        embed = discord.Embed(
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
            color=0x99ccff
        )
        embed.set_thumbnail(url=user_mention.avatar.url)
        await ctx.reply(embed=embed, mention_author=False)

    @commands.command(name="help")
    @commands.cooldown(1, 60, commands.BucketType.user)
    async def help_ctx(self, ctx):
        if await check_blist_msg(ctx, self.bot.db): return

        help_view = View()
        help_view.add_item(help_select)

        help_embbed.set_thumbnail(url=self.bot.user.avatar)
        help_msg = await ctx.reply(embed=help_embbed, view=help_view, mention_author=False)

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

async def setup(bot):
    await bot.add_cog(Information(bot))