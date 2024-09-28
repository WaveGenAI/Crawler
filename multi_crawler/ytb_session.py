""" 
Wrapper for downloading videos from Youtube using Tor as a proxy.
"""

import logging
import random
from typing import Any

import yt_dlp
from yt_dlp.utils import DownloadError


class YtbSession:
    """Wrapper class for YoutubeDL that uses Tor as a proxy."""

    def __init__(self, params: dict = None, **kwargs):
        """Initializes the TorWrapper with optional parameters.

        Args:
            params (dict, optional): Optional parameters for YoutubeDL. Defaults to None.

        """
        self.params = params if params is not None else {}
        self.kwargs = kwargs
        self._init_ytdl()

    def _gen_proxy(self) -> str:
        """Generates a random proxy string using Tor."""
        creds = str(random.randint(10000, 10**9)) + ":" + "foobar"
        return f"socks5://{creds}@127.0.0.1:9050"

    def _init_ytdl(self):
        """Initializes or reinitializes the YoutubeDL instance with a new proxy."""
        # Set a new proxy for each initialization
        self.params["proxy"] = self._gen_proxy()
        self.ytdl = yt_dlp.YoutubeDL(self.params, **self.kwargs)
        logging.info("Initialized YoutubeDL with proxy %s", self.params["proxy"])

    def _handle_download_error(self, method_name: str, *args, **kwargs) -> Any:
        """Handles DownloadError by reinitializing and retrying the method call.

        Args:
            method_name (str): The name of the method to call.

        Returns:
            any: The return value of the method call.
        """
        method = getattr(self.ytdl, method_name)
        try:
            return method(*args, **kwargs)
        except DownloadError:
            logging.warning(
                "DownloadError in %s, reinitializing with new proxy...", method_name
            )
            self._init_ytdl()
            return self._handle_download_error(method_name, *args, **kwargs)

    def extract_info(self, *args, **kwargs):
        """Extracts information and handles DownloadError by reinitializing YoutubeDL."""
        return self._handle_download_error("extract_info", *args, **kwargs)

    def download(self, *args, **kwargs):
        """Downloads a video and handles DownloadError by reinitializing YoutubeDL."""
        return self._handle_download_error("download", *args, **kwargs)

    def download_with_info_file(self, *args, **kwargs):
        """Downloads a video with an info file, handles DownloadError by reinitializing."""
        return self._handle_download_error("download_with_info_file", *args, **kwargs)

    def __getattr__(self, name: str) -> Any:
        """Redirects attribute access to the YoutubeDL instance.

        Args:
            name (str): The name of the attribute to access.

        Returns:
            any: The attribute value.
        """
        return getattr(self.ytdl, name)
