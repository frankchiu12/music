import discord
from discord.ext import commands, tasks
from dotenv import load_dotenv
import os
from youtubesearchpython import *
import youtube_dl
import spotipy
import spotipy.util as util
from lyricsgenius import Genius
import asyncio
import datetime
import random

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

current_song_id = ''
song_queue = []

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
    print('')

    on_inactivity.start()

@bot.command(name = 'hi', help = 'Respond to hi')
async def hi(ctx):
    await ctx.send('hi yvette! ☄️🍼🐣🐥🐎')

@bot.command(name = 'play', help = 'Play a song given a search query')
async def play(ctx, *search):
    voice = discord.utils.get(bot.voice_clients, guild = ctx.guild)
    if voice:
        await voice.disconnect()
        voice_channel = discord.utils.get(ctx.guild.voice_channels, name = 'General')
        voice = await voice_channel.connect()
    else:
        voice_channel = discord.utils.get(ctx.guild.voice_channels, name = 'General')
        voice = await voice_channel.connect()

    search = ' '.join(search)
    if search == '':
        await ctx.send('No search query. Please try again.')
    else:
        song_id = (sp.search(q = search, type = 'track', limit = 10))['tracks']['items'][0]['id']
        global current_song_id
        current_song_id = song_id
        spotify_song_name = sp.track(song_id)['name']
        spotify_song_main_artist = sp.track(song_id)['artists'][0]['name']
        artist_list = []
        for artist in sp.track(song_id)['artists']:
            artist_list.append(artist['name'])
        youtube_search = VideosSearch(spotify_song_name + ' ' + spotify_song_main_artist, limit = 1)
        youtube_url = youtube_search.result()['result'][0]['link']
        FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}
        ydl_options = {'format': 'bestaudio'}
        with youtube_dl.YoutubeDL(ydl_options) as ydl:
            song_information = ydl.extract_info(youtube_url, download = False)
            discord_url = song_information['formats'][0]['url']
            source = await discord.FFmpegOpusAudio.from_probe(discord_url, **FFMPEG_OPTIONS)
            voice.play(source, after = lambda e: asyncio.run(next(ctx)))
        await ctx.send('Playing **' + spotify_song_name + '** by ' + str(artist_list) + ' 😌')

@bot.command(name = 'get_info', help = 'Get song information')
async def information(ctx):
    song_id = current_song_id
    spotify_song_name = sp.track(song_id)['name']
    spotify_song_main_artist = sp.track(song_id)['artists'][0]['name']
    youtube_search = VideosSearch(spotify_song_name + ' ' + spotify_song_main_artist, limit = 1)
    youtube_url = youtube_search.result()['result'][0]['link']
    artist_name_list = []
    artist_id_list = []
    for artist in sp.track(song_id)['artists']:
        artist_name_list.append(artist['name'])
        artist_id_list.append(artist['id'])
    main_artist_id = artist_id_list[0]
    artist_image_URL =  sp.artist(main_artist_id)['images'][0]['url']
    song_image_URL = sp.track(song_id)['album']['images'][0]['url']
    song_name = sp.track(song_id)['name']
    album_name = sp.track(song_id)['album']['name']
    popularity = sp.track(song_id)['popularity']
    release_date = sp.track(song_id)['album']['release_date']
    duration = sp.track(song_id)['duration_ms']
    s, ms = divmod(duration, 1000)
    m, s = divmod(s, 60)
    if s == 0:
        s = '00'
    duration = str(m) + ':' + str(s)
    explicit = sp.track(song_id)['explicit']
    link = sp.track(song_id)['external_urls']['spotify']

    song_embed = discord.Embed(title = 'Song Information', color = discord.Colour.red())
    song_embed.set_author(name = ctx.author.display_name, icon_url = ctx.author.avatar_url)
    song_embed.set_thumbnail(url = artist_image_URL)
    song_embed.set_image(url = song_image_URL)
    song_embed.timestamp = datetime.datetime.utcnow()
    song_embed.set_footer(text = '\u200b', icon_url = 'https://ctl.s6img.com/society6/img/TXKHrMlteKoMhJdzwPP20QhBahk/w_700/wall-clocks/front/natural-frame/white-hands/~artwork,fw_3500,fh_3500,iw_3500,ih_3500/s6-0085/a/33579865_3499564/~~/red-pld-wall-clocks.jpg')
    song_embed.add_field(name = 'Song Name 🎵', value = song_name, inline = False)
    song_embed.add_field(name = 'Song Artists 🎨', value = artist_name_list, inline = False)
    song_embed.add_field(name = 'Album Name 🎶', value = album_name, inline = False)
    song_embed.add_field(name = 'Popularity 🔥', value = popularity, inline = False)
    song_embed.add_field(name = 'Release Date 🗓', value = release_date, inline = False)
    song_embed.add_field(name = 'Duration ⌛️', value = duration, inline = False)
    song_embed.add_field(name = 'Explicit 🤬', value = explicit, inline = False)
    song_embed.add_field(name = 'Link 🔗', value = link, inline = False)
    song_embed.add_field(name = 'YouTube 🎥', value = youtube_url, inline = False)
    await ctx.send(embed = song_embed)

    react_message = await ctx.send('React to this message for more commands ✅ (only one)')
    lyrics_emoji = '✍️'
    artist_emoji = '🎨'
    album_emoji = '🎶'
    valid_reactions = [lyrics_emoji, artist_emoji, album_emoji]
    await react_message.add_reaction(lyrics_emoji)
    await react_message.add_reaction(artist_emoji)
    await react_message.add_reaction(album_emoji)
    react_message = await ctx.channel.fetch_message(react_message.id)

    def check(reaction, user):
        return user == ctx.author and reaction.emoji in valid_reactions and reaction in react_message.reactions
    reaction, user = await bot.wait_for('reaction_add', timeout = 10, check = check)

    if str(reaction.emoji) == lyrics_emoji:
        song_name = sp.track(song_id)['name']
        if ' - From' in song_name:
            song_name = song_name.partition(' - From')[0]
        if ' (feat.' in song_name:
            song_name = song_name.partition(' (feat.')[0]
        if ' (with ' in song_name:
            song_name = song_name.partition(' (with ')[0]
        genius_searched_track = genius.search_song(song_name, artist_name_list[0])
        try:
            if genius_searched_track is None:
                await ctx.send('Unfortunately, no lyrics were found. 🥲')
            else:
                await ctx.send(genius_searched_track.lyrics)
        except discord.errors.HTTPException:
            await ctx.send('The lyrics exceeded the character limit of 2000. To view the lyrics, please follow the link: ' + genius_searched_track.url)

    if str(reaction.emoji) == artist_emoji:
        artist_id = main_artist_id
        genre_list = str(sp.artist(artist_id)['genres'])
        popularity = str(sp.artist(artist_id)['popularity'])
        total_followers = str(sp.artist(artist_id)['followers']['total'])
        related_artist_list = []
        for related_artist in sp.artist_related_artists(artist_id)['artists']:
            related_artist_list.append(related_artist['name'])
        link = sp.artist(artist_id)['external_urls']['spotify']
        artist_top_song_list = []
        counter = 1
        for song in sp.artist_top_tracks(artist_id)['tracks']:
            song_name = song['name']
            main_artist = song['artists'][0]['name']
            co_artist_list = []
            for co_artist in song['artists']:
                co_artist_list.append(co_artist['name'])
            if main_artist in co_artist_list:
                co_artist_list.remove(main_artist)
            if len(co_artist_list) != 0:
                artist_top_song_list.append(str(counter) + '. **' + song_name + '** with ' + str(co_artist_list))
            else:
                artist_top_song_list.append(str(counter) + '. **' + song_name + '**')
            counter += 1
        artist_top_song_string = '\n'.join(artist_top_song_list)
        artist_album_list = []
        counter = 1
        for album in sp.artist_albums(artist_id, limit = 10)['items']:
            album_name = album['name']
            total_songs = str(album['total_tracks'])
            artist_album_list.append(str(counter) + '. **' + album_name + '** with ' + total_songs + ' song(s)')
            counter += 1
        artist_album_string = '\n'.join(artist_album_list)

        artist_embed = discord.Embed(title = 'Artist Information', color = discord.Colour.blue())
        artist_embed.set_author(name = ctx.author.display_name, icon_url = ctx.author.avatar_url)
        artist_embed.set_image(url = artist_image_URL)
        artist_embed.timestamp = datetime.datetime.utcnow()
        artist_embed.set_footer(text = '\u200b', icon_url = 'https://www.kindpng.com/picc/m/567-5671142_clock-md-dodger-blue-clipart-png-blue-clock.png')
        artist_embed.add_field(name = 'Artist Name 🎨', value = artist_name_list[0], inline = False)
        artist_embed.add_field(name = 'Genres 📚', value = genre_list, inline = False)
        artist_embed.add_field(name = 'Popularity 🔥', value = popularity, inline = False)
        artist_embed.add_field(name = 'Total Followers ❤️', value = total_followers, inline = False)
        artist_embed.add_field(name = 'Related Artists 👥', value = related_artist_list, inline = False)
        artist_embed.add_field(name = 'Link 🔗', value = link, inline = False)
        artist_embed.add_field(name = 'Artist Top Songs 📈', value = artist_top_song_string, inline = False)
        artist_embed.add_field(name = 'Artist Albums 🎶', value = artist_album_string, inline = False)
        await ctx.send(embed = artist_embed)

    if str(reaction.emoji) == album_emoji:
        album_id = sp.track(song_id)['album']['id']
        album_image_URL = sp.album(album_id)['images'][0]['url']
        album_name = sp.album(album_id)['name']
        album_type = sp.album(album_id)['album_type']
        artist_list = []
        for artist in sp.album(album_id)['artists']:
            artist_list.append(artist['name'])
        release_date = sp.album(album_id)['release_date']
        total_songs = str(sp.album(album_id)['total_tracks'])
        genre_list = str(sp.album(album_id)['genres'])
        popularity = str(sp.album(album_id)['popularity'])
        label = str(sp.album(album_id)['label'])
        link = sp.album(album_id)['external_urls']['spotify']
        album_song_list = []
        counter = 1
        for song in sp.album_tracks(album_id)['items']:
            song_name = song['name']
            artist_list = []
            for artist in song['artists']:
                artist_list.append(artist['name'])
            album_song_list.append(str(counter) + '. **' + song_name + '** with ' + str(artist_list))
            counter += 1
            if counter > 10:
                break
        album_song_string = '\n'.join(album_song_list)

        album_embed = discord.Embed(title = 'Album Information', color = discord.Colour.green())
        album_embed.set_author(name = ctx.author.display_name, icon_url = ctx.author.avatar_url)
        album_embed.set_image(url = album_image_URL)
        album_embed.timestamp = datetime.datetime.utcnow()
        album_embed.set_footer(text = '\u200b', icon_url = 'https://www.iconsdb.com/icons/preview/green/clock-xxl.png')
        album_embed.add_field(name = 'Album Name 🎶', value = album_name, inline = False)
        album_embed.add_field(name = 'Album Type 📂', value = album_type, inline = False)
        album_embed.add_field(name = 'Album Artists 🎨', value = artist_list, inline = False)
        album_embed.add_field(name = 'Release Date 🗓', value = release_date, inline = False)
        album_embed.add_field(name = 'Total Songs 🔢', value = total_songs, inline = False)
        album_embed.add_field(name = 'Genres 📚', value = genre_list, inline = False)
        album_embed.add_field(name = 'Popularity 🔥', value = popularity, inline = False)
        album_embed.add_field(name = 'Label 🏷', value = label, inline = False)
        album_embed.add_field(name = 'Link 🔗', value = link, inline = False)
        album_embed.add_field(name = 'Album Songs 🎵', value = album_song_string, inline = False)
        await ctx.send(embed = album_embed)

@bot.command(name = 'resume', help = 'Resume the music')
async def resume(ctx):
    voice = discord.utils.get(bot.voice_clients, guild = ctx.guild)
    if voice and voice.is_paused():
        voice.resume()
        await ctx.send('Resuming ...')
    else:
        await ctx.send('The music_bot is already playing.')

@bot.command(name = 'pause', help = 'Pause the music')
async def pause(ctx):
    voice = discord.utils.get(bot.voice_clients, guild = ctx.guild)
    if voice and voice.is_playing():
        voice.pause()
        await ctx.send('Paused.')
    else:
        await ctx.send('The music_bot is not currently playing.')

@bot.command(name = 'disconnect', help = 'Disconnect the bot from the current voice channel')
async def disconnect(ctx):
    voice = discord.utils.get(bot.voice_clients, guild = ctx.guild)
    if voice:
        global song_queue
        song_queue = []
        await voice.disconnect()
        await ctx.send('Disconnected.')
    else:
        await ctx.send('The music_bot is not currently connected to a voice channel.')

@bot.command(name = 'queue', help = 'Queue a song given a search query')
async def queue(ctx, *search):
    search = ' '.join(search)
    if search == '':
        await ctx.send('No search query. Please try again.')
    else:
        song_id = (sp.search(q = search, type = 'track', limit = 10))['tracks']['items'][0]['id']
        song_queue.append(song_id)
        song_name = sp.track(song_id)['name']
        artist_list = []
        for artist in sp.track(song_id)['artists']:
            artist_list.append(artist['name'])
        await ctx.send('Added **' + song_name + '** by ' + str(artist_list) + ' 😉')

@bot.command(name = 'show_queue', help = 'Show the queue')
async def show_queue(ctx):
    song_queue_list = []
    counter = 1
    for song_id in song_queue:
        song_name = sp.track(song_id)['name']
        artist_list = []
        for artist in sp.track(song_id)['artists']:
            artist_list.append(artist['name'])
        song_queue_list.append(str(counter) + '. **' + song_name + '** by ' + str(artist_list))
        counter += 1
        if counter > 10:
            break
    song_queue_string = '\n'.join(song_queue_list)
    if song_queue_list == []:
        song_queue_string = 'No songs in queue. 🫡'

    song_queue_embed = discord.Embed(title = 'Song Queue', color = discord.Colour.lighter_grey())
    song_queue_embed.set_author(name = ctx.author.display_name, icon_url = ctx.author.avatar_url)
    song_queue_embed.set_image(url = 'https://upload.wikimedia.org/wikipedia/commons/7/74/Spotify_App_Logo.svg')
    song_queue_embed.timestamp = datetime.datetime.utcnow()
    song_queue_embed.set_footer(text = '\u200b', icon_url = 'https://foter.com/photos/245/unique-big-mirror-silver-wall-clock.jpg')
    song_queue_embed.add_field(name = 'List 📝', value = song_queue_string, inline = False)
    await ctx.send(embed = song_queue_embed)

@bot.command(name = 'clear_queue', help = 'Clear the entire song queue')
async def clear_queue(ctx):
    global song_queue
    song_queue = []
    await ctx.send('Queue clear. 🥺')

@bot.command(name = 'loop', help = 'Loop the current song')
async def loop(ctx):
    global song_queue
    await clear_queue(ctx)
    for i in range(100):
        song_queue.append(current_song_id)
    song_name = sp.track(current_song_id)['name']
    artist_list = []
    for artist in sp.track(current_song_id)['artists']:
        artist_list.append(artist['name'])
    await ctx.send('Looping **' + song_name + '** by ' + str(artist_list) + ' ♾')

@bot.command(name = 'shuffle', help = 'Shuffle the queue')
async def shuffle(ctx):
    global song_queue
    if song_queue == []:
        await ctx.send('No songs in queue. 🫡')
    else:
        random.shuffle(song_queue)
        await ctx.send('Shuffled! 😤')
        await show_queue(ctx)

async def next(ctx):
    if len(song_queue) != 0:
        next_song_id = song_queue.pop(0)
        global current_song_id
        current_song_id = next_song_id
        spotify_song_name = sp.track(next_song_id)['name']
        spotify_song_main_artist = sp.track(next_song_id)['artists'][0]['name']
        youtube_search = VideosSearch(spotify_song_name + ' ' + spotify_song_main_artist, limit = 1)
        youtube_url = youtube_search.result()['result'][0]['link']
        FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}
        ydl_options = {'format': 'bestaudio'}
        with youtube_dl.YoutubeDL(ydl_options) as ydl:
            song_information = ydl.extract_info(youtube_url, download = False)
            discord_url = song_information['formats'][0]['url']
            source = await discord.FFmpegOpusAudio.from_probe(discord_url, **FFMPEG_OPTIONS)
            voice = discord.utils.get(bot.voice_clients, guild = ctx.guild)
            if not voice:
                voice_channel = discord.utils.get(ctx.guild.voice_channels, name = 'General')
                voice = await voice_channel.connect()
            voice.play(source, after = lambda e: asyncio.run(next(ctx)))

@bot.command(name = 'skip', help = 'Skip the current song')
async def skip(ctx): 
    voice = discord.utils.get(bot.voice_clients, guild = ctx.guild)
    if voice:
        await voice.disconnect()
        voice_channel = discord.utils.get(ctx.guild.voice_channels, name = 'General')
        voice = await voice_channel.connect()
        await ctx.send('Skipping ... 🥰')
    else:
        await ctx.send('The music_bot is not currently playing.')

@bot.command(name = 'artist', help = 'Search up artist information')
async def artist(ctx, *search):
    search = ' '.join(search)
    if search == '':
        await ctx.send('No search query. Please try again.')
    else:
        artist_id = sp.search(q = search, type = 'artist')['artists']['items'][0]['id']
        artist_image_URL =  sp.artist(artist_id)['images'][0]['url']
        artist_name = sp.artist(artist_id)['name']
        genre_list = str(sp.artist(artist_id)['genres'])
        popularity = str(sp.artist(artist_id)['popularity'])
        total_followers = str(sp.artist(artist_id)['followers']['total'])
        related_artist_list = []
        for related_artist in sp.artist_related_artists(artist_id)['artists']:
            related_artist_list.append(related_artist['name'])
        link = sp.artist(artist_id)['external_urls']['spotify']
        artist_top_song_list = []
        counter = 1
        for song in sp.artist_top_tracks(artist_id)['tracks']:
            song_name = song['name']
            main_artist = song['artists'][0]['name']
            co_artist_list = []
            for co_artist in song['artists']:
                co_artist_list.append(co_artist['name'])
            if main_artist in co_artist_list:
                co_artist_list.remove(main_artist)
            if len(co_artist_list) != 0:
                artist_top_song_list.append(str(counter) + '. **' + song_name + '** with ' + str(co_artist_list))
            else:
                artist_top_song_list.append(str(counter) + '. **' + song_name + '**')
            counter += 1
        artist_top_song_string = '\n'.join(artist_top_song_list)
        artist_album_list = []
        counter = 1
        for album in sp.artist_albums(artist_id, limit = 10)['items']:
            album_name = album['name']
            total_songs = str(album['total_tracks'])
            artist_album_list.append(str(counter) + '. **' + album_name + '** with ' + total_songs + ' song(s)')
            counter += 1
        artist_album_string = '\n'.join(artist_album_list)

        artist_embed = discord.Embed(title = 'Artist Information', color = discord.Colour.blue())
        artist_embed.set_author(name = ctx.author.display_name, icon_url = ctx.author.avatar_url)
        artist_embed.set_image(url = artist_image_URL)
        artist_embed.timestamp = datetime.datetime.utcnow()
        artist_embed.set_footer(text = '\u200b', icon_url = 'https://www.kindpng.com/picc/m/567-5671142_clock-md-dodger-blue-clipart-png-blue-clock.png')
        artist_embed.add_field(name = 'Artist Name 🎨', value = artist_name, inline = False)
        artist_embed.add_field(name = 'Genres 📚', value = genre_list, inline = False)
        artist_embed.add_field(name = 'Popularity 🔥', value = popularity, inline = False)
        artist_embed.add_field(name = 'Total Followers ❤️', value = total_followers, inline = False)
        artist_embed.add_field(name = 'Related Artists 👥', value = related_artist_list, inline = False)
        artist_embed.add_field(name = 'Link 🔗', value = link, inline = False)
        artist_embed.add_field(name = 'Artist Top Songs 📈', value = artist_top_song_string, inline = False)
        artist_embed.add_field(name = 'Artist Albums 🎶', value = artist_album_string, inline = False)
        await ctx.send(embed = artist_embed)

@bot.command(name = 'album', help = 'Search up album information')
async def album(ctx, *search):
    search = ' '.join(search)
    if search == '':
        await ctx.send('No search query. Please try again.')
    else:
        album_id = sp.search(q = search, type = 'album', limit = 10)['albums']['items'][0]['id']
        album_image_URL = sp.album(album_id)['images'][0]['url']
        album_name = sp.album(album_id)['name']
        album_type = sp.album(album_id)['album_type']
        artist_list = []
        for artist in sp.album(album_id)['artists']:
            artist_list.append(artist['name'])
        release_date = sp.album(album_id)['release_date']
        total_songs = str(sp.album(album_id)['total_tracks'])
        genre_list = str(sp.album(album_id)['genres'])
        popularity = str(sp.album(album_id)['popularity'])
        label = str(sp.album(album_id)['label'])
        link = sp.album(album_id)['external_urls']['spotify']
        album_song_list = []
        counter = 1
        for song in sp.album_tracks(album_id)['items']:
            song_name = song['name']
            artist_list = []
            for artist in song['artists']:
                artist_list.append(artist['name'])
            album_song_list.append(str(counter) + '. **' + song_name + '** with ' + str(artist_list))
            counter += 1
            if counter > 10:
                break
        album_song_string = '\n'.join(album_song_list)

        album_embed = discord.Embed(title = 'Album Information', color = discord.Colour.green())
        album_embed.set_author(name = ctx.author.display_name, icon_url = ctx.author.avatar_url)
        album_embed.set_image(url = album_image_URL)
        album_embed.timestamp = datetime.datetime.utcnow()
        album_embed.set_footer(text = '\u200b', icon_url = 'https://www.iconsdb.com/icons/preview/green/clock-xxl.png')
        album_embed.add_field(name = 'Album Name 🎶', value = album_name, inline = False)
        album_embed.add_field(name = 'Album Type 📂', value = album_type, inline = False)
        album_embed.add_field(name = 'Album Artists 🎨', value = artist_list, inline = False)
        album_embed.add_field(name = 'Release Date 🗓', value = release_date, inline = False)
        album_embed.add_field(name = 'Total Songs 🔢', value = total_songs, inline = False)
        album_embed.add_field(name = 'Genres 📚', value = genre_list, inline = False)
        album_embed.add_field(name = 'Popularity 🔥', value = popularity, inline = False)
        album_embed.add_field(name = 'Label 🏷', value = label, inline = False)
        album_embed.add_field(name = 'Link 🔗', value = link, inline = False)
        album_embed.add_field(name = 'Album Songs 🎵', value = album_song_string, inline = False)
        await ctx.send(embed = album_embed)

@bot.command(name = 'playlist', help = 'Search up playlist information')
async def playlist(ctx, *search):
    search = ' '.join(search)
    if search == '':
        await ctx.send('No search query. Please try again.')
    else:
        playlist_id = sp.search(q = search, type = 'playlist', limit = 10)['playlists']['items'][0]['id']
        playlist_image_URL = sp.playlist(playlist_id)['images'][0]['url']
        playlist_name = sp.playlist(playlist_id)['name']
        playlist_description = sp.playlist(playlist_id)['description']
        if playlist_description == '':
            playlist_description = 'N/A'
        playlist_owner = sp.playlist(playlist_id)['owner']['display_name']
        total_followers = sp.playlist(playlist_id)['followers']['total']
        playlist_song_list = []
        counter = 1
        for song in sp.playlist_tracks(playlist_id)['items']:
            song_name = song['track']['name']
            artist_list = []
            for artist in song['track']['artists']:
                artist_list.append(artist['name'])
            playlist_song_list.append(str(counter) + '. **' + song_name + '** with ' + str(artist_list))
            counter += 1
            if counter > 10:
                break
        playlist_song_string = '\n'.join(playlist_song_list)

        playlist_embed = discord.Embed(title = 'Playlist Information', color = discord.Colour.purple())
        playlist_embed.set_author(name = ctx.author.display_name, icon_url = ctx.author.avatar_url)
        playlist_embed.set_image(url = playlist_image_URL)
        playlist_embed.timestamp = datetime.datetime.utcnow()
        playlist_embed.set_footer(text = '\u200b', icon_url = 'https://i.pinimg.com/736x/8d/34/a2/8d34a201ca7e25b9efebf16bd6c5d217.jpg')
        playlist_embed.add_field(name = 'Playlist Name 🎶', value = playlist_name, inline = False)
        playlist_embed.add_field(name = 'Playlist Description 📝', value = playlist_description, inline = False)
        playlist_embed.add_field(name = 'Playlist Owner 🎨', value = playlist_owner, inline = False)
        playlist_embed.add_field(name = 'Total Followers ❤️', value = total_followers, inline = False)
        playlist_embed.add_field(name = 'Playlist Songs 🎵', value = playlist_song_string, inline = False)
        await ctx.send(embed = playlist_embed)

@bot.command(name = 'featured', help = 'Search up featured playlist releases on Spotify')
async def featured(ctx):
    featured_playlist_list = []
    counter = 1
    for playlist in sp.featured_playlists()['playlists']['items']:
        playlist_name = playlist['name']
        playlist_owner = playlist['owner']['display_name']
        featured_playlist_list.append(str(counter) + '. **' + playlist_name + '** by ' + playlist_owner)
        counter += 1
    featured_playlist_string = '\n'.join(featured_playlist_list)

    featured_playlist_embed = discord.Embed(title = 'Featured Releases (Spotify)', color = discord.Colour.gold())
    featured_playlist_embed.set_author(name = ctx.author.display_name, icon_url = ctx.author.avatar_url)
    featured_playlist_embed.set_image(url = 'https://storage.googleapis.com/pr-newsroom-wp/1/2021/03/SPOTIFY_US_FOR-THE-RECORD_PR-ASSET_032521_V2_CF-01.jpg')
    featured_playlist_embed.timestamp = datetime.datetime.utcnow()
    featured_playlist_embed.set_footer(text = '\u200b', icon_url = 'https://cdn2.vectorstock.com/i/1000x1000/87/86/happy-new-year-background-gold-clock-vector-11288786.jpg')
    featured_playlist_embed.add_field(name = 'List 📝', value = featured_playlist_string, inline = False)
    await ctx.send(embed = featured_playlist_embed)

@bot.command(name = 'new', help = 'Search up new album releases on Spotify')
async def new(ctx):
    newly_released_album_list = []
    counter = 1
    for album in sp.new_releases()['albums']['items']:
        album_name = album['name']
        artist_list = []
        for artist in album['artists']:
            artist_list.append(artist['name'])
        newly_released_album_list.append(str(counter) + '. **' + album_name + '** with ' + str(artist_list))
        counter += 1
    newly_released_album_string = '\n'.join(newly_released_album_list)

    newly_released_album_embed = discord.Embed(title = 'New Releases (Spotify)', color = discord.Colour.magenta())
    newly_released_album_embed.set_author(name = ctx.author.display_name, icon_url = ctx.author.avatar_url)
    newly_released_album_embed.set_image(url = 'https://storage.googleapis.com/pr-newsroom-wp/1/2019/10/New-Release-Burst2.jpg')
    newly_released_album_embed.timestamp = datetime.datetime.utcnow()
    newly_released_album_embed.set_footer(text = '\u200b', icon_url = 'https://ctl.s6img.com/society6/img/DvR8-sYQam2esV_naOzeLUsGEos/w_700/wall-clocks/front/natural-frame/white-hands/~artwork,fw_3500,fh_3500,fy_-10,iw_3500,ih_3519/s6-original-art-uploads/society6/uploads/misc/7f800cefc518478dab4727b0325fa404/~~/megenta-wall-clocks.jpg')
    newly_released_album_embed.add_field(name = 'List 📝', value = newly_released_album_string, inline = False)
    await ctx.send(embed = newly_released_album_embed)

@tasks.loop(seconds = 20)
async def on_inactivity():
    guild = discord.utils.get(bot.guilds, name = SERVER)
    voice = discord.utils.get(bot.voice_clients, guild = guild)
    if voice:
        if not voice.is_playing() and not voice.is_paused():
            await voice.disconnect()

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        await ctx.send('That command doesn\'t exist.')
    elif isinstance(error, commands.CommandInvokeError):
        await ctx.send('An error has occurred. Please try again. 😟')
    else:
        # TODO: change to pass
        print(error)

@play.error
async def client_exception_error(ctx, error):
    if isinstance(error, discord.errors.ClientException):
        await ctx.send('An error has occurred. Please try again. 😟')

@skip.error
async def client_exception_error(ctx, error):
    if isinstance(error, discord.errors.ClientException):
        await ctx.send('An error has occurred. Please try again. 😟')

bot.run(TOKEN)

# https://stackoverflow.com/questions/67722188/add-button-components-to-a-message-discord-py, https://www.youtube.com/watch?v=NtoMyB8XcQU

# discord.errors.ClientException: Not connected to voice. and # 403