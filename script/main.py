import os
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from dotenv import load_dotenv
load_dotenv()
import spotify_func as spf
import google.generativeai as genai

spotify_client_id = os.getenv('SPOTIFY_CLIENT_ID')
spotify_client_secret = os.getenv('SPOTIFY_CLIENT_SECRET')
spotify_redirect_uri = os.getenv('SPOTIFY_REDIRECT_URI')
gemini_api_key = os.getenv('GEMINI_API_KEY')

#Basic check if credentials loaded (Good Practise)
if not all([spotify_client_id, spotify_client_secret, spotify_redirect_uri]):
    print("ERROR: Spotify Credentials (ID, SECRET, REDIRECT_URL) not found in .env file. ")
    exit() #Exit if credentials aren't present.

#Define permissions (scopes) your app needs from the user
# Full list of scopes https://developer.spotify.com/documentation/web-api/concepts/scopes
SPOTIFY_SCOPES = "playlist-modify-public playlist-modify-private user-read-playback-position user-read-recently-played ugc-image-upload user-library-read"



# Add this after defining scopes

# Create the SpotifyOAuth helper object
# It automatically uses the environment variables:
# SPOTIPY_CLIENT_ID, SPOTIPY_CLIENT_SECRET, SPOTIPY_REDIRECT_URI
# It will create a '.cache' file in your project root directory (SIPC)
# to store the tokens by default.

sp_oauth = SpotifyOAuth(
    client_id=spotify_client_id,
    client_secret = spotify_client_secret,
    redirect_uri= spotify_redirect_uri,
    scope=SPOTIFY_SCOPES,
    # Optional: Define a specific cache file name/location
    cache_path=".spotify_token_cache" # Will create '.spotify_token_cache' in SIPC
)

print("Attempting to authenticate with Spotify....")
#Try to get an authenticated Spotipy client instance.
# Using auth_manager=sp_oauth handles tokens caching and frefreshing automatically.

try:
    sp = spotipy.Spotify(auth_manager=sp_oauth)
# If the above line worked without errors, authentication was successful
    user_profile = sp.current_user() # Test call to verify authentication
    print(f"Successfully authenticated as: {user_profile['display_name']}")
    user_id = user_profile['id']
except Exception as e:
    print(f"Error during spotify auth: {e}")
    print("Could not authenticate with spotify. Please check")
    sp = None #Set sp to None if auth fails
    exit()


# -- Main application logic --

if sp:
    print(f"Spotify User ID: {user_id}")
    print("\nReady to proceed with next steps. ")

srch_result = spf.search_spotify(sp, "kendrick")
spf.display_search_results(srch_result)

'''
GEMINI INTEGRATION
Configure Gemini Client with API Key
'''

genai.configure(api_key=gemini_api_key)
model = genai.GenerativeModel('gemini-1.5-pro')

'''
    Simple test prompt below
'''

response = model.generate_content("What was the original capital of england?")
#print(response.text)