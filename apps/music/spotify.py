"""
Spotify API helper using Spotipy.
Handles OAuth flow and common API calls.
"""
import os
import spotipy
from spotipy.oauth2 import SpotifyOAuth, SpotifyClientCredentials

SPOTIFY_CLIENT_ID = os.environ.get('SPOTIFY_CLIENT_ID', '')
SPOTIFY_CLIENT_SECRET = os.environ.get('SPOTIFY_CLIENT_SECRET', '')
SPOTIFY_REDIRECT_URI = os.environ.get(
    'SPOTIFY_REDIRECT_URI',
    'http://localhost:8000/spotify/callback/'
)

SPOTIFY_SCOPES = [
    'user-read-private',
    'user-read-email',
    'user-top-read',
    'user-library-read',
    'playlist-read-private',
]


def get_auth_manager(request=None):
    """Return a SpotifyOAuth manager, optionally with a cached token from session."""
    cache_handler = None
    if request is not None:
        cache_handler = SessionCacheHandler(request)

    return SpotifyOAuth(
        client_id=SPOTIFY_CLIENT_ID,
        client_secret=SPOTIFY_CLIENT_SECRET,
        redirect_uri=SPOTIFY_REDIRECT_URI,
        scope=' '.join(SPOTIFY_SCOPES),
        cache_handler=cache_handler,
        show_dialog=False,
    )


def get_client_credentials_client():
    """Return a Spotify client using Client Credentials (no user login required)."""
    auth_manager = SpotifyClientCredentials(
        client_id=SPOTIFY_CLIENT_ID,
        client_secret=SPOTIFY_CLIENT_SECRET,
    )
    return spotipy.Spotify(auth_manager=auth_manager)


def get_spotify_client(request):
    """Return an authenticated Spotify client for the current user session."""
    auth_manager = get_auth_manager(request)
    if not auth_manager.validate_token(auth_manager.cache_handler.get_cached_token()):
        return None
    return spotipy.Spotify(auth_manager=auth_manager)


class SessionCacheHandler(spotipy.cache_handler.CacheHandler):
    """Store the Spotify token in Django's session."""

    def __init__(self, request):
        self.request = request

    def get_cached_token(self):
        return self.request.session.get('spotify_token')

    def save_token_to_cache(self, token_info):
        self.request.session['spotify_token'] = token_info
        self.request.session.modified = True
