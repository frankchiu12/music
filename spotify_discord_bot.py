import discord
from discord.ext import commands
from dotenv import load_dotenv
import os
from youtubesearchpython import *
import youtube_dl
import spotipy
import spotipy.util as util
from lyricsgenius import Genius
import datetime

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
    print('')

@bot.command(name = 'hi', help = 'Respond to hi')
async def hi(ctx):
    await ctx.send('hi! ☄️🍼🐣🐥🐎')

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
    song_id = (sp.search(q = search, type = 'track', limit = 10))['tracks']['items'][0]['id']
    spotify_track_name = sp.track(song_id)['name']
    spotify_track_main_artist = sp.track(song_id)['artists'][0]['name']
    youtube_search = VideosSearch(spotify_track_name + ' ' + spotify_track_main_artist, limit = 1)
    youtube_url = youtube_search.result()['result'][0]['link']
    FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}
    ydl_options = {'format': 'bestaudio'}
    with youtube_dl.YoutubeDL(ydl_options) as ydl:
        song_information = ydl.extract_info(youtube_url, download = False)
        discord_url = song_information['formats'][0]['url']
        source = await discord.FFmpegOpusAudio.from_probe(discord_url, **FFMPEG_OPTIONS)
        voice.play(source)
    await ctx.send('Playing ... 😌')

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
    song_embed.set_footer(text = '\u200b', icon_url = 'https://d2gg9evh47fn9z.cloudfront.net/800px_COLOURBOX5629612.jpg')
    song_embed.add_field(name = 'Song Name 🎹', value = song_name, inline = False)
    song_embed.add_field(name = 'Song Artists 🎨', value = artist_name_list, inline = False)
    song_embed.add_field(name = 'Album Name 🎶', value = album_name, inline = False)
    song_embed.add_field(name = 'Popularity 🔥', value = popularity, inline = False)
    song_embed.add_field(name = 'Release Date 🗓', value = release_date, inline = False)
    song_embed.add_field(name = 'Duration ⌛️', value = duration, inline = False)
    song_embed.add_field(name = 'Explicit 🤬', value = explicit, inline = False)
    song_embed.add_field(name = 'Link 🔗', value = link, inline = False)
    await ctx.send(embed = song_embed)

    message = await ctx.send('React to this message for more commands ✅')
    lyrics_emoji = '✍️'
    artist_emoji = '🎨'
    album_emoji = '💽'
    valid_reactions = [lyrics_emoji, artist_emoji, album_emoji]
    while True:
        def check(reaction, user):
            return user == ctx.author and str(reaction.emoji) in valid_reactions
        reaction, user = await bot.wait_for('reaction_add', timeout = 60.0, check = check)

        if str(reaction.emoji) == lyrics_emoji:
            song_name = sp.track(song_id)['name']
            if ' - From' in song_name:
                song_name = song_name.partition(' - From')[0]
            if ' (feat.' in song_name:
                song_name = song_name.partition(' (feat.')[0]
            if ' (with ' in song_name:
                song_name = song_name.partition(' (with ')[0]
            genius_searched_track = genius.search_song(song_name, artist_name_list[0])
            await ctx.send(genius_searched_track.lyrics)

        if str(reaction.emoji) == artist_emoji:
            genre_list = str(sp.artist(main_artist_id)['genres'])
            popularity = str(sp.artist(main_artist_id)['popularity'])
            total_followers = str(sp.artist(main_artist_id)['followers']['total'])
            related_artist_list = []
            for related_artist in sp.artist_related_artists(main_artist_id)['artists']:
                related_artist_list.append(related_artist['name'])
            link = sp.artist(main_artist_id)['external_urls']['spotify']
            artist_top_song_list = []
            counter = 1
            for song in sp.artist_top_tracks(main_artist_id)['tracks']:
                    song_name = song['name']
                    main_artist = song['artists'][0]['name']
                    co_artist_list = []
                    for co_artist in song['artists']:
                        co_artist_list.append(co_artist['name'])
                    if main_artist in co_artist_list:
                        co_artist_list.remove(main_artist)
                    if len(co_artist_list) != 0:
                        artist_top_song_list.append(str(counter) + '. ' + song_name + ' with ' + str(co_artist_list))
                    else:
                        artist_top_song_list.append(str(counter) + '. ' + song_name)
                    counter += 1
            artist_top_song_string = '\n'.join(artist_top_song_list)
            artist_album_list = []
            counter = 1
            for album in sp.artist_albums(main_artist_id, limit = 10)['items']:
                album_name = album['name']
                total_tracks = str(album['total_tracks'])
                artist_album_list.append(str(counter) + '. ' + album_name + ' with ' + total_tracks + ' song(s)')
                counter += 1
            artist_album_string = '\n'.join(artist_album_list)

            album_embed = discord.Embed(title = 'Artist Information', color = discord.Colour.blue())
            album_embed.set_author(name = ctx.author.display_name, icon_url = ctx.author.avatar_url)
            album_embed.set_thumbnail(url = song_image_URL)
            album_embed.set_image(url = artist_image_URL)
            album_embed.timestamp = datetime.datetime.utcnow()
            album_embed.set_footer(text = '\u200b', icon_url = 'https://d2gg9evh47fn9z.cloudfront.net/800px_COLOURBOX5629612.jpg')
            album_embed.add_field(name = 'Artist Name 🎨', value = artist_name_list[0], inline = False)
            album_embed.add_field(name = 'Genres 📚', value = genre_list, inline = False)
            album_embed.add_field(name = 'Popularity 🔥', value = popularity, inline = False)
            album_embed.add_field(name = 'Total Followers ❤️', value = total_followers, inline = False)
            album_embed.add_field(name = 'Related Artists 👥', value = related_artist_list, inline = False)
            album_embed.add_field(name = 'Link 🔗', value = link, inline = False)
            album_embed.add_field(name = 'Artist Top Songs 📈', value = artist_top_song_string, inline = False)
            album_embed.add_field(name = 'Artist Album 🎶', value = artist_album_string, inline = False)
            await ctx.send(embed = album_embed)

        if str(reaction.emoji) == album_emoji:
            album_id = sp.track(song_id)['album']['id']
            album_type = sp.album(album_id)['album_type']
            artist_list = []
            for artist in sp.album(album_id)['artists']:
                artist_list.append(artist['name'])
            release_date = sp.album(album_id)['release_date']
            total_tracks = str(sp.album(album_id)['total_tracks'])
            genre_list = str(sp.album(album_id)['genres'])
            popularity = str(sp.album(album_id)['popularity'])
            label = str(sp.album(album_id)['label'])
            link = sp.album(album_id)['external_urls']['spotify']
            album_image_URL = sp.album(album_id)['images'][0]['url']
            album_song_list = []
            counter = 1
            for song in sp.album_tracks(album_id)['items']:
                song_name = song['name']
                artist_list = []
                for artist in song['artists']:
                    artist_list.append(artist['name'])
                album_song_list.append(str(counter) + '. ' + song_name + ' with ' + str(artist_list))
                counter += 1
            album_song_string = '\n'.join(album_song_list)

            album_embed = discord.Embed(title = 'Album Information', color = discord.Colour.green())
            album_embed.set_author(name = ctx.author.display_name, icon_url = ctx.author.avatar_url)
            album_embed.set_thumbnail(url = song_image_URL)
            album_embed.set_image(url = album_image_URL)
            album_embed.timestamp = datetime.datetime.utcnow()
            album_embed.set_footer(text = '\u200b', icon_url = 'https://d2gg9evh47fn9z.cloudfront.net/800px_COLOURBOX5629612.jpg')
            album_embed.add_field(name = 'Album Name 🎶', value = album_name, inline = False)
            album_embed.add_field(name = 'Album Type 📂', value = album_type, inline = False)
            album_embed.add_field(name = 'Album Artists 🎨', value = artist_list, inline = False)
            album_embed.add_field(name = 'Release Date 🗓', value = release_date, inline = False)
            album_embed.add_field(name = 'Total Tracks', value = total_tracks, inline = False)
            album_embed.add_field(name = 'Genres 📚', value = genre_list, inline = False)
            album_embed.add_field(name = 'Popularity 🔥', value = popularity, inline = False)
            album_embed.add_field(name = 'Label', value = label, inline = False)
            album_embed.add_field(name = 'Link 🔗', value = link, inline = False)
            album_embed.add_field(name = 'Album Songs 🎵', value = album_song_string, inline = False)
            await ctx.send(embed = album_embed)

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

@bot.command(name = 'pause', help = 'Pause the music')
async def pause(ctx):
    voice = discord.utils.get(bot.voice_clients, guild = ctx.guild)
    if voice is not None and voice.is_playing():
        voice.pause()
        await ctx.send('Paused.')
    else:
        await ctx.send('The music_bot is not currently playing.')

@bot.command(name = 'disconnect', help = 'Disconnect the bot from the current voice channel')
async def disconnect(ctx):
    voice = discord.utils.get(bot.voice_clients, guild = ctx.guild)
    if voice is not None:
        await voice.disconnect()
        await ctx.send('Disconnected.')
    else:
        await ctx.send('The music_bot is not currently connected to a voice channel.')

@bot.command(name = 'artist', help = 'Search up artist information')
async def artist(ctx, *search):
    search = ' '.join(search)
    artist_id = (sp.search(q = search, type = 'artist'))['artists']['items'][0]['id']
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
            artist_top_song_list.append(str(counter) + '. ' + song_name + ' with ' + str(co_artist_list))
        else:
            artist_top_song_list.append(str(counter) + '. ' + song_name)
        counter += 1
    artist_top_song_string = '\n'.join(artist_top_song_list)
    artist_album_list = []
    counter = 1
    for album in sp.artist_albums(artist_id, limit = 10)['items']:
        album_name = album['name']
        total_songs = str(album['total_tracks'])
        artist_album_list.append(str(counter) + '. ' + album_name + ' with ' + total_songs + ' song(s)')
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
    album_id = (sp.search(q = search, type = 'album', limit = 10))['albums']['items'][0]['id']
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
        album_song_list.append(str(counter) + '. ' + song_name + ' with ' + str(artist_list))
        counter += 1
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
async def new(ctx, *search):
    search = ' '.join(search)
    playlist_id = (sp.search(q = search, type = 'playlist', limit = 10))['playlists']['items'][0]['id']
    playlist_name = sp.playlist(playlist_id)['name']
    playlist_description = sp.playlist(playlist_id)['description']
    if playlist_description == '':
        playlist_description = 'None'
    playlist_owner = sp.playlist(playlist_id)['owner']['display_name']
    total_followers = sp.playlist(playlist_id)['followers']['total']
    playlist_song_list = []
    counter = 1
    for song in sp.playlist_tracks(playlist_id)['items']:
        song_name = song['track']['name']
        artist_list = []
        for artist in song['track']['artists']:
            artist_list.append(artist['name'])
        playlist_song_list.append(str(counter) + '. ' + song_name + ' with ' + str(artist_list))
        counter += 1
        if counter > 10:
            break
    playlist_song_string = '\n'.join(playlist_song_list)
    playlist_embed = discord.Embed(title = 'Playlist Information', color = discord.Colour.purple())
    playlist_embed.set_author(name = ctx.author.display_name, icon_url = ctx.author.avatar_url)
    # playlist_embed.set_image(url = album_image_URL)
    playlist_embed.timestamp = datetime.datetime.utcnow()
    playlist_embed.set_footer(text = '\u200b', icon_url = 'https://d2gg9evh47fn9z.cloudfront.net/800px_COLOURBOX5629612.jpg')
    playlist_embed.add_field(name = 'Playlist Name 🎶', value = playlist_name, inline = False)
    playlist_embed.add_field(name = 'Playlist Description 📝', value = playlist_description, inline = False)
    playlist_embed.add_field(name = 'Playlist Owner 🎨', value = playlist_owner, inline = False)
    playlist_embed.add_field(name = 'Total Followers ❤️', value = total_followers, inline = False)
    playlist_embed.add_field(name = 'Playlist Songs (10) 🎵', value = playlist_song_string, inline = False)
    await ctx.send(embed = playlist_embed)

@bot.command(name = 'new', help = 'Search up new album releases on Spotify')
async def new(ctx):
    newly_released_album_list = []
    counter = 1
    for album in sp.new_releases()['albums']['items']:
        album_name = album['name']
        artist_list = []
        for artist in album['artists']:
            artist_list.append(artist['name'])
        newly_released_album_list.append(str(counter) + '. ' + album_name + ' with ' + str(artist_list))
        counter += 1
    newly_released_album_string = '\n'.join(newly_released_album_list)

    newly_released_album_embed = discord.Embed(title = 'New Releases (Spotify)', color = discord.Colour.gold())
    newly_released_album_embed.set_author(name = ctx.author.display_name, icon_url = ctx.author.avatar_url)
    newly_released_album_embed.set_image(url = 'https://storage.googleapis.com/pr-newsroom-wp/1/2019/10/New-Release-Burst2.jpg')
    newly_released_album_embed.timestamp = datetime.datetime.utcnow()
    newly_released_album_embed.set_footer(text = '\u200b', icon_url = 'https://d2gg9evh47fn9z.cloudfront.net/800px_COLOURBOX5629612.jpg')
    newly_released_album_embed.add_field(name = 'List 📝', value = newly_released_album_string, inline = False)
    await ctx.send(embed = newly_released_album_embed)

@bot.command(name = 'featured', help = 'Search up featured playlist releases on Spotify')
async def featured(ctx):
    featured_playlist_list = []
    counter = 1
    for playlist in sp.featured_playlists()['playlists']['items']:
        playlist_name = playlist['name']
        playlist_owner = playlist['owner']['display_name']
        featured_playlist_list.append(str(counter) + '. ' + playlist_name + ' by ' + playlist_owner)
        counter += 1
    featured_playlist_string = '\n'.join(featured_playlist_list)

    featured_playlist_embed = discord.Embed(title = 'Featured Releases (Spotify)', color = discord.Colour.magenta())
    featured_playlist_embed.set_author(name = ctx.author.display_name, icon_url = ctx.author.avatar_url)
    featured_playlist_embed.set_image(url = 'https://storage.googleapis.com/pr-newsroom-wp/1/2021/03/SPOTIFY_US_FOR-THE-RECORD_PR-ASSET_032521_V2_CF-01.jpg')
    featured_playlist_embed.timestamp = datetime.datetime.utcnow()
    featured_playlist_embed.set_footer(text = '\u200b', icon_url = 'https://d2gg9evh47fn9z.cloudfront.net/800px_COLOURBOX5629612.jpg')
    featured_playlist_embed.add_field(name = 'List 📝', value = featured_playlist_string, inline = False)
    await ctx.send(embed = featured_playlist_embed)

bot.run(TOKEN)

# https://stackoverflow.com/questions/67722188/add-button-components-to-a-message-discord-py, https://www.youtube.com/watch?v=NtoMyB8XcQU

# https://stackoverflow.com/questions/65768920/how-to-make-a-discord-music-bot-to-recognize-the-end-of-song-or-where-it-is-play

# if no search throw warning

# yt link