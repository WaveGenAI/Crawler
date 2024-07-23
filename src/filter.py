"""
Filter class
"""

import urllib.parse
from cachetools import TTLCache


class Filter:
    """
    Class to filter the domain and avoid crawling the same domain if it does not contain any song
    """

    def __init__(
        self, max_crawl: int = 20, cache_size: int = 500, ttl: int = 600
    ) -> None:
        """Class to filter the domain

        Args:
            max_crawl (int, optional): the maximum number of crawl before reject
            the url if no song is added. Defaults to 20.
            cache_size (int, optional): the cache size. Defaults to 500.
            ttl (int, optional): time to live for cache items in seconds. Defaults to 600 (10 minutes).
        """
        self._max_crawl = max_crawl
        self._domains = TTLCache(maxsize=cache_size, ttl=ttl)

    def check_domain(self, url: str) -> bool:
        """Check if the domain has not been visited more than max_crawl times and no songs are added

        Args:
            url (str): the url to check

        Returns:
            bool: True if the domain has not been visited more than max_crawl times, False otherwise
        """
        domain = urllib.parse.urlparse(url).netloc

        if domain not in self._domains:
            self._domains[domain] = 1
        else:
            self._domains[domain] += 1

        return self._domains[domain] <= self._max_crawl

    def valid_domain(self, url: str) -> None:
        """Reset the counter of the domain

        Args:
            url (str): the url to check
        """
        domain = urllib.parse.urlparse(url).netloc
        self._domains[domain] = 0
