import json
import logging
import time
from concurrent.futures import ThreadPoolExecutor
from typing import Callable, Sequence

from pytubefix import Search

from ..models import Audio
from ..ytb_session import YtbSession
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

        self.logging = logging.getLogger(__name__)
        self._ytb_sessions = {
            time.time(): YtbSession(
                {"quiet": True, "noprogress": True, "no_warnings": True}, max_attemps=50
            )
            for _ in range(num_processes)
        }

        # Create a thread pool with max 10 threads
        self.executor = ThreadPoolExecutor(max_workers=num_processes)
        self.futures = set()

        self._search = Search(terms, {"params": "EgIwAQ%3D%3D"})
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

        # get the oldest session
        session = self._ytb_sessions.pop(min(self._ytb_sessions.keys()))
        # append a new session
        self._ytb_sessions[time.time()] = session

        try:
            info = session.extract_info(url, download=False)
        except Exception as e:
            logging.error("Error extracting info from %s: %s", url, e)
            return

        logging.info("Found music video: %s", info["title"])
        audio = Audio(
            url=url,
            title=info["title"],
            author=info["channel"] if "channel" in info else "",
            description=info["description"],
            tags=info["tags"],
        )

        self._callback(audio)
        self._videos.add(url)

    def crawl(self, *args, **kwargs) -> None:
        """Find and return URLs of Youtube videos based on search terms."""

        last_nbm_results = 0
        while len(self._search.videos) > last_nbm_results:
            for result in self._search.videos[last_nbm_results:]:
                url = f"{self.YOUTUBE_ENDPOINT}/watch?v={result.video_id}"
                future = self.executor.submit(self._get_ytb_data, url)
                self.futures.add(future)

                while len(self.futures) >= self._num_processes:
                    time.sleep(0.1)
                    self._manage_futures()

            last_nbm_results = len(self._search.videos)
            self._search.get_next_results()
