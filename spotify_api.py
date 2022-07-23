import spotipy
import spotipy.util as util
from lyricsgenius import Genius
import speech_recognition as sr
import webbrowser
import sys, os
from termcolor import colored

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
            os.system('cls' if os.name == 'nt' else 'clear')
            print('Listening ...' + '\n')
            audio = r.listen(source)
            x = r.recognize_google(audio)

    if x == '!skip':
        if sp.current_user_playing_track() is not None:
            id_to_song_information = {}
            song = sp.current_user_playing_track()['item']
            populate_song_information_list(song, id_to_song_information)
            clear_terminal()
            get_song_information(id_to_song_information, song['id'])
        else:
            print('\n' + 'No song currently playing.' + '\n')
    else:
        search_helper(x, True)

def choose_song(id_to_song_information, counter_to_list, external_search):

    if external_search:
        x = input('song_number> ')

        if x.isdigit() and 1 <= int(x) <= 10:
            id = counter_to_list[int(x)].partition('id: ')[2]
            description = counter_to_list[int(x)].partition(', id: ')[0]
            os.system('cls' if os.name == 'nt' else 'clear')
            print('Selected song (' + description + ')' + '\n')
            get_song_information(id_to_song_information, id)
        elif x.isdigit():
            print('\n' + 'The number inputted is outside of the result list size of 10!' +'\n')
            choose_song(id_to_song_information, counter_to_list, True)
        elif x == 'redo':
            main()
        elif x == 'quit':
            os.system('cls' if os.name == 'nt' else 'clear')
            return
        else:
            print('\n' + 'Invalid command!' + '\n')
            choose_song(id_to_song_information, counter_to_list, True)
    else:
        id = counter_to_list[1].partition('id: ')[2]
        description = counter_to_list[1].partition(', id: ')[0]
        os.system('cls' if os.name == 'nt' else 'clear')
        print('Selected song (' + description + ')' + '\n')
        get_song_information(id_to_song_information, id)

def get_song_information(id_to_song_information, id):
    x = input('command> ')
    print('')

    if x == 'song name':
        get_song_information_helper(id_to_song_information, id, 0)
    elif x == 'artist name':
        get_song_information_helper(id_to_song_information, id, 1)
    elif x == 'album name':
        get_song_information_helper(id_to_song_information, id, 2)
    elif x == 'release date':
        get_song_information_helper(id_to_song_information, id, 3)
    elif x == 'popularity':
        get_song_information_helper(id_to_song_information, id, 4)
    elif x == 'open':
        song_URL = id_to_song_information[id][6]
        webbrowser.open(song_URL)
        print_and_clear(id_to_song_information, id, 'Opening song ...')
    elif x  == 'album page':
        album_URL = id_to_song_information[id][7]
        webbrowser.open(album_URL)
        print_and_clear(id_to_song_information, id, 'Opening album ...')
    elif x == 'artist page':
        artist_URL = id_to_song_information[id][8]
        webbrowser.open(artist_URL)
        print_and_clear(id_to_song_information, id, 'Opening artist page ...')
    elif x == 'image':
        image_URL = id_to_song_information[id][9]
        webbrowser.open(image_URL)
        print_and_clear(id_to_song_information, id, 'Opening image ...')
    elif x == 'artist info':
        artist_URL = id_to_song_information[id][8]
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
            main_artist = id_to_song_information[id][1][0]
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
        internal_search(id_to_song_information, id, counter_to_song_name_and_main_artist)

        # print('')
        # get_song_information(id_to_song_information, id)
    elif x == 'lyrics':
        song = id_to_song_information[id][0]
        if ' - From' in song:
            song = song.partition(' - From')[0]
        if ' (feat.' in song:
            song = song.partition(' (feat.')[0]
        print('Searching ...' + '\n')
        block_print()
        song = genius.search_song(song, id_to_song_information[id][1][0])
        enable_print()
        if song is None:
            print_and_clear(id_to_song_information, id, 'No lyrics found.')
        else:
            print_and_clear(id_to_song_information, id, song.lyrics)
    elif x == 'play':
        song_URI_list = [id_to_song_information[id][5]]
        song_name = id_to_song_information[id][0]
        artist_list = str(id_to_song_information[id][1])

        sp.start_playback(device_id = 'bddcb19206692c58a23c8c88a13144e1d7e4541e', uris = song_URI_list)
        print_and_clear(id_to_song_information, id, 'Playing ' + colored(song_name, 'red') + ' by ' + colored(artist_list, 'blue') + ' ...')
    elif x == 'continue':
        try:
            if not sp.current_playback()['is_playing']:
                sp.start_playback()
                print_and_clear(id_to_song_information, id, 'Continuing ...')
            else:
                print_and_clear(id_to_song_information, id, 'Already playing.')
        except:
            print_and_clear(id_to_song_information, id, 'No active device.')
    elif x == 'pause':
        try:
            if sp.current_playback()['is_playing']:
                sp.pause_playback()
                print_and_clear(id_to_song_information, id, 'Paused.')
            else:
                print_and_clear(id_to_song_information, id, 'Already paused.')
        except:
            print_and_clear(id_to_song_information, id, 'No active device.')
    elif x =='volume':
        volume(id_to_song_information, id)
    elif x == 'loop':
        sp.repeat('track')
        print_and_clear(id_to_song_information, id, 'Repeating ...')
    elif x == 'queue':
        try:
            song_URI = id_to_song_information[id][5]
            sp.add_to_queue(song_URI)
            print_and_clear(id_to_song_information, id, 'Adding to queue ...')
        except:
            print_and_clear(id_to_song_information, id, 'No active device.')
    elif x == 'current':
        if sp.current_user_playing_track() is not None:
            artist_name_list = []
            song_name = sp.current_user_playing_track()['item']['name']
            for artist in sp.current_user_playing_track()['item']['artists']:
                artist_name = artist['name']
                artist_name_list.append(artist_name)
            print(colored(song_name, 'red') + ' by ' + colored(str(artist_name_list), 'blue') + '\n')
            get_song_information(id_to_song_information, id)
        else:
            print('No song is currently playing.' + '\n')
            get_song_information(id_to_song_information, id)
    elif x == 'next':
        try:
            sp.next_track()
            print_and_clear(id_to_song_information, id, 'Skipping to next ...')
        except:
            print_and_clear(id_to_song_information, id, 'No active device.')
    elif x == 'previous':
        try:
            sp.previous_track()
            print_and_clear(id_to_song_information, id, 'Going back to previous ...')
        except:
            print_and_clear(id_to_song_information, id, 'No active device.')
    elif x == 'recent':
        counter = 1
        for song in sp.current_user_recently_played(10)['items']:
            song_name = song['track']['name']
            song_ID = song['track']['id']
            artist_list = []
            for artist in song['track']['artists']:
                artist_list.append(artist['name'])

            print(str(counter) + '. ' + colored(song_name, 'red') + ' by ' + colored(str(artist_list), 'blue') + ', id: ' + colored(song_ID, 'green'))
            counter += 1
        
        print('')
        get_song_information(id_to_song_information, id)
    elif x == 'redo':
        main()
    elif x == 'quit':
        os.system('cls' if os.name == 'nt' else 'clear')
        return
    else:
        print('Invalid command!' + '\n')
        get_song_information(id_to_song_information, id)

def clear_terminal():
    os.system('cls' if os.name == 'nt' else 'clear')
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
    id_to_song_information[song['id']].append(song['album']['name'])
    id_to_song_information[song['id']].append(song['album']['release_date'])
    id_to_song_information[song['id']].append(song['popularity'])
    id_to_song_information[song['id']].append(song['uri'])
    id_to_song_information[song['id']].append(song['external_urls']['spotify'])
    id_to_song_information[song['id']].append(song['album']['external_urls']['spotify'])
    id_to_song_information[song['id']].append(song['album']['artists'][0]['external_urls']['spotify'])
    id_to_song_information[song['id']].append(song['album']['images'][0]['url'])

def search_helper(x, external_search):
    search = (sp.search(q = x, type = 'track', limit = 10))['tracks']

    id_to_song_information = {}
    for song in search['items']:
        populate_song_information_list(song, id_to_song_information)

    os.system('cls' if os.name == 'nt' else 'clear')
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

    choose_song(id_to_song_information, counter_to_list, external_search)

def get_song_information_helper(id_to_song_information, id, index):
    print(colored(' ' + str(id_to_song_information[id][index]) + ' ', 'grey', on_color = 'on_white') + '\n')
    get_song_information(id_to_song_information, id)

def print_and_clear(id_to_song_information, id, message):
    os.system('cls' if os.name == 'nt' else 'clear')
    print(message + '\n')
    get_song_information(id_to_song_information, id)

def volume(id_to_song_information, id):
    x = input('    volume> ')

    if x.isdigit() and 0 <= int(x) <= 100:
        x = int(x)
    elif x.isdigit():
        print('\n' + 'The volume inputted is out of range!' +'\n')
        volume(id_to_song_information, id)
    elif x == 'keep':
        print('')
        get_song_information(id_to_song_information, id)
    else:
        print('\n' + 'Invalid command!' +'\n')
        get_song_information(id_to_song_information, id)

    os.system('cls' if os.name == 'nt' else 'clear')
    print('Setting the volume to: ' + colored(' ' + str(x) + ' ', on_color = 'on_white')  + '\n')
    sp.volume(x)
    get_song_information(id_to_song_information, id)

def internal_search(id_to_song_information, id, counter_to_song_name_and_main_artist):
    x = input('internal_search> ')

    if x.isdigit() and 1 <= int(x) <= 10:
        x = counter_to_song_name_and_main_artist[int(x)]
        search_helper(x, False)
    elif x.isdigit():
        print('\n' + 'The number inputted is outside of the result list size of 10!' +'\n')
        internal_search(id_to_song_information, id, counter_to_song_name_and_main_artist)
    elif x == '!back':
        os.system('cls' if os.name == 'nt' else 'clear')
        get_song_information(id_to_song_information, id)
    else:
        search_helper(x, True)

def block_print():
    sys.stdout = open(os.devnull, 'w')

def enable_print():
    sys.stdout = sys.__stdout__

if __name__ == '__main__':
    main()

# look through https://spotipy.readthedocs.io/en/2.12.0/