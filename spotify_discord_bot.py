import discord
from discord.ext import commands
from dotenv import load_dotenv
from youtubesearchpython import *
import youtube_dl
import spotipy
import spotipy.util as util
from lyricsgenius import Genius
import datetime
import os

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
SERVER = os.getenv('DISCORD_SERVER')
bot = commands.Bot(command_prefix = '!')

username = 'chiusiun'
scope = 'user-read-currently-playing user-modify-playback-state user-read-playback-state user-read-recently-played user-top-read user-library-modify user-library-read'
client_id = '3aa6dc3eea4b485497c73da406f11802'
client_secret = 'c08afd7602b740589ccf5198eb2982a2'
redirect_URI = 'http://google.com/'
spotify_token = util.prompt_for_user_token(username, scope, client_id, client_secret, redirect_URI)
sp = spotipy.Spotify(auth = spotify_token)

genius_token = 'Q8q2Cs-4YkZT_83az4gYWpQrkSthadNOWMeuJhJOmHmIB3sBj3_HMX9SY2gR2HC5'
genius = Genius(genius_token)

@bot.event
async def on_ready():
    guild = discord.utils.get(bot.guilds, name = SERVER)

    print('\033c', end = None)
    term_size = os.get_terminal_size()
    print('=' * term_size.columns + '\n')

    print(
        f'{bot.user.name} has connected to Discord! \n'
        f'{guild.name} (id: {guild.id}) \n'
    )

    members = '\n - '.join([member.name for member in guild.members])
    print(f'Guild Members:\n - {members}')
    print('\n')

@bot.command(name = 'hi', help = 'Responds to hi')
async def hi(ctx):
    response = 'hi! 🐣'
    await ctx.send(response)

@bot.command(name = 'disconnect', help = 'Make the bot disconnect from the current voice channel')
async def disconnect(ctx):
    voice = discord.utils.get(bot.voice_clients, guild = ctx.guild)
    if voice is not None:
        await voice.disconnect()
        await ctx.send('Disconnected.')
    else:
        await ctx.send('The music_bot is not connected to a voice channel.')

@bot.command(name = 'pause', help = 'Pause the music')
async def pause(ctx):
    voice = discord.utils.get(bot.voice_clients, guild = ctx.guild)
    if voice is not None and voice.is_playing():
        voice.pause()
        await ctx.send('Paused.')
    else:
        await ctx.send('The music_bot is not currently playing.')

song_file_path = 'song.mp3'

@bot.command(name = 'play', help = 'Play given a search query')
async def play(ctx, *search):
    voice = discord.utils.get(bot.voice_clients, guild=ctx.guild)
    if voice:
        await ctx.send('Already playing a song. Skip the current song?')
        return
    else:
        voice_channel = discord.utils.get(ctx.guild.voice_channels, name = 'General')
        voice = await voice_channel.connect()

    search = ' '.join(search)
    spotify_id = (sp.search(q = search, type = 'track', limit = 10))['tracks']['items'][0]['id']
    youtube_search = VideosSearch(spotify_id, limit = 1)
    youtube_url = youtube_search.result()['result'][0]['link']
    FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}
    ydl_options = {'format': 'bestaudio'}

    with youtube_dl.YoutubeDL(ydl_options) as ydl:
        song_information = ydl.extract_info(youtube_url, download = False)
        discord_url = song_information['formats'][0]['url']
        source = await discord.FFmpegOpusAudio.from_probe(discord_url, **FFMPEG_OPTIONS)
        voice.play(source)

    await ctx.send('Playing ... 😌')

    embed = discord.Embed(title = 'Song Information', color = discord.Colour.blue())
    artist_name_list = []
    artist_id_list = []
    for artist in sp.track(spotify_id)['artists']:
        artist_name_list.append(artist['name'])
        artist_id_list.append(artist['id'])
    artist_image_URL =  sp.artist(artist_id_list[0])['images'][0]['url']
    song_image_URL = sp.track(spotify_id)['album']['images'][0]['url']
    song_name = sp.track(spotify_id)['name']
    album_name = sp.track(spotify_id)['album']['name']
    popularity = sp.track(spotify_id)['popularity']
    release_date = sp.track(spotify_id)['album']['release_date']
    duration = sp.track(spotify_id)['duration_ms']
    s, ms = divmod(duration, 1000)
    m, s = divmod(s, 60)
    if s == 0:
        s = '00'
    duration = str(m) + ':' + str(s)
    explicit = sp.track(spotify_id)['explicit']
    embed.set_author(name = ctx.author.display_name, icon_url = ctx.author.avatar_url)
    embed.set_thumbnail(url = artist_image_URL)
    embed.set_image(url = song_image_URL)
    embed.timestamp = datetime.datetime.utcnow()
    embed.set_footer(text = '\u200b', icon_url = 'https://d2gg9evh47fn9z.cloudfront.net/800px_COLOURBOX5629612.jpg')
    embed.add_field(name = 'Song Name 🎹', value = song_name, inline = False)
    embed.add_field(name = 'Song Artist 🎨', value = artist_name_list, inline = False)
    embed.add_field(name = 'Album Name 🎶', value = album_name, inline = False)
    embed.add_field(name = 'Popularity 🔥', value = popularity, inline = False)
    embed.add_field(name = 'Release Date 🗓', value = release_date, inline = False)
    embed.add_field(name = 'Duration ⌛️', value = duration, inline = False)
    embed.add_field(name = 'Explicit 🤬', value = explicit, inline = False)
    await ctx.send(embed = embed)

    message = await ctx.send('React to this message for more commands ✅')
    lyrics_emoji = '✍️'
    artist_emoji = '🎨'
    valid_reactions = [lyrics_emoji, artist_emoji]
    while True:
        def check(reaction, user):
            return user == ctx.author and str(reaction.emoji) in valid_reactions
        reaction, user = await bot.wait_for('reaction_add', timeout=60.0, check=check)
        if str(reaction.emoji) == lyrics_emoji:
            if ' - From' in song_name:
                song_name = song_name.partition(' - From')[0]
            if ' (feat.' in song_name:
                song_name = song_name.partition(' (feat.')[0]
            if ' (with ' in song_name:
                song_name = song_name.partition(' (with ')[0]
            genius_searched_track = genius.search_song(song_name, artist_name_list[0])
            await ctx.send(genius_searched_track.lyrics)
        if str(reaction.emoji) == artist_emoji:
            pass

@play.error
async def play_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send('Please specify a song name.')
    else:
        print(error)

@bot.command(name = 'resume', help = 'Resume the music')
async def resume(ctx):
    voice = discord.utils.get(bot.voice_clients, guild = ctx.guild)
    if voice is not None and voice.is_paused():
        voice.resume()
        await ctx.send('Resuming ...')
    else:
        await ctx.send('The music_bot is already playing.')

bot.run(TOKEN)

# https://stackoverflow.com/questions/61019583/count-reactions-on-message-and-perform-action-after-there-is-a-certain-amount-of