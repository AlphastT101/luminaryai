import discord
from discord.ext import commands
from bot_utilities.owner_utils import *

class Owner(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="server")
    async def list_guilds(self, ctx):
        if ctx.author.id != 1026388699203772477: return

        guilds = ctx.bot.guilds
        per_page = 20  # Number of guilds to display per page
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


    @commands.command(name="say")
    async def say(self, ctx, *, message: str = None):
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

    @commands.command(name="mp")
    async def mp(self, ctx,*,message):
        if ctx.author.id == 1026388699203772477:
            print(message)
            await ctx.message.delete()
            await ctx.send(message)

    @commands.command(name="sync")
    async def sync(self, ctx):
        if ctx.author.id == 1026388699203772477:
            await ctx.send("**<@1026388699203772477> Syncing slash commands...**")
            await self.bot.tree.sync()
            await ctx.send("**<@1026388699203772477> Slash commands synced!**")

    @commands.command(name="blist")
    async def blist(self, ctx, object, id = None):
        if ctx.author.id != 1026388699203772477: return

        try:
            id = int(id)
        except TypeError:
            await ctx.send("Invalid Command or ID")
            return

        if object == "server":
            guild = self.bot.get_guild(id)
            if guild:
                insert = await insertdb('blist-servers', id, self.bot.db)
                await ctx.send(f"**{guild} is {insert}.**")
            else:
                await ctx.send(f"**Guild not found, `{guild}`**")

        elif object == 'user':
            user = self.bot.get_user(id)
            if user:
                insert = await insertdb('blist-users', id, self.bot.db)
                await ctx.send(f"**{user} is {insert}**")
            else:
                await ctx.send(f"**User not found, `{user}`**")
        else:
            await ctx.send(f"Invalid object")

    @commands.command(name="unblist")
    async def unblist(self, ctx, object, id = None):
        if ctx.author.id != 1026388699203772477: return

        try: id = int(id)
        except TypeError:
            await ctx.send("> **Invalid Command or ID**")
            return

        if object == "server":
            guild = self.bot.get_guild(id)
            if guild:
                insert = await deletedb('blist-servers', id, self.bot.db)
                await ctx.send(f"**{guild} is {insert}.**")
            else:
                await ctx.send(f"**Guild not found, `{guild}`**")

        elif object == 'user':
            user = self.bot.get_user(id)
            if user:
                insert = await deletedb('blist-users', id, self.bot.db)
                await ctx.send(f"**{user} is {insert}**")
            else:
                await ctx.send(f"**User not found, `{user}`**")
        else:
            await ctx.send(f"> **Invalid object**")


    @commands.command(name="eval")
    async def eval(self, ctx, *, code: str):
        if not ctx.author.id == 1026388699203772477: return

        code = code.strip('` ')
        if code.startswith('python'):
            code = code[6:]
        code = '\n'.join(f'    {i}' for i in code.splitlines())
        local_variables = {
            "discord": discord,
            "commands": commands,
            "bot": self.bot,
            "ctx": ctx,
            "__import__": __import__
        }

        stdout = self.bot.modules_io.StringIO()
        def wrapped_exec():
            try:
                exec(f"async def func():\n{code}", local_variables)
            except Exception as e:
                stdout.write(f"{type(e).__name__}: {e}")
        with self.bot.modules_contextlib.redirect_stdout(stdout):
            wrapped_exec()
            if 'func' in local_variables:
                func = local_variables['func']
                try:
                    await func()
                except Exception as e:
                    stdout.write(f"{type(e).__name__}: {e}")
        await ctx.send(f'{stdout.getvalue()}')

    @commands.command(name="cmd")
    async def cmdd(self, ctx):
        if not ctx.author.id == 1026388699203772477: return
        cmd_list = []
        for command in self.bot.commands:
            cmd_prefix = "ai." + command.name
            cmd_list.append(cmd_prefix)
        await ctx.send("\n".join(cmd_list))


async def setup(bot):
    await bot.add_cog(Owner(bot))