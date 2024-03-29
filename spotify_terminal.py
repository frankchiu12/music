import spotipy
import spotipy.util as util
from lyricsgenius import Genius
import speech_recognition as sr
import sys, os
import webbrowser
from termcolor import colored
import random

username = 'chiusiun'
scope = 'user-read-currently-playing user-modify-playback-state user-read-playback-state user-read-recently-played user-top-read user-library-modify user-library-read'
client_id = '3aa6dc3eea4b485497c73da406f11802'
client_secret = 'c08afd7602b740589ccf5198eb2982a2'
redirect_URI = 'http://google.com/'
spotify_token = util.prompt_for_user_token(username, scope, client_id, client_secret, redirect_URI)
sp = spotipy.Spotify(auth = spotify_token)

genius_token = 'Q8q2Cs-4YkZT_83az4gYWpQrkSthadNOWMeuJhJOmHmIB3sBj3_HMX9SY2gR2HC5'
genius = Genius(genius_token)

r = sr.Recognizer()
mic = sr.Microphone()

def main():
    print('\033c', end = None)
    term_size = os.get_terminal_size()
    print('=' * term_size.columns + '\n')
    search()

def search():
    current_track = sp.current_user_playing_track()
    if current_track is None:
        print('\033c', end = None)
        print('No active device.' + '\n')
        return

    x = input('search> ')
    if x == '!voice':
        with mic as source:
            print('\033c', end = None)
            print('Listening ...' + '\n')
            audio = r.listen(source)
            x = r.recognize_google(audio)
    if x == '!skip':
        id_to_current_track_information = {}
        current_track = sp.current_user_playing_track()['item']
        populate_id_to_information_dictionary(current_track, id_to_current_track_information, 'track')
        print('\033c', end = None)
        term_size = os.get_terminal_size()
        print('=' * term_size.columns + '\n')
        command(current_track['id'])
    else:
        search_helper(x, True)

def choose(counter_to_information, external_search, type):
    if external_search:
        x = input('item_number> ')
        if x.isdigit() and 1 <= int(x) <= 10:
            id = counter_to_information[int(x)].partition('id: ')[2]
            description = counter_to_information[int(x)].partition(', id: ')[0]
            print('\033c', end = None)
            print('Selected ' + colored(type, 'magenta') + ' ' + description + '\n')
            current_track_id = sp.current_user_playing_track()['item']['id']
            if type == 'track':
                command(id)
            elif type == 'artist':
                artist_name = sp.artist(id)['name']
                get_artist_information([current_track_id, id], [artist_name])
            elif type == 'playlist':
                get_playlist_information([current_track_id, id])
            elif type == 'album':
                get_album_information([current_track_id, id])
        elif x.isdigit():
            print('\n' + 'The number inputted is outside of the result list size of 10.' + '\n')
            choose(counter_to_information, True, type)
        elif x == 'redo':
            main()
        elif x == 'quit':
            print('\033c', end = None)
            return
        else:
            print('\n' + 'Invalid command.' + '\n')
            choose(counter_to_information, True, type)
    else:
        id = counter_to_information[1].partition('id: ')[2]
        description = counter_to_information[1].partition(', id: ')[0]
        print('\033c', end = None)
        if '#featured: ' in description:
            description = description.partition('#featured: ')[2]
            print('Selected ' + colored(type, 'magenta') + ' ' + description + '\n')
            get_playlist_information(id)
        elif '#new: ' in description:
            description = description.partition('#new: ')[2]
            print('Selected ' + colored(type, 'magenta') + ' ' + description + '\n')
            get_album_information(id)
        else:
            print('Selected ' + colored(type, 'magenta') + ' ' + description + '\n')
            command(id)

def command(id):
    x = input('command> ')
    print('')

    if x == 'album':
        album_id = [id, sp.track(id)['album']['id']]
        get_album_information(album_id)

    elif x == 'artist':
        artist_list = []
        for artist in sp.track(id)['artists']:
            artist_list.append(artist['name'])
        main_artist_id = sp.track(id)['artists'][0]['id']
        artist_id = [id, main_artist_id]
        get_artist_information(artist_id, artist_list)

    elif x == 'resume':
        if not sp.current_playback()['is_playing']:
            sp.start_playback()
            print_and_clear(id, 'Resuming ...')
        else:
            print_and_clear(id, 'Already playing.')

    elif x == 'current':
        current_track_name = sp.current_user_playing_track()['item']['name']
        artist_list = []
        for artist in sp.current_user_playing_track()['item']['artists']:
            artist_list.append(artist['name'])
        print(colored(current_track_name, 'red') + ' by ' + colored(str(artist_list), 'blue') + '\n')
        command(id)

    elif x == 'duration':
        duration = sp.track(id)['duration_ms']
        duration = parse_time(duration)
        print(colored(' ' + duration + ' ', 'grey', on_color = 'on_white') + '\n')
        command(id)

    elif x == 'explicit':
        explicit = sp.track(id)['explicit']
        if explicit:
            print(colored(str(explicit), 'red') + '\n')
        else:
            print(colored(str(explicit), 'green') + '\n')
        command(id)

    elif x == 'featured':
        counter_to_featured_playlist_information = {}
        counter = 1
        for playlist in sp.featured_playlists()['playlists']['items']:
            playlist_id = playlist['id']
            playlist_name = playlist['name']
            playlist_owner = playlist['owner']['display_name']
            if counter not in counter_to_featured_playlist_information:
                counter_to_featured_playlist_information[counter] = '#featured, id: ' + playlist_id
            print(str(counter) + '. ' + colored(playlist_name, 'red') + ' by ' + colored(playlist_owner, 'blue'))
            counter += 1
        print('')
        internal_search(id, counter_to_featured_playlist_information, 'playlist')

    elif x == 'image':
        image_URL = sp.track(id)['album']['images'][0]['url']
        webbrowser.open(image_URL)
        print_and_clear(id, 'Opening image ...')

    elif x == 'loop':
        sp.repeat('track')
        print_and_clear(id, 'Repeating ...')

    elif x == 'lyrics':
        track_name = sp.track(id)['name']
        main_artist = sp.track(id)['artists'][0]['name']
        if ' - From' in track_name:
            track_name = track_name.partition(' - From')[0]
        if ' (feat.' in track_name:
            track_name = track_name.partition(' (feat.')[0]
        if ' (with ' in track_name:
            track_name = track_name.partition(' (with ')[0]
        print('Searching ...' + '\n')
        sys.stdout = open(os.devnull, 'w')
        genius_searched_track = genius.search_song(track_name, main_artist)
        sys.stdout = sys.__stdout__
        if genius_searched_track is None:
            print_and_clear(id, 'No lyrics found.')
        else:
            print_and_clear(id, genius_searched_track.lyrics)

    elif x == 'name':
        track_name = sp.track(id)['name']
        print(colored(' ' + track_name + ' ', 'grey', on_color = 'on_white') + '\n')
        command(id)
    
    elif x == 'new':
        counter_to_newly_released_album_information = {}
        counter = 1
        for track in sp.new_releases()['albums']['items']:
            track_id = track['id']
            track_name = track['name']
            artist_list = []
            for artist in track['artists']:
                artist_list.append(artist['name'])
            if counter not in counter_to_newly_released_album_information:
                counter_to_newly_released_album_information[counter] = '#new, id: ' + track_id
            print(str(counter) + '. ' + colored(track_name, 'red') + ' by ' + colored(str(artist_list), 'blue'))
            counter += 1
        print('')
        internal_search(id, counter_to_newly_released_album_information, 'album')

    elif x == 'next':
        next_track_id = sp.current_user_playing_track()['item']['id']
        sp.next_track()
        print_and_clear(next_track_id, 'Skipping to next ...')

    elif x == 'open':
        track_URL = sp.track(id)['external_urls']['spotify']
        webbrowser.open(track_URL)
        print_and_clear(id, 'Opening track ...')

    elif x == 'pause':
        if sp.current_playback()['is_playing']:
            sp.pause_playback()
            print_and_clear(id, 'Paused.')
        else:
            print_and_clear(id, 'Already paused.')

    elif x == 'play':
        track_URI_list = [sp.track(id)['uri']]
        track_name = sp.track(id)['name']
        artist_list = []
        for artist in sp.track(id)['artists']:
            artist_list.append(artist['name'])
        sp.start_playback(device_id = 'bddcb19206692c58a23c8c88a13144e1d7e4541e', uris = track_URI_list)
        print_and_clear(id, 'Playing ' + colored(track_name, 'red') + ' by ' + colored(artist_list, 'blue') + ' ...')

    elif x == 'popularity':
        popularity = str(sp.track(id)['popularity'])
        print(colored(' ' + popularity + ' ', 'grey', on_color = 'on_white') + '\n')
        command(id)

    elif x == 'previous':
        previous_track_id = sp.current_user_playing_track()['item']['id']
        sp.previous_track()
        print_and_clear(previous_track_id, 'Going back to previous ...')

    elif x == 'queue':
        track_URI = sp.track(id)['uri']
        sp.add_to_queue(track_URI)
        print_and_clear(id, 'Adding to queue ...')

    elif x == 'quit':
        print('\033c', end = None)
        return

    elif x == 'recent':
        counter = 1
        counter_to_recent_track_information = {}
        for track in sp.current_user_recently_played(10)['items']:
            track_name = track['track']['name']
            track_ID = track['track']['id']
            artist_list = []
            for artist in track['track']['artists']:
                artist_list.append(artist['name'])
            if counter not in counter_to_recent_track_information:
                counter_to_recent_track_information[counter] = track_name + ' ' + artist_list[0]
            print(str(counter) + '. ' + colored(track_name, 'red') + ' by ' + colored(str(artist_list), 'blue') + ', id: ' + colored(track_ID, 'green'))
            counter += 1
        print('')
        internal_search(id, counter_to_recent_track_information, 'track')

    elif x == 'recommendation':
        track_id_list = []
        artist_id_list = []
        for track in sp.current_user_top_tracks()['items']:
            track_id_list.append(track['id'])
        for artist in sp.current_user_top_artists()['items']:
            artist_id_list.append(artist['id'])
        random.shuffle(track_id_list)
        random.shuffle(artist_id_list)
        print(colored('Recommended Tracks: ', 'magenta'))

        counter_to_recommended_track_information = {}
        counter = 1
        for track in sp.recommendations(seed_tracks = track_id_list[:3], seed_artists = artist_id_list[:2], limit = 50)['tracks']:
            track_name = track['name']
            main_artist = track['artists'][0]['name']
            artist_list = []
            for artist in track['artists']:
                artist_list.append(artist['name'])
            if counter not in counter_to_recommended_track_information:
                counter_to_recommended_track_information[counter] = track_name + ' ' + main_artist
            print(str(counter) + '. ' + colored(track_name, 'cyan') + colored(' by ', 'grey') + str(artist_list))
            counter += 1
        print('')
        internal_search(id, counter_to_recommended_track_information, 'track')

    elif x == 'redo':
        main()

    elif x == 'release date':
        release_date = sp.track(id)['album']['release_date']
        print(colored(' ' + release_date + ' ', 'grey', on_color = 'on_white') + '\n')
        command(id)

    elif x == 'save':
        saved = sp.current_user_saved_tracks_contains([id])[0]
        if saved:
            print_and_clear(id, 'Already saved.')
        else:
            sp.current_user_saved_tracks_add([id])
            print_and_clear(id, 'Saving ...')

    elif x == 'timestamp':
        timestamp_int = sp.current_user_playing_track()['progress_ms']
        duration_int = sp.track(id)['duration_ms']
        timestamp_string = parse_time(timestamp_int)
        duration_string = parse_time(duration_int)
        print(colored(' ' + timestamp_string + '/' + duration_string + ' ', 'grey', on_color = 'on_white') + '\n')
        print_progress_bar(timestamp_int, duration_int, prefix = 'Progress:', suffix = 'Complete', length = 50)
        print('\n')
        command(id)

    elif x == 'toggle':
        toggle(id)

    elif x == 'user':
        get_user_information(id)

    elif x =='volume':
        volume(id)

    else:
        print('Invalid command.' + '\n')
        command(id)

def populate_id_to_information_dictionary(item, id_to_information, type):
    item_id = item['id']
    if item_id not in id_to_information:
        id_to_information[item_id] = []
    id_to_information[item_id].append(item['name'])
    if type != 'artist' and type != 'playlist':
        artist_list = []
        for artist in item['artists']:
            artist_list.append(artist['name'])
        id_to_information[item_id].append(artist_list)

def search_helper(x, external_search):
    if '#featured' in x:
        counter_to_information = {}
        playlist_id = x.partition(', id: ')[2]
        playlist_name = sp.playlist(playlist_id)['name']
        playlist_owner = sp.playlist(playlist_id)['owner']['display_name']
        counter_to_information[1] = '#featured: ' + colored(playlist_name, 'red') + ' by ' + colored(playlist_owner, 'blue') + ', id: ' + playlist_id
        type = 'playlist'
    elif '#new' in x:
        counter_to_information = {}
        album_id = x.partition(', id: ')[2]
        album_name = sp.album(album_id)['name']
        artist_list = []
        for artist in sp.album(album_id)['artists']:
            artist_list.append(artist['name'])
        counter_to_information[1] = '#new: ' + colored(album_name, 'red') + ' by ' + colored(str(artist_list), 'blue') + ', id: ' + album_id
        type = 'album'
    else:
        if '/artist ' in x:
            x = x.partition('/artist ')[2]
            search = (sp.search(q = x, type = 'artist', limit = 10))['artists']
            type = 'artist'
        elif '/playlist ' in x:
            x = x.partition('/playlist ')[2]
            search = (sp.search(q = x, type = 'playlist', limit = 10))['playlists']
            type = 'playlist'
        elif '/album ' in x:
            x = x.partition('/album ')[2]
            search = (sp.search(q = x, type = 'album', limit = 10))['albums']
            type = 'album'
        else:
            search = (sp.search(q = x, type = 'track', limit = 10))['tracks']
            type = 'track'

        id_to_information = {}
        for item in search['items']:
            populate_id_to_information_dictionary(item, id_to_information, type)

        print('\033c', end = None)
        counter = 1
        counter_to_information = {}
        for id, information in id_to_information.items():
            id = str(id)
            item_name = information[0]
            if type != 'artist' and type != 'playlist':
                artist_list = str(information[1])
                colored_description = colored(item_name, 'red') + ' by ' + colored(artist_list, 'blue') + ', id: ' + colored(id, 'green')
                description = colored(item_name, 'red') + ' by ' + colored(artist_list, 'blue') + ', id: ' + id
            else:
                colored_description = colored(item_name, 'red') + ', id: ' + colored(id, 'blue')
                description = colored(item_name, 'red') + ', id: ' + id
            if external_search:
                print(str(counter) + '. ' + colored_description + ', ' + colored('type: ' + type, 'magenta'))
            if counter not in counter_to_information:
                counter_to_information[counter] = description
            counter += 1

    print('')
    choose(counter_to_information, external_search, type)

def internal_search(id, counter_to_information, type):
    x = input('internal_search> ')
    list_size = len(counter_to_information)
    if isinstance(id, list):
        original_id = id[0]
        new_id = id[1]
    else:
        original_id = id
        new_id = id

    if x.isdigit() and 1 <= int(x) <= list_size:
        x = counter_to_information[int(x)]
        search_helper(x, False)
    elif x.isdigit():
        print('\n' + 'The number inputted is outside of the result list size of ' + str(list_size) + '.' +'\n')
        internal_search(id, counter_to_information, type)
    elif x == '!play':
        if type == 'track':
            print('\n' + 'That command is reserved for items of type ' + colored('artist/playlist/album', 'magenta') + '.' + '\n')
            internal_search(id, counter_to_information, type)
        elif type == 'artist':
            artist_URI = sp.artist(new_id)['uri']
            sp.start_playback(device_id = 'bddcb19206692c58a23c8c88a13144e1d7e4541e', context_uri = artist_URI)
            print('\n' + 'Playing ...' + '\n')
            internal_search(id, counter_to_information, type)
        elif type == 'playlist':
            playlist_URI = sp.playlist(new_id)['uri']
            sp.start_playback(device_id = 'bddcb19206692c58a23c8c88a13144e1d7e4541e', context_uri = playlist_URI)
            print('\n' + 'Playing ...' + '\n')
            internal_search(id, counter_to_information, type)
        elif type == 'album':
            album_URI = sp.album(new_id)['uri']
            sp.start_playback(device_id = 'bddcb19206692c58a23c8c88a13144e1d7e4541e', context_uri = album_URI)
            print('\n' + 'Playing ...' + '\n')
            internal_search(id, counter_to_information, type)
    elif x == '!open':
        if type == 'track':
            print('\n' + 'That command is reserved for items of type ' + colored('artist/playlist/album', 'magenta') + '.' + '\n')
            internal_search(id, counter_to_information, type)
        elif type == 'artist':
            artist_URL = sp.artist(new_id)['external_urls']['spotify']
            webbrowser.open(artist_URL)
            print('\n' + 'Opening artist page ...' + '\n')
            internal_search(id, counter_to_information, type)
        elif type == 'playlist':
            playlist_URL = sp.playlist(new_id)['external_urls']['spotify']
            webbrowser.open(playlist_URL)
            print('\n' + 'Opening playlist page ...' + '\n')
            internal_search(id, counter_to_information, type)
        elif type == 'album':
            album_URL = sp.album(new_id)['external_urls']['spotify']
            webbrowser.open(album_URL)
            print('\n' + 'Opening album page ...' + '\n')
            internal_search(id, counter_to_information, type)
    elif x == '!image':
        if type == 'track':
            print('\n' + 'That command is reserved for items of type ' + colored('artist/playlist/album', 'magenta') + '.' + '\n')
            internal_search(id, counter_to_information, type)
        elif type == 'artist':
            artist_URL = sp.artist(new_id)['images'][0]['url']
            webbrowser.open(artist_URL)
            print('\n' + 'Opening artist image ...' + '\n')
            internal_search(id, counter_to_information, type)
        elif type == 'playlist':
            playlist_URL = sp.playlist(new_id)['images'][0]['url']
            webbrowser.open(playlist_URL)
            print('\n' + 'Opening playlist image ...' + '\n')
            internal_search(id, counter_to_information, type)
        elif type == 'album':
            album_URL = sp.album(new_id)['images'][0]['url']
            webbrowser.open(album_URL)
            print('\n' + 'Opening album image ...' + '\n')
            (id, counter_to_information, type)
    elif x == '!back':
        print('\033c', end = None)
        command(original_id)
    elif x == '!redo':
        main()
    else:
        search_helper(x, True)

def print_and_clear(id, message):
    print('\033c', end = None)
    print(message + '\n')
    command(id)

def get_album_information(id):
    if isinstance(id, list):
        album_id = id[1]
    else:
        album_id = id

    album_name = sp.album(album_id)['name']
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
    print(colored('Album Name: ', 'red') + album_name)
    print(colored('Album Type: ', 'yellow') + album_type)
    print(colored('Artist List: ', 'green') + str(artist_list))
    print(colored('Release Date: ', 'blue') + release_date)
    print(colored('Total Tracks: ', 'magenta') + total_tracks)
    print(colored('Genres: ', 'red') + genre_list)
    print(colored('Popularity: ', 'yellow') + popularity)
    print(colored('Label: ', 'green') + label)
    print(colored('Link: ', 'blue') + link)

    print(colored('Tracks: ', 'magenta'))
    counter_to_album_information = {}
    counter = 1
    for track in sp.album_tracks(album_id)['items']:
        track_name = track['name']
        main_artist = track['artists'][0]['name']
        artist_list = []
        for artist in track['artists']:
            artist_list.append(artist['name'])
        if counter not in counter_to_album_information:
            counter_to_album_information[counter] = track_name + ' ' + main_artist
        print(str(counter) + '. ' + colored(track_name, 'cyan') + colored(' by ', 'grey') + str(artist_list))
        counter += 1
    print('')
    internal_search(id, counter_to_album_information, 'album')

def get_artist_information(id, artist_list):
    if isinstance(id, list):
        artist_id = id[1]
    else:
        artist_id = id

    main_artist = sp.artist(artist_id)['name']
    if main_artist in artist_list:
        artist_list.remove(main_artist)
    genre_list = str(sp.artist(artist_id)['genres'])
    popularity = str(sp.artist(artist_id)['popularity'])
    total_followers = str(sp.artist(artist_id)['followers']['total'])
    if len(artist_list) != 0:
        print(colored(' ' + str(main_artist) + ' ', 'grey', on_color = 'on_white') + ' with ' + str(artist_list) + '\n')
    else:
        print(colored(' ' + str(main_artist) + ' ', 'grey', on_color = 'on_white') + '\n')
    print(colored('Genres: ', 'red') + genre_list)
    print(colored('Popularity: ', 'yellow') + popularity)
    print(colored('Total Followers: ', 'green') + total_followers)
    related_artist_list = []
    for related_artist in sp.artist_related_artists(artist_id)['artists']:
        related_artist_list.append(related_artist['name'])
    print(colored('Related Artists: ', 'blue') + str(related_artist_list))

    print(colored('Top Tracks:', 'magenta'))
    counter_to_artist_information = {}
    counter = 1
    for track in sp.artist_top_tracks(artist_id)['tracks']:
        track_name = track['name']
        main_artist = track['artists'][0]['name']
        co_artist_list = []
        for co_artist in track['artists']:
            co_artist_list.append(co_artist['name'])
        if main_artist in co_artist_list:
            co_artist_list.remove(main_artist)
        if counter not in counter_to_artist_information:
            counter_to_artist_information[counter] = track_name + ' ' + main_artist
        if len(co_artist_list) != 0:
            print(str(counter) + '. ' + colored(track_name, 'cyan') + colored(' with ', 'grey') + str(co_artist_list))
        else:
            print(str(counter) + '. ' + colored(track_name, 'cyan'))
        counter += 1

    print(colored('Albums:', attrs = ['bold', 'underline', 'dark']))
    counter = 1
    for album in sp.artist_albums(artist_id)['items']:
        album_name = album['name']
        total_tracks = str(album['total_tracks'])
        print(str(counter) + '. ' + colored(album_name, 'cyan') + colored(' with ', 'grey') + total_tracks + ' track(s)')
        counter += 1
    print('')
    internal_search(id, counter_to_artist_information, 'artist')

def parse_time(ms):
    s, ms = divmod(ms, 1000)
    m, s = divmod(s, 60)
    if s == 0:
        s = '00'
    time = str(m) + ':' + str(s)
    return time

def print_progress_bar (iteration, total, prefix = '', suffix = '', decimals = 1, length = 100, fill = '█', print_end = '\r'):
    percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
    filled_length = int(length * iteration // total)
    bar = fill * filled_length + '-' * (length - filled_length)
    print(f'\r{prefix} |{bar}| {percent}% {suffix}', end = print_end)

def toggle(id):
    x = input('    timestamp> ')
    if x != '!keep':
        try:
            x = x.partition(':')
            minute = int(x[0])
            second = int(x[2])
            x = (minute * 60 + second) * 1000
        except:
            print('\n' + 'Invalid command.' +'\n')
            command(id)
    else:
        print('')
        command(id)

    if 0 <= x <= sp.track(id)['duration_ms']:
        pass
    elif isinstance(x, int):
        print('\n' + 'The timestamp inputted is out of range.' +'\n')
        toggle(id)
    else:
        print('\n' + 'Invalid command.' +'\n')
        command(id)

    sp.seek_track(x)
    print('\033c', end = None)
    print('Setting the timestamp to: ' + colored(' ' + parse_time(x) + ' ', on_color = 'on_white')  + '\n')
    duration_int = sp.track(id)['duration_ms']
    print_progress_bar(x, duration_int, prefix = 'Progress:', suffix = 'Complete', length = 50)
    print('\n')
    command(id)

def get_user_information(id):
    display_name = sp.current_user()['display_name']
    followers = str(sp.current_user()['followers']['total'])
    user_link = sp.current_user()['external_urls']['spotify']
    print(colored('Display Name: ', 'red') + display_name)
    print(colored('Followers: ', 'yellow') + followers)
    print(colored('User Link: ', 'green') + user_link)

    print(colored('Top Tracks: ', 'blue'))
    counter_to_user_information = {}
    counter = 1
    for track in sp.current_user_top_tracks()['items']:
        track_name = track['name']
        main_artist = track['artists'][0]['name']
        artist_list = []
        for artist in track['artists']:
            artist_list.append(artist['name'])
        if counter not in counter_to_user_information:
            counter_to_user_information[counter] = track_name + ' ' + main_artist
        print(str(counter) + '. ' + colored(track_name, 'cyan') + colored(' by ', 'grey') + str(artist_list))
        counter += 1

    print(colored('Top Artists', 'magenta'))
    counter = 1
    for artist in sp.current_user_top_artists()['items']:
        print(str(counter) + '. ' + colored(artist['name'], 'cyan'))
        counter += 1

    print('')
    internal_search(id, counter_to_user_information, 'track')

def volume(id):
    x = input('    volume> ')
    if x.isdigit() and 0 <= int(x) <= 100:
        x = int(x)
    elif x.isdigit():
        print('\n' + 'The volume inputted is out of range.' +'\n')
        volume(id)
    elif x == '!keep':
        print('')
        command(id)
    else:
        print('\n' + 'Invalid command.' +'\n')
        command(id)

    print('\033c', end = None)
    print('Setting the volume to: ' + colored(' ' + str(x) + ' ', on_color = 'on_white')  + '\n')
    sp.volume(x)
    command(id)

def get_playlist_information(id):
    if isinstance(id, list):
        playlist_id = id[1]
    else:
        playlist_id = id

    playlist_name = sp.playlist(playlist_id)['name']
    playlist_description = sp.playlist(playlist_id)['description']
    playlist_owner = sp.playlist(playlist_id)['owner']['display_name']
    total_followers = sp.playlist(playlist_id)['followers']['total']
    print(colored('Playlist Name: ', 'red') + playlist_name)
    print(colored('Playlist Description: ', 'yellow') + playlist_description)
    print(colored('Playlist Owner: ', 'green') + playlist_owner)
    print(colored('Total Followers: ', 'blue') + str(total_followers))

    print(colored('Tracks: ', 'magenta'))
    counter_to_playlist_information = {}
    counter = 1
    for track in sp.playlist_tracks(playlist_id)['items']:
        track_name = track['track']['name']
        main_artist = track['track']['artists'][0]['name']
        artist_list = []
        for artist in track['track']['artists']:
            artist_list.append(artist['name'])
        if counter not in counter_to_playlist_information:
            counter_to_playlist_information[counter] = track_name + ' ' + main_artist
        print(str(counter) + '. ' + colored(track_name, 'cyan') + colored(' by ', 'grey') + str(artist_list))
        counter += 1
    print('')
    internal_search(id, counter_to_playlist_information, 'playlist')

if __name__ == '__main__':
    main()