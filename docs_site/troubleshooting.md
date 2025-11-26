# Troubleshooting

Common issues and their solutions.

## Configuration Issues

### "Configuration file not found"

**Error:**
```
✗ Configuration file not found: config.json
Run 'artistscraper print-config > config.json' to create a config file
```

**Solution:**

Create a configuration file:

```bash
artistscraper print-config > config.json
```

Then edit it with your credentials.

---

## Spotify Issues

### "Failed to authenticate with Spotify"

**Possible Causes:**

- Invalid `client_id`, `client_secret`, or `refresh_token`
- Expired refresh token
- Wrong redirect URI in Spotify app settings

**Solutions:**

1. Verify your credentials in `config.json` are correct
2. Check your Spotify app settings:
    - Redirect URI must be exactly: `http://localhost:8888/callback`
3. Regenerate your refresh token:
    - Use [spotify-refresh-token-generator](https://github.com/benblamey/spotify-refresh-token-generator)
    - Ensure all required scopes are included

### "Insufficient client scope"

**Error:**
```
Insufficient client scope: user-library-read
```

**Solution:**

Your refresh token doesn't have the required scopes. Regenerate it with all scopes:

- `user-library-read`
- `user-follow-read`
- `playlist-read-private`
- `playlist-read-collaborative`

---

## YouTube Music Issues

### "HTTP 403: Forbidden"

**Cause:** YouTube Data API v3 is not enabled in your Google Cloud project

**Solution:**

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Select your project
3. Go to **APIs & Services** → **Library**
4. Search for **"YouTube Data API v3"**
5. Click **Enable**
6. Regenerate your OAuth token:
    ```bash
    ytmusicapi oauth --client-id YOUR_ID --client-secret YOUR_SECRET
    ```

### "HTTP 400: Bad Request"

**Cause:** Invalid OAuth credentials or expired token

**Solution:**

1. Check `client_id` and `client_secret` in `config.json`
2. Regenerate your OAuth token:
    ```bash
    rm ytmusic_auth.json
    ytmusicapi oauth --client-id YOUR_ID --client-secret YOUR_SECRET
    ```

### "Failed to authenticate with YouTube Music"

**Possible Causes:**

- Expired OAuth token
- Wrong OAuth credentials
- Auth file not found

**Solutions:**

1. Check `auth_file` path in `config.json` matches the generated file
2. Regenerate authentication:
    ```bash
    ytmusicapi oauth --client-id YOUR_ID --client-secret YOUR_SECRET
    ```
3. Ensure YouTube Data API v3 is enabled

### "No Artists Found" from YouTube Music

**Possible Causes:**

- No liked videos, subscriptions, or playlists
- Content is private
- Couldn't extract artist names from titles

**Solutions:**

1. Like some music videos on YouTube
2. Subscribe to artist channels
3. Create playlists with music videos
4. Run with `--verbose` to see what's being fetched:
    ```bash
    artistscraper scrape --youtube-only --verbose
    ```

---

## Lidarr Issues

### "Failed to connect to Lidarr"

**Possible Causes:**

- Lidarr is not running
- Wrong URL in `config.json`
- Wrong API key
- Network/firewall blocking connection

**Solutions:**

1. Verify Lidarr is running:
    - Open Lidarr in your browser
    - Check the URL and port
2. Check `config.json`:
    - URL must include `http://` or `https://`
    - API key must match Settings → General → Security
3. Test from the same machine:
    ```bash
    curl -H "X-Api-Key: YOUR_API_KEY" http://localhost:8686/api/v1/system/status
    ```

### "No root folders configured"

**Cause:** Lidarr doesn't have any root folders set up

**Solution:**

1. In Lidarr, go to **Settings** → **Media Management**
2. Scroll to **Root Folders**
3. Add at least one root folder where music will be stored
4. Save settings
5. Try Artist Scraper again

### "Artist not found in Lidarr"

**Cause:** The artist's MusicBrainz ID is not in Lidarr's database

**This is normal** for:
- Very new artists
- Regional/local artists
- Artists not in MusicBrainz

**Solutions:**

- Wait for Lidarr database updates
- Check if artist exists in MusicBrainz
- Use `--verbose` to see details:
    ```bash
    artistscraper import artists.csv --verbose
    ```

---

## MusicBrainz Issues

### "Network error looking up [Artist]"

**Error:**
```
Network error looking up Taylor Swift: Connection reset by peer
```

**Cause:** MusicBrainz rate limiting or network issues

**This is normal** and expected for large libraries.

**Solutions:**

- The scraper automatically continues
- Failed artists are logged to `skipped_artists.log`
- You can manually look them up later on [musicbrainz.org](https://musicbrainz.org/)
- Run again to retry failed artists

### Low MusicBrainz Match Rate

**Issue:** Many artists in `skipped_artists.log`

**Possible Reasons:**

1. Artists not in MusicBrainz database
2. Name variations (typos, different spellings)
3. Fuzzy match below 90% threshold
4. Non-music content from YouTube

**Solutions:**

1. Review `skipped_artists.log`
2. Manually search important artists on [musicbrainz.org](https://musicbrainz.org/)
3. Add MusicBrainz IDs manually to CSV:
    ```csv
    Artist Name,MusicBrainz ID,Source,Play Count
    Your Artist,lidarr:MBID-HERE,Spotify,10
    ```
4. Re-import the CSV:
    ```bash
    artistscraper import artists.csv
    ```

### MusicBrainz is Slow

**Issue:** Takes a long time to look up IDs

**This is expected** due to MusicBrainz rate limiting:

- 1 request per second for regular users
- 100 artists ≈ 2 minutes
- 500 artists ≈ 9 minutes
- 1000 artists ≈ 17 minutes

**Options:**

1. **Skip lookups** for faster scraping:
    ```bash
    artistscraper scrape --skip-musicbrainz
    ```
    (Note: Cannot use with `--lidarr`)

2. **Be patient** - the progress bar shows status

3. **MusicBrainz supporter** - Higher rate limits available for supporters

---

## Performance Issues

### Scrape Takes Too Long

**Optimize by limiting sources:**

```bash
# Spotify only (faster than both)
artistscraper scrape --spotify-only

# Skip MusicBrainz (much faster)
artistscraper scrape --skip-musicbrainz

# Combine both
artistscraper scrape --spotify-only --skip-musicbrainz
```

### YouTube Music Fetching is Slow

**Cause:** Large number of liked videos or playlists

**Normal behavior:** YouTube API requires pagination

**Solution:** Be patient, progress bar shows status

---

## CSV/Import Issues

### "CSV must have 'Artist Name' and 'MusicBrainz ID' columns"

**Cause:** CSV file is missing required columns

**Solution:**

Ensure your CSV has these columns (exact names):
- `Artist Name`
- `MusicBrainz ID`

Header row is required:
```csv
Artist Name,MusicBrainz ID,Source,Play Count
Taylor Swift,lidarr:123...,Spotify,10
```

### "CSV must have 'Play Count' column when using --min-plays filter"

**Cause:** Using `--min-plays` but CSV doesn't have `Play Count` column

**Solution:**

Either:

1. Remove `--min-plays` filter:
    ```bash
    artistscraper import artists.csv
    ```

2. Or ensure CSV has `Play Count` column:
    ```csv
    Artist Name,MusicBrainz ID,Source,Play Count
    ...
    ```

---

## Getting More Help

### Enable Verbose Output

For detailed debugging information:

```bash
artistscraper scrape --verbose
```

This shows:
- Detailed API requests
- Response data
- Error stack traces
- Progress details

### Check Logs

Review the skip log for details:

```bash
cat skipped_artists.log
```

### Report Issues

If you've tried the above solutions and still have issues, please report:

1. Go to [GitHub Issues](https://github.com/lennarddevries/artistscraper/issues)
2. Include:
    - Python version: `python --version`
    - OS: macOS/Linux/Windows
    - Artist Scraper version: `pip show artistscraper`
    - Full error message
    - Steps to reproduce
    - Configuration (with credentials redacted)

### Community Support

- Check existing [GitHub Issues](https://github.com/lennarddevries/artistscraper/issues)
- Search [Discussions](https://github.com/lennarddevries/artistscraper/discussions)
