from email.policy import HTTP
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
    clear_terminal()
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
            populate_information_list(song, id_to_song_information)
            clear_terminal()
            get_information(song['id'], type)
        else:
            print('\n' + 'No song currently playing.' + '\n')
    else:
        search_helper(x, True)

def choose_item(counter_to_list, external_search, type):
    if external_search:
        x = input('item_number> ')

        if x.isdigit() and 1 <= int(x) <= 10:
            # TODO: helper?
            id = counter_to_list[int(x)].partition('id: ')[2]
            description = counter_to_list[int(x)].partition(', id: ')[0]
            print('\033c', end = None)
            print('Selected song ' + description + '\n')
            get_information(id, type)
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
        print('Selected song ' + description + '\n')
        get_information(id, type)

def get_information(id, type):
    x = input('command> ')
    print('')

    if x == 'name':
        if type == 'track':
            print(colored(' ' + sp.track(id)['name'] + ' ', 'grey', on_color = 'on_white') + '\n')
        elif type == 'album':
            print(colored(' ' + sp.album(id)['name'] + ' ', 'grey', on_color = 'on_white') + '\n')
        get_information(id, type)

    elif x == 'artist name':
        artist_list = []
        if type == 'track':
            for artist in sp.track(id)['artists']:
                artist_list.append(artist['name'])
            print(colored(' ' + str(artist_list) + ' ', 'grey', on_color = 'on_white') + '\n')
        elif type == 'album':
            pass
        get_information(id, type)

    elif x == 'popularity':
        popularity = str(sp.track(id)['popularity'])
        get_information_helper(id, popularity, type)

    elif x == 'album name':
        album_name = sp.track(id)['album']['name']
        get_information_helper(id, album_name, type)

    elif x == 'release date':
        release_date = sp.track(id)['album']['release_date']
        get_information_helper(id, release_date, type)

    elif x == 'duration':
        duration = sp.track(id)['duration_ms']
        duration = parse_time(duration)
        get_information_helper(id, duration, type)

    elif x == 'explicit':
        explicit = sp.track(id)['explicit']
        if explicit:
            print(colored(str(explicit), 'red') + '\n')
        else:
            print(colored(str(explicit), 'green') + '\n')
        get_information(id, type)

    elif x == 'artist info':
        artist_URL = sp.track(id)['album']['artists'][0]['external_urls']['spotify']
        popularity = str(sp.artist(artist_URL)['popularity'])
        total_followers = str(sp.artist(artist_URL)['followers']['total'])
        genre_list = str(sp.artist(artist_URL)['genres'])
        print(colored('Popularity: ', 'red') + popularity)
        print(colored('Total Followers: ', 'yellow') + total_followers)
        print(colored('Genres: ', 'green') + genre_list)

        related_artist_list = []
        for related_artist in sp.artist_related_artists(artist_URL)['artists']:
            related_artist_list.append(related_artist['name'])
        print(colored('Related Artists: ', 'blue') + str(related_artist_list))

        print(colored('Top Tracks:', 'magenta'))
        counter_to_song_name_and_main_artist = {}
        counter = 1
        for track in sp.artist_top_tracks(artist_URL)['tracks']:
            song_name = track['name']
            main_artist = sp.track(id)['artists'][0]['name']
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
        internal_search(id, counter_to_song_name_and_main_artist, type)

    elif x == 'lyrics':
        song_name = sp.track(id)['name']
        if ' - From' in song_name:
            song_name = song_name.partition(' - From')[0]
        if ' (feat.' in song_name:
            song_name = song_name.partition(' (feat.')[0]
        print('Searching ...' + '\n')
        block_print()
        song_name = genius.search_song(song_name, sp.track(id)['artists'][0]['name'])
        enable_print()
        if song_name is None:
            print_and_clear(id, 'No lyrics found.', type)
        else:
            print_and_clear(id, song_name.lyrics, type)

    elif x == 'open':
        song_URL = sp.track(id)['external_urls']['spotify']
        webbrowser.open(song_URL)
        print_and_clear(id, 'Opening song ...', type)

    elif x  == 'album page':
        album_URL = sp.track(id)['album']['external_urls']['spotify']
        webbrowser.open(album_URL)
        print_and_clear(id, 'Opening album ...', type)

    elif x == 'artist page':
        artist_URL = sp.track(id)['album']['artists'][0]['external_urls']['spotify']
        webbrowser.open(artist_URL)
        print_and_clear(id, 'Opening artist page ...', type)

    elif x == 'image':
        image_URL = sp.track(id)['album']['images'][0]['url']
        webbrowser.open(image_URL)
        print_and_clear(id, 'Opening image ...', type)

    elif x == 'play':
        song_URI_list = [sp.track(id)['uri']]
        song_name = sp.track(id)['name']
        artist_list = []
        for artist in sp.track(id)['artists']:
            artist_list.append(artist['name'])
        sp.start_playback(device_id = 'bddcb19206692c58a23c8c88a13144e1d7e4541e', uris = song_URI_list)
        print_and_clear(id, 'Playing ' + colored(song_name, 'red') + ' by ' + colored(artist_list, 'blue') + ' ...', type)

    elif x == 'continue':
        try:
            if not sp.current_playback()['is_playing']:
                sp.start_playback()
                print_and_clear(id, 'Continuing ...', type)
            else:
                print_and_clear(id, 'Already playing.', type)
        except:
            print_and_clear(id, 'No active device.', type)

    elif x == 'pause':
        try:
            if sp.current_playback()['is_playing']:
                sp.pause_playback()
                print_and_clear(id, 'Paused.', type)
            else:
                print_and_clear(id, 'Already paused.', type)
        except:
            print_and_clear(id, 'No active device.', type)

    elif x =='volume':
        volume(id, type)

    elif x == 'loop':
        sp.repeat('track')
        print_and_clear(id, 'Repeating ...', type)

    elif x == 'timestamp':
        timestamp_int = sp.current_user_playing_track()['progress_ms']
        duration_int = sp.track(id)['duration_ms']
        timestamp_string = parse_time(timestamp_int)
        duration_string = parse_time(duration_int)
        print(colored(' ' + timestamp_string + '/' + duration_string + ' ', 'grey', on_color = 'on_white') + '\n')
        print_progress_bar(timestamp_int, duration_int, prefix = 'Progress:', suffix = 'Complete', length = 50)
        print('\n')
        get_information(id, type)

    elif x == 'toggle':
        toggle(id, type)

    elif x == 'queue':
        try:
            song_URI = sp.track(id)['uri']
            sp.add_to_queue(song_URI)
            print_and_clear(id, 'Adding to queue ...', type)
        except:
            print_and_clear(id, 'No active device.', type)

    elif x == 'current':
        if sp.current_user_playing_track() is not None:
            song_name = sp.current_user_playing_track()['item']['name']
            artist_list = []
            for artist in sp.current_user_playing_track()['item']['artists']:
                artist_name = artist['name']
                artist_list.append(artist_name)
            print(colored(song_name, 'red') + ' by ' + colored(str(artist_list), 'blue') + '\n')
            get_information(id, type)
        else:
            print('No song is currently playing.' + '\n')
            get_information(id, type)

    elif x == 'next':
        try:
            sp.next_track()
            next_song_id = sp.current_user_playing_track()['item']['id']
            print_and_clear(next_song_id, 'Skipping to next ...', type)
        except:
            print_and_clear(id, 'No active device.', type)

    elif x == 'previous':
        try:
            sp.previous_track()
            previous_song_id = sp.current_user_playing_track()['item']['id']
            print_and_clear(previous_song_id, 'Going back to previous ...', type)
        except:
            print_and_clear(id, 'No active device.', type)

    elif x == 'save':
        saved = sp.current_user_saved_tracks_contains([id])[0]
        if saved:
            print_and_clear(id, 'Already saved.', type)
        else:
            sp.current_user_saved_tracks_add([id])
            print_and_clear(id, 'Saving ...', type)

    elif x == 'user info':
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
            main_artist = sp.track(id)['artists'][0]['name']
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
        internal_search(id, counter_to_song_name_and_main_artist, type)

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
        internal_search(id, counter_to_song_name_and_main_artist, type)

    elif x == 'redo':
        main()

    elif x == 'quit':
        print('\033c', end = None)
        return

    elif x == 'test':
        print(sp.new_releases())
        print(sp.featured_playlists())

        get_information(id, type)

    else:
        print('Invalid command!' + '\n')
        get_information(id, type)

def clear_terminal():
    print('\033c', end = None)
    term_size = os.get_terminal_size()
    print('=' * term_size.columns + '\n')

def populate_information_list(item, id_to_information):
    if item['id'] not in id_to_information:
        id_to_information[item['id']] = []
    id_to_information[item['id']].append(item['name'])
    artist_list = []
    for artist in item['artists']:
        artist_list.append(artist['name'])
    id_to_information[item['id']].append(artist_list)

def search_helper(x, external_search):
    if '!a' in x:
        x = x.partition('!a ')[2]
        search = (sp.search(q = x, type = 'album', limit = 10))['albums']
        type = 'album'
    elif '!p' in x:
        x = x.partition('!p ')[2]
        search = (sp.search(q = x, type = 'playlist', limit = 10))['playlists']
        type = 'playlist'
        print(search)
    else:
        search = (sp.search(q = x, type = 'track', limit = 10))['tracks']
        type = 'song'

    id_to_information = {}
    for item in search['items']:
        populate_information_list(item, id_to_information)
    print('\033c', end = None)

    counter = 1
    counter_to_list = {}
    for id, information in id_to_information.items():
        song_name = information[0]
        artist_list = str(information[1])
        id = str(id)
        colored_description = colored(song_name, 'red') + ' by ' + colored(artist_list, 'blue') + ', id: ' + colored(id, 'green')
        description = colored(song_name, 'red') + ' by ' + colored(artist_list, 'blue') + ', id: ' + id
        if external_search:
            print(str(counter) + '. ' + colored_description + ', ' + colored('type: ' + type, 'magenta'))
        if counter not in counter_to_list:
            counter_to_list[counter] = description
        counter += 1

    print('')
    choose_item(counter_to_list, external_search, type)

def get_information_helper(id, information, type):
    print(colored(' ' + information + ' ', 'grey', on_color = 'on_white') + '\n')
    get_information(id, type)

def print_and_clear(id, message, type):
    print('\033c', end = None)
    print(message + '\n')
    get_information(id, type)

def internal_search(id, counter_to_song_name_and_main_artist, type):
    x = input('internal_search> ')

    if x.isdigit() and 1 <= int(x) <= 10:
        x = counter_to_song_name_and_main_artist[int(x)]
        search_helper(x, False)
    elif x.isdigit():
        print('\n' + 'The number inputted is outside of the result list size of 10!' +'\n')
        internal_search(id, counter_to_song_name_and_main_artist, type)
    elif x == '!back':
        print('\033c', end = None)
        get_information(id, type)
    else:
        search_helper(x, True)

def volume(id, type):
    x = input('    volume> ')

    if x.isdigit() and 0 <= int(x) <= 100:
        x = int(x)
    elif x.isdigit():
        print('\n' + 'The volume inputted is out of range!' +'\n')
        volume(id, type)
    elif x == '!keep':
        print('')
        get_information(id, type)
    else:
        print('\n' + 'Invalid command!' +'\n')
        get_information(id, type)

    print('\033c', end = None)
    print('Setting the volume to: ' + colored(' ' + str(x) + ' ', on_color = 'on_white')  + '\n')
    sp.volume(x)
    get_information(id, type)

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

def toggle(id, type):
    x = input('    timestamp> ')

    if x != '!keep':
        try:
            x = x.partition(':')
            minute = int(x[0])
            second = int(x[2])
            x = (minute * 60 + second) * 1000
        except:
            print('\n' + 'Invalid command!' +'\n')
            get_information(id, type)
    else:
        print('')
        get_information(id, type)

    if 0 <= x <= sp.track(id)['duration_ms']:
        pass
    elif isinstance(x, int):
        print('\n' + 'The timestamp inputted is out of range!' +'\n')
        toggle(id, type)
    else:
        print('\n' + 'Invalid command!' +'\n')
        get_information(id, type)

    sp.seek_track(x)
    print('\033c', end = None)
    print('Setting the timestamp to: ' + colored(' ' + parse_time(x) + ' ', on_color = 'on_white')  + '\n')
    duration_int = sp.track(id)['duration_ms']
    print_progress_bar(x, duration_int, prefix = 'Progress:', suffix = 'Complete', length = 50)
    print('\n')
    get_information(id, type)

def block_print():
    sys.stdout = open(os.devnull, 'w')

def enable_print():
    sys.stdout = sys.__stdout__

if __name__ == '__main__':
    main()

# look through https://spotipy.readthedocs.io/en/2.12.0/, try-catch, info clear, type (album)