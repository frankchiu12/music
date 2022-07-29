import discord
from discord.ext import commands
from youtubesearchpython import *
import youtube_dl
from dotenv import load_dotenv
import os

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
SERVER = os.getenv('DISCORD_SERVER')
bot = commands.Bot(command_prefix = '!')

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
    guild = discord.utils.get(bot.guilds, name = SERVER)
    voice = discord.utils.get(bot.voice_clients, guild = guild)
    if voice is not None:
        await voice.disconnect()
        await ctx.send('Disconnected.')
    else:
        await ctx.send('The music_bot is not connected to a voice channel.')

@bot.command(name = 'pause', help = 'Pause the music')
async def pause(ctx):
    guild = discord.utils.get(bot.guilds, name = SERVER)
    voice = discord.utils.get(bot.voice_clients, guild = guild)
    if voice is not None and voice.is_playing():
        voice.pause()
        await ctx.send('Paused.')
    else:
        await ctx.send('The music_bot is not currently playing.')

@bot.command(name = 'play', help = 'Play given a search query')
async def play(ctx, *search):
    voice_channel = discord.utils.get(ctx.guild.voice_channels, name = 'General')
    guild = discord.utils.get(bot.guilds, name = SERVER)
    voice = discord.utils.get(bot.voice_clients, guild = guild)

    await voice_channel.connect()

    search = ''.join(search)
    youtube_search = VideosSearch(search, limit = 1)
    youtube_URL = [youtube_search.result()['result'][0]['link']]

    print(youtube_URL)

    song_there = os.path.isfile('song.mp3')
    try:
        if song_there:
            os.remove('song.mp3')
    except PermissionError:
        await ctx.send('Wait for the current song to end.')
        return

    ydl_opts = {
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
        }
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        ydl.download(youtube_URL)

    for file in os.listdir('./'):
        if file.endswith('.mp3'):
            os.rename(file, 'song.mp3')
    voice.play(discord.FFmpegPCMAudio('song.mp3'))

    await ctx.send('Playing ...')

@play.error
async def play_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send('Please specify a song name.')

@bot.command(name = 'resume', help = 'Resume the music')
async def resume(ctx):
    guild = discord.utils.get(bot.guilds, name = SERVER)
    voice = discord.utils.get(bot.voice_clients, guild = guild)
    if voice is not None and voice.is_paused():
        voice.resume()
        await ctx.send('Resuming ...')
    else:
        await ctx.send('The music_bot is currently paused.')

bot.run(TOKEN)