""" 
Archive net downloader
"""

import internetarchive


class ArchiveDownloader:
    """Class to download mp3 files from archive.org"""

    BASE_URL = "https://archive.org/download/"

    def __init__(self, output_file: str = "musics.txt"):
        """Initialize the downloader

        Args:
            output_file (str, optional): the file to export urls. Defaults to "musics.txt".
        """

        self.urls = []
        self.output_file = output_file

    def append_item(self, item_id: str) -> None:
        """Get mp3 files from an item

        Args:
            item_id (str): the item id
        """
        item = internetarchive.get_item(item_id)
        for file in item.files:
            if "mp3" in file["format"].lower():
                url = f"{self.BASE_URL}{item.identifier}/{file['name']}"
                self.urls.append(url)

        self.export_urls()

    def search_and_extract_ids(self, ids: list) -> None:
        """Search and extract ids

        Args:
            ids (list): a list of collections ids
        """

        for item_id in ids:
            search = internetarchive.search_items(f"collection:{item_id}")

            if len(search) == 0:
                self.append_item(item_id)
            else:
                for result in search:
                    item = result["identifier"]
                    self.append_item(item)

    def export_urls(self) -> None:
        """Export urls to a txt file

        Args:
            filename (str): name of the file to export to
        """
        with open(self.output_file, "a", encoding="utf-8") as f:
            for url in self.urls:
                f.write(f"{url}\n")

        self.urls = []

    @staticmethod
    def load_id_from_files(path: str) -> list:
        """Load id from a file

        Args:
            path (str): path to the file

        Returns:
            list: list of ids
        """
        with open(path, "r", encoding="utf-8") as f:
            return [
                line.replace("https://archive.org/details/", "").strip() for line in f
            ]
