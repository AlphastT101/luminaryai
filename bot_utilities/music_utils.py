import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import aiohttp

async def search_song(name, id, secret):
    sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(
        client_id=id,
        client_secret=secret
    ))

    results = sp.search(q=name, type='track', limit=1)

    # Check if we got any results
    if results['tracks']['items']:
        track = results['tracks']['items'][0]
        duration_ms = track['duration_ms']
        # Convert duration from milliseconds to minutes and seconds
        minutes, seconds = divmod(duration_ms // 1000, 60)
        duration = f"{minutes}:{seconds:02d}"

        return {
            'name': track['name'],
            'artist': track['artists'][0]['name'],
            'album': track['album']['name'],
            'release_date': track['album']['release_date'],
            'duration': duration,
            'url': track['external_urls']['spotify']
        }
    else:
        return None
    

async def get_audio_url(query):
    async with aiohttp.ClientSession() as session:
        async with session.get('https://audio.serveo.net/audio', params={'query': query}) as response:
            if response.status == 200:
                data = await response.json()
                return data
            else:
                return None