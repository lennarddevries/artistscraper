"""Lidarr API client."""

import logging
from typing import Dict, List, Optional

import requests

# Suppress requests/urllib3 debug logs
logging.getLogger("urllib3").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)


class LidarrClient:
    """Client for interacting with Lidarr API."""

    def __init__(self, url: str, api_key: str):
        """Initialize Lidarr client.

        Args:
            url: Lidarr instance URL (e.g., http://localhost:8686)
            api_key: Lidarr API key
        """
        self.url = url.rstrip("/")
        self.api_key = api_key
        self.session = requests.Session()
        self.session.headers.update(
            {"X-Api-Key": api_key, "Content-Type": "application/json"}
        )

    def test_connection(self) -> bool:
        """Test connection to Lidarr.

        Returns:
            True if connection successful, False otherwise
        """
        try:
            response = self.session.get(f"{self.url}/api/v1/system/status")
            response.raise_for_status()
            logger.info("Successfully connected to Lidarr")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to Lidarr: {e}")
            return False

    def get_root_folders(self) -> List[Dict]:
        """Get available root folders.

        Returns:
            List of root folder dictionaries
        """
        try:
            response = self.session.get(f"{self.url}/api/v1/rootfolder")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error getting root folders: {e}")
            return []

    def get_quality_profiles(self) -> List[Dict]:
        """Get available quality profiles.

        Returns:
            List of quality profile dictionaries
        """
        try:
            response = self.session.get(f"{self.url}/api/v1/qualityprofile")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error getting quality profiles: {e}")
            return []

    def get_metadata_profiles(self) -> List[Dict]:
        """Get available metadata profiles.

        Returns:
            List of metadata profile dictionaries
        """
        try:
            response = self.session.get(f"{self.url}/api/v1/metadataprofile")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error getting metadata profiles: {e}")
            return []

    def search_artist(self, musicbrainz_id: str) -> Optional[Dict]:
        """Search for an artist by MusicBrainz ID.

        Args:
            musicbrainz_id: MusicBrainz ID (without 'lidarr:' prefix)

        Returns:
            Artist data dictionary or None if not found
        """
        try:
            # Search using foreign ID (MusicBrainz ID)
            response = self.session.get(
                f"{self.url}/api/v1/search", params={"term": f"lidarr:{musicbrainz_id}"}
            )
            response.raise_for_status()
            results = response.json()

            if results and len(results) > 0:
                return results[0]

            return None
        except Exception as e:
            logger.error(f"Error searching for artist {musicbrainz_id}: {e}")
            return None

    def artist_exists(self, musicbrainz_id: str) -> bool:
        """Check if an artist already exists in Lidarr.

        Args:
            musicbrainz_id: MusicBrainz ID (without 'lidarr:' prefix)

        Returns:
            True if artist exists, False otherwise
        """
        try:
            response = self.session.get(f"{self.url}/api/v1/artist")
            response.raise_for_status()
            artists = response.json()

            for artist in artists:
                if artist.get("foreignArtistId") == musicbrainz_id:
                    return True

            return False
        except Exception as e:
            logger.error(f"Error checking if artist exists: {e}")
            return False

    def add_artist(
        self,
        artist_data: Dict,
        root_folder_path: str,
        quality_profile_id: int,
        metadata_profile_id: int,
        monitored: bool = True,
        search_for_missing: bool = False,
    ) -> bool:
        """Add an artist to Lidarr.

        Args:
            artist_data: Artist data from search
            root_folder_path: Root folder path for the artist
            quality_profile_id: Quality profile ID
            metadata_profile_id: Metadata profile ID
            monitored: Whether to monitor the artist
            search_for_missing: Whether to search for missing albums immediately

        Returns:
            True if successfully added, False otherwise
        """
        try:
            # Prepare the artist data for adding
            add_data = {
                "artistName": artist_data["artistName"],
                "foreignArtistId": artist_data["foreignArtistId"],
                "qualityProfileId": quality_profile_id,
                "metadataProfileId": metadata_profile_id,
                "rootFolderPath": root_folder_path,
                "monitored": monitored,
                "addOptions": {
                    "monitor": "all",
                    "searchForMissingAlbums": search_for_missing,
                },
            }

            response = self.session.post(f"{self.url}/api/v1/artist", json=add_data)
            response.raise_for_status()

            logger.info(f"Successfully added artist: {artist_data['artistName']}")
            return True

        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 400:
                logger.warning(
                    f"Artist already exists or invalid data: {artist_data.get('artistName', 'Unknown')}"
                )
            else:
                logger.error(f"HTTP error adding artist: {e}")
            return False
        except Exception as e:
            logger.error(
                f"Error adding artist {artist_data.get('artistName', 'Unknown')}: {e}"
            )
            return False

    def add_artists_from_csv(self, artist_data: Dict[str, str]) -> tuple[int, int]:
        """Add multiple artists to Lidarr from artist data.

        Args:
            artist_data: Dictionary mapping artist names to MusicBrainz IDs

        Returns:
            Tuple of (added_count, failed_count)
        """
        if not self.test_connection():
            logger.error("Cannot connect to Lidarr")
            return 0, 0

        # Get configuration from Lidarr
        root_folders = self.get_root_folders()
        quality_profiles = self.get_quality_profiles()
        metadata_profiles = self.get_metadata_profiles()

        if not root_folders or not quality_profiles or not metadata_profiles:
            logger.error("Failed to get required Lidarr configuration")
            return 0, 0

        # Use the first available options (user can configure these in Lidarr)
        root_folder_path = root_folders[0]["path"]
        quality_profile_id = quality_profiles[0]["id"]
        metadata_profile_id = metadata_profiles[0]["id"]

        logger.info(f"Using root folder: {root_folder_path}")
        logger.info(f"Using quality profile: {quality_profiles[0]['name']}")
        logger.info(f"Using metadata profile: {metadata_profiles[0]['name']}")

        added_count = 0
        failed_count = 0
        total = len([v for v in artist_data.values() if v])

        logger.info(f"Adding {total} artists to Lidarr...")

        for artist_name, mb_id in sorted(artist_data.items()):
            if not mb_id:
                continue

            # Remove 'lidarr:' prefix if present
            mb_id_clean = mb_id.replace("lidarr:", "")

            # Check if artist already exists
            if self.artist_exists(mb_id_clean):
                logger.info(f"Artist already exists in Lidarr: {artist_name}")
                added_count += 1  # Count as added since it's in Lidarr
                continue

            # Search for the artist
            artist_search_data = self.search_artist(mb_id_clean)

            if not artist_search_data:
                logger.warning(f"Could not find artist in Lidarr search: {artist_name}")
                failed_count += 1
                continue

            # Add the artist
            if self.add_artist(
                artist_search_data,
                root_folder_path,
                quality_profile_id,
                metadata_profile_id,
                monitored=True,
                search_for_missing=False,
            ):
                added_count += 1
            else:
                failed_count += 1

            # Progress logging
            if (added_count + failed_count) % 10 == 0:
                logger.info(f"Progress: {added_count + failed_count}/{total} processed")

        logger.info(f"Completed: {added_count} added/existing, {failed_count} failed")
        return added_count, failed_count
