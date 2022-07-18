import spotipy
import spotipy.util as util
import webbrowser
import os

username = 'chiusiun'
scope = 'user-read-currently-playing'
redirectURI = 'http://google.com/'
token = util.prompt_for_user_token(username, scope, '3aa6dc3eea4b485497c73da406f11802', 'c08afd7602b740589ccf5198eb2982a2', redirectURI)
sp = spotipy.Spotify(auth=token)

# playlist_link = 'https://open.spotify.com/playlist/37i9dQZEVXbNG2KDcFcKOF?si=1333723a6eff4b7f'
# playlist_URI = playlist_link.split("/")[-1].split("?")[0]

# for track in sp.playlist_tracks(playlist_URI)["items"]:
#     track_uri = track["track"]["uri"]
#     track_name = track["track"]["name"]
#     artist_uri = track["track"]["artists"][0]["uri"]
#     artist_info = sp.artist(artist_uri)
#     artist_name = track["track"]["artists"][0]["name"]
#     artist_pop = artist_info["popularity"]
#     artist_genres = artist_info["genres"]
#     album = track["track"]["album"]["name"]
#     track_pop = track["track"]["popularity"]

#     print(track_uri)
#     print(track_name)
#     print(artist_uri)
#     print(artist_info)
#     print(artist_name)
#     print(artist_pop)
#     print(artist_genres)
#     print(album)
#     print(track_pop)

def main():

    os.system('cls' if os.name == 'nt' else 'clear')
    term_size = os.get_terminal_size()
    print('=' * term_size.columns + '\n')

    dictionary_list = initial_search()
    id_to_song_information = dictionary_list[0]
    counter_to_id = dictionary_list[1]

    choose_song(id_to_song_information, counter_to_id)

def initial_search():
    x = input('search> ')
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

    return id_to_song_information, counter_to_list

def choose_song(id_to_song_information, counter_to_list):
    x = input('next_command> ')

    if x.isdigit() and 1 <= int(x) <= 10:
        id = counter_to_list[int(x)].partition('id:')[2]
        print('\n' + 'Selected song ' + str(x) + ' (' + counter_to_list[int(x)] + ')' + '\n')
        get_song_information(id_to_song_information, id)
    elif x.isdigit():
        print('\n' + 'The number inputted is outside of the result list size of 10!' +'\n')
        choose_song(id_to_song_information, counter_to_list)
    elif x == 'current':
        artist_name_list = []
        for artist in sp.current_user_playing_track()['item']['artists']:
            artist_name_list.append(artist['name'])
        print(str(sp.current_user_playing_track()['item']['name']) + ' by ' + str(artist_name_list))
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
    x = input('get_information> ')
    if x == 'name':
        print('\n' + str(id_to_song_information[id][0]) + '\n')
        get_song_information(id_to_song_information, id)
    elif x == 'artist name':
        print('\n' + str(id_to_song_information[id][1]) + '\n')
        get_song_information(id_to_song_information, id)
    elif x == 'album name':
        print('\n' + str(id_to_song_information[id][2]) + '\n')
        get_song_information(id_to_song_information, id)
    elif x == 'release date':
        print('\n' + str(id_to_song_information[id][3]) + '\n')
        get_song_information(id_to_song_information, id)
    elif x == 'popularity':
        print('\n' + str(id_to_song_information[id][4]) + '\n')
        get_song_information(id_to_song_information, id)
    elif x == 'play':
        webbrowser.open(id_to_song_information[id][5])
        os.system('cls' if os.name == 'nt' else 'clear')
        print('Opening song ...' + '\n')
        get_song_information(id_to_song_information, id)
    elif x  == 'album':
        webbrowser.open(id_to_song_information[id][6])
        os.system('cls' if os.name == 'nt' else 'clear')
        print('Opening album ...' + '\n')
        get_song_information(id_to_song_information, id)
    elif x == 'artist page':
        webbrowser.open(id_to_song_information[id][7])
        os.system('cls' if os.name == 'nt' else 'clear')
        print('Opening artist page ...' + '\n')
        get_song_information(id_to_song_information, id)
    elif x == 'image':
        webbrowser.open(id_to_song_information[id][8])
        os.system('cls' if os.name == 'nt' else 'clear')
        print('Opening artist page ...' + '\n')
        get_song_information(id_to_song_information, id)
    elif x == 'redo':
        main()
    elif x == 'quit':
        print('')
        return
    else:
        print('\n' + 'Invalid command!' + '\n')
        get_song_information(id_to_song_information, id)

# sp.add_to_queue()
# voice recognition, lyrics, fun facts

if __name__ == '__main__':
    main()