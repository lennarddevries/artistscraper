# Lidarr Configuration

Configure Lidarr integration to automatically add discovered artists to your music library.

!!! note "Optional Configuration"
    Lidarr configuration is only needed if you plan to use the `--lidarr` flag or the `import` command.

## What is Lidarr?

[Lidarr](https://lidarr.audio/) is a music collection manager for automatic music downloads. It can monitor artists for new releases and automatically download them.

## Prerequisites

- Running Lidarr instance (version 1.0 or higher)
- Network access to Lidarr from where you're running Artist Scraper

## Get Your API Key

1. Open your Lidarr web interface
2. Go to **Settings** → **General**
3. Scroll to the **Security** section
4. Copy your **API Key**

## Update config.json

Add your Lidarr configuration:

```json
{
  "lidarr": {
    "url": "http://localhost:8686",
    "api_key": "your_lidarr_api_key_here"
  }
}
```

### Configuration Options

- **url**: The full URL to your Lidarr instance
    - Local: `http://localhost:8686`
    - Remote: `http://192.168.1.100:8686`
    - With reverse proxy: `https://lidarr.yourdomain.com`
- **api_key**: Your Lidarr API key from Settings → General

## Test Connection

Test that Artist Scraper can connect to Lidarr:

```bash
artistscraper scrape --lidarr --skip-musicbrainz --spotify-only
```

If successful, you'll see:

```
✓ Connected to Lidarr
```

## How It Works

When you use the `--lidarr` flag:

1. Artist Scraper fetches artists from Spotify/YouTube Music
2. Looks up MusicBrainz IDs for each artist
3. Connects to Lidarr
4. For each artist with a MusicBrainz ID:
    - Checks if the artist already exists in Lidarr
    - If not, searches Lidarr's database
    - Adds new artists with default settings:
        - **Monitored**: Yes
        - **Search for missing**: No (to avoid mass downloads)
        - **Root folder**: Your default root folder
        - **Quality profile**: Your default quality profile
        - **Metadata profile**: Your default metadata profile

## Using the Import Command

Instead of adding to Lidarr immediately during scrape, you can:

1. First scrape and export to CSV:
    ```bash
    artistscraper scrape
    ```

2. Review the CSV file

3. Import to Lidarr later:
    ```bash
    artistscraper import artists.csv
    ```

4. Or filter by play count:
    ```bash
    artistscraper import artists.csv --min-plays 10
    ```

This gives you more control over which artists are added.

## Lidarr Settings

Artist Scraper uses your Lidarr default settings:

- **Root Folder**: First configured root folder
- **Quality Profile**: First configured quality profile
- **Metadata Profile**: First configured metadata profile

Make sure these are configured in Lidarr before importing.

## Troubleshooting

### "Failed to connect to Lidarr"

**Causes**:

- Lidarr is not running
- Wrong URL in `config.json`
- Wrong API key
- Network/firewall blocking connection

**Solutions**:

1. Verify Lidarr is running and accessible in your browser
2. Check the URL is correct (include `http://` or `https://`)
3. Verify the API key in Lidarr Settings → General
4. Try accessing Lidarr from the same machine running Artist Scraper

### "No root folders configured"

**Cause**: Lidarr doesn't have any root folders set up

**Solution**:

1. In Lidarr, go to **Settings** → **Media Management**
2. Add at least one root folder where music will be stored
3. Try again

### "Artist not found in Lidarr"

**Cause**: The artist's MusicBrainz ID is not in Lidarr's database

**Solution**:

- This is normal for some artists
- Lidarr's database is periodically updated
- The artist may not be in MusicBrainz or Lidarr's metadata sources
- Check `--verbose` output for details

### Artists Added But Not Downloading

**This is intentional**. Artist Scraper sets `search_for_missing=False` to prevent:

- Mass downloads of entire discographies
- Exceeding download quotas
- Network congestion

After adding artists, you can:

1. Review added artists in Lidarr
2. Manually search for specific albums
3. Enable "Search on add" in Lidarr settings if you want automatic downloads

## Next Steps

Now you're ready to use Artist Scraper:

- Learn about the [Scrape Command](../usage/scrape.md)
- Or the [Import Command](../usage/import.md)
