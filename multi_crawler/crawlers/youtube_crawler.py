import http
import logging
import random
import time
from concurrent.futures import ThreadPoolExecutor
from typing import Callable, Sequence

import pytubefix.exceptions
from pytubefix import Search, YouTube

from ..models import Audio
from .crawlers import BaseCrawler


class YoutubeCrawler(BaseCrawler):
    """Class to find and return URLs of Youtube videos based on search terms."""

    YOUTUBE_ENDPOINT = "https://www.youtube.com"

    def __init__(
        self,
        terms: Sequence[str],
        callback: Callable,
        num_processes: int = 10,
    ):
        self._terms = terms
        self._callback = callback
        self._num_processes = num_processes
        self._terms = terms
        self.logging = logging.getLogger(__name__)

        # Create a thread pool with max 10 threads
        self.executor = ThreadPoolExecutor(max_workers=num_processes)
        self.futures = set()
        self._videos = set()

    def _manage_futures(self):
        """Helper function to clean up completed futures and maintain a max of 10 threads."""
        # Check if any threads have finished and remove them
        completed_futures = {fut for fut in self.futures if fut.done()}
        for fut in completed_futures:
            fut.result()
            self.futures.remove(fut)

    def _get_ytb_data(self, url):
        # check if the video has already been processed
        if url in self._videos:
            return

        success = False
        while not success:
            try:
                video = YouTube(
                    url,
                    proxies={
                        "http": "http://127.0.0.1:3128",
                        "https": "http://127.0.0.1:3128",
                    },
                )
                _ = video.title
                success = True
            except Exception as e:  # pylint: disable=broad-except
                if not isinstance(e, pytubefix.exceptions.BotDetection):
                    logging.error("Failed to get video data: %s", e)
                    return

        logging.info("Found music video: %s", video.title)
        audio = Audio(
            url=url,
            title=video.title,
            author=video.author,
            description=video.description,
            tags=video.keywords,
        )

        self._callback(audio)
        self._videos.add(url)

    def crawl(self, *args, **kwargs) -> None:
        """Find and return URLs of Youtube videos based on search terms."""

        success = False
        while not success:
            try:
                search = Search(self._terms, {"params": "EgIwAQ%3D%3D"})
                last_nbm_results = 0
                while len(search.videos) > last_nbm_results:
                    for result in search.videos[last_nbm_results:]:
                        url = f"{self.YOUTUBE_ENDPOINT}/watch?v={result.video_id}"
                        future = self.executor.submit(self._get_ytb_data, url)
                        self.futures.add(future)

                        while len(self.futures) >= self._num_processes:
                            time.sleep(0.1)
                            self._manage_futures()

                    last_nbm_results = len(search.videos)
                    search.get_next_results()
                success = True
            except Exception as e:
                logging.error("Failed to get search results: %s", e)
                time.sleep(5)
