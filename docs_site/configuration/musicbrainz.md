# MusicBrainz Configuration

Configure the MusicBrainz user agent for artist ID lookups.

## What is MusicBrainz?

[MusicBrainz](https://musicbrainz.org/) is an open music encyclopedia that collects music metadata. Artist Scraper uses it to find unique IDs for artists, which are required for Lidarr integration.

## Configuration

Update the user agent in `config.json` with your email:

```json
{
  "musicbrainz": {
    "user_agent": "artistscraper/1.0.0 (your-email@example.com)"
  }
}
```

Replace `your-email@example.com` with your actual email address.

## Why is an Email Required?

MusicBrainz requires a user agent with contact information so they can:

- Contact you if your application is causing problems
- Track usage and improve their service
- Identify misbehaving clients

## Rate Limiting

MusicBrainz has a rate limit:

- **1 request per second** for regular users
- **Higher limits** for paid supporters

Artist Scraper automatically respects this rate limit by:

- Adding a 1-second delay between requests
- Retrying failed requests
- Logging errors for manual review

### Impact on Performance

For a large library:

- 100 artists = ~2 minutes for MusicBrainz lookups
- 500 artists = ~9 minutes for MusicBrainz lookups
- 1000 artists = ~17 minutes for MusicBrainz lookups

The scraper shows a progress bar during this process.

## Skipping MusicBrainz Lookups

If you want to skip MusicBrainz lookups (faster but no IDs):

```bash
artistscraper scrape --skip-musicbrainz
```

This will:

- Export only artist names (no MusicBrainz IDs)
- Complete much faster
- Log all artists to `skipped_artists.log`
- Cannot be used with `--lidarr` flag

## Matching Algorithm

Artist Scraper uses fuzzy matching to find MusicBrainz IDs:

1. **Exact match**: Look for exact artist name
2. **Fuzzy match**: Use 90% similarity threshold
3. **First result**: Take the first match if multiple results

### Low Match Rates

If you're getting low match rates:

- Some artists may not be in MusicBrainz database
- Artist names may have typos or variations
- Check `skipped_artists.log` for unmatched artists
- You can manually add MusicBrainz IDs to the CSV

## Manual MusicBrainz IDs

If an artist wasn't matched, you can manually add their ID:

1. Search for the artist on [musicbrainz.org](https://musicbrainz.org/)
2. Copy their MusicBrainz ID from the URL
3. Add it to your CSV with the `lidarr:` prefix:
    ```csv
    Artist Name,MusicBrainz ID,Source,Play Count
    Unmatched Artist,lidarr:MBID-HERE,Spotify,5
    ```

## No Account Required

Unlike Spotify and YouTube, MusicBrainz doesn't require:

- Account creation
- API keys
- OAuth tokens

Just provide an email address in the user agent.

## Next Steps

- (Optional) Configure [Lidarr](lidarr.md) for automatic imports
- Or skip to [Usage](../usage/scrape.md) to start scraping
