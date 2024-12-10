import yt_dlp
import asyncio
import discord
import logging
from discord import Embed as em
from youtube_dl import YoutubeDL
from discord import Color as color
from discord.ui import View, Button
from concurrent.futures import ThreadPoolExecutor


# import spotipy
# from spotipy.oauth2 import SpotifyClientCredentials

log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

async def search(query: str, ctx):
    ydl_opts = {
        'format': 'bestaudio/best',
        'restrictfilenames': True,
        'noplaylist': True,
        'nocheckcertificate': True,
        'ignoreerrors': False,
        'logtostderr': False,
        'no_warnings': True,
        'default_search': 'auto',
        'source_address': '0.0.0.0',
        'quiet': True,
        'extract_flat': True
    }

    try:
        # Check if the query is a URL
        if query.startswith("https://"):
            with YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(query, download=False)

                if 'entries' in info:  # Handle playlists
                    entries = info['entries']
                    return [{
                        'id': entry.get('id', 'Unknown ID'),
                        'title': entry.get('title', 'No Title'),
                        'url': f'https://youtu.be/{entry.get("id", "Unknown ID")}',
                        'user_req': ctx.author
                    } for entry in entries if entry.get('id')]

                else:
                    return [{
                        'id': info.get('id', 'Unknown ID'),
                        'title': info.get('title', 'No Title'),
                        'url': f'https://youtu.be/{info.get("id", "Unknown ID")}',
                        'user_req': ctx.author
                    }]

        else:  # Handle search queries
            with YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(f"ytsearch{4}:{query}", download=False)
                entries = info.get('entries', [])
                return [{
                    'id': entry.get('id', 'Unknown ID'),
                    'title': entry.get('title', 'No Title'),
                    'url': f'https://youtu.be/{entry.get("id", "Unknown ID")}',
                    'user_req': ctx.author
                } for entry in entries if entry.get('id')]

    except Exception as e:
        print(f"An error occurred: {e}")
        print("Traceback:", exc_info=True)
        raise  # Re-raise the exception after logging        


# async def search_song(name, id, secret):
#     sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(
#         client_id=id,
#         client_secret=secret
#     ))

#     results = sp.search(q=name, type='track', limit=1)

#     # Check if we got any results
#     if results['tracks']['items']:
#         track = results['tracks']['items'][0]
#         duration_ms = track['duration_ms']
#         # Convert duration from milliseconds to minutes and seconds
#         minutes, seconds = divmod(duration_ms // 1000, 60)
#         duration = f"{minutes}:{seconds:02d}"

#         return {
#             'name': track['name'],
#             'artist': track['artists'][0]['name'],
#             'album': track['album']['name'],
#             'release_date': track['album']['release_date'],
#             'duration': duration,
#             'url': track['external_urls']['spotify']
#         }
#     else:
#         return None


            
async def get_audio_url(query):
    
    ydl_opts = {
        'format': 'bestaudio/best',
        'noplaylist': True,
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'postprocessor_args': [
            '-id3v2_version', '4',
        ],
        'prefer_ffmpeg': False,
        'username': 'oauth2',
        'password': '',
        'quiet': True,              # Suppress output
        'no_warnings': True,        # Suppress warnings
    }

    # Run yt-dlp in a separate thread
    loop = asyncio.get_event_loop()
    with ThreadPoolExecutor() as pool:
        result = await loop.run_in_executor(pool, lambda: yt_dlp.YoutubeDL(ydl_opts).extract_info(f"ytsearch:{query}", download=False)['entries'][0])

    title = result.get('title')
    url = result.get('webpage_url')
    channel = result.get('uploader')
    f_duration = result.get('duration')
    duration = result.get('duration')
    thumbnail = result.get('thumbnail')
    audiouri = result.get('url')

    return {
        'title': title,
        'url': url,
        'audiouri': audiouri,
        'channel': channel,
        'f_duration': f"{f_duration // 60}m {f_duration % 60}s",
        'duration': duration,
        'thumbnail': thumbnail
    }



guild_queues = {}
FFMPEG_OPTIONS = {
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
    'options': '-vn',
}

async def play_next_song(vc, ctx, bot, loop:bool = None):

    if ctx.guild.id in guild_queues and len(guild_queues[ctx.guild.id]) > 0:
        next_song = guild_queues[ctx.guild.id][0]
        audio_source = discord.FFmpegPCMAudio(next_song['audio_url'], **FFMPEG_OPTIONS)

        def after_playing(e):
            try: guild_queues[ctx.guild.id].pop(0)
            except Exception as e: pass
            if controls_view.repeat:
                # Re-add the last song to the queue for repeat mode
                guild_queues[ctx.guild.id].append(next_song)
                ctx.bot.loop.create_task(play_next_song(vc, ctx, bot, True))
            elif guild_queues[ctx.guild.id]:
                ctx.bot.loop.create_task(play_next_song(vc, ctx, bot))
            else:
                ctx.bot.loop.create_task(ctx.send(embed=em(description="> **The queue is empty. No more songs to play.**")))

        vc.play(audio_source, after=after_playing)

        embed = em(description=f"> **🎧 Now playing**: [`{next_song['title']}`]({next_song['url']})\n\n* Duration: `{next_song['f_duration']}`\n* Channel: `{next_song['channel']}`",color=color.purple())
        embed.set_image(url=next_song['thumbnail'])
        controls_view = Music_Controls(bot, ctx, guild_queues[ctx.guild.id], True) if loop else  Music_Controls(bot, ctx, guild_queues[ctx.guild.id])
        await ctx.send(embed=embed, view=controls_view, delete_after=next_song['duration'])
    else:
        await ctx.send(embed=em(description="> **The queue is empty. No more songs to play.**"))



class Music_Controls(View):
    def __init__(self, bot, ctx, queue, loop:bool = None):
        super().__init__(timeout=None)
        self.bot = bot
        self.ctx = ctx
        self.queue = queue
        self.votes = {
            'skip': {},
            'stop': {}
        }
        self.repeat = loop  # Initialize repeat status
        
        # Make Buttons
        self.show_queue_button = Button(emoji="📜", style=discord.ButtonStyle.green, custom_id="show_queue")
        self.toggle_play_pause_button = Button(emoji="⏸️", style=discord.ButtonStyle.primary, custom_id="toggle_play_pause")
        self.repeat_button = Button(emoji="🔁", style=discord.ButtonStyle.secondary, custom_id="repeat")
        self.vote_skip_button = Button(emoji="⏭️", style=discord.ButtonStyle.primary, custom_id="vote_skip")
        self.vote_stop_button = Button(emoji="🛑", style=discord.ButtonStyle.danger, custom_id="vote_stop")

        # Assign callbacks
        self.show_queue_button.callback = self.show_queue
        self.toggle_play_pause_button.callback = self.toggle_play_pause
        self.repeat_button.callback = self.toggle_repeat
        self.vote_skip_button.callback = self.vote_skip
        self.vote_stop_button.callback = self.vote_stop

        # Add buttons to the view
        self.add_item(self.show_queue_button)
        self.add_item(self.toggle_play_pause_button)
        self.add_item(self.repeat_button)
        self.add_item(self.vote_skip_button)
        self.add_item(self.vote_stop_button)

    async def show_queue(self, interaction: discord.Interaction):
        await interaction.response.defer()

        if self.queue:
            current_song = self.queue[0]  # The song currently playing
            queue_length = len(self.queue)
            
            start_index = max(queue_length - 5, 0)
            
            queue_list = []
            for idx, track in enumerate(self.queue[start_index:], start=start_index + 1):
                if track == current_song:
                    queue_list.append(f"**{idx}. {track['title']} (Currently playing)**")
                else:
                    queue_list.append(f"{idx}. {track['title']}")
            
            embed = em(description=f"Current queue:\n" + '\n'.join(queue_list), color=color.purple())
        else:
            embed = em(description="The queue is currently empty.",  color=color.purple())
        
        await interaction.followup.send(embed=embed, ephemeral=True)

    async def toggle_play_pause(self, interaction: discord.Interaction):
        await interaction.response.defer()
        vc = interaction.guild.voice_client
        user = interaction.user.mention
        if vc and vc.is_playing():
            vc.pause()
            self.toggle_play_pause_button.emoji = "▶️"
            self.toggle_play_pause_button.style = discord.ButtonStyle.secondary
            await interaction.message.edit(content=f"Playback paused by {user}.", view=self)
        elif vc and vc.is_paused():
            vc.resume()
            self.toggle_play_pause_button.emoji = "⏸️"
            self.toggle_play_pause_button.style = discord.ButtonStyle.primary
            await interaction.message.edit(content=f"Playback resumed by {user}.", view=self)
        else:
            await interaction.followup.send(content="No song is currently playing.", ephemeral=True)

    async def vote_skip(self, interaction: discord.Interaction):
        await interaction.response.defer()
        await self.vote(interaction, 'skip')

    async def vote_stop(self, interaction: discord.Interaction):
        await interaction.response.defer()
        await self.vote(interaction, 'stop')

    async def vote(self, interaction: discord.Interaction, action: str):
        vc = interaction.guild.voice_client
        if not vc:
            await interaction.followup.send(content="I'm not connected to a voice channel.", ephemeral=True)
            return

        user = interaction.user
        voice_channel = vc.channel
        member_count = len(voice_channel.members) - 1
        required_votes = (member_count // 2) + 1

        if user.id in self.votes[action]:
            self.votes[action].pop(user.id)
            vote_count = len(self.votes[action])
            await interaction.message.edit(content=f"Vote removed for {action}: {vote_count}/{required_votes} votes needed.", view=self)
        else:
            self.votes[action][user.id] = user
            vote_count = len(self.votes[action])

            if vote_count >= required_votes:
                if action == 'skip':
                    vc.stop()
                    await play_next_song(vc, self.ctx, self.bot)
                    await interaction.message.edit(content=f"Song skipped by vote", view=self)
                elif action == 'stop':
                    vc.stop()
                    guild_queues[self.ctx.guild.id].clear()
                    await interaction.message.edit(content=f"Playback stopped and queue cleared by vote", view=self)
                
                self.votes[action].clear()
            else:
                await interaction.message.edit(content=f"Voted to {action}: {vote_count}/{required_votes} votes needed.", view=self)
            
            await self.notify_and_request_votes(interaction, action)

    async def toggle_repeat(self, interaction: discord.Interaction):
        await interaction.response.defer()
        self.repeat = not self.repeat
        status = "enabled" if self.repeat else "disabled"
        await interaction.message.edit(content=f"Repeat mode has been {status}.", view=self)

    async def notify_and_request_votes(self, interaction: discord.Interaction, action: str):
        vc = interaction.guild.voice_client
        if not vc:
            await interaction.followup.send(content="I'm not connected to a voice channel.", ephemeral=True)
            return

        voice_channel = vc.channel
        member_list = [member for member in voice_channel.members if member != self.bot.user and not member.bot]
        channel_link = f"{self.ctx.channel.mention}"

        for member in member_list:
            if member != interaction.user:
                try:
                    await member.send(
                       f"> ( *Request* ) | **{interaction.user.mention}** wants to `{action}` the song.\n🔗 {channel_link}\n✅ Vote in the channel."
                    )
                except discord.Forbidden:
                    continue

        await interaction.followup.send(content=f"> ⏩ | A DM has been sent to other members of the voice channel to vote on {action}.", ephemeral=True)