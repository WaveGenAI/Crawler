"""
Filter class
"""

import urllib.parse


class Filter:
    """
    Class to filter the domain and avoid to crawl the same domain if it does not contain any song
    """

    def __init__(self, max_crawl: int = 20, cache_size: int = 500) -> None:
        """Class to filter the domain

        Args:
            max_crawl (int, optional): the maximum number of crawl before reject
            the url if no song is added. Defaults to 20.
            cache_size (int, optional): the cache size. Defaults to 500.
        """
        self._domains = {}
        self._cache_size = cache_size
        self._max_crawl = max_crawl

    def check_domain(self, url: str) -> bool:
        """Check if the domain is has not been visited more than max_crawl times and not songs are added

        Args:
            url (str): the url to check

        Returns:
            bool: True if the domain has not been visited more than max_crawl times, False otherwise
        """

        domain = urllib.parse.urlparse(url).netloc

        if len(self._domains) > self._cache_size:
            oldest_domain = list(self._domains.keys())[0]
            del self._domains[oldest_domain]

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
