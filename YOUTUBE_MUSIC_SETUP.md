# YouTube Music Setup Guide

## Overview

The Artist Scraper now uses the **YouTube Data API v3** to fetch artists from your YouTube Music library. This approach is more reliable than using the unofficial YouTube Music API.

## What Changed

### Previous Implementation Issues

The original implementation used `ytmusicapi` to access YouTube Music's internal API. However, this approach had several issues:

1. YouTube Music's internal API returned HTTP 400 "Bad Request" errors
2. Custom OAuth credentials didn't work properly with ytmusicapi
3. The internal API had "Precondition check failed" errors

### New Implementation

The new implementation uses the official **YouTube Data API v3** instead, which:

- Uses official, supported Google APIs
- Works reliably with OAuth credentials
- Has better error handling and rate limiting
- Extracts artists from video titles, VEVO channels, and subscriptions

## Setup Instructions

### Prerequisites

1. A Google Cloud Project with OAuth credentials
2. YouTube Data API v3 enabled in your project

### Step 1: Create Google Cloud OAuth Credentials

If you haven't already:

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Enable the **YouTube Data API v3**:
   - Go to "APIs & Services" > "Library"
   - Search for "YouTube Data API v3"
   - Click "Enable"
4. Create OAuth 2.0 credentials:
   - Go to "APIs & Services" > "Credentials"
   - Click "Create Credentials" > "OAuth client ID"
   - Choose "Desktop app" as the application type
   - Save your `client_id` and `client_secret`

### Step 2: Configure OAuth Credentials

Add your OAuth credentials to `config.json`:

```json
{
  "youtube_music": {
    "auth_file": "ytmusic_auth.json",
    "client_id": "YOUR_CLIENT_ID.apps.googleusercontent.com",
    "client_secret": "YOUR_CLIENT_SECRET"
  }
}
```

### Step 3: Generate OAuth Token

Run the following Python script to generate your OAuth token:

```bash
poetry run python -c "
from ytmusicapi.auth.oauth import OAuthCredentials
import json
import time

# Replace with your credentials
creds = OAuthCredentials(
    client_id='YOUR_CLIENT_ID.apps.googleusercontent.com',
    client_secret='YOUR_CLIENT_SECRET'
)

code = creds.get_code()
print(f'Visit: {code[\"verification_url\"]}')
print(f'Code: {code[\"user_code\"]}')

# Wait for user to authorize
input('Press Enter after authorizing...')

# Exchange code for token
token = creds.token_from_code(code['device_code'])
if 'expires_in' in token:
    token['expires_at'] = int(time.time()) + token['expires_in']

# Save token
with open('ytmusic_auth.json', 'w') as f:
    json.dump(token, f, indent=2)

print('✓ Auth file saved to ytmusic_auth.json')
"
```

Or use the ytmusicapi command (simpler):

```bash
poetry run ytmusicapi oauth --client-id YOUR_CLIENT_ID --client-secret YOUR_CLIENT_SECRET
```

Follow the prompts to authorize the application.

### Step 4: Test the Integration

Run the scraper to test if everything works:

```bash
poetry run artistscraper scrape --youtube-only
```

You should see output like:

```
✓ YouTube Music: Found X unique artists
```

## How It Works

### Artist Extraction

The scraper extracts artists from three sources:

1. **Liked Videos/Songs**
   - Extracts artist names from video titles (format: "Artist - Song Title")
   - Identifies VEVO channels (e.g., "Taylor SwiftVEVO" → "Taylor Swift")

2. **Channel Subscriptions**
   - Uses subscribed channels as potential artists
   - Cleans up suffixes like "VEVO", "Official", etc.

3. **Playlists**
   - Fetches all your playlists
   - Extracts artists from playlist items
   - Uses the same title parsing and VEVO detection

### Data Sources Comparison

| Method | Pros | Cons |
|--------|------|------|
| YouTube Music Internal API | Direct access to music data | Unreliable, undocumented, prone to breakage |
| YouTube Data API v3 | Official, stable, documented | Requires parsing titles, less accurate |

## Troubleshooting

### HTTP 403 Forbidden

**Error**: `403 Client Error: Forbidden`

**Cause**: YouTube Data API v3 is not enabled or OAuth token doesn't have correct scopes

**Solution**:
1. Enable YouTube Data API v3 in Google Cloud Console
2. Regenerate your OAuth token (delete `ytmusic_auth.json` and run Step 3 again)

### HTTP 400 Bad Request

**Error**: `400 Client Error: Bad Request`

**Cause**: Invalid OAuth credentials or expired token

**Solution**:
1. Check that your `client_id` and `client_secret` are correct in `config.json`
2. Regenerate your OAuth token

### No Artists Found

**Issue**: Scraper completes but finds 0 artists

**Possible Causes**:
1. You don't have any liked videos, subscriptions, or playlists
2. Your liked content is private/hidden
3. Artist names couldn't be extracted from video titles

**Solution**:
- Like some music videos on YouTube
- Subscribe to artist channels
- Create playlists with music videos
- Run with `--verbose` to see what's being fetched

### Network Errors During MusicBrainz Lookup

**Error**: `Network error looking up [Artist]: caused by: Connection reset by peer`

**Cause**: MusicBrainz rate limiting or network issues

**Solution**:
- These are expected and normal
- The scraper will continue and skip artists that fail
- MusicBrainz has rate limits (1 request per second)
- Wait and retry later for failed artists

## API Rate Limits

### YouTube Data API v3

- Default quota: 10,000 units per day
- Each API call costs units (typically 1-3 units)
- The scraper is designed to minimize API calls

### MusicBrainz

- Rate limit: 1 request per second
- The scraper automatically respects this limit
- Large artist lists will take time to process

## Privacy & Security

- OAuth tokens are stored locally in `ytmusic_auth.json`
- Never commit `ytmusic_auth.json` to version control (it's in `.gitignore`)
- Tokens can access your YouTube account based on granted scopes
- You can revoke access anytime in your [Google Account settings](https://myaccount.google.com/permissions)

## Scope Requirements

The OAuth token requires the following scope:
- `https://www.googleapis.com/auth/youtube` - Full access to YouTube account

This scope is required to:
- Read liked videos
- Read playlists
- Read subscriptions
- Access your YouTube Music library

## Additional Notes

- The scraper attempts to extract artist names from video titles using common patterns
- VEVO channels are treated as artist channels
- Some artist names may be inaccurate due to title parsing
- Consider reviewing the exported CSV and cleaning up incorrect entries
