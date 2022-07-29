from dis import dis
import discord
from discord.ext import commands
from dotenv import load_dotenv
from youtubesearchpython import *
import youtube_dl
import spotipy
import spotipy.util as util
from lyricsgenius import Genius
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
    voice_channel = discord.utils.get(ctx.guild.voice_channels, name = 'General')
    await voice_channel.connect()
    voice = discord.utils.get(bot.voice_clients, guild = ctx.guild)

    search = ' '.join(search)
    spotify_id = (sp.search(q = search, type = 'track', limit = 10))['tracks']['items'][0]['id']
    youtube_search = VideosSearch(spotify_id, limit = 1)
    youtube_url = youtube_search.result()['result'][0]['link']
    ydl_options = {'format': 'bestaudio'}

    with youtube_dl.YoutubeDL(ydl_options) as ydl:
        song_information = ydl.extract_info(youtube_url, download = False)
        discord_url = song_information['formats'][0]['url']
        source = await discord.FFmpegOpusAudio.from_probe(discord_url)
        voice.play(source)

    await ctx.send('Playing ...')
    print(ctx.author.color)
    embed = discord.Embed(title = 'Song Information', color = ctx.author.color)
    song_name = sp.track(spotify_id)['name']
    artist_list = []
    for artist in sp.track(id)['artists']:
        artist_list.append(artist['name'])
    embed.add_field(name = 'Song Name', value = song_name, inline = True)
    embed.add_field(name = 'Song Artist', value = artist_list, inline = True)
    await ctx.send(embed = embed)

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
        await ctx.send('The music_bot is currently paused.')

bot.run(TOKEN)

#