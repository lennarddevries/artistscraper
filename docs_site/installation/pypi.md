# Installation from PyPI

The recommended way to install Artist Scraper is via PyPI.

## Using pip

Install directly with pip:

```bash
pip install artistscraper
```

### Upgrade to Latest Version

```bash
pip install --upgrade artistscraper
```

### Install Specific Version

```bash
pip install artistscraper==1.1.3
```

## Using pipx (Recommended for CLI Tools)

[pipx](https://github.com/pypa/pipx) installs CLI tools in isolated environments, preventing dependency conflicts.

### Install pipx

```bash
# macOS
brew install pipx
pipx ensurepath

# Linux
python3 -m pip install --user pipx
python3 -m pipx ensurepath

# Windows
python -m pip install --user pipx
python -m pipx ensurepath
```

### Install Artist Scraper with pipx

```bash
pipx install artistscraper
```

### Upgrade

```bash
pipx upgrade artistscraper
```

### Uninstall

```bash
pipx uninstall artistscraper
```

## Requirements

- Python 3.12 or higher
- pip or pipx

## Verify Installation

After installation, verify it works:

```bash
artistscraper --help
```

You should see the command-line help output.

## Next Steps

Continue to [Quick Start](quick-start.md) to configure and run your first scrape.
