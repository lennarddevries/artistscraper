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

    def export(self, artist_data: Dict[str, Dict[str, Optional[str]]]) -> tuple[int, int]:
        """Export artist data to CSV and log skipped artists.

        Args:
            artist_data: Dictionary mapping artist names to dict with 'mb_id' and 'source'

        Returns:
            Tuple of (exported_count, skipped_count)
        """
        exported_artists = []
        skipped_artists = []

        # Separate artists with and without MusicBrainz IDs
        for artist_name, data in sorted(artist_data.items()):
            mb_id = data.get('mb_id') if isinstance(data, dict) else data
            source = data.get('source', 'Unknown') if isinstance(data, dict) else 'Unknown'

            if mb_id:
                exported_artists.append((artist_name, mb_id, source))
            else:
                skipped_artists.append(artist_name)

        # Write CSV file
        try:
            logger.info(f"Writing {len(exported_artists)} artists to {self.csv_file}")

            with open(self.csv_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                # Write header
                writer.writerow(['Artist Name', 'MusicBrainz ID', 'Source'])

                # Write artist data
                for artist_name, mb_id, source in exported_artists:
                    writer.writerow([artist_name, mb_id, source])

            logger.info(f"Successfully exported {len(exported_artists)} artists to {self.csv_file}")

        except Exception as e:
            logger.error(f"Error writing CSV file: {e}")
            raise

        # Write skipped artists log
        if skipped_artists:
            try:
                logger.info(f"Writing {len(skipped_artists)} skipped artists to {self.skipped_log}")

                with open(self.skipped_log, 'w', encoding='utf-8') as f:
                    f.write("# Artists without MusicBrainz IDs\n")
                    f.write(f"# Total: {len(skipped_artists)}\n\n")

                    for artist_name in sorted(skipped_artists):
                        f.write(f"{artist_name}\n")

                logger.info(f"Successfully logged {len(skipped_artists)} skipped artists to {self.skipped_log}")

            except Exception as e:
                logger.error(f"Error writing skipped artists log: {e}")
                # Don't raise, this is less critical than the CSV export

        return len(exported_artists), len(skipped_artists)
