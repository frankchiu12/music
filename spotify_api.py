import spotipy
import spotipy.util as util
from lyricsgenius import Genius
import speech_recognition as sr
import sys, os
import webbrowser
from termcolor import colored

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

os.system('open /Applications/Spotify.app')

def main():
    print('\033c', end = None)
    term_size = os.get_terminal_size()
    print('=' * term_size.columns + '\n')
    initial_search()

def initial_search():
    x = input('search> ')

    if x == '!voice':
        with mic as source:
            print('\033c', end = None)
            print('Listening ...' + '\n')
            audio = r.listen(source)
            x = r.recognize_google(audio)

    if x == '!skip':
        if sp.current_user_playing_track() is not None:
            id_to_song_information = {}
            song = sp.current_user_playing_track()['item']
            populate_information_list(song, id_to_song_information, 'track')

            print('\033c', end = None)
            term_size = os.get_terminal_size()
            print('=' * term_size.columns + '\n')

            get_information(song['id'])
        else:
            print('\033c', end = None)
            print('\n' + 'No song currently playing.' + '\n')
            return
    else:
        external_search_helper(x, True)

def choose_item(counter_to_list, external_search, type):
    if external_search:
        x = input('item_number> ')

        if x.isdigit() and 1 <= int(x) <= 10:
            id = counter_to_list[int(x)].partition('id: ')[2]
            description = counter_to_list[int(x)].partition(', id: ')[0]
            print('\033c', end = None)
            print('Selected ' + colored(type, 'magenta') + ' ' + description + '\n')
            if type == 'track':
                get_information(id)
            # !back can't work if no current_song_id
            elif type == 'artist':
                current_song_id = sp.current_user_playing_track()['item']['id']
                return_artist_information([current_song_id, id], [sp.artist(id)['name']])
            elif type == 'playlist':
                current_song_id = sp.current_user_playing_track()['item']['id']
                return_playlist_information([current_song_id, id])
            elif type == 'album':
                current_song_id = sp.current_user_playing_track()['item']['id']
                return_album_information([current_song_id, id])
        elif x.isdigit():
            print('\n' + 'The number inputted is outside of the result list size of 10.' +'\n')
            choose_item(counter_to_list, True, type)
        elif x == 'redo':
            main()
        elif x == 'quit':
            print('\033c', end = None)
            return
        else:
            print('\n' + 'Invalid command!' + '\n')
            choose_item(counter_to_list, True, type)
    else:
        id = counter_to_list[1].partition('id: ')[2]
        description = counter_to_list[1].partition(', id: ')[0]
        print('\033c', end = None)
        print('Selected ' + colored(type, 'magenta') + ' ' + description + '\n')
        get_information(id)

'===================================================================================================================================='

def get_information(id):
    x = input('command> ')
    print('')

    if x == 'album':
        album_id = [id, sp.track(id)['album']['id']]
        return_album_information(album_id)

    elif x == 'artist':
        artist_list = []
        for artist in sp.track(id)['artists']:
            artist_list.append(artist['name'])
        artist_id = [id, sp.track(id)['artists'][0]['id']]
        return_artist_information(artist_id, artist_list)

    elif x == 'continue':
        try:
            if not sp.current_playback()['is_playing']:
                sp.start_playback()
                print_and_clear(id, 'Continuing ...')
            else:
                print_and_clear(id, 'Already playing.')
        except:
            print_and_clear(id, 'No active device.')

    elif x == 'current':
        if sp.current_user_playing_track() is not None:
            song_name = sp.current_user_playing_track()['item']['name']
            artist_list = []
            for artist in sp.current_user_playing_track()['item']['artists']:
                artist_name = artist['name']
                artist_list.append(artist_name)
            print(colored(song_name, 'red') + ' by ' + colored(str(artist_list), 'blue') + '\n')
            get_information(id)
        else:
            print('No song is currently playing.' + '\n')
            get_information(id)

    elif x == 'duration':
        duration = sp.track(id)['duration_ms']
        duration = parse_time(duration)
        print(colored(' ' + duration + ' ', 'grey', on_color = 'on_white') + '\n')
        get_information(id)

    elif x == 'explicit':
        explicit = sp.track(id)['explicit']
        if explicit:
            print(colored(str(explicit), 'red') + '\n')
        else:
            print(colored(str(explicit), 'green') + '\n')
        get_information(id)

    elif x == 'image':
        image_URL = sp.track(id)['album']['images'][0]['url']
        webbrowser.open(image_URL)
        print_and_clear(id, 'Opening image ...')

    elif x == 'loop':
        sp.repeat('track')
        print_and_clear(id, 'Repeating ...')

    elif x == 'lyrics':
        song_name = sp.track(id)['name']
        if ' - From' in song_name:
            song_name = song_name.partition(' - From')[0]
        if ' (feat.' in song_name:
            song_name = song_name.partition(' (feat.')[0]
        print('Searching ...' + '\n')
        sys.stdout = open(os.devnull, 'w')
        song_name = genius.search_song(song_name, sp.track(id)['artists'][0]['name'])
        sys.stdout = sys.__stdout__
        if song_name is None:
            print_and_clear(id, 'No lyrics found.')
        else:
            print_and_clear(id, song_name.lyrics)

    elif x == 'name':
        print(colored(' ' + sp.track(id)['name'] + ' ', 'grey', on_color = 'on_white') + '\n')
        get_information(id)
    
    elif x == 'new releases':
        counter_to_song_name_and_main_artist = {}
        counter = 1
        for track in sp.new_releases()['albums']['items']:
            song_name = track['name']
            main_artist = track['artists'][0]['name']
            artist_list = []
            if counter not in counter_to_song_name_and_main_artist:
                counter_to_song_name_and_main_artist[counter] = song_name + ' ' + main_artist
            for artist in track['artists']:
                artist_list.append(artist['name'])
            print(str(counter) + '. ' + colored(song_name, 'red') + ' by ' + colored(str(artist_list), 'blue'))
            counter += 1
        print('')
        internal_search(id, counter_to_song_name_and_main_artist, 'album')
        print(sp.new_releases())

    elif x == 'next':
        try:
            sp.next_track()
            next_song_id = sp.current_user_playing_track()['item']['id']
            print_and_clear(next_song_id, 'Skipping to next ...')
        except:
            print_and_clear(id, 'No active device.')

    elif x == 'open':
        song_URL = sp.track(id)['external_urls']['spotify']
        webbrowser.open(song_URL)
        print_and_clear(id, 'Opening song ...')

    elif x == 'pause':
        try:
            if sp.current_playback()['is_playing']:
                sp.pause_playback()
                print_and_clear(id, 'Paused.')
            else:
                print_and_clear(id, 'Already paused.')
        except:
            print_and_clear(id, 'No active device.')

    elif x == 'play':
        song_URI_list = [sp.track(id)['uri']]
        song_name = sp.track(id)['name']
        artist_list = []
        for artist in sp.track(id)['artists']:
            artist_list.append(artist['name'])
        sp.start_playback(device_id = 'bddcb19206692c58a23c8c88a13144e1d7e4541e', uris = song_URI_list)
        print_and_clear(id, 'Playing ' + colored(song_name, 'red') + ' by ' + colored(artist_list, 'blue') + ' ...')

    elif x == 'popularity':
        popularity = str(sp.track(id)['popularity'])
        print(colored(' ' + popularity + ' ', 'grey', on_color = 'on_white') + '\n')
        get_information(id)

    elif x == 'previous':
        try:
            sp.previous_track()
            previous_song_id = sp.current_user_playing_track()['item']['id']
            print_and_clear(previous_song_id, 'Going back to previous ...')
        except:
            print_and_clear(id, 'No active device.')

    elif x == 'queue':
        try:
            song_URI = sp.track(id)['uri']
            sp.add_to_queue(song_URI)
            print_and_clear(id, 'Adding to queue ...')
        except:
            print_and_clear(id, 'No active device.')

    elif x == 'quit':
        print('\033c', end = None)
        return

    elif x == 'recent':
        counter = 1
        counter_to_song_name_and_main_artist = {}
        for song in sp.current_user_recently_played(10)['items']:
            song_name = song['track']['name']
            song_ID = song['track']['id']
            artist_list = []
            for artist in song['track']['artists']:
                artist_list.append(artist['name'])
            if counter not in counter_to_song_name_and_main_artist:
                counter_to_song_name_and_main_artist[counter] = song_name + artist_list[0]
            print(str(counter) + '. ' + colored(song_name, 'red') + ' by ' + colored(str(artist_list), 'blue') + ', id: ' + colored(song_ID, 'green'))
            counter += 1
        print('')
        internal_search(id, counter_to_song_name_and_main_artist, 'track')

    elif x == 'redo':
        main()

    elif x == 'release date':
        release_date = sp.track(id)['album']['release_date']
        print(colored(' ' + release_date + ' ', 'grey', on_color = 'on_white') + '\n')
        get_information(id)

    elif x == 'save':
        if type != 'track':
            print('That command is reserved for items of type ' + colored('track', 'magenta') + '.' + '\n')
            get_information(id)
        else:
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
        get_information(id)

    elif x == 'toggle':
        toggle(id)

    elif x == 'user':
        get_user_information(id)

    elif x =='volume':
        volume(id)

    else:
        print('Invalid command!' + '\n')
        get_information(id)

def populate_information_list(item, id_to_information, type):
    if item['id'] not in id_to_information:
        id_to_information[item['id']] = []
    id_to_information[item['id']].append(item['name'])
    if type != 'artist' and type != 'playlist':
        artist_list = []
        for artist in item['artists']:
            artist_list.append(artist['name'])
        id_to_information[item['id']].append(artist_list)

def external_search_helper(x, external_search):
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
        populate_information_list(item, id_to_information, type)

    print('\033c', end = None)
    counter = 1
    counter_to_list = {}
    for id, information in id_to_information.items():
        item_name = information[0]
        id = str(id)
        if type != 'artist' and type != 'playlist':
            artist_list = str(information[1])
            colored_description = colored(item_name, 'red') + ' by ' + colored(artist_list, 'blue') + ', id: ' + colored(id, 'green')
            description = colored(item_name, 'red') + ' by ' + colored(artist_list, 'blue') + ', id: ' + id
        else:
            colored_description = colored(item_name, 'red') + ', id: ' + colored(id, 'blue')
            description = colored(item_name, 'red') + ', id: ' + id
        if external_search:
            print(str(counter) + '. ' + colored_description + ', ' + colored('type: ' + type, 'magenta'))
        if counter not in counter_to_list:
            counter_to_list[counter] = description
        counter += 1
    print('')

    choose_item(counter_to_list, external_search, type)

def internal_search(id, counter_to_song_name_and_main_artist, type):
    x = input('internal_search> ')
    list_size = len(counter_to_song_name_and_main_artist)
    if isinstance(id, list):
        original_id = id[0]
        new_id = id[1]
    else:
        original_id = id
        new_id = id

    if x.isdigit() and 1 <= int(x) <= list_size:
        x = counter_to_song_name_and_main_artist[int(x)]
        external_search_helper(x, False)
    elif x.isdigit():
        print('\n' + 'The number inputted is outside of the result list size of ' + str(list_size) + '.' +'\n')
        internal_search(id, counter_to_song_name_and_main_artist, type)
    elif x == '!open':
        if type == 'track':
            print('\n' + 'That command is reserved for items of type ' + colored('album/playlist/artist', 'magenta') + '.' + '\n')
            internal_search(id, counter_to_song_name_and_main_artist, type)
        elif type == 'artist':
            artist_URL = sp.artist(new_id)['external_urls']['spotify']
            webbrowser.open(artist_URL)
            print('\n' + 'Opening artist page ...' + '\n')
            internal_search(id, counter_to_song_name_and_main_artist, type)
        elif type == 'album':
            album_URL = sp.album(new_id)['external_urls']['spotify']
            webbrowser.open(album_URL)
            print('\n' + 'Opening album ...' + '\n')
            internal_search(id, counter_to_song_name_and_main_artist, type)
    elif x == '!image':
        if type == 'track':
            print('\n' + 'That command is reserved for items of type ' + colored('album/playlist/artist', 'magenta') + '.' + '\n')
            internal_search(id, counter_to_song_name_and_main_artist, type)
        elif type == 'artist':
            artist_URL = sp.artist(new_id)['images'][0]['url']
            webbrowser.open(artist_URL)
            print('\n' + 'Opening artist image ...' + '\n')
            internal_search(id, counter_to_song_name_and_main_artist, type)
        elif type == 'album':
            album_URL = sp.album(new_id)['images'][0]['url']
            webbrowser.open(album_URL)
            print('\n' + 'Opening artist image ...' + '\n')
            internal_search(id, counter_to_song_name_and_main_artist, type)
    elif x == '!back':
        print('\033c', end = None)
        get_information(original_id)
    else:
        external_search_helper(x, True)

def print_and_clear(id, message):
    print('\033c', end = None)
    print(message + '\n')
    get_information(id)

def return_album_information(id):
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
    counter_to_song_name_and_main_artist = {}
    counter = 1
    for track in sp.album_tracks(album_id)['items']:
        song_name = track['name']
        main_artist = track['artists'][0]['name']
        artist_list = []
        if counter not in counter_to_song_name_and_main_artist:
            counter_to_song_name_and_main_artist[counter] = song_name + ' ' + main_artist
        for artist in track['artists']:
            artist_list.append(artist['name'])
        print(str(counter) + '. ' + colored(song_name, 'cyan') + colored(' by ', 'grey') + str(artist_list))
        counter += 1
    print('')
    internal_search(id, counter_to_song_name_and_main_artist, 'album')

def return_artist_information(id, artist_list):
    if isinstance(id, list):
        artist_id = id[1]
    else:
        artist_id = id

    main_artist = sp.artist(artist_id)['name']
    if main_artist in artist_list:
        artist_list.remove(main_artist)
    artist_URL = sp.artist(artist_id)['external_urls']['spotify']
    genre_list = str(sp.artist(artist_URL)['genres'])
    popularity = str(sp.artist(artist_URL)['popularity'])
    total_followers = str(sp.artist(artist_URL)['followers']['total'])
    if len(artist_list) != 0:
        print(colored(' ' + str(main_artist) + ' ', 'grey', on_color = 'on_white') + ' with ' + str(artist_list) + '\n')
    else:
        print(colored(' ' + str(main_artist) + ' ', 'grey', on_color = 'on_white') + '\n')
    print(colored('Genres: ', 'red') + genre_list)
    print(colored('Popularity: ', 'yellow') + popularity)
    print(colored('Total Followers: ', 'green') + total_followers)

    related_artist_list = []
    for related_artist in sp.artist_related_artists(artist_URL)['artists']:
        related_artist_list.append(related_artist['name'])
    print(colored('Related Artists: ', 'blue') + str(related_artist_list))

    print(colored('Top Tracks:', 'magenta'))
    counter_to_song_name_and_main_artist = {}
    counter = 1
    for track in sp.artist_top_tracks(artist_URL)['tracks']:
        song_name = track['name']
        main_artist = track['artists'][0]['name']
        co_artist_list = []
        if counter not in counter_to_song_name_and_main_artist:
            counter_to_song_name_and_main_artist[counter] = song_name + ' ' + main_artist
        for co_artist in track['artists']:
            co_artist_list.append(co_artist['name'])
        if main_artist in co_artist_list:
            co_artist_list.remove(main_artist)
        if len(co_artist_list) != 0:
            print(str(counter) + '. ' + colored(song_name, 'cyan') + colored(' with ', 'grey') + str(co_artist_list))
        else:
            print(str(counter) + '. ' + colored(song_name, 'cyan'))
        counter += 1

    print(colored('Albums:', attrs = ['bold', 'underline', 'dark']))
    counter = 1
    for album in sp.artist_albums(artist_URL)['items']:
        album_name = album['name']
        album_total_tracks = str(album['total_tracks'])
        print(str(counter) + '. ' + colored(album_name, 'cyan') + colored(' with ', 'grey') + album_total_tracks + ' song(s)')
        counter += 1
    print('')
    internal_search(id, counter_to_song_name_and_main_artist, 'artist')

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
            print('\n' + 'Invalid command!' +'\n')
            get_information(id)
    else:
        print('')
        get_information(id)

    if 0 <= x <= sp.track(id)['duration_ms']:
        pass
    elif isinstance(x, int):
        print('\n' + 'The timestamp inputted is out of range!' +'\n')
        toggle(id)
    else:
        print('\n' + 'Invalid command!' +'\n')
        get_information(id)

    sp.seek_track(x)
    print('\033c', end = None)
    print('Setting the timestamp to: ' + colored(' ' + parse_time(x) + ' ', on_color = 'on_white')  + '\n')
    duration_int = sp.track(id)['duration_ms']
    print_progress_bar(x, duration_int, prefix = 'Progress:', suffix = 'Complete', length = 50)
    print('\n')
    get_information(id)

def get_user_information(id):
    display_name = sp.current_user()['display_name']
    followers = str(sp.current_user()['followers']['total'])
    print(colored('Display Name: ', 'red') + display_name)
    print(colored('Followers: ', 'yellow') + followers)
    print(colored('User Link: ', 'green') + sp.current_user()['external_urls']['spotify'])

    print(colored('User Top Tracks: ', 'blue'))
    counter_to_song_name_and_main_artist = {}
    counter = 1
    for track in sp.current_user_top_tracks()['items']:
        song_name = track['name']
        main_artist = track['artists'][0]['name']
        artist_list = []
        if counter not in counter_to_song_name_and_main_artist:
            counter_to_song_name_and_main_artist[counter] = song_name + ' ' + main_artist
        for artist in track['artists']:
            artist_list.append(artist['name'])
        print(str(counter) + '. ' + colored(song_name, 'cyan') + colored(' by ', 'grey') + str(artist_list))
        counter += 1

    print(colored('User Top Artists', 'magenta'))
    counter = 1
    for artist in sp.current_user_top_artists()['items']:
        print(str(counter) + '. ' + colored(artist['name'], 'cyan'))
        counter += 1

    print('')
    internal_search(id, counter_to_song_name_and_main_artist, 'track')

def volume(id):
    x = input('    volume> ')

    if x.isdigit() and 0 <= int(x) <= 100:
        x = int(x)
    elif x.isdigit():
        print('\n' + 'The volume inputted is out of range!' +'\n')
        volume(id)
    elif x == '!keep':
        print('')
        get_information(id)
    else:
        print('\n' + 'Invalid command!' +'\n')
        get_information(id)

    print('\033c', end = None)
    print('Setting the volume to: ' + colored(' ' + str(x) + ' ', on_color = 'on_white')  + '\n')
    sp.volume(x)
    get_information(id)

def return_playlist_information(id):
    if isinstance(id, list):
        playlist_id = id[1]
    else:
        playlist_id = id

    playlist_name = sp.playlist(playlist_id)['name']
    print(sp.playlist(playlist_id))
    pass

if __name__ == '__main__':
    main()