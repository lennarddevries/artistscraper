# YouTube Music Configuration

Configure YouTube Data API v3 access to fetch artists from your YouTube Music library.

!!! info "API Update - November 2025"
    Artist Scraper now uses the **YouTube Data API v3** instead of the YouTube Music internal API for better reliability and stability.

## Prerequisites

- A Google Cloud Project
- YouTube Data API v3 enabled
- OAuth 2.0 credentials

## Step 1: Create a Google Cloud Project

1. Go to the [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Note your project name

## Step 2: Enable YouTube Data API v3

1. In your Google Cloud Project, go to **"APIs & Services"** > **"Library"**
2. Search for **"YouTube Data API v3"**
3. Click on it and click **"Enable"**

## Step 3: Create OAuth 2.0 Credentials

1. Go to **"APIs & Services"** > **"Credentials"**
2. Click **"Create Credentials"** > **"OAuth client ID"**
3. If prompted, configure the OAuth consent screen:
    - **User Type**: External
    - **App name**: Artist Scraper
    - **User support email**: Your email
    - **Developer contact email**: Your email
    - **Scopes**: Add `../auth/youtube` scope
4. Choose **"Desktop app"** as the application type
5. Give it a name (e.g., "Artist Scraper Desktop")
6. Click **"Create"**
7. Save your `client_id` and `client_secret`

## Step 4: Generate OAuth Token

Run the OAuth flow to get your access token:

```bash
ytmusicapi oauth --client-id YOUR_CLIENT_ID.apps.googleusercontent.com --client-secret YOUR_CLIENT_SECRET
```

This will:

1. Open your browser
2. Ask you to authorize the app
3. Save the token to `ytmusic_auth.json`

Alternative: Use Python script:

```python
from ytmusicapi.auth.oauth import OAuthCredentials
import json
import time

creds = OAuthCredentials(
    client_id='YOUR_CLIENT_ID.apps.googleusercontent.com',
    client_secret='YOUR_CLIENT_SECRET'
)

code = creds.get_code()
print(f'Visit: {code["verification_url"]}')
print(f'Code: {code["user_code"]}')

input('Press Enter after authorizing...')

token = creds.token_from_code(code['device_code'])
if 'expires_in' in token:
    token['expires_at'] = int(time.time()) + token['expires_in']

with open('ytmusic_auth.json', 'w') as f:
    json.dump(token, f, indent=2)

print('✓ Auth file saved to ytmusic_auth.json')
```

## Step 5: Update config.json

Add your YouTube Music credentials to `config.json`:

```json
{
  "youtube_music": {
    "auth_file": "ytmusic_auth.json",
    "client_id": "YOUR_CLIENT_ID.apps.googleusercontent.com",
    "client_secret": "YOUR_CLIENT_SECRET"
  }
}
```

## How It Works

Artist Scraper extracts artists from three sources:

### 1. Liked Videos/Songs
- Fetches videos you've liked on YouTube
- Extracts artist names from video titles (format: "Artist - Song Title")
- Identifies VEVO channels (e.g., "Taylor SwiftVEVO" → "Taylor Swift")

### 2. Channel Subscriptions
- Uses your subscribed channels as potential artists
- Cleans up suffixes like "VEVO", "Official", etc.

### 3. Playlists
- Fetches all your YouTube playlists
- Extracts artists from playlist items
- Uses the same title parsing and VEVO detection

## API Quotas

YouTube Data API v3 has daily quota limits:

- **Default quota**: 10,000 units per day
- **Typical scrape**: 10-50 API calls
- **Cost per call**: 1-3 units

For most users, this is sufficient for daily scrapes.

## Required Scopes

The OAuth token requires:

- `https://www.googleapis.com/auth/youtube` - Full access to YouTube account

This scope allows reading:

- Liked videos
- Playlists
- Subscriptions
- Your YouTube Music library

## Privacy & Security

- OAuth tokens are stored locally in `ytmusic_auth.json`
- Never commit this file to version control (it's in `.gitignore`)
- You can revoke access anytime in your [Google Account settings](https://myaccount.google.com/permissions)

## Troubleshooting

### HTTP 403: Forbidden

**Cause**: YouTube Data API v3 is not enabled

**Solution**:

1. Enable YouTube Data API v3 in Google Cloud Console
2. Regenerate your OAuth token

### HTTP 400: Bad Request

**Cause**: Invalid OAuth credentials or expired token

**Solution**:

1. Check that your `client_id` and `client_secret` are correct in `config.json`
2. Regenerate your OAuth token

### No Artists Found

**Possible Causes**:

- You don't have any liked videos, subscriptions, or playlists
- Your content is private/hidden
- Artist names couldn't be extracted from video titles

**Solution**:

- Like some music videos on YouTube
- Subscribe to artist channels
- Create playlists with music videos
- Run with `--verbose` to see what's being fetched

## Next Steps

Configure [MusicBrainz](musicbrainz.md) for artist ID lookups.
