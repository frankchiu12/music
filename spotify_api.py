import spotipy
import spotipy.util as util
from lyricsgenius import Genius
import os
import webbrowser

username = 'chiusiun'
scope = 'user-read-currently-playing user-modify-playback-state user-read-playback-state user-read-recently-played'
redirectURI = 'http://google.com/'
token = util.prompt_for_user_token(username, scope, '3aa6dc3eea4b485497c73da406f11802', 'c08afd7602b740589ccf5198eb2982a2', redirectURI)
sp = spotipy.Spotify(auth=token)

client_access_token = 'Q8q2Cs-4YkZT_83az4gYWpQrkSthadNOWMeuJhJOmHmIB3sBj3_HMX9SY2gR2HC5'
genius = Genius(client_access_token)

os.system('open /Applications/Spotify.app')

def main():

    os.system('cls' if os.name == 'nt' else 'clear')
    term_size = os.get_terminal_size()
    print('=' * term_size.columns + '\n')

    initial_search()

def initial_search():
    x = input('search> ')

    if x == 'skip':
        if sp.current_user_playing_track() is not None:
            id_to_song_information = {}
            song = sp.current_user_playing_track()['item']
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

            os.system('cls' if os.name == 'nt' else 'clear')
            term_size = os.get_terminal_size()
            print('=' * term_size.columns + '\n')
            get_song_information(id_to_song_information, song['id'])
        else:
            print('\n' + 'No active device.' + '\n')
    else:
        search = (sp.search(q = x, type = 'track', limit = 10))['tracks']

        id_to_song_information = {}
        for song in search['items']:
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

        print('')
        counter = 1
        counter_to_list = {}
        for id, song_information in id_to_song_information.items():
            description = str(song_information[0]) + ' by ' + str(song_information[1]) + ', id:' + str(id)
            print(str(counter) + '. ' + description)
            if counter not in counter_to_list:
                counter_to_list[counter] = description
            counter += 1
        print('')

        choose_song(id_to_song_information, counter_to_list)

def choose_song(id_to_song_information, counter_to_list):
    x = input('song_number> ')

    if x.isdigit() and 1 <= int(x) <= 10:
        id = counter_to_list[int(x)].partition('id:')[2]
        print('\n' + 'Selected song ' + str(x) + ' (' + counter_to_list[int(x)] + ')' + '\n')
        get_song_information(id_to_song_information, id)
    elif x.isdigit():
        print('\n' + 'The number inputted is outside of the result list size of 10!' +'\n')
        choose_song(id_to_song_information, counter_to_list)
    elif x == 'redo':
        main()
    elif x == 'quit':
        print('\n')
        return
    else:
        print('\n' + 'Invalid command!' + '\n')
        choose_song(id_to_song_information, counter_to_list)

def get_song_information(id_to_song_information, id):
    x = input('command> ')
    print('')

    if x == 'name':
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
        webbrowser.open(id_to_song_information[id][6])
        print_and_clear(id_to_song_information, id, 'Opening song ...')
    elif x  == 'album':
        webbrowser.open(id_to_song_information[id][7])
        print_and_clear(id_to_song_information, id, 'Opening album ...')
    elif x == 'artist page':
        webbrowser.open(id_to_song_information[id][8])
        print_and_clear(id_to_song_information, id, 'Opening artist page ...')
    elif x == 'image':
        webbrowser.open(id_to_song_information[id][9])
        print_and_clear(id_to_song_information, id, 'Opening image ...')
    elif x == 'lyrics':
        song = genius.search_song(id_to_song_information[id][0], id_to_song_information[id][1])
        print_and_clear(id_to_song_information, id, '\n' + song.lyrics)
    elif x == 'play':
        sp.start_playback(device_id='bddcb19206692c58a23c8c88a13144e1d7e4541e', uris=[id_to_song_information[id][5]])
        print_and_clear(id_to_song_information, id, 'Playing ' + str(id_to_song_information[id][0]) + ' by ' + str(id_to_song_information[id][1]) + ' ...')
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
    elif x == 'loop':
        sp.repeat('track')
        print_and_clear(id_to_song_information, id, 'Repeating ...')
    elif x == 'queue':
        try:
            sp.add_to_queue(id_to_song_information[id][5])
            print_and_clear(id_to_song_information, id, 'Adding to queue ...')
        except:
            print_and_clear(id_to_song_information, id, 'No active device.')
    elif x == 'current':
        if sp.current_user_playing_track() is not None:
            artist_name_list = []
            for artist in sp.current_user_playing_track()['item']['artists']:
                artist_name_list.append(artist['name'])
            print('\n' 
            + str(sp.current_user_playing_track()['item']['name']) + ' by ' + str(artist_name_list) + '\n')
            get_song_information(id_to_song_information, id)
        else:
            print('\n' + 'No song is currently playing.' + '\n')
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
        # TODO
        print(sp.current_user_recently_played())
    elif x == 'redo':
        main()
    elif x == 'quit':
        print('')
        return
    else:
        print('\n' + 'Invalid command!' + '\n')
        get_song_information(id_to_song_information, id)

def clear_terminal():
    pass

def populate_song_information_list():
    pass

def get_song_information_helper(id_to_song_information, id, index):
    print(str(id_to_song_information[id][index]) + '\n')
    get_song_information(id_to_song_information, id)

def print_and_clear(id_to_song_information, id, message):
    os.system('cls' if os.name == 'nt' else 'clear')
    print(message + '\n')
    get_song_information(id_to_song_information, id)

if __name__ == '__main__':
    main()

# voice recognition, lyrics, fun facts, look through https://spotipy.readthedocs.io/en/2.12.0/ (later), sound notification