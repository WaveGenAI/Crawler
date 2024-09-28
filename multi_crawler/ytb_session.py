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

        self.params["proxy"] = "127.0.0.1:3128"
        self.ytdl = yt_dlp.YoutubeDL(self.params, **self.kwargs)

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
        except DownloadError as e:
            if (
                "sign in" in str(e).lower()
                or "failed to extract any player response" in str(e).lower()
            ):
                logging.warning(
                    "DownloadError in %s, reinitializing with new proxy...", method_name
                )
                return self._handle_download_error(method_name, *args, **kwargs)
            raise e

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
