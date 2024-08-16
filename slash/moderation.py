import re
import discord
import asyncio
from datetime import timedelta
from discord import app_commands
from discord.ext import commands
from bot_utilities.owner_utils import check_blist


def parse_duration(duration_str):
    match = re.match(r"(\d+)([dhm])", duration_str)
    if not match:
        return None
    duration, unit = match.groups()
    duration = int(duration)
    if unit == 'd':
        return timedelta(days=duration)
    elif unit == 'h':
        return timedelta(hours=duration)
    elif unit == 'm':
        return timedelta(minutes=duration)
    


def moderation_slash(bot, mongodb):

    @bot.tree.command(name='purge', description='Deletes a specified number of messages')
    @commands.guild_only()
    @app_commands.describe(messages="The number of messages you want to purge.")
    async def purge(interaction: discord.Interaction, messages: int):

        if await check_blist(interaction, mongodb): return
        await interaction.response.defer(ephemeral=False)

        channel = interaction.channel

        if interaction.user.guild_permissions.manage_messages:
            if channel.permissions_for(channel.guild.me).manage_messages:
                try:
                    num_messages_int = int(messages)  # Convert the string to an integer
                    if num_messages_int < 1:
                        await interaction.followup.send(f"**How can I delete {num_messages_int} messages?**")
                    if num_messages_int == 1:
                        await interaction.followup.send("**If you want to delete just one message, then please do this manually.**")
                    else:
                        await interaction.channel.purge(limit=num_messages_int + 1)  # +1 to include the command message
                        #await interaction.followup.send(embed=discord.Embed(description=f"**Successfully purged {num_messages_int} messages**"))
                except ValueError:
                    await interaction.followup.send("**Invalid input. Please provide a valid number of messages.**")
            else:
                await interaction.followup.send("**I don't have the necessary permission in this channel to perform this action!**")
        else:
            await interaction.followup.send("**You do not have the necessary permissions to perform this action!**")
        


    @bot.tree.command(name='kick', description="Kick a member")
    @commands.guild_only()
    @app_commands.describe(member="Select the member you want to kick.")
    @app_commands.describe(member="Reason for the kick")
    async def kick(interaction: discord.Interaction, member: discord.Member, reason: str):
        if await check_blist(interaction, mongodb): return
        await interaction.response.defer(ephemeral=False)

        # Protect the bot from kicking itself or the server owner
        if member == interaction.guild.owner:
            await interaction.followup.send(embed=discord.Embed(description="**I cannot kick the server owner**.",colour=0xFF0000))
            return
        if member == bot.user:
            await interaction.followup.send(embed=discord.Embed(description="**I can't kick myself!**",colour=0xFF0000))
            return
        
        # Check if the command caller has the required permission
        if not interaction.user.guild_permissions.kick_members:
            await interaction.followup.send(embed=discord.Embed(description="**You do not have the necessary permissions to perform this action.**",colour=0xFF0000))
            return

        # Check if the bot itself has the permission to kick members
        if not interaction.guild.me.guild_permissions.kick_members:
            await interaction.followup.send(embed=discord.Embed(description="**I don't have the necessary permission in this channel to perform this action.**",colour=0xFF0000))
            return


        try:
            # Send a confirmation message to the moderator
            confirm_msg = await interaction.followup.send(embed=discord.Embed(title="LuminaryAI - confirmation",description=f"**Are you sure you want to kick this member?**\n**Member: `{member}`**\n**Reason: `{reason}`**\n**Moderator: {interaction.user}**", color=0xc8dc6c))
            # Add reactions for confirmation
            await confirm_msg.add_reaction('✅')
            await confirm_msg.add_reaction('❌')

            # Check for the moderator's reaction
            def check(reaction, user):
                return user == interaction.user and str(reaction.emoji) in ['✅', '❌']

            reaction, user = await bot.wait_for('reaction_add', timeout=20.0, check=check)
            
            if str(reaction.emoji) == '✅':
                await member.kick(reason=reason)
                await confirm_msg.delete()
                await interaction.followup.send(embed=discord.Embed(description=f"**Member {member} has been kicked.**\n**Reason: `{reason}`**\n**Moderator: `{interaction.user}`**",colour=0xc8dc6c))

            elif str(reaction.emoji) == '❌':
                await confirm_msg.delete()
                await interaction.followup.send(embed=discord.Embed(description="**Action cancelled.**\n`{member}` has not been kicked.",colour=0xc8dc6c))

        except asyncio.TimeoutError:
            await confirm_msg.delete()
            await interaction.followup.send(embed=discord.Embed(description="**No reaction received. Kick action cancelled.**",colour=0xFF0000))
        except discord.Forbidden:
            confirm_msg.delete()
            await interaction.followup.send(embed=discord.Embed(description="**Kick failed. I don't have enough permissions to kick this user.**",colour=0xFF0000))




    @bot.tree.command(name='ban', description="Ban a member")
    @commands.guild_only()
    @app_commands.describe(member="Select the member you want to ban.")
    @app_commands.describe(member="Reason for the ban")
    async def kick(interaction: discord.Interaction, member: discord.Member, reason: str):
        if await check_blist(interaction, mongodb): return
        await interaction.response.defer(ephemeral=False)

        # Protect the bot from kicking itself or the server owner
        if member == interaction.guild.owner:
            await interaction.followup.send(embed=discord.Embed(description="**I cannot ban the server owner.**",colour=0xFF0000))
            return
        if member == bot.user:
            await interaction.followup.send(embed=discord.Embed(description="**I can't ban myself**",colour=0xFF0000))
            return
        
        # Check if the command caller has the required permission
        if not interaction.user.guild_permissions.ban_members:
            await interaction.followup.send(embed=discord.Embed(description="**You do not have the necessary permissions to perform this action.**",colour=0xFF0000))
            return

        # Check if the bot itself has the permission to kick members
        if not interaction.guild.me.guild_permissions.ban_members:
            await interaction.followup.send(embed=discord.Embed(description="**I don't have the necessary permission in this channel to perform this action!**",colour=0xFF0000))
            return

        try:
            # Send a confirmation message to the moderator
            confirm_msg = await interaction.followup.send(embed=discord.Embed(title="LuminaryAI - confirmation",description=f"Are you sure you want to ban this member?\n**Member: `{member}`**\n**Reason: `{reason}`**\n**Moderator: `{interaction.user}`**\n React with ✅ to confirm.",colour=0xc8dc6c))
            # Add reactions for confirmation
            await confirm_msg.add_reaction('✅')
            await confirm_msg.add_reaction('❌')

            # Check for the moderator's reaction
            def check(reaction, user):
                return user == interaction.user and str(reaction.emoji) in ['✅', '❌']

            reaction, user = await bot.wait_for('reaction_add', timeout=20.0, check=check)
            
            if str(reaction.emoji) == '✅':
                await member.ban(reason=reason)
                await confirm_msg.delete()
            
                await interaction.followup.send(embed=discord.Embed(description=f"**Member {member} has been banned.**\n**Reason: {reason}**\n**Moderator: `{interaction.user}`**",colour=0xc8dc6c))
            
            elif str(reaction.emoji) == '❌':
                await confirm_msg.delete()
                await interaction.followup.send(embed=discord.Embed(description=f"**Action cancelled.**`\n{member}` has not been banned.",colour=0xFF0000))

        except asyncio.TimeoutError:
            await confirm_msg.delete()
            await interaction.followup.send(embed=discord.Embed(description="**No reaction received. ban action cancelled.**", color=0xFF0000))
        except discord.Forbidden:
            await confirm_msg.delete()
            await interaction.followup.send(embed=discord.Embed(description="**Kick failed. I don't have enough permissions to ban this user.**",colour=0xFF0000))



    @bot.tree.command(name='unban', description='Unban a previously banned user.')
    @commands.guild_only()
    @app_commands.describe(user="Select the member you want to unban.")
    @app_commands.describe(reason="Reason for the unban")
    async def unban(interaction: discord.Interaction, user: discord.User, reason: str):

        if await check_blist(interaction, mongodb): return
        await interaction.response.defer(ephemeral=False)

        # Check if the command caller has the required permission
        if not interaction.user.guild_permissions.ban_members:
            await interaction.followup.send(embed=discord.Embed(description="**You do not have the necessary permissions to perform this action.**",colour=0xFF0000))
            return

        # Check if the bot itself has the permission to ban members
        if not interaction.guild.me.guild_permissions.ban_members:
            await interaction.followup.send(embed=discord.Embed(description="I don't have the ban members permission to perform this action.",colour=0xFF0000))
            return

        # Retrieve the ban entries to check if the user is banned
        banned_users = [ban_entry async for ban_entry in interaction.guild.bans()]
        for ban_entry in banned_users:
            if ban_entry.user == user:
                try:
                    # Ask for confirmation
                    confirm_message = await interaction.followup.send(embed=discord.Embed(title="LuminaryAI - confirmation",description=f"Are you sure you want to unban this member?\n**Member: `{user}`**\n**Reason: `{reason}`**\n**Moderator: `{interaction.user}`**\n React with ✅ to confirm.",colour=0xc8dc6c))
                    await confirm_message.add_reaction("✅")
                    await confirm_message.add_reaction('❌')

                    def check(reaction, user_check):
                        return user_check == interaction.user and str(reaction.emoji) in ['✅', '❌'] and reaction.message.id == confirm_message.id

                    try:
                        # Waiting for the reaction to be added
                        reaction, user_check = await bot.wait_for('reaction_add', timeout=20.0, check=check)
                    except asyncio.TimeoutError:
                        await confirm_message.delete()
                        await interaction.followup.send(embed=discord.Embed(description="**Unban confirmation failed. Command cancelled.**", color=0xFF0000))
                        return

                    if str(reaction.emoji) == '✅':
                        # Perform the unban
                        await interaction.guild.unban(user, reason=reason)
                        await confirm_message.delete()
                        await interaction.followup.send(embed=discord.Embed(description=f"**Member unbanned**\n**Unbanned member: {user.mention}**\n **Reason: {reason}**\n**Moderator: `{interaction.user}`**", color=0x99ccff))
        
                    elif str(reaction.emoji) == '❌':
                        await confirm_message.delete()
                        await interaction.followup.send(embed=discord.Embed(description="**Action cancelled.**\n**`{member}` has not been unbanned.**",colour=0xc8dc6c))
                except discord.Forbidden:
                    await confirm_message.delete()
                    await interaction.followup.send(embed=discord.Embed(description="**I do not have permission to unban this user.**", color=0xFF0000))
                    return
                except discord.HTTPException as e:
                    await confirm_message.delete()
                    await interaction.followup.send(embed=discord.Embed(title="Failed to unban due to an HTTP error.", color=0xFF0000))
                    return
                break
        else:
            # User is not in the ban entries
            await interaction.followup.send(embed=discord.Embed(description=f"**{user.mention} is not banned.**", color=0xFF0000))






    @bot.tree.command(name='timeout', description='Timeout a user for a specified duration.')
    @commands.guild_only()
    @app_commands.describe(member="Select the member you want to timeout.")
    @app_commands.describe(reason="Reason for the timeout")
    @app_commands.describe(duration="Please provide a valid time duration(eg, 1m, 4d, 1h)")
    async def timeout(interaction: discord.Interaction, member: discord.Member, duration: str, reason: str):

        if await check_blist(interaction, mongodb): return
        await interaction.response.defer(ephemeral=False)

        if member == interaction.guild.owner:
            await interaction.followup.send(embed=discord.Embed(description="**I cannot timeout the server owner.**", color=0xFF0000))
            return

        if member == bot.user:
            await interaction.followup.send(embed=discord.Embed(description="**I cannot timeout myself.**", color=0xFF0000))
            return

        if member == interaction.user:
            await interaction.followup.send(embed=discord.Embed(description="**You cannot timeout yourself.**", color=0xFF0000))
            return
        
        if not interaction.guild.me.guild_permissions.manage_roles:
            await interaction.followup.send(embed=discord.Embed(description="**I don't have the `manage roles` permission to perform this command.**",colour=0xFF0000))
            return
    
        # Check if the command caller has the required permission
        if not interaction.user.guild_permissions.manage_roles:
            await interaction.followup.send(embed=discord.Embed(description="**You do not have the necessary permissions to perform this action.**",colour=0xFF0000))
            return
        

        time_delta = parse_duration(duration)
        if time_delta is None:
            await interaction.followup.send(embed=discord.Embed(description="**Invalid duration. Use 'd' for days, 'h' for hours, 'm' for minutes.**", color=0xFF0000))
            return

        time_now = discord.utils.utcnow()
        timeout_until = time_now + time_delta

        try:
            # Ask for confirmation
            confirm_message = await interaction.followup.send(embed=discord.Embed(title="LuminaryAI - confirmation",description=f"Are you sure you want to timeout this member?\n**Member: `{member}`**\n**Reason: `{reason}`**\n**Moderator: `{interaction.user}`**\n**Duration: `{duration}`**\n React with ✅ to confirm.",colour=0xc8dc6c))
            await confirm_message.add_reaction("✅")
            await confirm_message.add_reaction('❌')

            def check(reaction, user):
                return user == interaction.user and str(reaction.emoji) in ['✅', '❌'] and reaction.message.id == confirm_message.id

            try:

                reaction, user = await bot.wait_for('reaction_add', timeout=20.0, check=check)
            except asyncio.TimeoutError:
                await confirm_message.delete()
                await interaction.followup.send(embed=discord.Embed(description="**Timeout confirmation failed. Command cancelled.**", color=0xFF0000))
                return

            if str(reaction.emoji) == '✅':
                # Apply timeout
                await member.edit(timed_out_until=timeout_until)
                await confirm_message.delete()
                await interaction.followup.send(embed=discord.Embed(description=f"**{member.mention} has been timed out for `{duration}`**.\n**Reason: `{reason}`**\n**Moderaator: `{interaction.user}`**", color=0x99ccff))
            elif str(reaction.emoji) == '❌':
                await confirm_message.delete()
                await interaction.followup.send(embed=discord.Embed(description=f"**Action cancelled, {member} has not been timed out.**", color=0xFF0000))
            
        except discord.Forbidden:
            await confirm_message.delete()
            await interaction.followup.send(embed=discord.Embed(description="**I do not have permission to timeout this user.**", color=0xFF0000))
        except discord.HTTPException as e:
            await confirm_message.delete()
            await interaction.followup.send(embed=discord.Embed(description=f"**Failed to timeout due to an HTTP error.**", color=0xFF0000))





    @bot.tree.command(name="unmute", description="Unmute a member.")
    @commands.guild_only()
    @app_commands.describe(member="Select the member you want to Unmute.")
    @app_commands.describe(reason="Reason for the Unmute")
    async def unmute(interaction: discord.Interaction, member: discord.Member, reason: str):

        if await check_blist(interaction, mongodb): return
        await interaction.response.defer(ephemeral=False)

        # Check if bot has necessary permissions
        if not interaction.guild.me.guild_permissions.manage_roles:
            await interaction.followup.send(embed=discord.Embed(description="**I don't have the `manage roles` permission to perform this action.**", color=0xFF0000))
            return

        # Check if member is already unmuted
        if member.timed_out_until is None:
            await interaction.followup.send(embed=discord.Embed(description="**Member is not muted.**", color=0xFF0000))
            return

        # Check if command caller has necessary permissions
        if not interaction.user.guild_permissions.manage_roles:
            await interaction.followup.send(embed=discord.Embed(description="**You don't have the necessary permissions to perform this command**", color=0xFF0000))
            return

        try:
            # Ask for confirmation
            confirm_message = await interaction.followup.send(embed=discord.Embed(title="LuminaryAI - confirmation",description=f"Are you sure you want to unmute this member?\n**Member: `{member}`**\n**Reason: `{reason}`**\n**Moderator: `{interaction.user}`**\n React with ✅ to confirm.",colour=0xc8dc6c))
            await confirm_message.add_reaction("✅")
            await confirm_message.add_reaction('❌')

            def check(reaction, user):
                return user == interaction.user and str(reaction.emoji) in ['✅', '❌'] and reaction.message.id == confirm_message.id

            reaction, user = await bot.wait_for('reaction_add', timeout=20.0, check=check)
            if str(reaction.emoji) == '✅':
                # Apply unmute
                await member.edit(timed_out_until=None)
                await confirm_message.delete()
                await interaction.followup.send(embed=discord.Embed(description=f"**{member.mention} has been unmuted**.\n**Reason: `{reason}`**\n**Moderator: `{interaction.user}`**", color=0x99ccff))
                return
            elif str(reaction.emoji) == '❌':
                await confirm_message.delete()
                await interaction.followup.send(embed=discord.Embed(description=f"**Action cancelled, {member} has not been unmuted**", color=0xFF0000))
                return

        except asyncio.TimeoutError:
            await confirm_message.delete()
            await interaction.followup.send(embed=discord.Embed(description="**Confirmation timed out. Action cancelled.**", color=0xFF0000))
        except discord.Forbidden:
            await confirm_message.delete()
            await interaction.followup.send(embed=discord.Embed(description="**I do not have permission to unmute this user.**", color=0xFF0000))
        except discord.HTTPException as e:
            await confirm_message.delete()
            await interaction.followup.send(embed=discord.Embed(description="**Failed to unmute due to an HTTP error.**", color=0xFF0000))





    @bot.tree.command(name='purgelinks', description='Purges messages containing links from the channel.')
    @commands.guild_only()
    @app_commands.describe(limit="The number of messages you want to purge that contains links")
    async def purge_links(interaction: discord.Interaction, limit: int):        

        if await check_blist(interaction, mongodb): return
        await interaction.response.defer(ephemeral=False)
        
        if not interaction.channel.permissions_for(interaction.channel.guild.me).manage_messages:
            await interaction.followup.send(embed=discord.Embed(description="**I do not have the `manage_messages` permission in this channel to perform this action.**",colour=0xFF0000))
            return
        if not interaction.user.guild_permissions.manage_messages:
            await interaction.followup.send(embed=discord.Embed(description="**You do not have the nessesarry permission.**",colour=0xFF0000))
            return

        def is_link(message):
            # Simple check, can be replaced with a more advanced regex for detecting links
            return 'http://' in message.content or 'https://' in message.content

        # Confirmation message
        confirmation_message = await interaction.followup.send(embed=discord.Embed(title="LuminaryAI - confirmation",description=f"**Are you sure you want to delete up to {limit} messages containing links?**\n **React with ✅ to confirm.**",colour=0xc8dc6c))
        await confirmation_message.add_reaction("✅")
        await confirmation_message.add_reaction('❌')

        def check(reaction, user):
            return user == interaction.user and str(reaction.emoji) in ['✅', '❌'] and reaction.message.id == confirmation_message.id

        try:
            # Wait for confirmation reaction
            reaction, user = await bot.wait_for('reaction_add', timeout=20.0, check=check)
        except asyncio.TimeoutError:
            await confirmation_message.delete()
            await interaction.followup.send(embed=discord.Embed(description="**Purge links command cancelled.**", color=0xFF0000))
            return

        # Perform the purge
        if str(reaction.emoji) == '✅':
            try:
                deleted_messages = await interaction.channel.purge(limit=limit+1, check=is_link)
                await confirmation_message.delete()
                await interaction.followup.send(embed=discord.Embed(description=f"**Deleted {len(deleted_messages)} messages containing links.**",colour=0xc8dc6c))

            except discord.Forbidden:
                await confirmation_message.delete()
                await interaction.followup.send(embed=discord.Embed(description="**I lack the required permissions to delete messages.**",colour=0xFF0000))
            except discord.HTTPException as e:
                await confirmation_message.delete()
                await interaction.followup.send(embed=discord.Embed(description="**Failed to purge messages due to an HTTP error.**",colour=0xFF0000))
        elif str(reaction.emoji) == '❌':
            await confirmation_message.delete()
            await interaction.followup.send(embed=discord.Embed(description="**Action cancelled**",colour=0xFF0000))






    @bot.tree.command(name='purgefiles', description='Purges messages containing files/attachments from the channel.')
    @commands.guild_only()
    @app_commands.describe(limit="The number of messages you want to purge that contains files")
    async def purge_files(interaction: discord.Interaction, limit: int):

        if await check_blist(interaction, mongodb): return
        await interaction.response.defer(ephemeral=False)
    
        # Check permissions
        if not interaction.channel.permissions_for(interaction.guild.me).manage_messages:
            await interaction.followup.send(embed=discord.Embed(description="**I don't have the necessary permissions to manage messages in this channel.**",colour=0xFF0000))
            return
        if not interaction.user.guild_permissions.manage_messages:
            await interaction.followup.send(embed=discord.Embed(description="**You don't have the necessary permissions to manage messages in this channel.**",colour=0xFF0000))
            return

        def has_files(message):
            return len(message.attachments) > 0

        # Confirmation message
        confirmation_message = await interaction.followup.send(embed=discord.Embed(title="LuminaryAI - confirmation", description=f"**Are you sure you want to delete up to {limit} messages containing files/attachments?**\n**React with ✅ to confirm.**",colour=0xc8dc6c))
        await confirmation_message.add_reaction("✅")
        await confirmation_message.add_reaction("❌")

        # Check for reaction
        def check(reaction, user):
            return user == interaction.user and str(reaction.emoji) in ['✅', '❌'] and reaction.message.id == confirmation_message.id

        try:
            # Wait for confirmation reaction
            reaction, user = await bot.wait_for('reaction_add', timeout=20.0, check=check)
        except asyncio.TimeoutError:
            await confirmation_message.delete()
            await interaction.followup.send(embed=discord.Embed(description="**Purge files command cancelled.**",colour=0xFF0000))
            return

        # Perform the purge
        if str(reaction.emoji) == '✅':
            try:
                deleted_messages = await interaction.channel.purge(limit=limit, check=has_files)
                await confirmation_message.delete()
                await interaction.followup.send(embed=discord.Embed(description=f"**Deleted {len(deleted_messages)} messages containing files/attachments.**",colour=0xc8dc6c))
            except discord.Forbidden:
                await confirmation_message.delete()
                await interaction.followup.send(embed=discord.Embed(description="**I lack the required permissions to delete messages.**",colour=0xFF0000))
            except discord.HTTPException as e:
                await confirmation_message.delete()
                await interaction.followup.send(embed=discord.Embed(description=f"**Failed to purge messages due to an HTTP error.**",colour=0xFF0000))
        elif str(reaction.emoji) == '❌':
            await confirmation_message.delete()
            await interaction.followup.send(embed=discord.Embed(description="**Action cancelled.**",colour=0xFF0000))