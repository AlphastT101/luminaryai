import discord
from discord import Color as color
from discord import Embed as em
from discord.ext import commands
from bot_utilities.music_utils import *



no_result_embed = discord.Embed(
    title="LumianryAI - music",
    description="No results found",
    color=0xFF0000
)
no_result_embed.set_thumbnail(url="attachment://thumbnail.png")


not_in_voice = discord.Embed(
    title="LumianryAI - music",
    description="I am not currently in a voice channel.",
    color=0xFF0000
)
not_in_voice.set_thumbnail(url="attachment://thumbnail.png")

playback_stopped_left = discord.Embed(
    title="LumianryAI - music",
    description="Playback stopped, and I left the voice channel.",
    color=0x99ccff
)
playback_stopped_left.set_thumbnail(url="attachment://thumbnail.png")



playback_stopped = discord.Embed(
    description="Playback stopped.",
    color=0x99ccff
)
playback_paused = discord.Embed(
    description="Playback paused.",
    color=0x99ccff
)
playback_resumed = discord.Embed(
    description="Playback resumed.",
    color=0x99ccff
)



need_same_channel_to_stop = discord.Embed(
    title="LumianryAI - music",
    description="You need to be in the same voice channel as me to perform this action.",
    color=0xFF0000
)
need_same_channel_to_stop.set_thumbnail(url="attachment://thumbnail.png")



loop_enabled = discord.Embed(
    description="Loop enabled",
    color=0x99ccff
)
loop_disabled = discord.Embed(
    description="Loop disabled",
    color=0x99ccff
)



alread_playing = discord.Embed(
    title="LumianryAI - music",
    description="Already playing!\n\n looking for the queue system?\n help us by joining our support server.",
    color=0x99ccff
)
alread_playing.set_thumbnail(url="attachment://thumbnail.png")


def music(bot, sp_id, sp_secret):

    @bot.command(name='join')
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def join(ctx):

        if ctx.author.voice is None:
            await ctx.send(embed=em(description="> ❌ You're not in a voice channel.", color=color.red()))
            return

        if ctx.voice_client is not None and ctx.voice_client.is_connected():
            await ctx.send(embed=em(description="> ❌ I am already connected to a voice channel.", color=color.red()))
            return

        bot_member = ctx.guild.get_member(bot.user.id)
        channel = ctx.author.voice.channel

        # Check if the bot has necessary permissions in the voice channel
        required_permissions = ["connect", "speak", "send_messages"]
        missing_permissions = [perm for perm in required_permissions if not getattr(channel.permissions_for(bot_member), perm)]

        if missing_permissions:
            perms_embed = discord.Embed(
                title="LumianryAI - missing perms",
                description=f"> **❌ I don't have the following permissions in the voice channel:**\n\n{', '.join(missing_permissions)}",
                color=0xFF0000
            )
            await ctx.send(embed=perms_embed)
            return

        await channel.connect()
        await ctx.guild.change_voice_state(channel=channel, self_mute=False, self_deaf=True)
        ctx.voice_client.stop()

        joined_embed = discord.Embed(
            description=f"**> Joined {channel}**",
            color=0x99ccff
        )
        await ctx.send(embed=joined_embed)




    # server_loops = {}

    # @bot.command(name='loop')
    # @commands.cooldown(1, 10, commands.BucketType.user)
    # async def toggle_loop(ctx):
    #     server_id = ctx.guild.id
    #     if server_id not in server_loops:
    #         server_loops[server_id] = True  # Initialize loop status for the server if not present

    #         await ctx.send(embed=loop_enabled)
    #     elif server_loops[server_id] == True:
    #         server_loops[server_id] = False

    #         await ctx.send(embed=loop_disabled)
    #     elif server_loops[server_id] == False:
    #         server_loops[server_id] = True

    #         await ctx.send(embed=loop_enabled)


    @bot.command(name='play')
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def play(ctx, *, song_name):
        if ctx.author.voice is None:
            await ctx.send(embed=em(description="> **❌ You're not in a voice channel.**", color=color.red()))
            return

        if ctx.voice_client is None:
            await ctx.send(embed=em(description="> **❌ I am not in a voice channel. Use `ai.join`.**", color=color.red()))
            return

        if ctx.author.voice.channel != ctx.voice_client.channel:
            await ctx.send(embed=em(description="> **❌ You have to be in the same channel to use music commands.**", color=color.red()))
            return

        wait = await ctx.send(embed=em(description="> **🕒 Please wait while I process the playback.**", color=color.blue()))

        song = await get_audio_url(song_name)
        if not song:
            await wait.edit(embed=em(description="> **❌ Sorry, it seems that our music engine is offline.**", color=color.red()))
            return

        name = song.get('title')
        channel = song.get('channel')
        f_duration = song.get('f_duration')
        duration = song.get('duration')
        video_url = song.get('url')
        audio_url = song.get('audiouri')
        thumbnail = song.get('thumbnail')

        if ctx.guild.id not in guild_queues:
            guild_queues[ctx.guild.id] = []

        guild_queues[ctx.guild.id].append({
            'title': name,
            'channel': channel,
            'f_duration': f_duration,
            'url': video_url,
            'audio_url': audio_url,
            'thumbnail': thumbnail,
            'duration': duration
        })

        embed = em(description=f"> **🎧 Track Queued:** `{name}` by `{channel}`.", color=color.purple())
        await wait.edit(embed=embed)
        if not ctx.voice_client.is_playing():
            await play_next_song(ctx.voice_client, ctx, bot)



    @bot.command(name='leave')
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def leave(ctx):
        # Check if the bot is in a voice channel
        if ctx.voice_client is not None:
            # Check if the user is in the same voice channel as the bot
            if ctx.author.voice is not None and ctx.author.voice.channel == ctx.voice_client.channel:
                # Stop playing and disconnect from the voice channel
                ctx.voice_client.stop()
                await ctx.voice_client.disconnect()

                await ctx.send(embed=playback_stopped_left)
            else:

                await ctx.send(embed=need_same_channel_to_stop)
        else:

            await ctx.send(embed=not_in_voice)


    @bot.command(name='stop')
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def stop(ctx):
        # Check if the bot is in a voice channel
        if ctx.voice_client is not None:
            # Check if the user is in the same voice channel as the bot
            if ctx.author.voice is not None and ctx.author.voice.channel == ctx.voice_client.channel:
                # Stop playing and disconnect from the voice channel
                ctx.voice_client.stop()

                await ctx.send(embed=playback_stopped)
            else:

                await ctx.send(embed=need_same_channel_to_stop)
        else:
            await ctx.send(embed=not_in_voice)


    @bot.command(name='pause')
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def stop(ctx):
        # Check if the bot is in a voice channel
        if ctx.voice_client is not None:
            # Check if the user is in the same voice channel as the bot
            if ctx.author.voice is not None and ctx.author.voice.channel == ctx.voice_client.channel:
                # Stop playing and disconnect from the voice channel
                ctx.voice_client.pause()

                await ctx.send(embed=playback_paused)
            else:
                await ctx.send(embed=need_same_channel_to_stop)
        else:
            await ctx.send(embed=not_in_voice)


    @bot.command(name='resume')
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def stop(ctx):
        if ctx.voice_client is not None:
            if ctx.author.voice is not None and ctx.author.voice.channel == ctx.voice_client.channel:

                ctx.voice_client.resume()

                await ctx.send(embed=playback_resumed)
            else:
                await ctx.send(embed=need_same_channel_to_stop)
        else:
            await ctx.send(embed=not_in_voice)


    @bot.command(name='volume')
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def volume(ctx, volume_str: str):

        if ctx.voice_client is not None:
            if ctx.author.voice is not None and ctx.author.voice.channel == ctx.voice_client.channel:
                try:

                    volume_percentage = int(volume_str)
                    volume = volume_percentage / 100.0
                    ctx.voice_client.source.volume = volume
                    await ctx.send(embed=discord.Embed(description=f"**Volume has been successfully set to {volume_percentage}%**", color=0x99ccff))

                except ValueError:
                    await ctx.send(embed=discord.Embed(description="**Please provide a valid integer to set the volume.**\n\nExample:\n```ai.volume 70```", color=0x99ccff))
            else:
                await ctx.send(embed=need_same_channel_to_stop)
        else:
            await ctx.send(embed=not_in_voice)