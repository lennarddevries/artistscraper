"""Artist Scraper - Fetch artists from YouTube Music and Spotify."""

import csv
import json
import logging
import sys
from pathlib import Path
from typing import Dict, List, Optional

import typer
from rich import print as rprint
from rich.console import Console
from rich.logging import RichHandler
from rich.panel import Panel
from rich.progress import (
    BarColumn,
    Progress,
    SpinnerColumn,
    TaskProgressColumn,
    TextColumn,
)
from rich.table import Table

from .config import Config
from .exporter import CSVExporter
from .lidarr_client import LidarrClient
from .musicbrainz_lookup import MusicBrainzLookup
from .spotify_fetcher import SpotifyFetcher
from .youtube_music_fetcher import YouTubeMusicFetcher

app = typer.Typer(
    name="artistscraper",
    help="Fetch artists from YouTube Music and Spotify with MusicBrainz IDs",
    add_completion=False,
)

console = Console()

# Example configuration template
EXAMPLE_CONFIG = {
    "spotify": {
        "client_id": "your_spotify_client_id_here",
        "client_secret": "your_spotify_client_secret_here",
        "refresh_token": "your_spotify_refresh_token_here",
    },
    "youtube_music": {
        "auth_file": "ytmusic_auth.json",
        "client_id": "your_google_client_id_here (optional)",
        "client_secret": "your_google_client_secret_here (optional)",
    },
    "lidarr": {
        "url": "http://localhost:8686",
        "api_key": "your_lidarr_api_key_here",
    },
    "musicbrainz": {
        "user_agent": "artistscraper/0.1.0 (your-email@example.com)",
    },
    "output": {
        "csv_file": "artists.csv",
        "skipped_log": "skipped_artists.log",
    },
}


@app.command(name="scrape")
def main(
    config_file: str = typer.Option(
        "config.json", "--config", "-c", help="Path to configuration file"
    ),
    spotify_only: bool = typer.Option(
        False, "--spotify-only", help="Fetch artists from Spotify only"
    ),
    youtube_only: bool = typer.Option(
        False, "--youtube-only", help="Fetch artists from YouTube Music only"
    ),
    skip_musicbrainz: bool = typer.Option(
        False, "--skip-musicbrainz", help="Skip MusicBrainz ID lookup"
    ),
    lidarr: bool = typer.Option(
        False, "--lidarr", help="Add artists to Lidarr after export"
    ),
    output: Optional[str] = typer.Option(
        None, "--output", "-o", help="Output CSV file path (overrides config)"
    ),
    verbose: bool = typer.Option(
        False, "--verbose", "-v", help="Enable verbose output"
    ),
) -> None:
    """Fetch artists from YouTube Music and Spotify with MusicBrainz IDs."""

    # Configure logging based on verbose flag
    if verbose:
        logging.basicConfig(
            level=logging.DEBUG,
            format="%(name)s - %(message)s",
            handlers=[RichHandler(console=console, show_time=False, show_path=False)],
        )
        # Set specific loggers to appropriate levels
        logging.getLogger("artistscraper").setLevel(logging.DEBUG)
        logging.getLogger("urllib3").setLevel(logging.WARNING)
        logging.getLogger("spotipy").setLevel(logging.WARNING)
        logging.getLogger("ytmusicapi").setLevel(logging.WARNING)
    else:
        logging.basicConfig(
            level=logging.WARNING,
            format="%(message)s",
            handlers=[RichHandler(console=console, show_time=False, show_path=False)],
        )

    console.print(
        Panel.fit(
            "[bold cyan]Artist Scraper[/bold cyan]\n"
            "Fetch artists from YouTube Music and Spotify",
            border_style="cyan",
        )
    )
    console.print()

    # Load configuration
    try:
        config = Config(config_file)
        console.print(
            "[green]✓[/green] Configuration loaded successfully", style="bold"
        )
    except FileNotFoundError as e:
        console.print(f"[red]✗[/red] {e}", style="bold")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"[red]✗[/red] Error loading configuration: {e}", style="bold")
        raise typer.Exit(1)

    console.print()

    # Collect artists from sources with source and play count tracking
    all_artists = set()
    artist_sources: Dict[str, List[str]] = (
        {}
    )  # Track which source(s) each artist came from
    play_counts: Dict[str, int] = {}  # Track how many songs by each artist
    source_stats = {}

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TaskProgressColumn(),
        console=console,
    ) as progress:

        # Fetch from Spotify
        if not youtube_only:
            task = progress.add_task("[cyan]Fetching from Spotify...", total=None)

            spotify_fetcher = SpotifyFetcher(
                config.spotify_client_id,
                config.spotify_client_secret,
                config.spotify_refresh_token,
            )

            spotify_artists = spotify_fetcher.get_all_artists(play_counts)
            all_artists.update(spotify_artists)
            source_stats["Spotify"] = len(spotify_artists)

            # Track source for each artist
            for artist in spotify_artists:
                if artist not in artist_sources:
                    artist_sources[artist] = []
                artist_sources[artist].append("Spotify")

            progress.update(task, completed=True)
            console.print(
                f"[green]✓[/green] Spotify: Found {len(spotify_artists)} unique artists",
                style="bold",
            )

        # Fetch from YouTube Music
        if not spotify_only:
            task = progress.add_task("[red]Fetching from YouTube Music...", total=None)

            youtube_fetcher = YouTubeMusicFetcher(
                config.youtube_auth_file,
                config.youtube_client_id,
                config.youtube_client_secret,
            )
            youtube_artists = youtube_fetcher.get_all_artists(play_counts)
            all_artists.update(youtube_artists)
            source_stats["YouTube Music"] = len(youtube_artists)

            # Track source for each artist
            for artist in youtube_artists:
                if artist not in artist_sources:
                    artist_sources[artist] = []
                artist_sources[artist].append("YouTube Music")

            progress.update(task, completed=True)
            console.print(
                f"[green]✓[/green] YouTube Music: Found {len(youtube_artists)} unique artists",
                style="bold",
            )

    if not all_artists:
        console.print("[red]✗[/red] No artists found from any source", style="bold")
        raise typer.Exit(1)

    console.print()
    console.print(
        Panel(
            f"[bold green]Total unique artists: {len(all_artists)}[/bold green]",
            border_style="green",
        )
    )
    console.print()

    # Look up MusicBrainz IDs and export incrementally
    exported_count = 0
    skipped_count = 0

    output_file = output if output else config.output_csv_file
    exporter = CSVExporter(output_file, config.output_skipped_log)

    with exporter:
        if skip_musicbrainz:
            console.print(
                "[yellow]⚠[/yellow]  Skipping MusicBrainz lookup", style="bold"
            )
            for artist_name in sorted(all_artists):
                exporter.log_skipped_artist(artist_name)
        else:
            console.print(
                "[cyan]Looking up MusicBrainz IDs and exporting...[/cyan]", style="bold"
            )
            mb_lookup = MusicBrainzLookup(config.musicbrainz_user_agent)

            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                BarColumn(),
                TaskProgressColumn(),
                console=console,
            ) as progress:
                task = progress.add_task(
                    "[cyan]Processing artists...", total=len(all_artists)
                )

                for artist_name in sorted(all_artists):
                    mb_id = mb_lookup.lookup_artist(artist_name)
                    if mb_id:
                        source = ", ".join(artist_sources.get(artist_name, ["Unknown"]))
                        play_count = play_counts.get(artist_name, 0)
                        exporter.export_artist(artist_name, mb_id, source, play_count)
                    else:
                        exporter.log_skipped_artist(artist_name)

                    progress.update(
                        task,
                        advance=1,
                        description=f"[cyan]Processing... ({artist_name[:40]})",
                    )

        exported_count = exporter.exported_count
        skipped_count = exporter.skipped_count

        console.print(
            f"[green]✓[/green] MusicBrainz: Found IDs for {exported_count}/{len(all_artists)} artists",
            style="bold",
        )

    console.print()

    # Create summary table
    summary_table = Table(title="Summary", show_header=True, header_style="bold cyan")
    summary_table.add_column("Metric", style="cyan")
    summary_table.add_column("Count", justify="right", style="green")

    summary_table.add_row("Total Artists Found", str(len(all_artists)))
    summary_table.add_row("Artists Exported", str(exported_count))
    if skipped_count > 0:
        summary_table.add_row("Artists Skipped", str(skipped_count))

    console.print(summary_table)
    console.print()

    # Add to Lidarr if requested
    if lidarr:
        console.print(
            Panel(
                "[bold magenta]Adding artists to Lidarr[/bold magenta]",
                border_style="magenta",
            )
        )
        console.print()

        lidarr_client = LidarrClient(config.lidarr_url, config.lidarr_api_key)

        # Read artists from the generated CSV
        artists_with_ids = {}
        try:
            with open(output_file, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    artists_with_ids[row["Artist Name"]] = row["MusicBrainz ID"]
        except FileNotFoundError:
            console.print(
                f"[red]✗[/red] Exported CSV file not found: {output_file}", style="bold"
            )
            raise typer.Exit(1)
        except Exception as e:
            console.print(
                f"[red]✗[/red] Error reading exported CSV file: {e}", style="bold"
            )
            raise typer.Exit(1)

        if not artists_with_ids:
            console.print(
                "[yellow]⚠[/yellow]  No artists with MusicBrainz IDs to add to Lidarr",
                style="bold",
            )
        else:
            with console.status("[magenta]Connecting to Lidarr...", spinner="dots"):
                if not lidarr_client.test_connection():
                    console.print(
                        "[red]✗[/red] Failed to connect to Lidarr", style="bold"
                    )
                    raise typer.Exit(1)

            console.print("[green]✓[/green] Connected to Lidarr", style="bold")

            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                BarColumn(),
                TaskProgressColumn(),
                console=console,
            ) as progress:

                task = progress.add_task(
                    "[magenta]Adding artists to Lidarr...", total=len(artists_with_ids)
                )

                # We'll need to track progress manually
                added = 0
                failed = 0

                for artist_name, mb_id in sorted(artists_with_ids.items()):
                    mb_id_clean = mb_id.replace("lidarr:", "")

                    if lidarr_client.artist_exists(mb_id_clean):
                        added += 1
                    else:
                        artist_search_data = lidarr_client.search_artist(mb_id_clean)
                        if artist_search_data:
                            root_folders = lidarr_client.get_root_folders()
                            quality_profiles = lidarr_client.get_quality_profiles()
                            metadata_profiles = lidarr_client.get_metadata_profiles()

                            if root_folders and quality_profiles and metadata_profiles:
                                if lidarr_client.add_artist(
                                    artist_search_data,
                                    root_folders[0]["path"],
                                    quality_profiles[0]["id"],
                                    metadata_profiles[0]["id"],
                                    monitored=True,
                                    search_for_missing=False,
                                ):
                                    added += 1
                                else:
                                    failed += 1
                            else:
                                failed += 1
                        else:
                            failed += 1

                    progress.update(
                        task,
                        advance=1,
                        description=f"[magenta]Adding to Lidarr... ({artist_name[:40]})",
                    )

            console.print(
                f"[green]✓[/green] Lidarr: {added} artists added/existing, {failed} failed",
                style="bold",
            )
            console.print()

    # Final success message
    console.print(
        Panel.fit(
            "[bold green]✓ Artist Scraper completed successfully![/bold green]",
            border_style="green",
        )
    )


@app.command(name="import")
def import_csv(
    csv_file: str = typer.Argument(..., help="Path to CSV file containing artists"),
    config_file: str = typer.Option(
        "config.json", "--config", "-c", help="Path to configuration file"
    ),
    min_plays: Optional[int] = typer.Option(
        None, "--min-plays", help="Only import artists with at least this many plays"
    ),
    verbose: bool = typer.Option(
        False, "--verbose", "-v", help="Enable verbose output"
    ),
) -> None:
    """Import artists from CSV and add them to Lidarr."""

    # Configure logging based on verbose flag
    if verbose:
        logging.basicConfig(
            level=logging.DEBUG,
            format="%(name)s - %(message)s",
            handlers=[RichHandler(console=console, show_time=False, show_path=False)],
        )
        logging.getLogger("artistscraper").setLevel(logging.DEBUG)
    else:
        logging.basicConfig(
            level=logging.WARNING,
            format="%(message)s",
            handlers=[RichHandler(console=console, show_time=False, show_path=False)],
        )

    console.print(
        Panel.fit(
            "[bold magenta]Artist Scraper - Import to Lidarr[/bold magenta]\n"
            "Import artists from CSV to Lidarr",
            border_style="magenta",
        )
    )
    console.print()

    # Load configuration
    try:
        config = Config(config_file)
        console.print(
            "[green]✓[/green] Configuration loaded successfully", style="bold"
        )
    except FileNotFoundError as e:
        console.print(f"[red]✗[/red] {e}", style="bold")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"[red]✗[/red] Error loading configuration: {e}", style="bold")
        raise typer.Exit(1)

    console.print()

    # Read CSV file
    csv_path = Path(csv_file)

    if not csv_path.exists():
        console.print(f"[red]✗[/red] CSV file not found: {csv_file}", style="bold")
        raise typer.Exit(1)

    artists_to_add = {}
    total_in_csv = 0
    filtered_out = 0

    try:
        with open(csv_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)

            # Check if required columns exist
            if (
                reader.fieldnames is None
                or "Artist Name" not in reader.fieldnames
                or "MusicBrainz ID" not in reader.fieldnames
            ):
                console.print(
                    "[red]✗[/red] CSV must have 'Artist Name' and 'MusicBrainz ID' columns",
                    style="bold",
                )
                raise typer.Exit(1)

            # Check if Play Count column exists when filtering is requested
            has_play_count = (
                reader.fieldnames is not None and "Play Count" in reader.fieldnames
            )
            if min_plays is not None and not has_play_count:
                console.print(
                    "[red]✗[/red] CSV must have 'Play Count' column when using --min-plays filter",
                    style="bold",
                )
                raise typer.Exit(1)

            for row in reader:
                artist_name = row["Artist Name"]
                mb_id = row["MusicBrainz ID"]

                if artist_name and mb_id:
                    total_in_csv += 1

                    # Check play count filter if specified
                    if min_plays is not None:
                        try:
                            play_count = int(row.get("Play Count", 0))
                            if play_count < min_plays:
                                filtered_out += 1
                                if verbose:
                                    console.print(
                                        f"[dim]Filtered out: {artist_name} ({play_count} plays < {min_plays})[/dim]"
                                    )
                                continue
                        except (ValueError, TypeError):
                            # If play count is invalid, skip this artist
                            filtered_out += 1
                            if verbose:
                                console.print(
                                    f"[dim]Filtered out: {artist_name} (invalid play count)[/dim]"
                                )
                            continue

                    # Remove 'lidarr:' prefix if present
                    mb_id_clean = mb_id.replace("lidarr:", "")
                    artists_to_add[artist_name] = mb_id_clean

        if min_plays is not None:
            console.print(
                f"[green]✓[/green] Loaded {len(artists_to_add)} artists from CSV (filtered out {filtered_out} with < {min_plays} plays)",
                style="bold",
            )
        else:
            console.print(
                f"[green]✓[/green] Loaded {len(artists_to_add)} artists from CSV",
                style="bold",
            )

    except Exception as e:
        console.print(f"[red]✗[/red] Error reading CSV file: {e}", style="bold")
        raise typer.Exit(1)

    if not artists_to_add:
        console.print(
            "[yellow]⚠[/yellow]  No artists with MusicBrainz IDs found in CSV",
            style="bold",
        )
        raise typer.Exit(0)

    console.print()

    # Connect to Lidarr
    console.print(
        Panel(
            "[bold magenta]Adding artists to Lidarr[/bold magenta]",
            border_style="magenta",
        )
    )
    console.print()

    lidarr_client = LidarrClient(config.lidarr_url, config.lidarr_api_key)

    with console.status("[magenta]Connecting to Lidarr...", spinner="dots"):
        if not lidarr_client.test_connection():
            console.print("[red]✗[/red] Failed to connect to Lidarr", style="bold")
            raise typer.Exit(1)

    console.print("[green]✓[/green] Connected to Lidarr", style="bold")
    console.print()

    # Add artists to Lidarr
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TaskProgressColumn(),
        console=console,
    ) as progress:

        task = progress.add_task(
            "[magenta]Adding artists to Lidarr...", total=len(artists_to_add)
        )

        added = 0
        already_exists = 0
        failed = 0

        for artist_name, mb_id in sorted(artists_to_add.items()):
            if lidarr_client.artist_exists(mb_id):
                already_exists += 1
            else:
                artist_search_data = lidarr_client.search_artist(mb_id)
                if artist_search_data:
                    root_folders = lidarr_client.get_root_folders()
                    quality_profiles = lidarr_client.get_quality_profiles()
                    metadata_profiles = lidarr_client.get_metadata_profiles()

                    if root_folders and quality_profiles and metadata_profiles:
                        if lidarr_client.add_artist(
                            artist_search_data,
                            root_folders[0]["path"],
                            quality_profiles[0]["id"],
                            metadata_profiles[0]["id"],
                            monitored=True,
                            search_for_missing=False,
                        ):
                            added += 1
                        else:
                            failed += 1
                            if verbose:
                                console.print(
                                    f"[red]✗[/red] Failed to add: {artist_name}",
                                    style="dim",
                                )
                    else:
                        failed += 1
                        if verbose:
                            console.print(
                                f"[red]✗[/red] Missing Lidarr configuration for: {artist_name}",
                                style="dim",
                            )
                else:
                    failed += 1
                    if verbose:
                        console.print(
                            f"[red]✗[/red] Not found in Lidarr: {artist_name}",
                            style="dim",
                        )

            progress.update(
                task,
                advance=1,
                description=f"[magenta]Adding to Lidarr... ({artist_name[:40]})",
            )

    console.print()
    console.print(f"[green]✓[/green] Added: {added} artists", style="bold")
    console.print(
        f"[cyan]ℹ[/cyan] Already exists: {already_exists} artists", style="bold"
    )
    if failed > 0:
        console.print(f"[red]✗[/red] Failed: {failed} artists", style="bold")

    console.print()

    # Create summary table
    summary_table = Table(
        title="Import Summary", show_header=True, header_style="bold magenta"
    )
    summary_table.add_column("Metric", style="magenta")
    summary_table.add_column("Count", justify="right", style="green")

    if min_plays is not None:
        summary_table.add_row("Total in CSV", str(total_in_csv))
        summary_table.add_row(
            "Filtered out (< {} plays)".format(min_plays),
            str(filtered_out),
            style="yellow",
        )
        summary_table.add_row("After filtering", str(len(artists_to_add)))
    else:
        summary_table.add_row("Total in CSV", str(len(artists_to_add)))

    summary_table.add_row("Added to Lidarr", str(added))
    summary_table.add_row("Already in Lidarr", str(already_exists))
    if failed > 0:
        summary_table.add_row("Failed", str(failed), style="red")

    console.print(summary_table)
    console.print()

    # Final success message
    console.print(
        Panel.fit("[bold green]✓ Import completed![/bold green]", border_style="green")
    )


@app.command(name="print-config")
def print_config() -> None:
    """Print example configuration to stdout."""
    print(json.dumps(EXAMPLE_CONFIG, indent=2))


def cli_main():
    """Entry point for the CLI."""
    try:
        app()
    except KeyboardInterrupt:
        console.print("\n[yellow]⚠[/yellow]  Operation cancelled by user", style="bold")
        sys.exit(130)
    except Exception as e:
        console.print(f"\n[red]✗[/red] Unexpected error: {e}", style="bold")
        sys.exit(1)


if __name__ == "__main__":
    cli_main()
