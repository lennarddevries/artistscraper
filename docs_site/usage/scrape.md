# Scrape Command

The `scrape` command fetches artists from Spotify and/or YouTube Music, looks up MusicBrainz IDs, and exports to CSV.

## Basic Usage

Fetch artists from both Spotify and YouTube Music:

```bash
artistscraper scrape
```

## Command Options

```
Options:
  --config, -c PATH     Path to configuration file (default: config.json)
  --spotify-only        Fetch artists from Spotify only
  --youtube-only        Fetch artists from YouTube Music only
  --skip-musicbrainz    Skip MusicBrainz ID lookup
  --lidarr              Add artists to Lidarr after export
  --output, -o PATH     Output CSV file path (overrides config)
  --verbose, -v         Enable verbose output
  --help                Show this message and exit
```

## Examples

### Fetch from Specific Source

**Spotify only:**
```bash
artistscraper scrape --spotify-only
```

**YouTube Music only:**
```bash
artistscraper scrape --youtube-only
```

### Custom Output File

```bash
artistscraper scrape --output my_artists.csv
```

Or short form:
```bash
artistscraper scrape -o my_artists.csv
```

### Skip MusicBrainz Lookup

For faster scraping without ID lookups:

```bash
artistscraper scrape --skip-musicbrainz
```

!!! warning
    When using `--skip-musicbrainz`, you cannot use `--lidarr` as Lidarr requires MusicBrainz IDs.

### Add to Lidarr

Fetch, lookup IDs, and add to Lidarr in one command:

```bash
artistscraper scrape --lidarr
```

### Verbose Output

See detailed logging:

```bash
artistscraper scrape --verbose
```

Or short form:
```bash
artistscraper scrape -v
```

### Combining Options

You can combine multiple options:

```bash
# Fetch from Spotify only, enable verbose output, custom file
artistscraper scrape --spotify-only --verbose --output spotify_artists.csv

# Fetch from YouTube Music and add to Lidarr
artistscraper scrape --youtube-only --lidarr

# Fast scrape without IDs, Spotify only
artistscraper scrape --spotify-only --skip-musicbrainz
```

## Using a Custom Config File

Specify a different configuration file:

```bash
artistscraper scrape --config /path/to/config.json
```

Short form:
```bash
artistscraper scrape -c /path/to/config.json
```

## What Happens During Scrape

### Step 1: Fetch from Sources

The scraper:

- Connects to Spotify (if enabled)
    - Fetches all liked tracks
    - Fetches all followed artists
    - Fetches all playlists (public, private, collaborative)
    - Extracts unique artist names
- Connects to YouTube Music (if enabled)
    - Fetches all liked videos
    - Fetches all channel subscriptions
    - Fetches all playlists
    - Extracts artist names from titles and channels

Progress is shown with a progress bar.

### Step 2: Deduplicate

- Combines artists from all sources
- Removes duplicates
- Tracks which source(s) each artist came from
- Counts how many tracks by each artist

### Step 3: MusicBrainz Lookup

Unless `--skip-musicbrainz` is used:

- Looks up MusicBrainz ID for each artist
- Uses fuzzy matching (90% similarity threshold)
- Respects 1 request/second rate limit
- Shows progress bar
- Logs artists without matches to `skipped_artists.log`

### Step 4: Export

- Writes matched artists to CSV with:
    - Artist Name
    - MusicBrainz ID (format: `lidarr:ID`)
    - Source (Spotify, YouTube Music, or both)
    - Play Count
- Writes unmatched artists to `skipped_artists.log`

### Step 5: Lidarr Integration (Optional)

If `--lidarr` is used:

- Connects to Lidarr
- For each artist with MusicBrainz ID:
    - Checks if already exists
    - Searches Lidarr's database
    - Adds new artists with monitoring enabled
- Shows summary of added/existing/failed artists

## Output

The scraper generates:

1. **artists.csv** (or custom name): Main output file
2. **skipped_artists.log**: Artists without MusicBrainz IDs

See [Output Files](output.md) for details.

## Performance

Typical execution times:

- **Fetching (Spotify + YouTube)**: 30-60 seconds
- **MusicBrainz lookups**: 1 second per artist
    - 100 artists ≈ 2 minutes
    - 500 artists ≈ 9 minutes
    - 1000 artists ≈ 17 minutes
- **Lidarr import**: 1-5 seconds per artist

Total time depends on your library size.

## From Source Installation

If you installed from source with Poetry:

```bash
poetry run artistscraper scrape [options]
```

## Next Steps

- Learn about [Output Files](output.md)
- Use the [Import Command](import.md) to add artists to Lidarr later
- Check [Troubleshooting](../troubleshooting.md) if you encounter issues
