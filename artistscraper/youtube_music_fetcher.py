"""YouTube Music artist fetcher using YouTube Data API v3."""

import logging
import json
import requests
from typing import Set
from pathlib import Path

logger = logging.getLogger(__name__)

YOUTUBE_API_BASE = "https://www.googleapis.com/youtube/v3"


class YouTubeMusicFetcher:
    """Fetch artists from YouTube Music using YouTube Data API v3."""

    def __init__(self, auth_file: str, client_id: str = None, client_secret: str = None):
        """Initialize YouTube Music fetcher.

        Args:
            auth_file: Path to YouTube Music authentication file (OAuth token JSON)
            client_id: Ignored (kept for compatibility)
            client_secret: Ignored (kept for compatibility)
        """
        self.auth_file = auth_file
        self.access_token: str | None = None

    def authenticate(self) -> bool:
        """Authenticate with YouTube Music.

        Returns:
            True if authentication successful, False otherwise
        """
        auth_path = Path(self.auth_file)
        if not auth_path.exists():
            logger.error(
                f"YouTube Music auth file not found: {self.auth_file}\n"
                f"To authenticate with YouTube Music:\n"
                f"1. Run: poetry run ytmusicapi oauth\n"
                f"2. Follow the browser authentication flow\n"
                f"3. Save the file as '{self.auth_file}'\n"
                f"Or use --spotify-only to skip YouTube Music"
            )
            return False

        try:
            with open(auth_path) as f:
                token_data = json.load(f)
                self.access_token = token_data.get('access_token')

            if not self.access_token:
                logger.error("No access token found in auth file")
                return False

            logger.info("Successfully authenticated with YouTube Music")
            return True
        except Exception as e:
            logger.error(f"Failed to authenticate with YouTube Music: {e}")
            return False

    def _make_request(self, endpoint: str, params: dict) -> dict:
        """Make a request to YouTube Data API.

        Args:
            endpoint: API endpoint (e.g., 'playlists', 'playlistItems')
            params: Query parameters

        Returns:
            API response as dict
        """
        url = f"{YOUTUBE_API_BASE}/{endpoint}"
        headers = {"Authorization": f"Bearer {self.access_token}"}

        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        return response.json()

    def _extract_artist_from_title(self, title: str) -> str | None:
        """Extract artist name from video/track title.

        Many YouTube Music videos have format: "Artist - Song Title"

        Args:
            title: Video/track title

        Returns:
            Artist name or None
        """
        # Common separators: " - ", " – ", " — "
        for sep in [" - ", " – ", " — ", " | "]:
            if sep in title:
                artist = title.split(sep)[0].strip()
                # Filter out obvious non-artist patterns
                if len(artist) > 0 and len(artist) < 100:
                    return artist
        return None

    def get_artists_from_liked_songs(self, play_counts: dict = None) -> Set[str]:
        """Get artists from liked songs/videos.

        Args:
            play_counts: Optional dict to track play counts per artist

        Returns:
            Set of artist names
        """
        if not self.access_token:
            logger.warning("Not authenticated with YouTube Music")
            return set()

        artists = set()
        if play_counts is None:
            play_counts = {}

        try:
            logger.info("Fetching liked videos from YouTube...")

            # Get liked videos (this includes liked music)
            page_token = None
            while True:
                params = {
                    "part": "snippet",
                    "myRating": "like",
                    "maxResults": 50
                }
                if page_token:
                    params["pageToken"] = page_token

                data = self._make_request("videos", params)

                for item in data.get("items", []):
                    snippet = item.get("snippet", {})
                    title = snippet.get("title", "")
                    channel_title = snippet.get("channelTitle", "")

                    # Try to extract artist from title
                    artist = self._extract_artist_from_title(title)
                    if artist:
                        artists.add(artist)
                        if play_counts is not None:
                            play_counts[artist] = play_counts.get(artist, 0) + 1

                    # Also consider channel title as potential artist
                    # (many music channels are named after the artist)
                    if channel_title and "VEVO" in channel_title.upper():
                        # Extract artist name from VEVO channels (e.g., "Taylor SwiftVEVO")
                        artist_name = channel_title.replace("VEVO", "").replace("Vevo", "").strip()
                        if artist_name:
                            artists.add(artist_name)
                            if play_counts is not None:
                                play_counts[artist_name] = play_counts.get(artist_name, 0) + 1

                page_token = data.get("nextPageToken")
                if not page_token:
                    break

            logger.info(f"Found {len(artists)} unique artists from liked videos")
        except Exception as e:
            logger.error(f"Error fetching liked videos: {e}")

        return artists

    def get_subscribed_artists(self) -> Set[str]:
        """Get subscribed/followed artists (YouTube channel subscriptions).

        Returns:
            Set of artist names
        """
        if not self.access_token:
            logger.warning("Not authenticated with YouTube Music")
            return set()

        artists = set()
        try:
            logger.info("Fetching subscriptions from YouTube...")

            page_token = None
            while True:
                params = {
                    "part": "snippet",
                    "mine": "true",
                    "maxResults": 50
                }
                if page_token:
                    params["pageToken"] = page_token

                data = self._make_request("subscriptions", params)

                for item in data.get("items", []):
                    snippet = item.get("snippet", {})
                    channel_title = snippet.get("title", "")

                    if channel_title:
                        # Clean up VEVO and other suffixes
                        artist_name = channel_title.replace("VEVO", "").replace("Vevo", "").replace("Official", "").strip()
                        if artist_name:
                            artists.add(artist_name)

                page_token = data.get("nextPageToken")
                if not page_token:
                    break

            logger.info(f"Found {len(artists)} subscribed channels")
        except Exception as e:
            logger.error(f"Error fetching subscriptions: {e}")

        return artists

    def get_artists_from_playlists(self, play_counts: dict = None) -> Set[str]:
        """Get artists from all playlists.

        Args:
            play_counts: Optional dict to track play counts per artist

        Returns:
            Set of artist names
        """
        if not self.access_token:
            logger.warning("Not authenticated with YouTube Music")
            return set()

        artists = set()
        if play_counts is None:
            play_counts = {}

        try:
            logger.info("Fetching playlists from YouTube...")

            # Get all playlists
            page_token = None
            playlist_ids = []

            while True:
                params = {
                    "part": "id,snippet",
                    "mine": "true",
                    "maxResults": 50
                }
                if page_token:
                    params["pageToken"] = page_token

                data = self._make_request("playlists", params)

                for item in data.get("items", []):
                    playlist_ids.append(item["id"])

                page_token = data.get("nextPageToken")
                if not page_token:
                    break

            logger.info(f"Found {len(playlist_ids)} playlists")

            # Get items from each playlist
            for playlist_id in playlist_ids:
                try:
                    page_token = None
                    while True:
                        params = {
                            "part": "snippet",
                            "playlistId": playlist_id,
                            "maxResults": 50
                        }
                        if page_token:
                            params["pageToken"] = page_token

                        data = self._make_request("playlistItems", params)

                        for item in data.get("items", []):
                            snippet = item.get("snippet", {})
                            title = snippet.get("title", "")
                            channel_title = snippet.get("videoOwnerChannelTitle", snippet.get("channelTitle", ""))

                            # Extract artist from title
                            artist = self._extract_artist_from_title(title)
                            if artist:
                                artists.add(artist)
                                if play_counts is not None:
                                    play_counts[artist] = play_counts.get(artist, 0) + 1

                            # Check channel title for VEVO artists
                            if channel_title and "VEVO" in channel_title.upper():
                                artist_name = channel_title.replace("VEVO", "").replace("Vevo", "").strip()
                                if artist_name:
                                    artists.add(artist_name)
                                    if play_counts is not None:
                                        play_counts[artist_name] = play_counts.get(artist_name, 0) + 1

                        page_token = data.get("nextPageToken")
                        if not page_token:
                            break

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
