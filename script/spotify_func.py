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
