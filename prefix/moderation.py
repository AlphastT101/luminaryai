import discord
from discord.ext import commands

def parse_duration(duration_str, bot):
    match = bot.modules_re.match(r"(\d+)([dhm])", duration_str)
    if not match:
        return None
    duration, unit = match.groups()
    duration = int(duration)
    if unit == 'd':
        return bot.modules_datetime.timedelta(days=duration)
    elif unit == 'h':
        return bot.modules_datime.timedelta(hours=duration)
    elif unit == 'm':
        return bot.modules_datetime.timedelta(minutes=duration)

class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='purge', help='Deletes a specified number of messages')
    @commands.cooldown(1, 15, commands.BucketType.user)
    async def purge(self, ctx, num_messages: str = None):
        channel = ctx.channel
        if num_messages is None:
            await ctx.send("**Please provide a number of messages to purge!**")
            return
        if ctx.author.guild_permissions.manage_messages:
            if channel.permissions_for(channel.guild.me).manage_messages:
                try:
                    num_messages_int = int(num_messages)  # Convert the string to an integer
                    if num_messages_int < 1:
                        await ctx.send(f"**How can I delete {num_messages_int} messages?**", delete_after=3)
                    if num_messages_int == 1:
                        await ctx.send("**If you want to delete just one message, then please do this manually.**", delete_after=3)
                    else:
                        await ctx.channel.purge(limit=num_messages_int + 1)  # +1 to include the command message
                        await ctx.send(embed=self.bot.modules_discord.Embed(title=f"**Successfully purged {num_messages_int} messages**"), delete_after=3)
                except ValueError:
                    await ctx.send("**Invalid input. Please provide a valid number of messages.**", delete_after=3)
            else:
                await ctx.send("**I don't have the necessary permission in this channel to perform this action!**", delete_after=3)
        else:
            await ctx.send("**You do not have the necessary permissions to perform this action!**", delete_after=3)

    @commands.command(name='kick')
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def kick(self, ctx, member: discord.Member = None, *, reason: str = "No reason provided"):
        if member is None:
            await ctx.send(embed=discord.Embed(description="**Please provide a valid Discord member to kick.**",colour=0xFF0000), delete_after=10)
            return

        if member == ctx.guild.owner:
            await ctx.send(embed=discord.Embed(description="**I cannot kick the server owner**.",colour=0xFF0000))
            return
        if member == ctx.bot.user:
            await ctx.send(embed=discord.Embed(description="**I can't kick myself!**",colour=0xFF0000))
            return

        if not ctx.author.guild_permissions.kick_members:
            await ctx.send(embed=discord.Embed(description="**You do not have the necessary permissions to perform this action.**",colour=0xFF0000))
            return

        if not ctx.guild.me.guild_permissions.kick_members:
            await ctx.send(embed=discord.Embed(description="**I don't have the necessary permission in this channel to perform this action.**",colour=0xFF0000))
            return

        try:

            confirm_msg = await ctx.send(embed=discord.Embed(title="LuminaryAI - confirmation",description=f"**Are you sure you want to kick this member?**\n**Member: `{member}`**\n**Reason: `{reason}`**\n**Moderator: {ctx.author}**", color=0xc8dc6c))

            await confirm_msg.add_reaction('✅')
            await confirm_msg.add_reaction('❌')

            def check(reaction, user):
                return user == ctx.author and str(reaction.emoji) in ['✅', '❌']

            reaction, user = await ctx.bot.wait_for('reaction_add', timeout=20.0, check=check)
            
            if str(reaction.emoji) == '✅':
                await member.kick(reason=reason)
                await confirm_msg.delete()
                await ctx.send(embed=discord.Embed(description=f"**Member {member} has been kicked.**\n**Reason: `{reason}`**\n**Moderator: `{ctx.author}`**",colour=0xc8dc6c))

            elif str(reaction.emoji) == '❌':
                await confirm_msg.delete()
                await ctx.send(embed=discord.Embed(description="**Action cancelled.**\n`{member}` has not been kicked.",colour=0xc8dc6c))

        except self.bot.modules_asyncio.TimeoutError:
            await confirm_msg.delete()
            await ctx.send(embed=discord.Embed(description="**No reaction received. Kick action cancelled.**",colour=0xFF0000))
        except discord.Forbidden:
            confirm_msg.delete()
            await ctx.send(embed=discord.Embed(description="**Kick failed. I don't have enough permissions to kick this user.**",colour=0xFF0000))

    @commands.command(name='ban')
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def ban(self, ctx, member: discord.Member = None, *, reason: str = "No reason provided"):
        if member is None:
            await ctx.send(embed=discord.Embed(description="**Please provide a valid Discord member to ban.**",colour=0xFF0000))
            return

        if member == ctx.guild.owner:
            await ctx.send(embed=discord.Embed(description="**I cannot ban the server owner.**",colour=0xFF0000))
            return
        if member == ctx.bot.user:
            await ctx.send(embed=discord.Embed(description="**I can't ban myself**",colour=0xFF0000))
            return

        if not ctx.author.guild_permissions.ban_members:
            await ctx.send(embed=discord.Embed(description="**You do not have the necessary permissions to perform this action.**",colour=0xFF0000))
            return

        if not ctx.guild.me.guild_permissions.ban_members:
            await ctx.send(embed=discord.Embed(description="**I don't have the necessary permission in this channel to perform this action!**",colour=0xFF0000))
            return

        try:

            confirm_msg = await ctx.send(embed=discord.Embed(title="LuminaryAI - confirmation",description=f"Are you sure you want to ban this member?\n**Member: `{member}`**\n**Reason: `{reason}`**\n**Moderator: `{ctx.author}`**\n React with ✅ to confirm.",colour=0xc8dc6c))

            await confirm_msg.add_reaction('✅')
            await confirm_msg.add_reaction('❌')

            def check(reaction, user):
                return user == ctx.author and str(reaction.emoji) in ['✅', '❌']

            reaction, user = await ctx.bot.wait_for('reaction_add', timeout=20.0, check=check)
            
            if str(reaction.emoji) == '✅':
                await member.ban(reason=reason)
                await confirm_msg.delete()
            
                await ctx.send(embed=discord.Embed(description=f"**Member {member} has been banned.**\n**Reason: {reason}**\n**Moderator: `{ctx.author}`**",colour=0xc8dc6c))
            
            elif str(reaction.emoji) == '❌':
                await confirm_msg.delete()
                await ctx.send(embed=discord.Embed(description=f"**Action cancelled.**`\n{member}` has not been banned.",colour=0xFF0000))

        except self.bot.modules_asyncio.TimeoutError:
            await confirm_msg.delete()
            await ctx.send(embed=discord.Embed(description="**No reaction received. ban action cancelled.**", color=0xFF0000))
        except discord.Forbidden:
            await confirm_msg.delete()
            await ctx.send(embed=discord.Embed(description="**Kick failed. I don't have enough permissions to ban this user.**",colour=0xFF0000))

    @commands.command(name='unban', help='Unban a previously banned user.')
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def unban(self, ctx, user: discord.User, *, reason="No reason provided"):

        if not ctx.author.guild_permissions.ban_members:
            await ctx.send(embed=discord.Embed(description="**You do not have the necessary permissions to perform this action.**",colour=0xFF0000))
            return

        if not ctx.guild.me.guild_permissions.ban_members:
            await ctx.send(embed=discord.Embed(description="I don't have the ban members permission to perform this action.",colour=0xFF0000))
            return

        banned_users = [ban_entry async for ban_entry in ctx.guild.bans()]
        for ban_entry in banned_users:
            if ban_entry.user == user:
                try:

                    confirm_message = await ctx.send(embed=discord.Embed(title="LuminaryAI - confirmation",description=f"Are you sure you want to unban this member?\n**Member: `{user}`**\n**Reason: `{reason}`**\n**Moderator: `{ctx.author}`**\n React with ✅ to confirm.",colour=0xc8dc6c))
                    await confirm_message.add_reaction("✅")
                    await confirm_message.add_reaction('❌')

                    def check(reaction, user_check):
                        return user_check == ctx.author and str(reaction.emoji) in ['✅', '❌'] and reaction.message.id == confirm_message.id

                    try:
                        reaction, user_check = await self.bot.wait_for('reaction_add', timeout=20.0, check=check)
                    except self.bot.modules_asyncio.TimeoutError:
                        await confirm_message.delete()
                        await ctx.send(embed=discord.Embed(description="**Unban confirmation failed. Command cancelled.**", color=0xFF0000))
                        return

                    if str(reaction.emoji) == '✅':

                        await ctx.guild.unban(user, reason=reason)
                        await confirm_message.delete()
                        await ctx.send(embed=discord.Embed(description=f"**Member unbanned**\n**Unbanned member: {user.mention}**\n **Reason: {reason}**\n**Moderator: `{ctx.author}`**", color=0x99ccff))
        
                    elif str(reaction.emoji) == '❌':
                        await confirm_message.delete()
                        await ctx.send(embed=discord.Embed(description="**Action cancelled.**\n**`{member}` has not been unbanned.**",colour=0xc8dc6c))
                except discord.Forbidden:
                    await confirm_message.delete()
                    await ctx.send(embed=discord.Embed(description="**I do not have permission to unban this user.**", color=0xFF0000))
                    return
                except discord.HTTPException as e:
                    await confirm_message.delete()
                    await ctx.send(embed=discord.Embed(title="Failed to unban due to an HTTP error.", color=0xFF0000))
                    return
                break
        else:

            await ctx.send(embed=discord.Embed(description=f"**{user.mention} is not banned.**", color=0xFF0000))

    @commands.command(name='timeout', help='Timeout a user for a specified duration.')
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def timeout(self, ctx, member: discord.Member = None, duration: str = None, *, reason: str = "No reason provided"):
        if member == ctx.guild.owner:
            await ctx.send(embed=discord.Embed(description="**I cannot timeout the server owner.**", color=0xFF0000))
            return

        if member == ctx.bot.user:
            await ctx.send(embed=discord.Embed(description="**I cannot timeout myself.**", color=0xFF0000))
            return

        if member == ctx.author:
            await ctx.send(embed=discord.Embed(description="**You cannot timeout yourself.**", color=0xFF0000))
            return
        
        if not ctx.guild.me.guild_permissions.manage_roles:
            await ctx.send(embed=discord.Embed(description="**I don't have the `manage roles` permission to perform this command.**",colour=0xFF0000))
            return
    
        if not ctx.author.guild_permissions.manage_roles:
            await ctx.send(embed=discord.Embed(description="**You do not have the necessary permissions to perform this action.**",colour=0xFF0000))
            return
        
        if member is None:
            await ctx.send(embed=discord.Embed(description="**Please provide a member to timeout**", color=0xFF0000))
            return

        if duration is None:
            await ctx.send(embed=discord.Embed(description="**Please provide a valid duration.**", color=0xFF0000))
            return
        time_delta = parse_duration(duration, self.bot)
        if time_delta is None:
            await ctx.send(embed=discord.Embed(description="**Invalid duration. Use 'd' for days, 'h' for hours, 'm' for minutes.**", color=0xFF0000))
            return

        time_now = discord.utils.utcnow()
        timeout_until = time_now + time_delta

        try:
            # Ask for confirmation
            confirm_message = await ctx.send(embed=discord.Embed(title="LuminaryAI - confirmation",description=f"Are you sure you want to timeout this member?\n**Member: `{member}`**\n**Reason: `{reason}`**\n**Moderator: `{ctx.author}`**\n**Duration: `{duration}`**\n React with ✅ to confirm.",colour=0xc8dc6c))
            await confirm_message.add_reaction("✅")
            await confirm_message.add_reaction('❌')

            def check(reaction, user):
                return user == ctx.author and str(reaction.emoji) in ['✅', '❌'] and reaction.message.id == confirm_message.id

            try:

                reaction, user = await ctx.bot.wait_for('reaction_add', timeout=20.0, check=check)
            except self.bot.modules_asyncio.TimeoutError:
                await confirm_message.delete()
                await ctx.send(embed=discord.Embed(description="**Timeout confirmation failed. Command cancelled.**", color=0xFF0000))
                return

            if str(reaction.emoji) == '✅':
                # Apply timeout
                await member.edit(timed_out_until=timeout_until)
                await confirm_message.delete()
                await ctx.send(embed=discord.Embed(description=f"**{member.mention} has been timed out for `{duration}`**.\n**Reason: `{reason}`**\n**Moderaator: `{ctx.author}`**", color=0x99ccff))
            elif str(reaction.emoji) == '❌':
                await confirm_message.delete()
                await ctx.send(embed=discord.Embed(description=f"**Action cancelled, {member} has not been timed out.**", color=0xFF0000))
            
        except discord.Forbidden:
            await confirm_message.delete()
            await ctx.send(embed=discord.Embed(description="**I do not have permission to timeout this user.**", color=0xFF0000))
        except discord.HTTPException as e:
            await confirm_message.delete()
            await ctx.send(embed=discord.Embed(description=f"**Failed to timeout due to an HTTP error.**", color=0xFF0000))

    @commands.command(name="unmute")
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def unmute(self, ctx, member: discord.Member = None, reason: str = "No reason given"):

        if member is None:
            await ctx.send(embed=discord.Embed(description="**Please provide a member to unmute.**", color=0xFF0000))
            return

        if not ctx.guild.me.guild_permissions.manage_roles:
            await ctx.send(embed=discord.Embed(description="**I don't have the `manage roles` permission to perform this action.**", color=0xFF0000))
            return

        if member.timed_out_until is None:
            await ctx.send(embed=discord.Embed(description="**Member is not muted.**", color=0xFF0000))
            return

        if not ctx.author.guild_permissions.manage_roles:
            await ctx.send(embed=discord.Embed(description="**You don't have the necessary permissions to perform this command**", color=0xFF0000))
            return

        try:

            confirm_message = await ctx.send(embed=discord.Embed(title="LuminaryAI - confirmation",description=f"Are you sure you want to unmute this member?\n**Member: `{member}`**\n**Reason: `{reason}`**\n**Moderator: `{ctx.author}`**\n React with ✅ to confirm.",colour=0xc8dc6c))
            await confirm_message.add_reaction("✅")
            await confirm_message.add_reaction('❌')

            def check(reaction, user):
                return user == ctx.author and str(reaction.emoji) in ['✅', '❌'] and reaction.message.id == confirm_message.id

            reaction, user = await ctx.bot.wait_for('reaction_add', timeout=20.0, check=check)

            if str(reaction.emoji) == '✅':

                await member.edit(timed_out_until=None)
                await confirm_message.delete()
                await ctx.send(embed=discord.Embed(description=f"**{member.mention} has been unmuted**.\n**Reason: `{reason}`**\n**Moderator: `{ctx.author}`**", color=0x99ccff))
                return
            elif str(reaction.emoji) == '❌':
                await confirm_message.delete()
                await ctx.send(embed=discord.Embed(description=f"**Action cancelled, {member} has not been unmuted**", color=0xFF0000))
                return

        except self.bot.modules_asyncio.TimeoutError:
            await confirm_message.delete()
            await ctx.send(embed=discord.Embed(description="**Confirmation timed out. Action cancelled.**", color=0xFF0000))
        except discord.Forbidden:
            await confirm_message.delete()
            await ctx.send(embed=discord.Embed(description="**I do not have permission to unmute this user.**", color=0xFF0000))
        except discord.HTTPException as e:
            await confirm_message.delete()
            await ctx.send(embed=discord.Embed(description="**Failed to unmute due to an HTTP error.**", color=0xFF0000))
        print(e)


    @commands.command(name='purgelinks', help='Purges messages containing links from the channel.')
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def purge_links(self, ctx, limit: str = None):        
        if limit is None:
            await ctx.send(embed=discord.Embed(description="**Please provide a number to purge**",colour=0xFF0000))
            return

        try:
            limit = int(limit)
        except ValueError:
            await ctx.send(embed=discord.Embed(description="**Please provide a valid number to purge**",colour=0xFF0000))
            return
        
        if not ctx.channel.permissions_for(ctx.channel.guild.me).manage_messages:
            await ctx.send(embed=discord.Embed(description="**I do not have the `manage_messages` permission in this channel to perform this action.**",colour=0xFF0000))
            return
        if not ctx.author.guild_permissions.manage_messages:
            await ctx.send(embed=discord.Embed(description="**You do not have the nessesarry permission.**",colour=0xFF0000))
            return

        def is_link(message):
            # Simple check, can be replaced with a more advanced regex for detecting links
            return 'http://' in message.content or 'https://' in message.content

        confirmation_message = await ctx.send(embed=discord.Embed(title="LuminaryAI - confirmation",description=f"**Are you sure you want to delete up to {limit} messages containing links?**\n **React with ✅ to confirm.**",colour=0xc8dc6c))
        await confirmation_message.add_reaction("✅")
        await confirmation_message.add_reaction('❌')

        def check(reaction, user):
            return user == ctx.message.author and str(reaction.emoji) in ['✅', '❌'] and reaction.message.id == confirmation_message.id

        try:

            reaction, user = await ctx.bot.wait_for('reaction_add', timeout=20.0, check=check)
        except self.bot.modules_asyncio.TimeoutError:
            await confirmation_message.delete()
            await ctx.send(embed=discord.Embed(description="**Purge links command cancelled.**", color=0xFF0000))
            return

        # Perform the purge
        if str(reaction.emoji) == '✅':
            try:
                deleted_messages = await ctx.channel.purge(limit=limit, check=is_link)
                await confirmation_message.delete()
                await ctx.send(embed=discord.Embed(description=f"**Deleted {len(deleted_messages)} messages containing links.**",colour=0xc8dc6c))

            except discord.Forbidden:
                await confirmation_message.delete()
                await ctx.send(embed=discord.Embed(description="**I lack the required permissions to delete messages.**",colour=0xFF0000))
            except discord.HTTPException as e:
                await confirmation_message.delete()
                await ctx.send(embed=discord.Embed(description="**Failed to purge messages due to an HTTP error.**",colour=0xFF0000))
        elif str(reaction.emoji) == '❌':
            await confirmation_message.delete()
            await ctx.send(embed=discord.Embed(description="**Action cancelled**",colour=0xFF0000))

    @commands.command(name='purgefiles', help='Purges messages containing files/attachments from the channel.')
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def purge_files(self, ctx, limit: str = None):

        if not ctx.channel.permissions_for(ctx.guild.me).manage_messages:
            await ctx.send(embed=discord.Embed(description="**I don't have the necessary permissions to manage messages in this channel.**",colour=0xFF0000))
            return
        if not ctx.author.guild_permissions.manage_messages:
            await ctx.send(embed=discord.Embed(description="**You don't have the necessary permissions to manage messages in this channel.**",colour=0xFF0000))
            return
        
        if limit is None:
            await ctx.send(embed=discord.Embed(description="**Please provide a number of messages to delete**",colour=0xFF0000))
            return
        
        try:
            limit = int(limit)
        except ValueError:
            await ctx.send(embed=discord.Embed(description="**Please provide a valid number of messages to delete.**",colour=0xFF0000))

        def has_files(message):
            return len(message.attachments) > 0

        confirmation_message = await ctx.send(embed=discord.Embed(title="LuminaryAI - confirmation", description=f"**Are you sure you want to delete up to {limit} messages containing files/attachments?**\n**React with ✅ to confirm.**",colour=0xc8dc6c))
        await confirmation_message.add_reaction("✅")
        await confirmation_message.add_reaction("❌")

        def check(reaction, user):
            return user == ctx.message.author and str(reaction.emoji) in ['✅', '❌'] and reaction.message.id == confirmation_message.id

        try:

            reaction, user = await self.bot.wait_for('reaction_add', timeout=20.0, check=check)
        except self.bot.modules_asyncio.TimeoutError:
            await confirmation_message.delete()
            await ctx.send(embed=discord.Embed(description="**Purge files command cancelled.**",colour=0xFF0000))
            return

        if str(reaction.emoji) == '✅':
            try:
                deleted_messages = await ctx.channel.purge(limit=limit, check=has_files)
                await confirmation_message.delete()
                await ctx.send(embed=discord.Embed(description=f"**Deleted {len(deleted_messages)} messages containing files/attachments.**",colour=0xc8dc6c))
            except discord.Forbidden:
                await confirmation_message.delete()
                await ctx.send(embed=discord.Embed(description="**I lack the required permissions to delete messages.**",colour=0xFF0000))
            except discord.HTTPException as e:
                await confirmation_message.delete()
                await ctx.send(embed=discord.Embed(description=f"**Failed to purge messages due to an HTTP error.**",colour=0xFF0000))
        elif str(reaction.emoji) == '❌':
            await confirmation_message.delete()
            await ctx.send(embed=discord.Embed(description="**Action cancelled.**",colour=0xFF0000))


async def setup(bot):
    await bot.add_cog(Moderation(bot))