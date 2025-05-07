import re
import asyncio
import discord
import datetime
from discord.ext import commands

def parse_duration(duration_str):
    match = re.match(r"(\d+)([dhm])", duration_str)
    if not match:
        return None
    duration, unit = match.groups()
    duration = int(duration)
    if unit == 'd':
        return datetime.timedelta(days=duration)
    elif unit == 'h':
        return datetime.timedelta(hours=duration)
    elif unit == 'm':
        return datetime.timedelta(minutes=duration)

class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='purge', help='Deletes messages')
    async def purge(self, ctx, amount: int = None):
        if not amount:
            await ctx.reply(embed=discord.Embed(description="Specify how many messages to delete"), mention_author=False)
            return

        if not ctx.author.guild_permissions.manage_messages:
            await ctx.reply(embed=discord.Embed(description="You need message management permissions"))
            return

        if not ctx.channel.permissions_for(ctx.guild.me).manage_messages:
            await ctx.reply(embed=discord.Embed(description="I need message management permissions"))
            return

        if amount < 2:
            await ctx.reply(embed=discord.Embed(description="Delete single messages manually"))
            return

        await ctx.channel.purge(limit=amount + 1)  # +1 includes the command
        await ctx.reply(embed=discord.Embed(description=f"Deleted {amount} messages"), mention_author=False)

    @commands.command(name='kick')
    async def kick(self, ctx, member: discord.Member = None, *, reason: str = "No reason provided"):
        if not member:
            await ctx.reply(embed=discord.Embed(description="Please specify a member to kick"), mention_author=False)
            return

        if member == ctx.guild.owner:
            await ctx.reply(embed=discord.Embed(description="Cannot kick server owner"))
            return
        
        if member == ctx.bot.user:
            await ctx.reply(embed=discord.Embed(description="I cannot kick myself"))
            return

        if not ctx.author.guild_permissions.kick_members:
            await ctx.reply(embed=discord.Embed(description="You lack kick permissions"))
            return

        if not ctx.guild.me.guild_permissions.kick_members:
            await ctx.reply(embed=discord.Embed(description="I lack kick permissions"))
            return

        confirm = await ctx.reply(
            embed=discord.Embed(
                description=f"Kick {member}?\nReason: {reason}\nModerator: {ctx.author}"
            ).set_footer(text="React with ✅ to confirm"),
            mention_author=False
        )

        await confirm.add_reaction('✅')
        await confirm.add_reaction('❌')

        try:
            reaction, _ = await ctx.bot.wait_for(
                'reaction_add',
                timeout=20.0,
                check=lambda r, u: u == ctx.author and str(r.emoji) in ('✅', '❌')
            )
            
            if str(reaction.emoji) == '✅':
                await member.kick(reason=reason)
                await ctx.reply(embed=discord.Embed(description=f"Kicked {member}\nReason: {reason}"))
            else:
                await ctx.reply(embed=discord.Embed(description=f"Canceled kick for {member}"))
                
        except asyncio.TimeoutError:
            await ctx.reply(embed=discord.Embed(description="Kick timed out"))
        except discord.Forbidden:
            await ctx.reply(embed=discord.Embed(description="Missing permissions to kick"))

    @commands.command(name='ban')
    async def ban(self, ctx, member: discord.Member = None, *, reason: str = "No reason provided"):
        if not member:
            await ctx.reply(embed=discord.Embed(description="Please specify a member to ban"), mention_author=False)
            return

        if member == ctx.guild.owner:
            await ctx.reply(embed=discord.Embed(description="Cannot ban server owner"))
            return
        
        if member == ctx.bot.user:
            await ctx.reply(embed=discord.Embed(description="I cannot ban myself"))
            return

        if not ctx.author.guild_permissions.ban_members:
            await ctx.reply(embed=discord.Embed(description="You lack ban permissions"))
            return

        if not ctx.guild.me.guild_permissions.ban_members:
            await ctx.reply(embed=discord.Embed(description="I lack ban permissions"))
            return

        confirm = await ctx.reply(
            embed=discord.Embed(
                description=f"Ban {member}?\nReason: {reason}\nModerator: {ctx.author}"
            ).set_footer(text="React with ✅ to confirm")
        )
        
        await confirm.add_reaction('✅')
        await confirm.add_reaction('❌')

        try:
            reaction, _ = await ctx.bot.wait_for(
                'reaction_add',
                timeout=20.0,
                check=lambda r, u: u == ctx.author and str(r.emoji) in ('✅', '❌')
            )
            
            if str(reaction.emoji) == '✅':
                await member.ban(reason=reason)
                await ctx.reply(embed=discord.Embed(description=f"Banned {member}\nReason: {reason}"))
            else:
                await ctx.reply(embed=discord.Embed(description=f"Canceled ban for {member}"))
                
        except asyncio.TimeoutError:
            await ctx.reply(embed=discord.Embed(description="Ban timed out"))
        except discord.Forbidden:
            await ctx.reply(embed=discord.Embed(description="Missing permissions to ban"))


    @commands.command(name='unban')
    async def unban(self, ctx, user: discord.User, *, reason="No reason"):

        if not ctx.author.guild_permissions.ban_members:
            await ctx.reply(embed=discord.Embed(description="You need ban permissions"), mention_author=False)
            return

        if not ctx.guild.me.guild_permissions.ban_members:
            await ctx.reply(embed=discord.Embed(description="I need ban permissions"))
            return

        bans = [ban_entry async for ban_entry in ctx.guild.bans()]
        if user not in [ban.user for ban in bans]:
            await ctx.reply(embed=discord.Embed(description=f"{user} is not banned"))
            return

        confirm = await ctx.reply(
            embed=discord.Embed(description=f"Unban {user}?\nReason: {reason}\nModerator: {ctx.author}").set_footer(text="React ✅ to confirm"),
            mention_author=False
        )
        
        await confirm.add_reaction('✅')
        await confirm.add_reaction('❌')

        try:
            reaction, _ = await ctx.bot.wait_for(
                'reaction_add',
                timeout=20.0,
                check=lambda r, u: u == ctx.author and str(r.emoji) in ('✅', '❌')
            )
            
            if str(reaction.emoji) == '✅':
                await ctx.guild.unban(user, reason=reason)
                await ctx.reply(embed=discord.Embed(description=f"Unbanned {user}\nReason: {reason}"))
            elif str(reaction.emoji) == '❌':
                await ctx.reply(embed=discord.Embed(description=f"Canceled unban for {user}"))
                
        except asyncio.TimeoutError:
            await ctx.reply(embed=discord.Embed(description="Unban timed out"))
        except discord.Forbidden:
            await ctx.reply(embed=discord.Embed(description="Missing unban permissions"))

    @commands.command(name='timeout')
    async def timeout(self, ctx, member: discord.Member = None, duration: str = None, *, reason: str = "No reason"):

        if not member or not duration:
            await ctx.reply(embed=discord.Embed(description="Specify member and duration (e.g. 30m)"), mention_author=False)
            return

        if member.top_role >= ctx.author.top_role:
            await ctx.reply(embed=discord.Embed(description="Cannot timeout this member"))
            return

        time_delta = parse_duration(duration)
        if not time_delta:
            await ctx.reply(embed=discord.Embed(description="Invalid duration (use 1d, 2h, 30m)"))
            return

        confirm = await ctx.reply(
            embed=discord.Embed(description=f"Timeout {member} for {duration}?\nReason: {reason}").set_footer(text="React ✅ to confirm"),
            mention_author=False
        )
        
        await confirm.add_reaction('✅')
        await confirm.add_reaction('❌')

        try:
            reaction, _ = await ctx.bot.wait_for(
                'reaction_add',
                timeout=20.0,
                check=lambda r, u: u == ctx.author and str(r.emoji) in ('✅', '❌')
            )
            
            if str(reaction.emoji) == '✅':
                await member.edit(timed_out_until=discord.utils.utcnow() + time_delta)
                await ctx.reply(embed=discord.Embed(description=f"Timed out {member} for {duration}"))
            elif str(reaction.emoji) == '❌':
                await ctx.reply(embed=discord.Embed(description=f"Canceled timeout for {member}"))
                
        except asyncio.TimeoutError:
            await ctx.reply(embed=discord.Embed(description="Timeout timed out"))
        except discord.Forbidden:
            await ctx.reply(embed=discord.Embed(description="Missing timeout permissions"))

    @commands.command(name='unmute')
    async def unmute(self, ctx, member: discord.Member = None, *, reason: str = "No reason"):

        if not member:
            await ctx.reply(embed=discord.Embed(description="Specify member to unmute"), mention_author=False)
            return

        if member.timed_out_until is None:
            await ctx.reply(embed=discord.Embed(description=f"{member} is not muted"))
            return

        confirm = await ctx.reply(
            embed=discord.Embed(description=f"Unmute {member}?\nReason: {reason}").set_footer(text="React ✅ to confirm"),
            mention_author=False
        )

        await confirm.add_reaction('✅')
        await confirm.add_reaction('❌')

        try:
            reaction, _ = await ctx.bot.wait_for(
                'reaction_add',
                timeout=20.0,
                check=lambda r, u: u == ctx.author and str(r.emoji) in ('✅', '❌')
            )
            
            if str(reaction.emoji) == '✅':
                await member.edit(timed_out_until=None)
                await ctx.reply(embed=discord.Embed(description=f"Unmuted {member}"))
            elif str(reaction.emoji) == '❌':
                await ctx.reply(embed=discord.Embed(description=f"Canceled unmute for {member}"))
                
        except asyncio.TimeoutError:
            await ctx.reply(embed=discord.Embed(description="Unmute timed out"))
        except discord.Forbidden:
            await ctx.reply(embed=discord.Embed(description="Missing unmute permissions"))

    @commands.command(name='purgelinks')
    async def purge_links(self, ctx, limit: int = None):
        if not limit:
            await ctx.reply(embed=discord.Embed(description="Specify number of messages to check"), mention_author=False)
            return

        def is_link(m):
            return 'http://' in m.content or 'https://' in m.content

        confirm = await ctx.reply(
            embed=discord.Embed(description=f"Delete {limit} messages with links?").set_footer(text="React ✅ to confirm"),
            mention_author=False
        )
        
        await confirm.add_reaction('✅')
        await confirm.add_reaction('❌')

        try:
            reaction, _ = await ctx.bot.wait_for(
                'reaction_add',
                timeout=20.0,
                check=lambda r, u: u == ctx.author and str(r.emoji) in ('✅', '❌')
            )
            
            if str(reaction.emoji) == '✅':
                deleted = await ctx.channel.purge(limit=limit, check=is_link)
                await ctx.reply(embed=discord.Embed(description=f"Deleted {len(deleted)} messages with links"))
            elif str(reaction.emoji) == '❌':
                await ctx.reply(embed=discord.Embed(description="Canceled link purge"))
                
        except asyncio.TimeoutError:
            await ctx.reply(embed=discord.Embed(description="Purge timed out"))
        except discord.Forbidden:
            await ctx.reply(embed=discord.Embed(description="Missing purge permissions"))

    @commands.command(name='purgefiles')
    async def purge_files(self, ctx, limit: int = None):
        if not limit:
            await ctx.reply(embed=discord.Embed(description="Specify number of messages to check"), mention_author=False)
            return

        def has_files(m):
            return bool(m.attachments)

        confirm = await ctx.reply(
            embed=discord.Embed(description=f"Delete {limit} messages with files?").set_footer(text="React ✅ to confirm"),
            mention_author=False
        )
        
        await confirm.add_reaction('✅')
        await confirm.add_reaction('❌')

        try:
            reaction, _ = await ctx.bot.wait_for(
                'reaction_add',
                timeout=20.0,
                check=lambda r, u: u == ctx.author and str(r.emoji) in ('✅', '❌')
            )
            
            if str(reaction.emoji) == '✅':
                deleted = await ctx.channel.purge(limit=limit, check=has_files)
                await ctx.reply(embed=discord.Embed(description=f"Deleted {len(deleted)} messages with files"))
            elif str(reaction.emoji) == '❌':
                await ctx.reply(embed=discord.Embed(description="Canceled file purge"))
                
        except asyncio.TimeoutError:
            await ctx.reply(embed=discord.Embed(description="Purge timed out"))
        except discord.Forbidden:
            await ctx.reply(embed=discord.Embed(description="Missing purge permissions"))


async def setup(bot):
    await bot.add_cog(Moderation(bot))