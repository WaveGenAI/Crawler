""" 
Archive net downloader
"""

from typing import Callable

import internetarchive

from .crawlers import BaseCrawler


class ArchiveCrawler(BaseCrawler):
    """Class to find and return URLs of audio files from the Archive.org website."""

    BASE_URL = "https://archive.org/download/"

    def __init__(self, collection: str, callback: Callable):
        """Initialize the ArchiveDownloader object.

        Args:
            collection (str): the collections to search for mp3 files
            callback (Callable): the function to call with the URLs of the audio files
        """

        self._callback = callback
        self._collection = collection

    def _find_url(self, item_id: str) -> None:
        """Get mp3 files from an item

        Args:
            item_id (str): the item id
        """
        item = internetarchive.get_item(item_id)

        for file in item.files:
            if "mp3" in file["format"].lower():
                url = f"{self.BASE_URL}{item.identifier}/{file['name']}"

                subject = item.metadata.get("subject", [])
                if isinstance(subject, str):
                    subject = [subject]

                metadata = {}

                if "title" in item.metadata:
                    metadata["title"] = item.metadata["title"]

                if "album" in item.metadata:
                    metadata["album"] = item.metadata["album"]

                if "genre" in item.metadata:
                    metadata["genre"] = item.metadata["genre"]

                if len(subject) > 0:
                    metadata["keywords"] = ", ".join(subject)

                self._callback(url, **metadata)

    def crawl(self) -> None:
        """Search and extract ids"""

        search = internetarchive.search_items(f"collection:{self._collection}")

        if len(search) == 0:
            self._find_url(self._collection)
        else:
            for result in search:
                collection_id = result["identifier"]
                self._find_url(collection_id)
