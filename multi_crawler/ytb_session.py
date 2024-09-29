import logging
import random
from typing import Any

import yt_dlp
from yt_dlp.utils import DownloadError

# create a logger for the module with the module name
logger = logging.getLogger(__name__)


class SilentLogger:
    """Silent logger class that does not log anything to avoid ram usage."""

    def debug(self, msg):
        pass

    def info(self, msg):
        pass

    def warning(self, msg):
        pass

    def error(self, msg):
        pass


class YtbSession:
    """Wrapper class for YoutubeDL that uses Tor as a proxy."""

    def __init__(self, params: dict = None, max_attemps: int = -1, **kwargs):
        """Initializes the TorWrapper with optional parameters.

        Args:
            params (dict, optional): Optional parameters for YoutubeDL. Defaults to None.
            max_attemps (int, optional): Maximum number of attempts to retry a failed download. Defaults to -1 (infinite).

        """
        self.params = params if params is not None else {}
        self.kwargs = kwargs
        self._max_attempts = max_attemps

        self.params["logger"] = SilentLogger()

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
        logger.info("Initialized YoutubeDL with proxy %s", self.params["proxy"])

    def _handle_download_error(self, method_name: str, *args, **kwargs) -> Any:
        """Handles DownloadError by reinitializing and retrying the method call in a loop.

        Args:
            method_name (str): The name of the method to call.

        Returns:
            any: The return value of the method call or raises the error if unrecoverable.
        """

        attempt = 0

        while attempt < self._max_attempts or self._max_attempts == -1:
            try:
                method = getattr(self.ytdl, method_name)
                return method(*args, **kwargs)
            except DownloadError as e:
                if (
                    "sign in" in str(e).lower()
                    or "failed to extract any player response" in str(e).lower()
                ):
                    logger.warning(
                        "DownloadError in %s, reinitializing with new proxy... Attempt %d",
                        method_name,
                        attempt + 1,
                    )
                    attempt += 1
                    self._init_ytdl()
                else:
                    raise e
        # If maximum attempts exceeded, raise DownloadError
        raise DownloadError(f"Failed after {attempt} attempts")

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
