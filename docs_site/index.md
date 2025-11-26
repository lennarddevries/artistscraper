# Artist Scraper

A production-ready tool to fetch artists from YouTube Music and Spotify, look up their MusicBrainz IDs, and optionally add them to Lidarr for monitoring.

[![Build](https://github.com/lennarddevries/artistscraper/actions/workflows/ci.yml/badge.svg)](https://github.com/lennarddevries/artistscraper/actions/workflows/ci.yml) [![PyPI](https://img.shields.io/pypi/v/artistscraper.svg)](https://pypi.org/project/artistscraper/)

## Features

- **Multi-source Fetching**: Collect artists from multiple sources
    - **Spotify**: Liked tracks, followed artists, and all playlists (public & private)
    - **YouTube Music**: Liked videos, channel subscriptions, and all playlists (via YouTube Data API v3)
- **MusicBrainz Integration**: Look up MusicBrainz IDs for all artists
- **Play Count Tracking**: Track how many songs you have from each artist
- **CSV Export**: Export to CSV with artist names, MusicBrainz IDs, sources, and play counts
- **Lidarr Integration**: Import CSV to Lidarr with optional filtering by play count
- **Deduplication**: Automatic deduplication of artists across sources
- **Beautiful CLI**: Colors, progress bars, and clear feedback
- **Comprehensive Logging**: Track skipped artists and errors

## Recent Updates

!!! info "YouTube Music Integration - November 25, 2025"
    Major update to YouTube Music integration:

    - Replaced unreliable ytmusicapi internal API with official YouTube Data API v3
    - Fixed HTTP 400 errors that prevented YouTube Music from working
    - Improved artist extraction from video titles and channel names

    See the [Changelog](changelog.md) for full details.

## Quick Start

```bash
# Install
pip install artistscraper

# Create config file
artistscraper print-config > config.json

# Edit config.json with your API credentials
# (See Configuration section for details)

# Run
artistscraper scrape
```

## Example Output

```csv
Artist Name,MusicBrainz ID,Source,Play Count
Taylor Swift,lidarr:20244d07-534f-4eff-b4d4-930878889970,Spotify,45
The Beatles,lidarr:b10bbbfc-cf9e-42e0-be17-e2c3e1d2600d,"Spotify, YouTube Music",23
Radiohead,lidarr:a74b1b7f-71a5-4011-9441-d0b5e4122711,YouTube Music,12
```

## Support

If you find this project useful, consider supporting development:

[![Buy Me A Coffee](https://img.shields.io/badge/Buy%20Me%20A%20Coffee-Support-yellow?logo=buy-me-a-coffee)](https://www.buymeacoffee.com/lennarddevries)

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- [ytmusicapi](https://github.com/sigma67/ytmusicapi) - YouTube Music API
- [spotipy](https://github.com/spotipy-dev/spotipy) - Spotify API
- [musicbrainzngs](https://github.com/alastair/python-musicbrainzngs) - MusicBrainz API
- [typer](https://github.com/tiangolo/typer) - CLI framework
- [rich](https://github.com/Textualize/rich) - Terminal formatting
