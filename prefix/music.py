import discord
from discord import Embed as em
from discord.ext import commands
from discord import Color as color
from bot_utilities.music_utils import *


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
loop_enabled = discord.Embed(
    description="Loop enabled",
    color=0x99ccff
)
loop_disabled = discord.Embed(
    description="Loop disabled",
    color=0x99ccff
)
no_result_embed = discord.Embed(
    title="LumianryAI - music",
    description="No results found",
    color=0xFF0000
)
alread_playing = discord.Embed(
    description="Already playing.",
    color=0x99ccff
)
not_in_voice = discord.Embed(
    title="LumianryAI - music",
    description="I am not currently in a voice channel.",
    color=0xFF0000
)
playback_stopped_left = discord.Embed(
    title="LumianryAI - music",
    description="Playback stopped, and I left the voice channel.",
    color=0x99ccff
)

need_same_channel_to_stop = discord.Embed(
    description="You need to be in the same voice channel as me to perform this action.",
    color=0xFF0000
)

not_in_voice.set_thumbnail(url="attachment://thumbnail.png")
alread_playing.set_thumbnail(url="attachment://thumbnail.png")
no_result_embed.set_thumbnail(url="attachment://thumbnail.png")
playback_stopped_left.set_thumbnail(url="attachment://thumbnail.png")
need_same_channel_to_stop.set_thumbnail(url="attachment://thumbnail.png")

class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='join')
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def join(self, ctx):

        if ctx.author.voice is None:
            await ctx.send(embed=em(description="> ❌ You're not in a voice channel.", color=color.red()))
            return

        if ctx.voice_client is not None and ctx.voice_client.is_connected():
            await ctx.send(embed=em(description="> ❌ I am already connected to a voice channel.", color=color.red()))
            return

        bot_member = ctx.guild.get_member(self.bot.user.id)
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



    @commands.command(name='play')
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def play(self, ctx, *, song_name):
        if ctx.author.voice is None:
            await ctx.send(embed=em(description="> **❌ You're not in a voice channel.**", color=color.red()))
            return

        if ctx.voice_client is None:
            await ctx.send(embed=em(description="> **❌ I am not in a voice channel. Use `ai.join`.**", color=color.red()))
            return

        if ctx.author.voice.channel != ctx.voice_client.channel:
            await ctx.send(embed=em(description="> **❌ You have to be in the same channel to use music commands.**", color=color.red()))
            return

        wait = await ctx.send(embed=em(description="> **🕒 Searching for songs...**", color=color.blue()))
        songs = await search(song_name, ctx)
    
        if not songs:
            await wait.edit(embed=em(description="> **❌ No songs found.**", color=color.red()))
            return

        embed = em(title="Choose a song", description="Type a number from 1 to 5 to select a song, or 'c' to cancel.", color=color.blue())
        for i, song in enumerate(songs[:5], start=1):
            embed.add_field(name='\u200b', value=f"[`{i}. {song['title']}`]({song['url']})", inline=False)

        await wait.edit(embed=embed)
        def check(m): return m.author == ctx.author and m.channel == ctx.channel and (m.content.isdigit() or m.content.lower() == 'c')

        try: msg = await self.bot.wait_for('message', check=check, timeout=30.0)
        except asyncio.TimeoutError:
            await ctx.send(embed=em(description="> **❌ You took too long to respond.**", color=color.red()))
            return

        if msg.content.lower() == 'c':
            await ctx.send(embed=em(description="> **❌ Selection cancelled.**", color=color.red()))
            return

        if msg.content.isdigit():
            index = int(msg.content)
            if 1 <= index <= 5:
                selected_song = songs[index - 1]
                message = await ctx.send(embed=em(description=f"> **🎧 You selected:** `{selected_song['title']}`", color=color.green()))

                # Get audio details and add to queue
                song = await get_audio_url(selected_song['url'])  # Call to get audio URL
                if not song:
                    await ctx.send(embed=em(description="> **❌ Sorry, it seems that our music engine is offline.**", color=color.red()))
                    return

                name = song.get('title')
                channel = song.get('channel')
                f_duration = song.get('f_duration')
                duration = song.get('duration')
                video_url = song.get('url')
                audio_url = song.get('audiouri')
                thumbnail = song.get('thumbnail')

                # Add song details to the queue
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

                await message.edit(embed=em(description=f"> **🎧 Track Queued:** `{name}` by `{channel}`.", color=color.purple()))
                if not ctx.voice_client.is_playing():
                    await play_next_song(ctx.voice_client, ctx, self.bot)

            else:
                await ctx.send(embed=em(description="> **❌ Invalid selection.**", color=color.red()))
        else:
            await ctx.send(embed=em(description="> **❌ Invalid input.**", color=color.red()))



    @commands.command(name='leave')
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def leave(self, ctx):
        if ctx.voice_client is not None:
            if ctx.author.voice.channel == ctx.voice_client.channel:
                ctx.voice_client.stop()
                await ctx.voice_client.disconnect()
                await ctx.send(embed=playback_stopped_left)
            else:
                await ctx.send(embed=need_same_channel_to_stop)
        else:
            await ctx.send(embed=not_in_voice)


    @commands.command(name='stop')
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def stop(self, ctx):
        if ctx.voice_client is not None:
            if ctx.author.voice.channel == ctx.voice_client.channel:
                ctx.voice_client.stop()
                await ctx.send(embed=playback_stopped)
            else:
                await ctx.send(embed=need_same_channel_to_stop)
        else:
            await ctx.send(embed=not_in_voice)


    @commands.command(name='pause')
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def stop(self, ctx):
        if ctx.voice_client is not None:
            if ctx.author.voice.channel == ctx.voice_client.channel:
                ctx.voice_client.pause()
                await ctx.send(embed=playback_paused)
            else:
                await ctx.send(embed=need_same_channel_to_stop)
        else:
            await ctx.send(embed=not_in_voice)


    @commands.command(name='resume')
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def stop(self, ctx):
        if ctx.voice_client is not None:
            if ctx.author.voice.channel == ctx.voice_client.channel:
                ctx.voice_client.resume()
                await ctx.send(embed=playback_resumed)
            else:
                await ctx.send(embed=need_same_channel_to_stop)
        else:
            await ctx.send(embed=not_in_voice)


    @commands.command(name='volume')
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def volume(self, ctx, volume_str: str):
        if ctx.voice_client is None: await ctx.send(embed=not_in_voice)
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

async def setup(bot):
    await bot.add_cog(Music(bot))