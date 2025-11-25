# Changelog: YouTube Music Integration Fix

## Date: November 25, 2025

## Summary

Fixed YouTube Music integration by replacing the unreliable ytmusicapi internal API with the official YouTube Data API v3.

## Problem Description

The YouTube Music integration was failing with HTTP 400 errors:

```
ERROR: Server returned HTTP 400: Bad Request.
       Request contains an invalid argument.
```

This occurred across all YouTube Music API endpoints:
- `get_liked_songs()`
- `get_library_subscriptions()`
- `get_library_playlists()`

### Root Cause Analysis

After extensive investigation, we identified several issues:

1. **Internal API Issues**: YouTube Music's internal API (used by ytmusicapi) was returning "Precondition check failed" errors
2. **OAuth Client Compatibility**: Custom OAuth credentials were not properly supported by ytmusicapi's implementation
3. **API Instability**: The unofficial YouTube Music API is undocumented and prone to breaking changes

Even with:
- Proper OAuth scopes (`https://www.googleapis.com/auth/youtube`)
- Correctly configured Google Cloud project
- YouTube Data API v3 enabled
- Valid access tokens that worked with YouTube Data API

The ytmusicapi library still failed to make successful requests to YouTube Music's internal endpoints.

## Solution

### Complete Rewrite Using YouTube Data API v3

We completely rewrote `youtube_music_fetcher.py` to use the official YouTube Data API v3 instead of ytmusicapi's internal API client.

### Key Changes

#### 1. Removed ytmusicapi Dependency (for API calls)

**Before:**
```python
from ytmusicapi import YTMusic

ytmusic = YTMusic(auth_file, oauth_credentials=oauth_credentials)
liked = ytmusic.get_liked_songs(limit=None)
```

**After:**
```python
import requests
import json

def _make_request(endpoint, params):
    url = f"https://www.googleapis.com/youtube/v3/{endpoint}"
    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.get(url, headers=headers, params=params)
    return response.json()
```

#### 2. Artist Extraction Methods

**Liked Videos:**
- Fetches liked videos via `/youtube/v3/videos?myRating=like`
- Extracts artists from video titles (e.g., "Artist - Song Title")
- Identifies VEVO channels and extracts artist names

**Subscriptions:**
- Fetches subscriptions via `/youtube/v3/subscriptions?mine=true`
- Treats subscribed channels as potential artists
- Cleans up suffixes (VEVO, Official, etc.)

**Playlists:**
- Fetches playlists via `/youtube/v3/playlists?mine=true`
- Iterates through playlist items via `/youtube/v3/playlistItems`
- Extracts artists using same title parsing logic

#### 3. Title Parsing

Implemented intelligent artist extraction from video titles:

```python
def _extract_artist_from_title(title):
    for sep in [" - ", " – ", " — ", " | "]:
        if sep in title:
            artist = title.split(sep)[0].strip()
            return artist
    return None
```

## Files Changed

### Modified Files

1. **`artistscraper/youtube_music_fetcher.py`**
   - Complete rewrite (327 lines)
   - Removed ytmusicapi.YTMusic dependency
   - Added direct YouTube Data API v3 integration
   - Added artist extraction from titles and channels

2. **`config.json`**
   - Updated `youtube_music.client_id` with working credentials
   - Updated `youtube_music.client_secret` with working credentials

3. **`ytmusic_auth.json`**
   - Regenerated OAuth token with proper scopes

4. **`pyproject.toml`**
   - Updated ytmusicapi from 1.11.1 to 1.11.2 (for OAuth utilities only)

### New Files

1. **`YOUTUBE_MUSIC_SETUP.md`**
   - Comprehensive setup guide
   - Troubleshooting section
   - API rate limits documentation

2. **`CHANGELOG_YOUTUBE_FIX.md`**
   - This file - documents the fix

### Removed Files

None (kept for compatibility)

## Testing Results

### Before Fix
```
ERROR    Error fetching liked songs: Server returned HTTP 400: Bad Request.
ERROR    Error fetching subscribed artists: Server returned HTTP 400: Bad Request.
ERROR    Error fetching playlists: Server returned HTTP 400: Bad Request.
✗ No artists found from any source
```

### After Fix
```
✓ Successfully authenticated with YouTube Music
INFO  Fetching liked videos from YouTube...
INFO  Found 48 unique artists from liked videos
INFO  Fetching subscriptions from YouTube...
INFO  Found 223 subscribed channels
INFO  Fetching playlists from YouTube...
INFO  Found 21 playlists
INFO  Found 20 unique artists from playlists
✓ YouTube Music: Found 290 unique artists
```

## Backwards Compatibility

### Configuration File

The configuration format remains unchanged:

```json
{
  "youtube_music": {
    "auth_file": "ytmusic_auth.json",
    "client_id": "YOUR_CLIENT_ID",
    "client_secret": "YOUR_CLIENT_SECRET"
  }
}
```

### Command Line Interface

All CLI commands remain unchanged:

```bash
poetry run artistscraper scrape --youtube-only
poetry run artistscraper scrape --spotify-only
poetry run artistscraper scrape  # Both sources
```

### Auth File Format

The `ytmusic_auth.json` format is compatible with ytmusicapi OAuth:

```json
{
  "access_token": "ya29...",
  "expires_in": 3599,
  "refresh_token": "1//09...",
  "scope": "https://www.googleapis.com/auth/youtube",
  "token_type": "Bearer",
  "expires_at": 1764144057
}
```

## Migration Guide

### For Existing Users

If you were using the old implementation:

1. **Update the code**: Pull the latest changes
2. **Regenerate OAuth token**:
   ```bash
   rm ytmusic_auth.json
   poetry run ytmusicapi oauth --client-id YOUR_ID --client-secret YOUR_SECRET
   ```
3. **Run the scraper**: `poetry run artistscraper scrape --youtube-only`

### For New Users

Follow the setup guide in `YOUTUBE_MUSIC_SETUP.md`

## Known Limitations

### Artist Extraction Accuracy

- Artist names are extracted from video titles using pattern matching
- Not all videos follow the "Artist - Title" format
- Some artist names may be inaccurate or missing

**Example Issues:**
- Videos titled "Song Title (Official Video)" → No artist extracted
- Videos with unusual separators → May extract incorrect portion
- Non-music videos in liked videos → May extract incorrect "artists"

### Data Completeness

- Only extracts data from liked videos, subscriptions, and playlists
- Does not access:
  - Watch history
  - Recommended artists
  - YouTube Music-specific data (albums, etc.)

### API Quotas

- YouTube Data API v3 has daily quota limits (10,000 units/day)
- Large collections may hit quota limits
- MusicBrainz rate limiting (1 request/second) affects total runtime

## Performance

### API Calls

For a typical user:
- Liked videos: 1-5 API calls (depending on page count)
- Subscriptions: 1-5 API calls
- Playlists: 1 + N API calls (N = number of playlists)
- Total: ~10-50 API calls for most users

### Execution Time

- YouTube API fetching: 10-30 seconds
- MusicBrainz lookup: 290 seconds (290 artists × 1 second rate limit)
- Total: ~5-10 minutes for 290 artists

## Future Improvements

### Short Term
1. Add caching for artist extraction patterns
2. Improve artist name cleaning (remove featuring artists, etc.)
3. Add support for YouTube Music-specific playlists (liked songs, etc.)

### Long Term
1. Machine learning model for artist extraction from titles
2. Integration with Spotify API for artist verification
3. Support for YouTube Music branded content
4. Incremental updates (only fetch new content since last run)

## Dependencies

### Production Dependencies
- `requests>=2.31.0` - For HTTP API calls
- `ytmusicapi>=1.11.2` - For OAuth utilities only (not API calls)
- Existing dependencies unchanged

### Development Dependencies
No changes

## Breaking Changes

**None** - The changes are fully backwards compatible with existing configurations and workflows.

## Credits

- Issue identified and fixed by Claude (Anthropic)
- Testing by user: lennarddevries
- YouTube Data API v3 documentation: https://developers.google.com/youtube/v3

## Additional Resources

- [YouTube Data API v3 Documentation](https://developers.google.com/youtube/v3)
- [Google OAuth 2.0 Documentation](https://developers.google.com/identity/protocols/oauth2)
- [ytmusicapi GitHub Repository](https://github.com/sigma67/ytmusicapi)
- [Setup Guide](./YOUTUBE_MUSIC_SETUP.md)
