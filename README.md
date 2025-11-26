# Artist Scraper [![Build](https://github.com/lennarddevries/artistscraper/actions/workflows/ci.yml/badge.svg)](https://github.com/lennarddevries/artistscraper/actions/workflows/ci.yml) [![PyPI](https://img.shields.io/pypi/v/artistscraper.svg)](https://pypi.org/project/artistscraper/) [![Buy Me A Coffee](https://img.shields.io/badge/Buy%20Me%20A%20Coffee-Support-yellow?logo=buy-me-a-coffee)](https://www.buymeacoffee.com/lennarddevries)

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

### From PyPI (Recommended)

```bash
pip install artistscraper
```

Or with pipx for isolated installation:

```bash
pipx install artistscraper
```

### From Source

#### Prerequisites

- Python 3.12 or higher
- Poetry (for dependency management)

#### Setup

1. Clone the repository:
```bash
git clone https://github.com/lennarddevries/artistscraper.git
cd artistscraper
```

2. Install dependencies:
```bash
poetry install
```

## Configuration

Before using the tool, you need to set up your API credentials.

1. Create a configuration file:
```bash
artistscraper print-config > config.json
```

2. Edit `config.json` with your credentials (see sections below)

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
ytmusicapi oauth --client-id YOUR_CLIENT_ID --client-secret YOUR_CLIENT_SECRET
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
  "user_agent": "artistscraper/1.0.0 (your-email@example.com)"
}
```

### Lidarr Configuration (Optional)

If you plan to use the `--lidarr` flag:

1. Open your Lidarr instance
2. Go to Settings → General
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
artistscraper scrape
```

If installed from source with Poetry:
```bash
poetry run artistscraper scrape
```

#### Options

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

#### Examples

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
artistscraper import artists.csv
```

#### Options

```
Options:
  --config, -c PATH          Path to configuration file (default: config.json)
  --min-plays INTEGER        Only import artists with at least this many plays
  --verbose, -v              Enable verbose output
  --help                     Show this message and exit
```

#### Examples

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
Make sure you've created `config.json` with `artistscraper print-config > config.json` and filled in your credentials.

### "Failed to authenticate with Spotify"
- Verify your `client_id`, `client_secret`, and `refresh_token` are correct
- Make sure your refresh token hasn't expired (regenerate if needed)

### "Failed to authenticate with YouTube Music"
- Run `ytmusicapi oauth --client-id YOUR_ID --client-secret YOUR_SECRET` to regenerate authentication
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

Contributions are welcome! Whether it's bug reports, feature requests, or code contributions, all input is appreciated.

### Development Setup

1. Clone the repository:
```bash
git clone https://github.com/lennarddevries/artistscraper.git
cd artistscraper
```

2. Install dependencies (including development tools):
```bash
poetry install
```

3. Install pre-commit hooks:
```bash
poetry run pre-commit install
```

### Development Workflow

**Run the application:**
```bash
poetry run artistscraper scrape
```

**Run code quality checks:**
```bash
# Format code with black
poetry run black artistscraper

# Sort imports with ruff
poetry run ruff check --select I --fix artistscraper

# Type checking with mypy
poetry run mypy artistscraper
```

**Run all quality checks (same as CI):**
```bash
# All checks run automatically via pre-commit hooks
poetry run pre-commit run --all-files
```

### Code Style

This project uses:
- **black** for code formatting (88 character line length)
- **ruff** for import sorting and linting
- **mypy** for static type checking

All code must pass these checks before being committed (enforced by pre-commit hooks).

### Project Structure

```
artistscraper/
├── artistscraper/          # Main package
│   ├── __init__.py
│   ├── __main__.py         # CLI entry point
│   ├── config.py           # Configuration management
│   ├── lidarr.py           # Lidarr integration
│   ├── musicbrainz.py      # MusicBrainz ID lookup
│   ├── spotify.py          # Spotify integration
│   └── youtube.py          # YouTube Music integration
├── .github/workflows/      # CI/CD workflows
│   ├── ci.yml             # Quality control
│   └── cd.yml             # Automated releases
├── config.example.json     # Example configuration
├── pyproject.toml          # Project metadata & dependencies
└── README.md              # This file
```

### Reporting Issues

When reporting bugs, please include:
- Python version
- Operating system
- Full error message and stack trace
- Steps to reproduce the issue
- Your configuration (with credentials redacted)

### Submitting Pull Requests

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Run quality checks (`poetry run pre-commit run --all-files`)
5. Commit your changes (use [conventional commits](https://www.conventionalcommits.org/))
6. Push to your fork (`git push origin feature/amazing-feature`)
7. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- [ytmusicapi](https://github.com/sigma67/ytmusicapi) - YouTube Music API
- [spotipy](https://github.com/spotipy-dev/spotipy) - Spotify API
- [musicbrainzngs](https://github.com/alastair/python-musicbrainzngs) - MusicBrainz API
- [typer](https://github.com/tiangolo/typer) - CLI framework
- [rich](https://github.com/Textualize/rich) - Terminal formatting
