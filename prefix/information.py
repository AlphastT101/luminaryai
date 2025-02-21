from discord.ext import commands
from discord.ui import Button, View
from bot_utilities.help_embed import *

class Information(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='support')
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def support(self, ctx):
        await ctx.send("> **Support server invite link:** [here](https://discord.com/invite/hmMBe8YyJ4)")

    @commands.command(name='owner')
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def owner(self, ctx):
        await ctx.send("> **My owner is:** [AlphasT101](https://owner.xet.one)")
    
    @commands.command(name="ping")
    async def ping(self, ctx):
        latency_ms = round(self.bot.latency * 1000)
        await ctx.send(content=f'**Latency: `{latency_ms}ms`.**')

    @commands.command(name="uptime")
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def uptime(self, ctx):
        current_time = self.bot.modules_time.time()
        difference = int(round(current_time - self.bot.start_time))
        uptime_duration = self.bot.modules_datetime.timedelta(seconds=difference)

        embed = discord.Embed(colour=0xc8dc6c)
        embed.add_field(name="LuminaryAI - Uptime", value=str(uptime_duration))
        await ctx.send(embed=embed)

    @commands.command(name='about')
    @commands.cooldown(1, 30, commands.BucketType.user)
    async def about(self, ctx):
        about = await self.bot.about_embed(self.bot.start_time, self.bot)
        owner = self.bot.get_user(1026388699203772477)
        about.set_author(name="alphast101", icon_url=owner.avatar.url)
        await ctx.send(embed=about, file=discord.File("images/ai.png", filename="ai.png"))

    @commands.command(name='userinfo')
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def user(self, ctx, user_mention: discord.Member = None):

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
        await ctx.send(embed=embed)

    @commands.command(name="help")
    @commands.cooldown(1, 60, commands.BucketType.user)
    async def help_ctx(self, ctx):
        help_view = View()
        help_view.add_item(help_select)

        help_embbed.set_thumbnail(url=self.bot.user.avatar)
        help_msg = await ctx.send(embed=help_embbed, view=help_view)

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