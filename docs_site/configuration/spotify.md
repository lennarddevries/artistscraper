# Spotify Configuration

Configure Spotify API access to fetch your liked tracks, followed artists, and playlists.

## Create a Spotify App

1. Go to the [Spotify Developer Dashboard](https://developer.spotify.com/dashboard)
2. Log in with your Spotify account
3. Click **"Create app"**
4. Fill in the app details:
    - **App name**: Artist Scraper (or any name you prefer)
    - **App description**: Personal music library scraper
    - **Redirect URI**: `http://localhost:8888/callback`
    - **APIs used**: Web API
5. Click **"Save"**
6. In your app settings, note your:
    - **Client ID**
    - **Client Secret** (click "View client secret")

## Get a Refresh Token

You need a refresh token to access your Spotify data.

### Option 1: Using spotify-refresh-token-generator

1. Install the tool:
    ```bash
    npm install -g spotify-refresh-token-generator
    ```

2. Run it:
    ```bash
    spotify-refresh-token-generator
    ```

3. Follow the prompts and paste your Client ID and Client Secret

4. Authorize the scopes:
    - `user-library-read`
    - `user-follow-read`
    - `playlist-read-private`
    - `playlist-read-collaborative`

5. Copy the refresh token

### Option 2: Using Spotipy (Python)

```python
import spotipy
from spotipy.oauth2 import SpotifyOAuth

sp = SpotifyOAuth(
    client_id='YOUR_CLIENT_ID',
    client_secret='YOUR_CLIENT_SECRET',
    redirect_uri='http://localhost:8888/callback',
    scope='user-library-read user-follow-read playlist-read-private playlist-read-collaborative'
)

token_info = sp.get_access_token(as_dict=False)
print(f"Refresh token: {token_info}")
```

## Update config.json

Add your Spotify credentials to `config.json`:

```json
{
  "spotify": {
    "client_id": "your_spotify_client_id_here",
    "client_secret": "your_spotify_client_secret_here",
    "refresh_token": "your_spotify_refresh_token_here"
  }
}
```

## Required Scopes

The refresh token must have these scopes:

- `user-library-read` - Access your liked tracks
- `user-follow-read` - Access your followed artists
- `playlist-read-private` - Access your private playlists
- `playlist-read-collaborative` - Access collaborative playlists

## What Data is Accessed?

Artist Scraper fetches:

- All tracks you've liked
- All artists you follow
- All your playlists (public, private, and collaborative)
- Track metadata (artist names, play counts)

It does **not** modify any data - all access is read-only.

## Troubleshooting

### "Failed to authenticate with Spotify"

- Verify your `client_id`, `client_secret`, and `refresh_token` are correct
- Make sure your refresh token hasn't expired (regenerate if needed)
- Check that your redirect URI is exactly `http://localhost:8888/callback`

### "Insufficient client scope"

Your refresh token doesn't have the required scopes. Regenerate it with all required scopes listed above.

## Next Steps

Configure [YouTube Music](youtube-music.md) to fetch artists from your YouTube Music library.
