# Output Files

Artist Scraper generates two output files after each scrape.

## artists.csv

The main output file containing all artists with MusicBrainz IDs.

### Format

CSV file with four columns:

| Column | Description | Example |
|--------|-------------|---------|
| Artist Name | The artist's name | Taylor Swift |
| MusicBrainz ID | Unique ID (prefixed with `lidarr:`) | lidarr:20244d07-534f-4eff-b4d4-930878889970 |
| Source | Where the artist was found | Spotify, YouTube Music, or both |
| Play Count | Number of tracks by this artist | 45 |

### Example

```csv
Artist Name,MusicBrainz ID,Source,Play Count
Taylor Swift,lidarr:20244d07-534f-4eff-b4d4-930878889970,Spotify,45
The Beatles,lidarr:b10bbbfc-cf9e-42e0-be17-e2c3e1d2600d,"Spotify, YouTube Music",23
Radiohead,lidarr:a74b1b7f-71a5-4011-9441-d0b5e4122711,YouTube Music,12
Ed Sheeran,lidarr:b8a7c51f-362c-4dcb-a259-bc6e0095f0a6,Spotify,8
```

### Field Details

#### Artist Name

- The artist's name as it appears in Spotify/YouTube Music
- May include variations (e.g., "The Beatles" vs "Beatles")
- Unicode characters are preserved

#### MusicBrainz ID

- Format: `lidarr:` + MusicBrainz UUID
- The `lidarr:` prefix is required by Lidarr's import format
- Can be used to look up the artist on [musicbrainz.org](https://musicbrainz.org/)
- Example URL: `https://musicbrainz.org/artist/20244d07-534f-4eff-b4d4-930878889970`

#### Source

- `Spotify` - Found only in Spotify
- `YouTube Music` - Found only in YouTube Music
- `Spotify, YouTube Music` - Found in both sources

Helps identify:
- Which platform you use most for an artist
- Artists unique to one platform
- Cross-platform favorites

#### Play Count

- Total number of tracks by this artist in your library
- Includes:
    - Liked tracks
    - Tracks in playlists
    - Albums by followed artists (Spotify)
- Useful for:
    - Filtering with `--min-plays`
    - Identifying your most-listened artists
    - Prioritizing imports to Lidarr

## skipped_artists.log

A log file containing artists that couldn't be matched to MusicBrainz IDs.

### Format

Plain text file with one artist name per line:

```
Unknown Artist Name
Artist With Typo
很新艺人 (New Artist in Chinese)
```

### Why Artists are Skipped

Artists may be skipped for several reasons:

1. **Not in MusicBrainz Database**
    - Very new/emerging artists
    - Local/regional artists
    - Artists with limited online presence

2. **Name Variations**
    - Different spellings
    - Special characters
    - Language differences

3. **Fuzzy Match Threshold**
    - Match quality below 90% threshold
    - Multiple possible matches with low confidence

4. **Parsing Errors (YouTube Music)**
    - Couldn't extract artist from video title
    - Non-music content (podcasts, audiobooks)
    - Unusual title format

### Using the Skip Log

1. **Review the log:**
    ```bash
    cat skipped_artists.log
    ```

2. **Manually search for important artists:**
    - Go to [musicbrainz.org](https://musicbrainz.org/)
    - Search for the artist
    - Copy their MusicBrainz ID

3. **Add to CSV manually:**
    ```csv
    Skipped Artist,lidarr:MBID-HERE,Spotify,10
    ```

4. **Re-import:**
    ```bash
    artistscraper import artists.csv
    ```

## Customizing Output Paths

### Via Configuration File

Edit `config.json`:

```json
{
  "output": {
    "csv_file": "my_artists.csv",
    "skipped_log": "my_skipped.log"
  }
}
```

### Via Command Line

Override the CSV path for a single run:

```bash
artistscraper scrape --output custom_output.csv
```

The skip log will be named based on your config file setting.

## File Locations

By default, files are created in the current directory:

```
./artists.csv
./skipped_artists.log
```

You can use absolute or relative paths:

```json
{
  "output": {
    "csv_file": "/path/to/output/artists.csv",
    "skipped_log": "/path/to/output/skipped.log"
  }
}
```

## Handling Existing Files

Artist Scraper **overwrites** existing files without warning.

To preserve previous scrapes:

### Option 1: Custom Output Path

```bash
artistscraper scrape --output artists_$(date +%Y%m%d).csv
```

### Option 2: Move Before Scraping

```bash
mv artists.csv artists_backup.csv
artistscraper scrape
```

### Option 3: Version in Config

Update your config before each scrape:

```json
{
  "output": {
    "csv_file": "artists_v2.csv",
    "skipped_log": "skipped_v2.log"
  }
}
```

## Importing to Other Tools

### Excel/Google Sheets

Both Excel and Google Sheets can open CSV files directly:

- **Excel**: File → Open → Select CSV
- **Google Sheets**: File → Import → Upload CSV

### Python/Pandas

```python
import pandas as pd

df = pd.read_csv('artists.csv')
print(df.head())
```

### SQL Database

```sql
LOAD DATA INFILE '/path/to/artists.csv'
INTO TABLE artists
FIELDS TERMINATED BY ','
ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS;
```

### Custom Scripts

The CSV format is standard and can be parsed by any programming language.

## Next Steps

- Use the [Import Command](import.md) to add artists to Lidarr
- Filter imports with `--min-plays` based on Play Count
- Check [Troubleshooting](../troubleshooting.md) for common issues
