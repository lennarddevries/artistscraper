# Artist Scraper

[![Build](https://github.com/lennarddevries/artistscraper/actions/workflows/ci.yml/badge.svg)](https://github.com/lennarddevries/artistscraper/actions/workflows/ci.yml) [![PyPI](https://img.shields.io/pypi/v/artistscraper.svg)](https://pypi.org/project/artistscraper/) [![Buy Me A Coffee](https://img.shields.io/badge/Buy%20Me%20A%20Coffee-Support-yellow?logo=buy-me-a-coffee)](https://www.buymeacoffee.com/lennarddevries)

A production-ready tool to fetch artists from YouTube Music and Spotify, look up their MusicBrainz IDs, and optionally add them to Lidarr for monitoring.

## Features

- Fetch artists from **Spotify** (liked tracks, followed artists, playlists) and **YouTube Music** (liked videos, subscriptions, playlists)
- Look up MusicBrainz IDs for all artists
- Track play counts and export to CSV
- Import to Lidarr with optional filtering by play count
- Beautiful CLI with progress bars and clear feedback

## Quick Start

```bash
# Install
pip install artistscraper

# Create config file
artistscraper print-config > config.json

# Edit config.json with your API credentials

# Run
artistscraper scrape
```

## Documentation

📚 **[Full Documentation](https://lennarddevries.github.io/artistscraper/)** - Installation, configuration, usage guides

🛠️ **[Developer Wiki](https://github.com/lennarddevries/artistscraper/wiki)** - Contributing, development setup, architecture

## License

MIT License - see the LICENSE file for details.
