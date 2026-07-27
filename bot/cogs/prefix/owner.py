import contextlib
import io

import discord
from discord.ext import commands

from bot import config
from bot.utils.embeds import create_embed


class Owner(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="server")
    @commands.is_owner()
    async def list_guilds(self, ctx):
        guilds = ctx.bot.guilds
        per_page = 20
        total_pages = (len(guilds) + per_page - 1) // per_page
        pages = []
        for i in range(0, len(guilds), per_page):
            page = "\n".join([f"{guild.name} - `{guild.id}`" for guild in guilds[i : i + per_page]])
            pages.append(page)
        current_page = 0

        async def update_message(interaction):
            embed = create_embed(title="Guilds List")
            embed.description = pages[current_page]
            embed.set_footer(text=f"Page {current_page + 1}/{total_pages}")
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

        initial_embed = create_embed(title="Guilds List")
        initial_embed.description = pages[current_page]
        initial_embed.set_footer(text=f"Page {current_page + 1}/{total_pages}")

        previous_button = discord.ui.Button(label="⬅️", style=discord.ButtonStyle.primary)
        next_button = discord.ui.Button(label="➡️", style=discord.ButtonStyle.primary)
        stop_button = discord.ui.Button(label="❌", style=discord.ButtonStyle.danger)

        view = discord.ui.View(timeout=20)
        view.add_item(previous_button)
        view.add_item(next_button)
        view.add_item(stop_button)

        previous_button.disabled = True
        paginator_message = await ctx.send(embed=initial_embed, view=view)

        previous_button.callback = previous_callback
        next_button.callback = next_callback
        stop_button.callback = stop_callback
        view.timeout_callback = on_timeout

    @commands.command(name="say")
    async def say(self, ctx, *, message: str = None):
        if message is None:
            return
        allowed = [973461136680845382, 1026388699203772477, 885977942776246293]
        if ctx.author.id in allowed:
            permissions = ctx.channel.permissions_for(ctx.guild.me)
            if permissions.manage_messages:
                await ctx.message.delete()
            await ctx.send(message)

    @commands.command(name="mp")
    @commands.is_owner()
    async def mp(self, ctx, *, message):
        print(message)
        await ctx.message.delete()
        await ctx.send(message)

    @commands.command(name="sync")
    @commands.is_owner()
    async def sync(self, ctx):
        await ctx.send("Syncing slash commands...")
        await self.bot.tree.sync()
        await ctx.send("Slash commands synced.")

    @commands.command(name="eval")
    @commands.is_owner()
    async def eval(self, ctx, *, code: str):
        code = code.strip("` ")
        if code.startswith("python"):
            code = code[6:]
        code = "\n".join(f"    {i}" for i in code.splitlines())
        local_variables = {
            "discord": discord,
            "commands": commands,
            "bot": self.bot,
            "ctx": ctx,
            "__import__": __import__,
        }

        stdout = io.StringIO()

        def wrapped_exec():
            try:
                exec(f"async def func():\n{code}", local_variables)
            except Exception as e:
                stdout.write(f"{type(e).__name__}: {e}")

        with contextlib.redirect_stdout(stdout):
            wrapped_exec()
            if "func" in local_variables:
                func = local_variables["func"]
                try:
                    await func()
                except Exception as e:
                    stdout.write(f"{type(e).__name__}: {e}")
        await ctx.send(f"{stdout.getvalue()}")

    @commands.command(name="cmd")
    @commands.is_owner()
    async def cmdd(self, ctx):
        cmd_list = []
        for command in self.bot.commands:
            cmd_prefix = config.BOT_PREFIX + command.name
            cmd_list.append(cmd_prefix)
        await ctx.send("\n".join(cmd_list))


async def setup(bot):
    await bot.add_cog(Owner(bot))
