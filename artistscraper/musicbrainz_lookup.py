"""MusicBrainz ID lookup service."""

import logging
import time
from typing import Optional, Tuple
import musicbrainzngs


logger = logging.getLogger(__name__)


class MusicBrainzLookup:
    """Look up MusicBrainz IDs for artists."""

    def __init__(self, user_agent: str):
        """Initialize MusicBrainz lookup service.

        Args:
            user_agent: User agent string for MusicBrainz API
        """
        self.user_agent = user_agent
        musicbrainzngs.set_useragent(
            app="artistscraper",
            version="0.1.0",
            contact=user_agent
        )
        # Rate limiting: MusicBrainz allows 1 request per second
        self.last_request_time = 0
        self.min_request_interval = 1.0

    def _rate_limit(self) -> None:
        """Enforce rate limiting for MusicBrainz API."""
        current_time = time.time()
        time_since_last_request = current_time - self.last_request_time

        if time_since_last_request < self.min_request_interval:
            sleep_time = self.min_request_interval - time_since_last_request
            time.sleep(sleep_time)

        self.last_request_time = time.time()

    def lookup_artist(self, artist_name: str) -> Optional[str]:
        """Look up MusicBrainz ID for an artist.

        Args:
            artist_name: Name of the artist to look up

        Returns:
            MusicBrainz ID in format 'lidarr:ID' or None if not found
        """
        try:
            self._rate_limit()

            logger.debug(f"Looking up MusicBrainz ID for: {artist_name}")

            # Search for the artist
            result = musicbrainzngs.search_artists(
                artist=artist_name,
                limit=10,
                strict=False
            )

            if not result or 'artist-list' not in result:
                logger.debug(f"No results found for: {artist_name}")
                return None

            artists = result['artist-list']

            if not artists:
                logger.debug(f"Empty artist list for: {artist_name}")
                return None

            # Try to find the best match
            best_match = None
            best_score = 0

            for artist in artists:
                # Get the score (0-100, where 100 is exact match)
                score = int(artist.get('ext:score', 0))
                artist_mb_name = artist.get('name', '')

                # Prefer exact matches or very high scores
                if score > best_score:
                    best_score = score
                    best_match = artist

                # If we have an exact match (case-insensitive), use it
                if artist_mb_name.lower() == artist_name.lower():
                    best_match = artist
                    break

            # Only accept matches with score >= 90 for good quality results
            if best_match and best_score >= 90:
                mb_id = best_match.get('id')
                if mb_id:
                    logger.debug(f"Found MusicBrainz ID for {artist_name}: {mb_id} (score: {best_score})")
                    return f"lidarr:{mb_id}"

            logger.debug(f"No good match found for {artist_name} (best score: {best_score})")
            return None

        except musicbrainzngs.NetworkError as e:
            logger.error(f"Network error looking up {artist_name}: {e}")
            return None
        except musicbrainzngs.ResponseError as e:
            logger.error(f"MusicBrainz API error looking up {artist_name}: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error looking up {artist_name}: {e}")
            return None

    def lookup_multiple_artists(self, artist_names: set[str]) -> dict[str, Optional[str]]:
        """Look up MusicBrainz IDs for multiple artists.

        Args:
            artist_names: Set of artist names to look up

        Returns:
            Dictionary mapping artist names to their MusicBrainz IDs (or None)
        """
        results = {}
        total = len(artist_names)

        logger.info(f"Looking up MusicBrainz IDs for {total} artists...")

        for i, artist_name in enumerate(sorted(artist_names), 1):
            if i % 10 == 0:
                logger.info(f"Progress: {i}/{total} artists processed")

            mb_id = self.lookup_artist(artist_name)
            results[artist_name] = mb_id

        logger.info(f"Completed MusicBrainz lookups: {sum(1 for v in results.values() if v is not None)}/{total} found")
        return results
