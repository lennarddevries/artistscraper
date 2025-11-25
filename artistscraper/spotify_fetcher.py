"""Spotify artist fetcher."""

import logging
from typing import Set
import spotipy
from spotipy.oauth2 import SpotifyOAuth

# Suppress spotipy and urllib3 debug logs
logging.getLogger('spotipy').setLevel(logging.WARNING)
logging.getLogger('urllib3').setLevel(logging.WARNING)

logger = logging.getLogger(__name__)


class SpotifyFetcher:
    """Fetch artists from Spotify."""

    def __init__(self, client_id: str, client_secret: str, refresh_token: str):
        """Initialize Spotify fetcher.

        Args:
            client_id: Spotify client ID
            client_secret: Spotify client secret
            refresh_token: Spotify refresh token
        """
        self.client_id = client_id
        self.client_secret = client_secret
        self.refresh_token = refresh_token
        self.sp: spotipy.Spotify | None = None

    def authenticate(self) -> bool:
        """Authenticate with Spotify.

        Returns:
            True if authentication successful, False otherwise
        """
        try:
            # Create OAuth handler with refresh token
            auth_manager = SpotifyOAuth(
                client_id=self.client_id,
                client_secret=self.client_secret,
                redirect_uri="http://localhost:8888/callback",
                scope="user-library-read user-follow-read playlist-read-private playlist-read-collaborative"
            )

            # Set the refresh token
            token_info = auth_manager.refresh_access_token(self.refresh_token)
            self.sp = spotipy.Spotify(auth=token_info['access_token'])

            logger.info("Successfully authenticated with Spotify")
            return True
        except Exception as e:
            logger.error(f"Failed to authenticate with Spotify: {e}")
            return False

    def get_artists_from_saved_tracks(self) -> Set[str]:
        """Get artists from saved/liked tracks.

        Returns:
            Set of artist names
        """
        if not self.sp:
            logger.warning("Not authenticated with Spotify")
            return set()

        artists = set()
        try:
            logger.info("Fetching saved tracks from Spotify...")
            offset = 0
            limit = 50

            while True:
                results = self.sp.current_user_saved_tracks(limit=limit, offset=offset)

                if not results or not results['items']:
                    break

                for item in results['items']:
                    track = item.get('track')
                    if track and 'artists' in track:
                        for artist in track['artists']:
                            if 'name' in artist:
                                artists.add(artist['name'])

                # Check if there are more tracks
                if not results['next']:
                    break

                offset += limit

            logger.info(f"Found {len(artists)} unique artists from saved tracks")
        except Exception as e:
            logger.error(f"Error fetching saved tracks: {e}")

        return artists

    def get_followed_artists(self) -> Set[str]:
        """Get followed artists.

        Returns:
            Set of artist names
        """
        if not self.sp:
            logger.warning("Not authenticated with Spotify")
            return set()

        artists = set()
        try:
            logger.info("Fetching followed artists from Spotify...")
            after = None
            limit = 50

            while True:
                results = self.sp.current_user_followed_artists(limit=limit, after=after)

                if not results or 'artists' not in results:
                    break

                artists_data = results['artists']
                if not artists_data or not artists_data['items']:
                    break

                for artist in artists_data['items']:
                    if 'name' in artist:
                        artists.add(artist['name'])

                # Check if there are more artists
                if not artists_data['next']:
                    break

                # Get the last artist ID for pagination
                if artists_data['items']:
                    after = artists_data['items'][-1]['id']
                else:
                    break

            logger.info(f"Found {len(artists)} followed artists")
        except Exception as e:
            logger.error(f"Error fetching followed artists: {e}")

        return artists

    def get_artists_from_playlists(self) -> Set[str]:
        """Get artists from all playlists (including private and collaborative).

        Returns:
            Set of artist names
        """
        if not self.sp:
            logger.warning("Not authenticated with Spotify")
            return set()

        artists = set()
        try:
            logger.info("Fetching playlists from Spotify...")
            offset = 0
            limit = 50

            while True:
                playlists = self.sp.current_user_playlists(limit=limit, offset=offset)

                if not playlists or not playlists['items']:
                    break

                for playlist in playlists['items']:
                    playlist_id = playlist.get('id')
                    playlist_name = playlist.get('name', 'Unknown')

                    if not playlist_id:
                        continue

                    try:
                        logger.info(f"Fetching tracks from playlist: {playlist_name}")
                        track_offset = 0
                        track_limit = 100

                        while True:
                            tracks_result = self.sp.playlist_tracks(
                                playlist_id,
                                limit=track_limit,
                                offset=track_offset
                            )

                            if not tracks_result or not tracks_result['items']:
                                break

                            for item in tracks_result['items']:
                                track = item.get('track')
                                if track and 'artists' in track:
                                    for artist in track['artists']:
                                        if 'name' in artist:
                                            artists.add(artist['name'])

                            # Check if there are more tracks
                            if not tracks_result['next']:
                                break

                            track_offset += track_limit

                    except Exception as e:
                        logger.warning(f"Error fetching playlist {playlist_id}: {e}")
                        continue

                # Check if there are more playlists
                if not playlists['next']:
                    break

                offset += limit

            logger.info(f"Found {len(artists)} unique artists from playlists")
        except Exception as e:
            logger.error(f"Error fetching playlists: {e}")

        return artists

    def get_all_artists(self) -> Set[str]:
        """Get all unique artists from all sources.

        Returns:
            Set of all unique artist names
        """
        if not self.authenticate():
            return set()

        all_artists = set()

        # Get artists from saved tracks
        all_artists.update(self.get_artists_from_saved_tracks())

        # Get followed artists
        all_artists.update(self.get_followed_artists())

        # Get artists from playlists
        all_artists.update(self.get_artists_from_playlists())

        logger.info(f"Total unique artists from Spotify: {len(all_artists)}")
        return all_artists
