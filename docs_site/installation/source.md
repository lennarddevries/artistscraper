# Installation from Source

For development or to use the latest unreleased features, you can install from source.

## Prerequisites

- Python 3.12 or higher
- [Poetry](https://python-poetry.org/) for dependency management
- Git

## Install Poetry

If you don't have Poetry installed:

```bash
# macOS/Linux
curl -sSL https://install.python-poetry.org | python3 -

# Windows (PowerShell)
(Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content | python -
```

## Clone and Install

1. **Clone the repository:**

    ```bash
    git clone https://github.com/lennarddevries/artistscraper.git
    cd artistscraper
    ```

2. **Install dependencies:**

    ```bash
    poetry install
    ```

    This installs all production and development dependencies.

## Running from Source

When installed from source, prefix commands with `poetry run`:

```bash
# Run the scraper
poetry run artistscraper scrape

# Show help
poetry run artistscraper --help

# Generate config
poetry run artistscraper print-config > config.json
```

## Development Installation

For development with additional tools (linting, type checking, etc.):

```bash
poetry install --with dev
```

See the [Developer Wiki](https://github.com/lennarddevries/artistscraper/wiki) for contribution guidelines.

## Updating

To update to the latest version:

```bash
git pull origin main
poetry install
```

## Switch to Stable Release

If you want to switch back to a stable PyPI release:

```bash
# Uninstall the development version
cd ..
rm -rf artistscraper

# Install from PyPI
pip install artistscraper
```

## Next Steps

Continue to [Quick Start](quick-start.md) to configure and run your first scrape.
