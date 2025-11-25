"""YouTube Music artist fetcher."""

import logging
from typing import Set
from ytmusicapi import YTMusic

# Suppress ytmusicapi debug logs
logging.getLogger('ytmusicapi').setLevel(logging.WARNING)

logger = logging.getLogger(__name__)


class YouTubeMusicFetcher:
    """Fetch artists from YouTube Music."""

    def __init__(self, auth_file: str):
        """Initialize YouTube Music fetcher.

        Args:
            auth_file: Path to YouTube Music authentication file
        """
        self.auth_file = auth_file
        self.ytmusic: YTMusic | None = None

    def authenticate(self) -> bool:
        """Authenticate with YouTube Music.

        Returns:
            True if authentication successful, False otherwise
        """
        from pathlib import Path

        # Check if auth file exists
        auth_path = Path(self.auth_file)
        if not auth_path.exists():
            logger.error(
                f"YouTube Music auth file not found: {self.auth_file}\n"
                f"To authenticate with YouTube Music:\n"
                f"1. Run: ytmusicapi oauth\n"
                f"2. Follow the browser authentication flow\n"
                f"3. Save the file as '{self.auth_file}'\n"
                f"Or use --spotify-only to skip YouTube Music"
            )
            return False

        try:
            self.ytmusic = YTMusic(self.auth_file)
            logger.info("Successfully authenticated with YouTube Music")
            return True
        except Exception as e:
            logger.error(f"Failed to authenticate with YouTube Music: {e}")
            return False

    def get_artists_from_liked_songs(self, play_counts: dict = None) -> Set[str]:
        """Get artists from liked songs.

        Args:
            play_counts: Optional dict to track play counts per artist

        Returns:
            Set of artist names
        """
        if not self.ytmusic:
            logger.warning("Not authenticated with YouTube Music")
            return set()

        artists = set()
        if play_counts is None:
            play_counts = {}

        try:
            logger.info("Fetching liked songs from YouTube Music...")
            liked_songs = self.ytmusic.get_liked_songs(limit=None)

            if liked_songs and 'tracks' in liked_songs:
                for track in liked_songs['tracks']:
                    if 'artists' in track and track['artists']:
                        for artist in track['artists']:
                            artist_name = artist.get('name')
                            if artist_name:
                                artists.add(artist_name)
                                if play_counts is not None:
                                    play_counts[artist_name] = play_counts.get(artist_name, 0) + 1

            logger.info(f"Found {len(artists)} unique artists from liked songs")
        except Exception as e:
            logger.error(f"Error fetching liked songs: {e}")

        return artists

    def get_subscribed_artists(self) -> Set[str]:
        """Get subscribed/followed artists.

        Returns:
            Set of artist names
        """
        if not self.ytmusic:
            logger.warning("Not authenticated with YouTube Music")
            return set()

        artists = set()
        try:
            logger.info("Fetching subscribed artists from YouTube Music...")
            subscribed = self.ytmusic.get_library_subscriptions(limit=None)

            for item in subscribed:
                if 'artist' in item and item['artist']:
                    artists.add(item['artist'])

            logger.info(f"Found {len(artists)} subscribed artists")
        except Exception as e:
            logger.error(f"Error fetching subscribed artists: {e}")

        return artists

    def get_artists_from_playlists(self, play_counts: dict = None) -> Set[str]:
        """Get artists from all playlists.

        Args:
            play_counts: Optional dict to track play counts per artist

        Returns:
            Set of artist names
        """
        if not self.ytmusic:
            logger.warning("Not authenticated with YouTube Music")
            return set()

        artists = set()
        if play_counts is None:
            play_counts = {}

        try:
            logger.info("Fetching playlists from YouTube Music...")
            playlists = self.ytmusic.get_library_playlists(limit=None)

            for playlist in playlists:
                playlist_id = playlist.get('playlistId')
                if not playlist_id:
                    continue

                try:
                    logger.info(f"Fetching tracks from playlist: {playlist.get('title', 'Unknown')}")
                    playlist_details = self.ytmusic.get_playlist(playlist_id, limit=None)

                    if 'tracks' in playlist_details:
                        for track in playlist_details['tracks']:
                            if 'artists' in track and track['artists']:
                                for artist in track['artists']:
                                    artist_name = artist.get('name')
                                    if artist_name:
                                        artists.add(artist_name)
                                        if play_counts is not None:
                                            play_counts[artist_name] = play_counts.get(artist_name, 0) + 1
                except Exception as e:
                    logger.warning(f"Error fetching playlist {playlist_id}: {e}")
                    continue

            logger.info(f"Found {len(artists)} unique artists from playlists")
        except Exception as e:
            logger.error(f"Error fetching playlists: {e}")

        return artists

    def get_all_artists(self, play_counts: dict = None) -> Set[str]:
        """Get all unique artists from all sources.

        Args:
            play_counts: Optional dict to track play counts per artist

        Returns:
            Set of all unique artist names
        """
        if not self.authenticate():
            return set()

        all_artists = set()

        # Get artists from liked songs
        all_artists.update(self.get_artists_from_liked_songs(play_counts))

        # Get subscribed artists (don't count these as plays)
        all_artists.update(self.get_subscribed_artists())

        # Get artists from playlists
        all_artists.update(self.get_artists_from_playlists(play_counts))

        logger.info(f"Total unique artists from YouTube Music: {len(all_artists)}")
        return all_artists
