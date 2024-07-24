import yt_dlp as youtube_dl
from discord.ext import commands
import discord
import pyshorteners
import asyncio


# Define the FFMPEG options
FFMPEG_OPTIONS = {
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
    'options': '-vn',
}

# Function to shorten a URL using TinyURL
def shorten_url(original_url):
    s = pyshorteners.Shortener()
    return s.tinyurl.short(original_url)






join_first_embed = discord.Embed(
    title="LumianryAI - music",
    description="Please join a voice channel first.",
    color=0xFF0000
)
join_first_embed.set_thumbnail(url="attachment://thumbnail.png")

already_joined = discord.Embed(
    title="LumianryAI - music",
    description="Bot is already connected to a voice channel. use `ai.leave` to leave.",
    color=0xFF0000
)
already_joined.set_thumbnail(url="attachment://thumbnail.png")


pls_wait_embed = discord.Embed(
    title="LumianryAI - music",
    description="Please wait...",
    color=0xFF0000
)
pls_wait_embed.set_thumbnail(url="attachment://thumbnail.png")

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
def music(bot):
    @bot.command(name='join')
    @commands.cooldown(1, 20, commands.BucketType.user)
    async def join(ctx):
        if ctx.author.voice is None:

            await ctx.send(embed=join_first_embed)
            return

        # Get the bot's Member object
        bot_member = ctx.guild.get_member(bot.user.id)

        if ctx.voice_client is not None and ctx.voice_client.is_connected():

            await ctx.send(embed=already_joined)
            return
        else:
            channel = ctx.author.voice.channel

            # Check if the bot has necessary permissions in the voice channel
            required_permissions = ["connect", "speak", "send_messages"]
            missing_permissions = [perm for perm in required_permissions if not getattr(channel.permissions_for(bot_member), perm)]

            if missing_permissions:
                perms_embed = discord.Embed(
                    title="LumianryAI - missing perms",
                    description=f"I don't have the following permissions in the voice channel:\n{', '.join(missing_permissions)}",
                    color=0xFF0000
                )
                file = discord.File("images/music.png", filename="thumbnail.png")
                perms_embed.set_thumbnail(url="attachment://thumbnail.png")
                await ctx.send(embed=perms_embed, file=file)
                return

            if ctx.voice_client is None:
                voice_channel = await channel.connect()
                await ctx.guild.change_voice_state(channel=channel, self_mute=False, self_deaf=True)
            else:
                voice_channel = ctx.voice_client.channel

            joined_embed = discord.Embed(
                description=f"**Joined {channel}**",
                color=0x99ccff
            )
            await ctx.send(embed=joined_embed)




    server_loops = {}  # Dictionary to store loop status for each server

    @bot.command(name='loop')
    @commands.cooldown(1, 20, commands.BucketType.user)
    async def toggle_loop(ctx):
        server_id = ctx.guild.id
        if server_id not in server_loops:
            server_loops[server_id] = True  # Initialize loop status for the server if not present

            await ctx.send(embed=loop_enabled)
        elif server_loops[server_id] == True:
            server_loops[server_id] = False

            await ctx.send(embed=loop_disabled)
        elif server_loops[server_id] == False:
            server_loops[server_id] = True

            await ctx.send(embed=loop_enabled)

    @bot.command(name='play')
    @commands.cooldown(1, 15, commands.BucketType.user)
    async def play(ctx, *, song_name):
        server_id = ctx.guild.id
        if server_id not in server_loops:
            server_loops[server_id] = False


        file = discord.File("images/music.png", filename="thumbnail.png")
        wait = await ctx.send(embed=pls_wait_embed, file=file)

        if ctx.author.voice is None or ctx.author.voice.channel is None:
            await wait.edit(embed=join_first_embed)
            return

        channel = ctx.author.voice.channel
        voice_channel = ctx.voice_client

        # Check if the bot is already in a voice channel
        if voice_channel is None and channel is not None:
            await wait.edit(embed=not_in_voice)
            return
        if not voice_channel.is_playing():
            # Download the song information using yt_dlp
            ydl_opts = {'format': 'bestaudio', 'noplaylist': True, 'no_warnings': True}
            with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(f"ytsearch:{song_name}", download=False)
                video_url = info['entries'][0]['webpage_url']
                if 'entries' in info and info['entries']:
                    # Get the first entry (song) in the search results
                    first_entry = info['entries'][0]

                    # Extract the song name and video link and duration
                    song_name = first_entry.get('title', 'Unknown Title')
                    video_link = first_entry.get('url', 'Unknown Link')
                    duration = first_entry.get('duration', 0)

                    # Shorten the video link
                    shortened_video_link = shorten_url(video_link)
                    # Format the duration in a user-friendly way
                    duration_formatted = str(round(duration / 60, 2)) + " minutes"

                    # Play the song
                    # Wrap the FFmpegPCMAudio source with PCMVolumeTransformer
                    audio_source = discord.FFmpegPCMAudio(video_link, **FFMPEG_OPTIONS)
                    volume_transformer = discord.PCMVolumeTransformer(audio_source, volume=0.5)  # Default volume at 50%

                    voice_channel.play(volume_transformer)

                    playing_embed = discord.Embed(
                        title="LumianryAI - music",
                        description=f"Now playing: {song_name}\n\n [Video link]({video_url}) \n[Audio link]({shortened_video_link})\n Song duration: {duration_formatted}",
                        color=0x99ccff
                    )
                    file = discord.File("music.png", filename="thumbnail.png")
                    playing_embed.set_thumbnail(url="attachment://thumbnail.png")
                    await wait.edit(embed=playing_embed)
                    await asyncio.sleep(duration)  # Wait for the song to finish
                    loop = server_loops[server_id]  # Get loop status for the current server

                    while loop:
                        loop = server_loops[server_id]  # Get loop status for the current server
                        if loop:
                            voice_channel.stop()
                            voice_channel.play(discord.FFmpegPCMAudio(video_link, **FFMPEG_OPTIONS))
                            await asyncio.sleep(duration)  # Wait for the song to finish
                        elif loop == False and not voice_channel.is_playing():
                            await ctx.voice_client.disconnect()
                            break
                else:
                    await wait.edit(embed=no_result_embed)

        else:
            await wait.edit(embed=alread_playing)

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
        # Check if the bot is in a voice channel
        if ctx.voice_client is not None:
            # Check if the user is in the same voice channel as the bot
            if ctx.author.voice is not None and ctx.author.voice.channel == ctx.voice_client.channel:
                # Stop playing and disconnect from the voice channel
                ctx.voice_client.resume()

                await ctx.send(embed=playback_resumed)
            else:
                await ctx.send(embed=need_same_channel_to_stop)
        else:
            await ctx.send(embed=not_in_voice)


    @bot.command(name='volume')
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def volume(ctx, volume_str: str):
        # Check if the bot is in a voice channel
        if ctx.voice_client is not None:
            # Check if the user is in the same voice channel as the bot
            if ctx.author.voice is not None and ctx.author.voice.channel == ctx.voice_client.channel:
                try:
                    # Convert the volume from a percentage to a float (0.0 to 1.0)
                    volume_percentage = int(volume_str)
                    volume = volume_percentage / 100.0
                    # Set the volume; ensure it's within the valid range (0.0 to 1.0)
                    # if 0.0 <= volume <= 1.0:
                    ctx.voice_client.source.volume = volume
                    await ctx.send(embed=discord.Embed(description=f"**Volume has been successfully set to {volume_percentage}%**", color=0x99ccff))
                    # else:
                    #     await ctx.send(embed=discord.Embed(description="**Please provide an integer between 0 and 100 for the volume.**"))
                except ValueError:
                    await ctx.send(embed=discord.Embed(description="**Please provide a valid integer to set the volume.**\n\nExample:\n```ai.volume 70```", color=0x99ccff))
            else:
                await ctx.send(embed=need_same_channel_to_stop)
        else:
            await ctx.send(embed=not_in_voice)