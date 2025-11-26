# Import Command

The `import` command reads a CSV file of artists and adds them to Lidarr.

## Basic Usage

Import all artists from a CSV file:

```bash
artistscraper import artists.csv
```

## Command Options

```
Arguments:
  CSV_FILE              Path to CSV file containing artists (required)

Options:
  --config, -c PATH     Path to configuration file (default: config.json)
  --min-plays INTEGER   Only import artists with at least this many plays
  --verbose, -v         Enable verbose output
  --help                Show this message and exit
```

## Examples

### Import All Artists

```bash
artistscraper import artists.csv
```

### Filter by Play Count

Import only artists with at least 10 plays:

```bash
artistscraper import artists.csv --min-plays 10
```

Import only artists with at least 50 plays:

```bash
artistscraper import artists.csv --min-plays 50
```

### Verbose Output

See detailed information about each artist:

```bash
artistscraper import artists.csv --verbose
```

Or short form:

```bash
artistscraper import artists.csv -v
```

### Combining Options

```bash
# Import artists with 20+ plays, verbose output
artistscraper import artists.csv --min-plays 20 --verbose

# Short form
artistscraper import artists.csv --min-plays 20 -v
```

### Custom Config File

```bash
artistscraper import artists.csv --config /path/to/config.json
```

## CSV File Format

The CSV file must have these columns:

- **Artist Name** - The artist's name
- **MusicBrainz ID** - The MusicBrainz ID (format: `lidarr:ID` or just `ID`)
- **Source** (optional) - Where the artist was found
- **Play Count** (optional, required for `--min-plays`) - Number of tracks

Example CSV:

```csv
Artist Name,MusicBrainz ID,Source,Play Count
Taylor Swift,lidarr:20244d07-534f-4eff-b4d4-930878889970,Spotify,45
The Beatles,lidarr:b10bbbfc-cf9e-42e0-be17-e2c3e1d2600d,"Spotify, YouTube Music",23
Radiohead,lidarr:a74b1b7f-71a5-4011-9441-d0b5e4122711,YouTube Music,12
```

## How It Works

### Step 1: Read CSV

- Opens and validates the CSV file
- Checks for required columns (`Artist Name`, `MusicBrainz ID`)
- If `--min-plays` is used, checks for `Play Count` column

### Step 2: Filter (Optional)

If `--min-plays` is specified:

- Filters out artists with fewer plays than the threshold
- Shows count of filtered artists

### Step 3: Connect to Lidarr

- Tests connection to Lidarr
- Retrieves Lidarr configuration (root folders, profiles)

### Step 4: Import Artists

For each artist:

1. Checks if artist already exists in Lidarr
2. If exists: Skip (counted as "already exists")
3. If not exists:
    - Search Lidarr's database with MusicBrainz ID
    - Add artist with default settings:
        - **Monitored**: Yes
        - **Search for missing**: No
        - **Root folder**: Default
        - **Quality profile**: Default
        - **Metadata profile**: Default
4. Count successes and failures

### Step 5: Summary

Shows a summary table with:

- Total artists in CSV
- Filtered out (if `--min-plays` used)
- Added to Lidarr
- Already in Lidarr
- Failed to add

## Use Cases

### Two-Stage Workflow

Separate scraping from importing:

```bash
# Stage 1: Scrape and export (no Lidarr)
artistscraper scrape

# Stage 2: Review CSV, then import
artistscraper import artists.csv
```

### Curated Imports

1. Scrape all artists:
    ```bash
    artistscraper scrape
    ```

2. Edit the CSV to remove unwanted artists

3. Import the curated list:
    ```bash
    artistscraper import artists.csv
    ```

### Selective Imports by Play Count

Only import artists you listen to frequently:

```bash
# Get all artists
artistscraper scrape

# Import only those with 20+ plays
artistscraper import artists.csv --min-plays 20
```

### Re-import After Lidarr Reset

If you reset your Lidarr database, re-import from CSV:

```bash
artistscraper import artists.csv
```

This is faster than re-scraping since MusicBrainz lookups are already done.

## Performance

Import speed:

- **Connection test**: <1 second
- **Per artist**: 1-5 seconds
    - Check if exists: ~0.5 seconds
    - Search and add: ~2-4 seconds

For 100 artists: ~3-8 minutes

## Error Handling

The import command handles errors gracefully:

- **Artist already exists**: Skipped, counted separately
- **Artist not found in Lidarr**: Logged, counted as failed
- **Network errors**: Retried, then logged as failed
- **Invalid MusicBrainz ID**: Skipped, counted as failed

Use `--verbose` to see detailed error messages.

## From Source Installation

If installed from source with Poetry:

```bash
poetry run artistscraper import artists.csv [options]
```

## Next Steps

- Learn about [Output Files](output.md) format
- Check [Troubleshooting](../troubleshooting.md) if you encounter issues
