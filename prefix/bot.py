import io
import time
import discord
import datetime
import contextlib
from discord.ui import Button
from discord.ext import commands
from bot_utilities.help_embed import *
from bot_utilities.owner_utils import *
from bot_utilities.about_embed import about_embed

def bbot(bot, start_time, mongodb):

    @bot.command(name="server")
    async def list_guilds(ctx):
        """Lists all the guilds the bot is in along with their IDs."""
        guilds = ctx.bot.guilds
        per_page = 15  # Number of guilds to display per page
        total_pages = (len(guilds) + per_page - 1) // per_page  # Calculate total pages
        pages = []
        for i in range(0, len(guilds), per_page):
            page = "\n".join([f"{guild.name} - `{guild.id}`" for guild in guilds[i:i + per_page]])
            pages.append(page)
        current_page = 0

        async def update_message(interaction):
            embed = discord.Embed(title="Guilds List", color=discord.Color.blue())
            embed.description = pages[current_page]
            embed.set_footer(text=f"Page {current_page + 1}/{total_pages}")

            # Disable buttons as needed
            previous_button.disabled = current_page == 0
            next_button.disabled = current_page == total_pages - 1

            await interaction.response.defer()
            await interaction.message.edit(embed=embed, view=view)

        async def previous_callback(interaction):
            nonlocal current_page
            if current_page > 0:
                current_page -= 1
                await update_message(interaction)

        async def next_callback(interaction):
            nonlocal current_page
            if current_page < len(pages) - 1:
                current_page += 1
                await update_message(interaction)

        async def stop_callback(interaction):
            await paginator_message.edit(embed=initial_embed, view=None)
            view.stop()

        async def on_timeout():
            await paginator_message.edit(embed=initial_embed, view=None)
            view.stop()

        initial_embed = discord.Embed(title="Guilds List", color=discord.Color.blue())
        initial_embed.description = pages[current_page]
        initial_embed.set_footer(text=f"Page {current_page + 1}/{total_pages}")

        previous_button = discord.ui.Button(label="⬅️", style=discord.ButtonStyle.primary)
        next_button = discord.ui.Button(label="➡️", style=discord.ButtonStyle.primary)
        stop_button = discord.ui.Button(label="❌", style=discord.ButtonStyle.danger)

        view = discord.ui.View(timeout=20)
        view.add_item(previous_button)
        view.add_item(next_button)
        view.add_item(stop_button)

        # Disable buttons initially for first page
        previous_button.disabled = True
        paginator_message = await ctx.send(embed=initial_embed, view=view)

        previous_button.callback = previous_callback
        next_button.callback = next_callback
        stop_button.callback = stop_callback

        view.timeout_callback = on_timeout


    @bot.command(name="say")
    async def m(ctx, *, message: str = None):
		# 1026388699203772477 - alphast101
		# 973461136680845382 - wqypp
        # 885977942776246293 -jeydalio
        if message is None:
            return
        allowed = [973461136680845382, 1026388699203772477, 885977942776246293]
        if ctx.author.id in allowed:
            bot_member = ctx.guild.me
            if bot_member.guild_permissions.manage_messages:
                await ctx.message.delete()
                await ctx.send(message)
            else:
                await ctx.send(message)
        else:
            await ctx.send("**This command is restricted**", delete_after=3)

    @bot.command(name="mp")
    async def mp(ctx,*,message):
        if ctx.author.id == 1026388699203772477:
            print(message)
            await ctx.message.delete()
            await ctx.send(message)

    @bot.command(name="sync")
    async def sync(ctx):
        if ctx.author.id == 1026388699203772477:
            await ctx.send("**<@1026388699203772477> Syncing slash commands...**")
            await bot.tree.sync()
            await ctx.send("**<@1026388699203772477> Slash commands synced!**")


    @bot.command(name="blist")
    async def blist(ctx, object, id = None):
        if ctx.author.id != 1026388699203772477:
            return

        try:
            id = int(id)
        except TypeError:
            await ctx.send("Invalid Command or ID")
            return

        if object == "server":
            guild = bot.get_guild(id)
            if guild:
                insert = await insertdb('blist-servers', id, mongodb)
                await ctx.send(f"**{guild} is {insert}.**")
            else:
                await ctx.send(f"**Guild not found, `{guild}`**")

        elif object == 'user':
            user = bot.get_user(id)
            if user:
                insert = await insertdb('blist-users', id, mongodb)
                await ctx.send(f"**{user} is {insert}**")
            else:
                await ctx.send(f"**User not found, `{user}`**")
        else:
            await ctx.send(f"Invalid object")

    @bot.command(name="unblist")
    async def unblist(ctx, object, id = None):
        if ctx.author.id != 1026388699203772477: return

        try: id = int(id)
        except TypeError:
            await ctx.send("> **Invalid Command or ID**")
            return

        if object == "server":
            guild = bot.get_guild(id)
            if guild:
                insert = await deletedb('blist-servers', id, mongodb)
                await ctx.send(f"**{guild} is {insert}.**")
            else:
                await ctx.send(f"**Guild not found, `{guild}`**")

        elif object == 'user':
            user = bot.get_user(id)
            if user:
                insert = await deletedb('blist-users', id, mongodb)
                await ctx.send(f"**{user} is {insert}**")
            else:
                await ctx.send(f"**User not found, `{user}`**")
        else:
            await ctx.send(f"> **Invalid object**")


    @bot.command(name="eval")
    async def eval(ctx, *, code: str):

        if ctx.author.id == 1026388699203772477:
            # Remove backticks from the code block
            code = code.strip('` ')
            # Check if the code is in a python code block
            if code.startswith('python'):
                code = code[6:]
            code = '\n'.join(f'    {i}' for i in code.splitlines())

            # Prepare the environment for the code execution
            local_variables = {
                "discord": discord,
                "commands": commands,
                "bot": bot,
                "ctx": ctx,
                "__import__": __import__
            }

            # Prepare stdout to capture output
            stdout = io.StringIO()

            # Define the wrapped exec
            def wrapped_exec():
                try:
                    exec(f"async def func():\n{code}", local_variables)
                except Exception as e:
                    stdout.write(f"{type(e).__name__}: {e}")

            # Capture the output of the exec
            with contextlib.redirect_stdout(stdout):
                wrapped_exec()
                if 'func' in local_variables:
                    func = local_variables['func']
                    try:
                        await func()
                    except Exception as e:
                        stdout.write(f"{type(e).__name__}: {e}")

            # Send the output back to the Discord channel
            await ctx.send(f'{stdout.getvalue()}')
        else:
            return
    @bot.command(name="cmd")
    async def cmdd(ctx):
        cmd_list = []
        for command in bot.commands:
            cmd_prefix = "ai." + command.name
            cmd_list.append(cmd_prefix)
        if ctx.author.id == 1026388699203772477: await ctx.send("\n".join(cmd_list))


    @bot.command(name="ping")
    async def ping(ctx):
        wait = await ctx.send("**Please wait while I calculate my latency.**")
        latency_ms = round(bot.latency * 1000)
        await wait.edit(content=f'**Pong! My Latency is `{latency_ms}ms`.**')

    @bot.command(name="uptime")
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def uptime(ctx):
        current_time = time.time()
        difference = int(round(current_time - start_time))
        uptime_duration = datetime.timedelta(seconds=difference)

        embed = discord.Embed(colour=0xc8dc6c)
        embed.add_field(name="LuminaryAI - Uptime", value=str(uptime_duration))
        await ctx.send(embed=embed)

    @bot.command(name='about')
    @commands.cooldown(1, 30, commands.BucketType.user)
    async def about(ctx):
        about = await about_embed(start_time, bot)
        owner = bot.get_user(1026388699203772477)
        about.set_author(name="alphast101", icon_url=owner.avatar.url)
        await ctx.send(embed=about, file=discord.File("images/ai.png", filename="ai.png"))


    @bot.command(name="help")
    @commands.cooldown(1, 60, commands.BucketType.user)
    async def help_ctx(ctx):
        help_view = View()
        help_view.add_item(help_select)

        help_embbed.set_thumbnail(url=bot.user.avatar)
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