""" 
This module contains the CSVExporter class, which is used to export 
the results of the crawler to a CSV file.
"""

import csv
import os
from typing import List


class CSVExporter:
    """Class to export the results of the crawler to a CSV file."""

    def __init__(self, filename: str, *columns: List[str], overwrite: bool = False):
        self._filename = filename
        self._columns = columns

        # Write the columns to the CSV file
        if overwrite or not os.path.exists(self._filename):
            with open(self._filename, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(columns)

    def __call__(self, *items: List[str]):
        """Add a URL to the CSV file.

        Args:
            items (List[str]): the items to add to the CSV file
        """

        with open(self._filename, "a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(items)
