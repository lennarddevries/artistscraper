# Artist Scraper

A production-ready tool to fetch artists from YouTube Music and Spotify, look up their MusicBrainz IDs, and optionally add them to Lidarr for monitoring.

## Recent Updates

**November 25, 2025**: Major update to YouTube Music integration
- Replaced unreliable ytmusicapi internal API with official YouTube Data API v3
- Fixed HTTP 400 errors that prevented YouTube Music from working
- Improved artist extraction from video titles and channel names
- See [CHANGELOG_YOUTUBE_FIX.md](CHANGELOG_YOUTUBE_FIX.md) for full details

## Features

- Fetch artists from multiple sources:
  - **Spotify**: Liked tracks, followed artists, and all playlists (public & private)
  - **YouTube Music**: Liked videos, channel subscriptions, and all playlists (via YouTube Data API v3)
- Look up MusicBrainz IDs for all artists
- Track play counts for each artist
- Export to CSV with artist names, MusicBrainz IDs, sources, and play counts
- Import CSV to Lidarr with optional filtering by play count
- Automatic deduplication of artists
- Optional Lidarr integration to automatically add and monitor artists
- Beautiful CLI with colors, progress bars, and clear feedback
- Comprehensive logging of skipped artists

## Installation

### Prerequisites

- Python 3.12 or higher
- Poetry (for dependency management)

### Setup

1. Clone the repository:
```bash
cd /path/to/artistscraper
```

2. Install dependencies:
```bash
poetry install
```

3. Copy the example configuration:
```bash
cp config.example.json config.json
```

4. Configure your API credentials (see Configuration section below)

## Configuration

Edit `config.json` with your credentials:

### Spotify Configuration

1. Go to [Spotify Developer Dashboard](https://developer.spotify.com/dashboard)
2. Create a new app
3. Note your `Client ID` and `Client Secret`
4. Add `http://localhost:8888/callback` as a Redirect URI
5. Get a refresh token:
   - Use a tool like [spotify-refresh-token-generator](https://github.com/benblamey/spotify-refresh-token-generator) or the Spotipy documentation
   - Required scopes: `user-library-read`, `user-follow-read`, `playlist-read-private`, `playlist-read-collaborative`

Add to `config.json`:
```json
"spotify": {
  "client_id": "your_spotify_client_id",
  "client_secret": "your_spotify_client_secret",
  "refresh_token": "your_spotify_refresh_token"
}
```

### YouTube Music Configuration

> **Note**: As of November 2025, the YouTube Music integration uses the **YouTube Data API v3** for better reliability. See [YOUTUBE_MUSIC_SETUP.md](YOUTUBE_MUSIC_SETUP.md) for detailed setup instructions and troubleshooting.

#### Quick Setup

1. Create a Google Cloud Project and enable YouTube Data API v3
2. Create OAuth 2.0 credentials (Desktop app type)
3. Run the OAuth flow:
```bash
poetry run ytmusicapi oauth --client-id YOUR_CLIENT_ID --client-secret YOUR_CLIENT_SECRET
```

4. Update `config.json`:
```json
"youtube_music": {
  "auth_file": "ytmusic_auth.json",
  "client_id": "your_google_client_id.apps.googleusercontent.com",
  "client_secret": "your_google_client_secret"
}
```

For detailed instructions, troubleshooting, and information about the recent API changes, see [YOUTUBE_MUSIC_SETUP.md](YOUTUBE_MUSIC_SETUP.md).

### MusicBrainz Configuration

Update with your email:
```json
"musicbrainz": {
  "user_agent": "artistscraper/0.1.0 (your-email@example.com)"
}
```

### Lidarr Configuration (Optional)

If you plan to use the `--lidarr` flag:

1. Open your Lidarr instance
2. Go to Settings � General
3. Copy your API Key

Add to `config.json`:
```json
"lidarr": {
  "url": "http://localhost:8686",
  "api_key": "your_lidarr_api_key"
}
```

## Usage

### Scrape Command

Fetch artists from both Spotify and YouTube Music:
```bash
poetry run artistscraper scrape
```

Or if installed globally:
```bash
artistscraper scrape
```

#### Scrape Command Options

```
Options:
  --config, -c PATH          Path to configuration file (default: config.json)
  --spotify-only             Fetch artists from Spotify only
  --youtube-only             Fetch artists from YouTube Music only
  --skip-musicbrainz         Skip MusicBrainz ID lookup
  --lidarr                   Add artists to Lidarr after export
  --output, -o PATH          Output CSV file path (overrides config)
  --verbose, -v              Enable verbose output
  --help                     Show this message and exit
```

#### Scrape Examples

**Fetch from Spotify only:**
```bash
artistscraper scrape --spotify-only
```

**Fetch from YouTube Music only:**
```bash
artistscraper scrape --youtube-only
```

**Fetch and add to Lidarr:**
```bash
artistscraper scrape --lidarr
```

**Custom output file:**
```bash
artistscraper scrape --output my_artists.csv
```

**Skip MusicBrainz lookup (faster, just export artist names):**
```bash
artistscraper scrape --skip-musicbrainz
```

### Import Command

Import artists from a CSV file to Lidarr:
```bash
poetry run artistscraper import artists.csv
```

#### Import Command Options

```
Options:
  --config, -c PATH          Path to configuration file (default: config.json)
  --min-plays INTEGER        Only import artists with at least this many plays
  --verbose, -v              Enable verbose output
  --help                     Show this message and exit
```

#### Import Examples

**Import all artists from CSV:**
```bash
artistscraper import artists.csv
```

**Import only artists with at least 10 plays:**
```bash
artistscraper import artists.csv --min-plays 10
```

**Import only artists with at least 50 plays (with verbose output):**
```bash
artistscraper import artists.csv --min-plays 50 --verbose
```

## Output

The tool generates two files:

1. **artists.csv** (or custom name): Main output with four columns:
   - Artist Name
   - MusicBrainz ID (format: `lidarr:ID`)
   - Source (Spotify, YouTube Music, or both)
   - Play Count (number of tracks by this artist)

2. **skipped_artists.log**: List of artists without MusicBrainz IDs

Example CSV output:
```csv
Artist Name,MusicBrainz ID,Source,Play Count
Taylor Swift,lidarr:20244d07-534f-4eff-b4d4-930878889970,Spotify,45
The Beatles,lidarr:b10bbbfc-cf9e-42e0-be17-e2c3e1d2600d,"Spotify, YouTube Music",23
Radiohead,lidarr:a74b1b7f-71a5-4011-9441-d0b5e4122711,YouTube Music,12
```

## Lidarr Integration

When using the `--lidarr` flag:

1. The tool connects to your local Lidarr instance
2. Artists with MusicBrainz IDs are searched in Lidarr
3. New artists are added with monitoring enabled
4. Existing artists are skipped
5. Uses your Lidarr default settings for:
   - Root folder
   - Quality profile
   - Metadata profile

## Troubleshooting

### "Configuration file not found"
Make sure you've copied `config.example.json` to `config.json` and filled in your credentials.

### "Failed to authenticate with Spotify"
- Verify your `client_id`, `client_secret`, and `refresh_token` are correct
- Make sure your refresh token hasn't expired (regenerate if needed)

### "Failed to authenticate with YouTube Music"
- Run `poetry run ytmusicapi oauth --client-id YOUR_ID --client-secret YOUR_SECRET` to regenerate authentication
- Make sure the auth file path in `config.json` matches the generated file
- Ensure YouTube Data API v3 is enabled in your Google Cloud project
- See [YOUTUBE_MUSIC_SETUP.md](YOUTUBE_MUSIC_SETUP.md) for detailed troubleshooting

### "HTTP 400: Bad Request" from YouTube Music
This error was fixed in the November 2025 update. If you're still seeing it:
- Make sure you have the latest version of the code
- Regenerate your OAuth token with your Google Cloud credentials
- See [CHANGELOG_YOUTUBE_FIX.md](CHANGELOG_YOUTUBE_FIX.md) for migration instructions

### "HTTP 403: Forbidden" from YouTube Music
- YouTube Data API v3 is not enabled in your Google Cloud project
- Your OAuth token doesn't have the correct scopes
- Regenerate your token after enabling the API

### "Failed to connect to Lidarr"
- Verify Lidarr is running
- Check the URL and API key in `config.json`
- Ensure you're using `http://` or `https://` in the URL

### MusicBrainz rate limiting
The tool automatically respects MusicBrainz's rate limit (1 request per second). For large libraries, this process may take a while.

### Low MusicBrainz match rate
- MusicBrainz matching uses a 90% similarity threshold
- Some artists may not be in the MusicBrainz database
- Check `skipped_artists.log` for artists without matches
- You can manually add MusicBrainz IDs for important artists

## Contributing

This is a personal project, but suggestions and improvements are welcome!

## Acknowledgments

- [ytmusicapi](https://github.com/sigma67/ytmusicapi) - YouTube Music API
- [spotipy](https://github.com/spotipy-dev/spotipy) - Spotify API
- [musicbrainzngs](https://github.com/alastair/python-musicbrainzngs) - MusicBrainz API
- [typer](https://github.com/tiangolo/typer) - CLI framework
- [rich](https://github.com/Textualize/rich) - Terminal formatting
