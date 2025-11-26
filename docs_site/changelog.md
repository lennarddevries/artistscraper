# Changelog

## Recent Updates

### November 25, 2025 - YouTube Music API Migration

**Major update to YouTube Music integration:**

- ✅ Replaced unreliable ytmusicapi internal API with official YouTube Data API v3
- ✅ Fixed HTTP 400 errors that prevented YouTube Music from working
- ✅ Improved artist extraction from video titles and channel names
- ✅ Better error handling and reliability

For full technical details, see:

- [YouTube Music Fix Changelog](https://github.com/lennarddevries/artistscraper/wiki/CHANGELOG_YOUTUBE_FIX) - Detailed changelog
- [YouTube Music Setup Guide](https://github.com/lennarddevries/artistscraper/wiki/YOUTUBE_MUSIC_SETUP) - New setup instructions

### Version 1.1.3 - Configuration Improvements

**New Feature: print-config command**

- ✅ Added `artistscraper print-config` command
- ✅ Outputs example configuration to stdout
- ✅ Solves config.example.json accessibility when installed from PyPI/pipx
- ✅ Users can now run: `artistscraper print-config > config.json`

**Updates:**

- Updated README with new config command
- Updated error messages to reference new command
- Improved installation experience

## All Releases

See the [GitHub Releases](https://github.com/lennarddevries/artistscraper/releases) page for complete version history.

## Semantic Versioning

This project follows [Semantic Versioning](https://semver.org/):

- **MAJOR** version for incompatible API changes
- **MINOR** version for new functionality in a backward compatible manner
- **PATCH** version for backward compatible bug fixes

## Release Process

Releases are automated via [Semantic Release](https://github.com/semantic-release/semantic-release):

1. Commits follow [Conventional Commits](https://www.conventionalcommits.org/)
2. CI/CD pipeline builds and tests
3. Semantic Release determines version bump
4. Changelog is automatically generated
5. Package is published to PyPI
6. GitHub release is created

## Migration Guides

### Migrating from Pre-1.1 Versions

If you were using Artist Scraper before the YouTube Music API update:

1. **Update to latest version:**
    ```bash
    pip install --upgrade artistscraper
    ```

2. **Regenerate YouTube OAuth token:**
    ```bash
    rm ytmusic_auth.json
    ytmusicapi oauth --client-id YOUR_ID --client-secret YOUR_SECRET
    ```

3. **Ensure YouTube Data API v3 is enabled** in Google Cloud Console

4. **Run scraper:**
    ```bash
    artistscraper scrape
    ```

No changes needed to:
- Configuration file format
- Command-line interface
- CSV output format
- Lidarr integration

## Deprecation Policy

- Deprecated features are marked in documentation
- Deprecated features are supported for at least 2 minor versions
- Breaking changes only in major versions
- Migration guides provided for breaking changes

## Feature Requests

Have an idea for Artist Scraper?

- Check [existing issues](https://github.com/lennarddevries/artistscraper/issues)
- Open a [feature request](https://github.com/lennarddevries/artistscraper/issues/new)
- Start a [discussion](https://github.com/lennarddevries/artistscraper/discussions)

## Stay Updated

- ⭐ Star the [GitHub repository](https://github.com/lennarddevries/artistscraper)
- 👀 Watch releases for notifications
- 📦 Check [PyPI](https://pypi.org/project/artistscraper/) for latest version
