"""Configuration management for artist scraper."""

import json
from pathlib import Path
from typing import Any


class Config:
    """Configuration loader and manager."""

    def __init__(self, config_path: str = "config.json"):
        """Initialize configuration.

        Args:
            config_path: Path to the configuration file
        """
        self.config_path = Path(config_path)
        self._config: dict[str, Any] = {}
        self.load()

    def load(self) -> None:
        """Load configuration from file."""
        if not self.config_path.exists():
            raise FileNotFoundError(
                f"Configuration file not found: {self.config_path}\n"
                f"Please copy config.example.json to config.json and fill in your credentials."
            )

        with open(self.config_path) as f:
            self._config = json.load(f)

    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value by dot-notation key.

        Args:
            key: Configuration key in dot notation (e.g., 'spotify.client_id')
            default: Default value if key not found

        Returns:
            Configuration value
        """
        keys = key.split(".")
        value: Any = self._config

        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
                if value is None:
                    return default
            else:
                return default

        return value

    @property
    def spotify_client_id(self) -> str:
        """Get Spotify client ID."""
        return self.get("spotify.client_id", "")

    @property
    def spotify_client_secret(self) -> str:
        """Get Spotify client secret."""
        return self.get("spotify.client_secret", "")

    @property
    def spotify_refresh_token(self) -> str:
        """Get Spotify refresh token."""
        return self.get("spotify.refresh_token", "")

    @property
    def youtube_auth_file(self) -> str:
        """Get YouTube Music auth file path."""
        return self.get("youtube_music.auth_file", "ytmusic_auth.json")

    @property
    def youtube_client_id(self) -> str:
        """Get YouTube Music OAuth client ID."""
        return self.get("youtube_music.client_id", "")

    @property
    def youtube_client_secret(self) -> str:
        """Get YouTube Music OAuth client secret."""
        return self.get("youtube_music.client_secret", "")

    @property
    def lidarr_url(self) -> str:
        """Get Lidarr URL."""
        return self.get("lidarr.url", "http://localhost:8686")

    @property
    def lidarr_api_key(self) -> str:
        """Get Lidarr API key."""
        return self.get("lidarr.api_key", "")

    @property
    def musicbrainz_user_agent(self) -> str:
        """Get MusicBrainz user agent."""
        return self.get("musicbrainz.user_agent", "artistscraper/0.1.0")

    @property
    def output_csv_file(self) -> str:
        """Get output CSV file path."""
        return self.get("output.csv_file", "artists.csv")

    @property
    def output_skipped_log(self) -> str:
        """Get skipped artists log file path."""
        return self.get("output.skipped_log", "skipped_artists.log")
