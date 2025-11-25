"""CSV export functionality."""

import csv
import logging
from pathlib import Path
from typing import Dict, Optional

logger = logging.getLogger(__name__)


class CSVExporter:
    """Export artist data to CSV."""

    def __init__(self, csv_file: str, skipped_log: str):
        """Initialize CSV exporter.

        Args:
            csv_file: Path to output CSV file
            skipped_log: Path to skipped artists log file
        """
        self.csv_file = Path(csv_file)
        self.skipped_log = Path(skipped_log)
        self.csv_f = None
        self.skipped_f = None
        self.csv_writer = None
        self.exported_count = 0
        self.skipped_count = 0

    def __enter__(self):
        self.open()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def open(self):
        """Open files and write headers."""
        try:
            logger.info(f"Opening {self.csv_file} for writing")
            self.csv_f = open(self.csv_file, "w", newline="", encoding="utf-8")
            self.csv_writer = csv.writer(self.csv_f)
            self.csv_writer.writerow(
                ["Artist Name", "MusicBrainz ID", "Source", "Play Count"]
            )

            logger.info(f"Opening {self.skipped_log} for writing")
            self.skipped_f = open(self.skipped_log, "w", encoding="utf-8")
            self.skipped_f.write("# Artists without MusicBrainz IDs\n")

        except Exception as e:
            logger.error(f"Error opening files: {e}")
            raise

    def close(self):
        """Close files and log summary."""
        if self.csv_f:
            self.csv_f.close()
            logger.info(
                f"Successfully exported {self.exported_count} artists to {self.csv_file}"
            )
        if self.skipped_f:
            # Write total count at the end
            self.skipped_f.write(f"\n# Total: {self.skipped_count}\n")
            self.skipped_f.close()
            logger.info(
                f"Successfully logged {self.skipped_count} skipped artists to {self.skipped_log}"
            )

    def export_artist(self, artist_name: str, mb_id: str, source: str, play_count: int):
        """Write a single artist to the CSV file.

        Args:
            artist_name: Artist name
            mb_id: MusicBrainz ID
            source: Source of the artist data
            play_count: Play count for the artist
        """
        if self.csv_writer:
            self.csv_writer.writerow([artist_name, mb_id, source, play_count])
            self.exported_count += 1

    def log_skipped_artist(self, artist_name: str):
        """Write a single skipped artist to the log file.

        Args:
            artist_name: Artist name
        """
        if self.skipped_f:
            self.skipped_f.write(f"{artist_name}\n")
            self.skipped_count += 1
