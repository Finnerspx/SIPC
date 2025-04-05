import spotify.client
import spotipy
from spotipy.oauth2 import SpotifyOAuth

"""
Search Tracks: Create a function that takes search parameters (keywords, genres, artists) and uses spotipy's search() method to find tracks.
Get Recommendations: Create a function using spotipy's recommendations() method. This is powerful as it allows seeding with genres, artists, tracks, and targeting specific audio features (danceability, energy, valence, etc.). This will likely be key for interpreting Gemini's output.
Get Audio Features: Function to get audio_features() for tracks if needed for further filtering or analysis.
Create Playlist: Function that takes a user ID, playlist name, and description, and uses user_playlist_create() to create an empty playlist.
Add Tracks to Playlist: Function that takes a playlist ID and a list of track URIs/IDs and uses playlist_add_items() (or user_playlist_add_tracks) to populate the playlist.

"""

'''
    Function: search_spotify
    Desc: Searches Spotify for tracks, artists, albums or playlists.
    
    Args: 
        sp (spotipy.Spotify): An authenticated Spotify Client object
        query (str): The search query
        search_type (str): The type of search (track, artist, album, playlist). (Default is track)
        limit (int): Max number of results to return. 
    
    Returns:
        dict: A dictionary containing the search results, or None if an error has occurred. 
'''

def search_spotify(sp, query, search_type='track', limit=10):
    try:
        results = sp.search(q=query, type=search_type, limit=limit)
        return results
    except spotipy.exceptions.SpotifyException as e:
        print(f"An error has occurred during the search: {e}")
        return None

'''
 Function: display_search_results
 Desc: Displays the search results in a user friendly format from 'search_spotify()'
 
 Args:
    results (dict): The search results dictionary from the Spotify API
    search_type (str): Type of search (track, artist, album, playlist). Default track
'''
def display_search_results(results, search_type='track'):

    if results:
        items = results[f'{search_type}s']['items']
        if items:
            print(f"Search results for '{search_type}'")
            for i, item in enumerate(items):
                if search_type == 'track':
                    print(f"{i + 1}. {item['name']} - {','.join([artist['name'] for artist in item['artists']])}")
                    print(f"   Album: {item['album']['name']}")
                    print(f"   URI: {item['uri']}")
                elif search_type == 'artist':
                    print(f"{i + 1}. {item['name']}")
                    print(f"   URI: {item['uri']}")
                    if item['images']:  # check for images
                        print(f"   Image URL: {item['images'][0]['url']}")
                    else:
                        print(f"   Image URL: No Image available")
                elif search_type == 'album':
                    print(f"{i + 1}. {item['name']} - {', '.join([artist['name'] for artist in item['artists']])}")
                    print(f"   URI: {item['uri']}")
                    if item['images']:
                        print(f"   Image URL: {item['images'][0]['url']}")
                    else:
                        print(f"   Image URL: No image available")

                elif search_type == 'playlist':
                    print(f"{i + 1}. {item['name']} - {item['owner']['display_name']}")
                    print(f"   URI: {item['uri']}")
                    if item['images']:
                        print(f"   Image URL: {item['images'][0]['url']}")
                    else:
                        print(f"   Image URL: No image available")

                print("-" * 20)
        else:
            print("No results found.")
    else:
        print("Search failed.")

def get_recommendations(sp, seed_artists=None, seed_tracks=None, seed_genres=None, limit=10, **kwargs):

    try:
        recommendations = sp.recommendations(seed_artists=seed_artists, seed_tracks=seed_tracks, seed_genres=seed_genres, limit=limit, **kwargs)
        return recommendations['tracks']
    except spotipy.SpotifyException as e:
        print(f"An error occurred with recommendations: {e}")
        return None
def display_recommendations(recommendations):
    if recommendations:
        print("Recommended Tracks:")
        for i, track in enumerate(recommendations):
            print(f"{i + 1}. {track['name']} - {','.join([artist['name'] for artist in track['artists']])}")
            print(f"   Album: {track['album']['name']}")
            print(f"   URI: {track['uri']}")
            print("-" * 20)
        else:
            print("No Recommendations Found")

def create_playlist(sp, user_id, playlist_name, track_uris):
    playlist = sp.user_playlist_create(user_id, playlist_name)
    sp.playlist_add_items(playlist['id'], track_uris)
    return playlist

def get_spotify_track_uris(parsed_data, sp):
    track_uris = []
    if parsed_data:
        if parsed_data.get('seed_genres') or parsed_data.get('seed_artists') or parsed_data.get('seed_tracks') or parsed_data.get('target_audio_features'):
            recommendations = sp.recommendations(seed_genres=parsed_data.get('seed_genres'),
                                                 seed_artists=parsed_data.get('seed_artists'),
                                                 seed_tracks=parsed_data.get('seed_tracks'),
                                                 target_audio_features=parsed_data.get('target_audio_features'))
            if parsed_data.get('keywords'):
                for keyword in parsed_data['keywords']:
                    results = sp.search(q=keyword, type='track', limit=10)
                    track_uris.extend([track['uri'] for track in results['tracks']])
    return track_uris


def get_spotify_recommendations_new(sp, model_data, limit=30):
    """
    Takes Model response data and fetches track recommendations from Spotify
    :param sp: Authenticated Spotify Client Instance
    :param model_data: (dict) Parsed data from model (gemini)
    :param limit: (int) Max number of tracks to recommend
    :return: A list of Spotify track URIs, or an empty list if none found/error
    """
    print("Translating into Spotify recommendations...")

    recommendation_args = {'limit': limit}

    #1.Seed Data (Genres, Artists, Tracks) - Nax 5 seeds in total!
    seed_genres = model_data.get('seed_genres', [])
    seed_artists = model_data.get('seed_artists', [])
    seed_tracks = model_data.get('seed_tracks', [])

    #Combine seeds, respecting the 5-seed limit
    seed_count = 0
    if seed_genres:
        recommendation_args['seed_genres'] = seed_genres[:5]
        seed_count += len(recommendation_args['seed_genres'])
    if seed_artists and seed_count < 5:
        recommendation_args['seed_artists'] = seed_artists[:(5 - seed_count)]
        seed_count += len(recommendation_args['seed_artists'])
    if seed_tracks and seed_count < 5:
        recommendation_args['seed_tracks'] =  seed_tracks[:(5 - seed_count)]

    if seed_count == 0:
        print("Warning: No seed genres, artists, or tracks provided.")

    #2. Target Audio Features
    target_features = model_data.get('target_audio_features', {})
    if target_features:
        if 'energy' in target_features: recommendation_args['target_energy'] = float(target_features['energy'])
        if 'danceability' in target_features: recommendation_args['target_danceability'] = float(target_features['danceability'])
        if 'valence' in target_features: recommendation_args['target_valence'] = float(target_features['valence'])
        if 'instrumentalness' in target_features: recommendation_args['target_instrumentalness'] = float(target_features['instrumentalness'])
        if 'acousticness' in target_features: recommendation_args['target_acousticness'] = float(target_features['acousticness'])


    try:
        result_test = sp.recommendations(**recommendation_args)
        track_uris = [track['uri'] for track in result_test['tracks']]
        if not track_uris:
            print("Spotify returned no recommendations")
            return []

        print(f"Found {len(track_uris)} recommended tracks")
        return track_uris
    except Exception as e:
        print(f"Error getting recommendations: {e}")
        return []

def create_spotify_playlist_new(sp_client, user_id, playlist_name, description=""):
    """
    Creates empty playlist for the user.
    :param sp_client:
    :param user_id:
    :param playlist_name:
    :param description:
    :return:
    """

    try:
        playlist = sp_client.user_playlist_create(
            user = user_id,
            name = playlist_name,
            public=False,
            description=description
        )
        playlist_id =playlist['id']
        playlist_url = playlist['external_urls']['spotify']
        print(f"Return URL: {playlist_url}")
        return playlist_id, playlist_url
    except Exception as e:
        print(f"Error creating playlist: {e}")
        return None, None


def generate_playlist_name(model_data, default_name="AI Generated Toones"):
    """Generates a name based on Gemini keywords or uses a default."""
    keywords = model_data.get('keywords, []')
    if keywords:
        return " ".join(k.capitalize() for k in keywords) + " Toon"

    return default_name

def add_tracks_to_playlist(sp_client, playlist_id, track_uris):

    if not track_uris:
        print("No tracks to add.")
        return False
    if not playlist_id:
        print(f"Invalid playlist id. {playlist_id}. Cannot add tracks")
        return False

    print(f"Adding {len(track_uris)} to Playlist ID: {playlist_id}")
    try:
        for i in range(0, len(track_uris), 100):
            chunk = track_uris[i:i + 100]
            sp_client.playlist_add_items(playlist_id, chunk)
        print ("Beats: Yooo! Track added successfully!")
        return True
    except Exception as e:
        print(f"Error Handling: {e}")
        return False
