""" 
This module contains the CSVExporter class, which is used to export 
the results of the crawler to a CSV file.
"""

import csv
import os
from typing import Any

from ..models import Audio


class CSVExporter:
    """Class to export the results of the crawler to a CSV file."""

    def __init__(self, filename: str, overwrite: bool = False):
        self._filename = filename
        self._columns = list(Audio.model_fields.keys())

        # Write the columns to the CSV file
        if overwrite or not os.path.exists(self._filename):
            with open(self._filename, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(self._columns)

    def _clean_value(self, value: Any) -> Any:
        """Method to clean the value before writing it to the CSV file.

        Args:
            value (Any): the value to clean

        Returns:
            Any: the cleaned value
        """

        if isinstance(value, str):
            return value.replace("\n", " ")

        if isinstance(value, list):
            value = ", ".join(value)
            value = value.replace("\n", " ")

        return value

    def __call__(self, audio: Audio):
        """Write the information of the audio to the CSV file.

        Args:
            audio (Audio): the audio object to write to the CSV file
        """

        with open(self._filename, "a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)

            # Write the values of the audio object to the CSV file
            writer.writerow(
                [
                    (
                        ""
                        if getattr(audio, field) is None
                        else self._clean_value(getattr(audio, field))
                    )
                    for field in self._columns
                ]
            )
