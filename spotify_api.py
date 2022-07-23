import spotipy
import spotipy.util as util
from lyricsgenius import Genius
import speech_recognition as sr
import webbrowser
import sys, os
from termcolor import colored
import math

username = 'chiusiun'
scope = 'user-read-currently-playing user-modify-playback-state user-read-playback-state user-read-recently-played'
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
            populate_song_information_list(song, id_to_song_information)
            clear_terminal()
            get_song_information(song['id'])
        else:
            print('\n' + 'No song currently playing.' + '\n')
    else:
        search_helper(x, True)

def choose_song(counter_to_list, external_search):
    if external_search:
        x = input('song_number> ')

        if x.isdigit() and 1 <= int(x) <= 10:
            id = counter_to_list[int(x)].partition('id: ')[2]
            description = counter_to_list[int(x)].partition(', id: ')[0]
            print('\033c', end = None)
            print('Selected song (' + description + ')' + '\n')
            get_song_information(id)
        elif x.isdigit():
            print('\n' + 'The number inputted is outside of the result list size of 10!' +'\n')
            choose_song(counter_to_list, True)
        elif x == 'redo':
            main()
        elif x == 'quit':
            print('\033c', end = None)
            return
        else:
            print('\n' + 'Invalid command!' + '\n')
            choose_song(counter_to_list, True)
    else:
        id = counter_to_list[1].partition('id: ')[2]
        description = counter_to_list[1].partition(', id: ')[0]
        print('\033c', end = None)
        print('Selected song (' + description + ')' + '\n')
        get_song_information(id)

def get_song_information(id):
    x = input('command> ')
    print('')

    if x == 'song name':
        print(colored(' ' + sp.track(id)['name'] + ' ', 'grey', on_color = 'on_white') + '\n')
        get_song_information(id)

    elif x == 'artist name':
        artist_list = []
        for artist in sp.track(id)['artists']:
            artist_list.append(artist['name'])
        print(colored(' ' + str(artist_list) + ' ', 'grey', on_color = 'on_white') + '\n')
        get_song_information(id)

    elif x == 'album name':
        album_name = sp.track(id)['album']['name']
        get_song_information_helper(id, album_name)

    elif x == 'release date':
        release_date = sp.track(id)['album']['release_date']
        get_song_information_helper(id, release_date)

    elif x == 'popularity':
        popularity = str(sp.track(id)['popularity'])
        get_song_information_helper(id, popularity)

    elif x == 'duration':
        duration = sp.track(id)['duration_ms']/60000
        frac, whole = math.modf(duration)
        duration = str(int(whole)) + ':' + str(round(frac, 2)).partition('.')[2]
        get_song_information_helper(id, duration)

    elif x == 'open':
        song_URL = sp.track(id)['external_urls']['spotify']
        webbrowser.open(song_URL)
        print_and_clear(id, 'Opening song ...')

    elif x  == 'album page':
        album_URL = sp.track(id)['album']['external_urls']['spotify']
        webbrowser.open(album_URL)
        print_and_clear(id, 'Opening album ...')

    elif x == 'artist page':
        artist_URL = sp.track(id)['album']['artists'][0]['external_urls']['spotify']
        webbrowser.open(artist_URL)
        print_and_clear(id, 'Opening artist page ...')

    elif x == 'image':
        image_URL = sp.track(id)['album']['images'][0]['url']
        webbrowser.open(image_URL)
        print_and_clear(id, 'Opening image ...')

    elif x == 'explicit':
        explicit = sp.track(id)['explicit']
        if explicit:
            print(colored(str(explicit), 'red') + '\n')
        else:
            print(colored(str(explicit), 'green') + '\n')
        get_song_information(id)

    elif x == 'artist info':
        artist_URL = sp.track(id)['album']['artists'][0]['external_urls']['spotify']
        total_followers = str(sp.artist(artist_URL)['followers']['total'])
        genre_list = str(sp.artist(artist_URL)['genres'])
        popularity = str(sp.artist(artist_URL)['popularity'])

        print(colored('Total Followers: ', 'red') + total_followers)
        print(colored('Genres: ', 'yellow') + genre_list)
        print(colored('Popularity: ', 'green') + popularity)

        related_artist_list = []
        for related_artist in sp.artist_related_artists(artist_URL)['artists']:
            related_artist_list.append(related_artist['name'])
        print(colored('Related Artists: ', 'blue') + str(related_artist_list))
        print(colored('Top Tracks:', 'magenta'))

        counter_to_song_name_and_main_artist = {}
        counter = 1
        for track in sp.artist_top_tracks(artist_URL)['tracks']:
            co_artist_list = []
            main_artist = sp.track(id)['artists'][0]['name']
            song_name = track['name']

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
        print(colored('Albums:', attrs = ['bold', 'underline']))

        counter = 1
        for album in sp.artist_albums(artist_URL)['items']:
            album_name = album['name']
            album_total_track = str(album['total_tracks'])

            print(str(counter) + '. ' + colored(album_name, 'cyan') + colored(' with ', 'grey') + album_total_track + ' song(s)')
            counter += 1
        print('')
        internal_search(id, counter_to_song_name_and_main_artist)

    elif x == 'lyrics':
        song_name = sp.track(id)['name']
        if ' - From' in song_name:
            song_name = song_name.partition(' - From')[0]
        if ' (feat.' in song_name:
            song_name = song_name.partition(' (feat.')[0]
        print('Searching ...' + '\n')
        block_print()
        song_name = genius.search_song(song_name, sp.track(id)['artists'][0])
        enable_print()
        if song_name is None:
            print_and_clear(id, 'No lyrics found.')
        else:
            print_and_clear(id, song_name.lyrics)

    elif x == 'play':
        song_URI_list = [sp.track(id)['uri']]
        song_name = sp.track(id)['name']
        artist_list = []
        for artist in sp.track(id)['artists']:
            artist_list.append(artist['name'])

        sp.start_playback(device_id = 'bddcb19206692c58a23c8c88a13144e1d7e4541e', uris = song_URI_list)
        print_and_clear(id, 'Playing ' + colored(song_name, 'red') + ' by ' + colored(artist_list, 'blue') + ' ...')

    elif x == 'continue':
        try:
            if not sp.current_playback()['is_playing']:
                sp.start_playback()
                print_and_clear(id, 'Continuing ...')
            else:
                print_and_clear(id, 'Already playing.')
        except:
            print_and_clear(id, 'No active device.')

    elif x == 'pause':
        try:
            if sp.current_playback()['is_playing']:
                sp.pause_playback()
                print_and_clear(id, 'Paused.')
            else:
                print_and_clear(id, 'Already paused.')
        except:
            print_and_clear(id, 'No active device.')

    elif x =='volume':
        volume(id)

    elif x == 'loop':
        sp.repeat('track')
        print_and_clear(id, 'Repeating ...')

    elif x == 'toggle':
        pass

    elif x == 'queue':
        try:
            song_URI = sp.track(id)['uri']
            sp.add_to_queue(song_URI)
            print_and_clear(id, 'Adding to queue ...')
        except:
            print_and_clear(id, 'No active device.')

    elif x == 'current':
        if sp.current_user_playing_track() is not None:
            artist_list = []
            song_name = sp.current_user_playing_track()['item']['name']
            for artist in sp.current_user_playing_track()['item']['artists']:
                artist_name = artist['name']
                artist_list.append(artist_name)
            print(colored(song_name, 'red') + ' by ' + colored(str(artist_list), 'blue') + '\n')
            get_song_information(id)
        else:
            print('No song is currently playing.' + '\n')
            get_song_information(id)

    elif x == 'next':
        try:
            sp.next_track()
            print_and_clear(id, 'Skipping to next ...')
        except:
            print_and_clear(id, 'No active device.')

    elif x == 'previous':
        try:
            sp.previous_track()
            print_and_clear(id, 'Going back to previous ...')
        except:
            print_and_clear(id, 'No active device.')

    elif x == 'user info':
        display_name = sp.current_user()['display_name']
        followers = str(sp.current_user()['followers']['total'])

        print(colored('Display Name: ', 'red') + display_name)
        print(colored('Followers: ', 'yellow') + followers)
        print(sp.currently_playing())
        print(sp.track(id))
        print('')

        get_song_information(id)

    elif x == 'recent':
        # TODO: internal search
        counter = 1
        for song_name in sp.current_user_recently_played(10)['items']:
            song_name = song_name['track']['name']
            song_ID = song_name['track']['id']
            artist_list = []
            for artist in song_name['track']['artists']:
                artist_list.append(artist['name'])
            print(str(counter) + '. ' + colored(song_name, 'red') + ' by ' + colored(str(artist_list), 'blue') + ', id: ' + colored(song_ID, 'green'))
            counter += 1
        print('')
        get_song_information(id)

    elif x == 'redo':
        main()

    elif x == 'quit':
        print('\033c', end = None)
        return

    else:
        print('Invalid command!' + '\n')
        get_song_information(id)

def clear_terminal():
    print('\033c', end = None)
    term_size = os.get_terminal_size()
    print('=' * term_size.columns + '\n')

def populate_song_information_list(song, id_to_song_information):
    if song['id'] not in id_to_song_information:
        id_to_song_information[song['id']] = []
    id_to_song_information[song['id']].append(song['name'])
    artist_name_list = []
    for artist in song['artists']:
        artist_name_list.append(artist['name'])
    id_to_song_information[song['id']].append(artist_name_list)

def search_helper(x, external_search):
    search = (sp.search(q = x, type = 'track', limit = 10))['tracks']

    id_to_song_information = {}
    for song in search['items']:
        populate_song_information_list(song, id_to_song_information)

    print('\033c', end = None)
    counter = 1
    counter_to_list = {}
    for id, song_information in id_to_song_information.items():
        song_name = song_information[0]
        artist_list = str(song_information[1])
        id = str(id)

        colored_description = colored(song_name, 'red') + ' by ' + colored(artist_list, 'blue') + ', id: ' + colored(id, 'green')
        description = colored(song_name, 'red') + ' by ' + colored(artist_list, 'blue') + ', id: ' + id
        if external_search:
            print(str(counter) + '. ' + colored_description)
        if counter not in counter_to_list:
            counter_to_list[counter] = description
        counter += 1
    print('')

    choose_song(counter_to_list, external_search)

def get_song_information_helper(id, information):
    print(colored(' ' + information + ' ', 'grey', on_color = 'on_white') + '\n')
    get_song_information(id)

def print_and_clear(id, message):
    print('\033c', end = None)
    print(message + '\n')
    get_song_information(id)

def volume(id):
    x = input('    volume> ')

    if x.isdigit() and 0 <= int(x) <= 100:
        x = int(x)
    elif x.isdigit():
        print('\n' + 'The volume inputted is out of range!' +'\n')
        volume(id)
    elif x == '!keep':
        print('')
        get_song_information(id)
    else:
        print('\n' + 'Invalid command!' +'\n')
        get_song_information(id)

    print('\033c', end = None)
    print('Setting the volume to: ' + colored(' ' + str(x) + ' ', on_color = 'on_white')  + '\n')
    sp.volume(x)
    get_song_information(id)

def toggle(id):
    x = input('    toggle> ')

    if x.isdigit() and 0 <= int(x) <= 100:
        x = int(x)
    elif x.isdigit():
        print('\n' + 'The volume inputted is out of range!' +'\n')
        volume(id)
    elif x == '!keep':
        print('')
        get_song_information(id)
    else:
        print('\n' + 'Invalid command!' +'\n')
        get_song_information(id)

    print('\033c', end = None)
    print('Setting the timestamp to: ' + colored(' ' + str(x) + ' ', on_color = 'on_white')  + '\n')
    sp.volume(x)
    get_song_information(id)

def internal_search(id, counter_to_song_name_and_main_artist):
    x = input('internal_search> ')

    if x.isdigit() and 1 <= int(x) <= 10:
        x = counter_to_song_name_and_main_artist[int(x)]
        search_helper(x, False)
    elif x.isdigit():
        print('\n' + 'The number inputted is outside of the result list size of 10!' +'\n')
        internal_search(id, counter_to_song_name_and_main_artist)
    elif x == '!back':
        print('\033c', end = None)
        get_song_information(id)
    else:
        search_helper(x, True)

def block_print():
    sys.stdout = open(os.devnull, 'w')

def enable_print():
    sys.stdout = sys.__stdout__

if __name__ == '__main__':
    main()

# look through https://spotipy.readthedocs.io/en/2.12.0/, playlist methods, timeline using progress_ms, next = select it