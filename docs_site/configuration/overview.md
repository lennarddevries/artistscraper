# Configuration Overview

Artist Scraper uses a JSON configuration file to store API credentials and settings.

## Creating the Configuration File

Generate an example configuration file:

```bash
artistscraper print-config > config.json
```

This creates a `config.json` file with the following structure:

```json
{
  "spotify": {
    "client_id": "your_spotify_client_id_here",
    "client_secret": "your_spotify_client_secret_here",
    "refresh_token": "your_spotify_refresh_token_here"
  },
  "youtube_music": {
    "auth_file": "ytmusic_auth.json",
    "client_id": "your_google_client_id_here (optional)",
    "client_secret": "your_google_client_secret_here (optional)"
  },
  "lidarr": {
    "url": "http://localhost:8686",
    "api_key": "your_lidarr_api_key_here"
  },
  "musicbrainz": {
    "user_agent": "artistscraper/0.1.0 (your-email@example.com)"
  },
  "output": {
    "csv_file": "artists.csv",
    "skipped_log": "skipped_artists.log"
  }
}
```

## Configuration Sections

### Required Sections

- **[Spotify](spotify.md)**: Spotify API credentials
- **[YouTube Music](youtube-music.md)**: YouTube Data API v3 credentials
- **[MusicBrainz](musicbrainz.md)**: User agent for MusicBrainz API

### Optional Sections

- **[Lidarr](lidarr.md)**: Only needed if using `--lidarr` flag
- **Output**: Customize output file paths (optional)

## Security

!!! warning "Keep Your Credentials Safe"
    - Never commit `config.json` to version control
    - The file is already in `.gitignore`
    - Store credentials securely
    - Don't share your config file publicly

## Using a Custom Configuration File

By default, Artist Scraper looks for `config.json` in the current directory. You can specify a different path:

```bash
artistscraper scrape --config /path/to/custom-config.json
```

Or use the short form:

```bash
artistscraper scrape -c /path/to/custom-config.json
```

## Next Steps

Configure each API service:

1. [Spotify Configuration](spotify.md)
2. [YouTube Music Configuration](youtube-music.md)
3. [MusicBrainz Configuration](musicbrainz.md)
4. [Lidarr Configuration](lidarr.md) (Optional)
