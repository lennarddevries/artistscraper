# Quick Start

Get up and running with Artist Scraper in minutes.

## Installation

Install via pip (recommended):

```bash
pip install artistscraper
```

Or with pipx for isolated installation:

```bash
pipx install artistscraper
```

## Initial Setup

1. **Create a configuration file:**

    ```bash
    artistscraper print-config > config.json
    ```

2. **Edit the configuration file** with your API credentials:

    ```bash
    nano config.json  # or use your preferred editor
    ```

3. **Set up your API credentials:**

    - [Spotify Configuration](../configuration/spotify.md) - Get Spotify API credentials
    - [YouTube Music Configuration](../configuration/youtube-music.md) - Set up YouTube Data API v3
    - [MusicBrainz Configuration](../configuration/musicbrainz.md) - Configure user agent
    - [Lidarr Configuration](../configuration/lidarr.md) (Optional) - Connect to Lidarr

## First Run

Once configured, run your first scrape:

```bash
artistscraper scrape
```

This will:

1. Fetch artists from Spotify and YouTube Music
2. Look up MusicBrainz IDs for all artists
3. Export results to `artists.csv`
4. Log skipped artists to `skipped_artists.log`

## What's Next?

- Learn about [all scrape command options](../usage/scrape.md)
- Understand the [output files](../usage/output.md)
- Set up [Lidarr integration](../configuration/lidarr.md)
- Check [troubleshooting](../troubleshooting.md) if you encounter issues
