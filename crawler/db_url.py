"""
A module to store the list of url visited by the crawler
"""

from typing import List, Union
import redis


class DBUrl:
    """
    A class to store the list of url visited by the crawler
    """

    def __init__(
        self, host: str = "localhost", port: int = 6379, reset_db: bool = False
    ):
        """Initialize the redis connection to store the list of url visited by the crawler

        Args:
            host (str, optional): the host url. Defaults to "localhost".
            port (int, optional): the port of the database. Defaults to 6379.
            reset_db (bool, optional): if True, reset the database. Defaults to False.
        """

        self.redis = redis.Redis(host=host, port=port)

        if reset_db:
            self.redis.delete("urls")

    def add_url(self, url: Union[str, List[str]]):
        """Add a url to the list of visited urls

        Args:
            url (Union[str, List[str]]): the url to add
        """

        if isinstance(url, list):
            for u in url:
                self.redis.sadd("urls", u)
        else:
            self.redis.sadd("urls", url)

    def is_url_visited(self, url: Union[str, List[str]]) -> bool:
        """Check if a url is already visited

        Args:
            url (Union[str, List[str]]): the url to check

        Returns:
            bool: True if the url is already visited, False otherwise
        """

        if isinstance(url, list):
            return all(self.redis.sismember("urls", u) for u in url)
        return self.redis.sismember("urls", url)

    def filter_url(self, url: Union[str, List[str]]) -> list:
        """Filter the list of url to keep only the non visited ones

        Args:
            url (Union[str, List[str]]): the list of url to filter

        Returns:
            list: the list of non visited url
        """

        if isinstance(url, list):
            return [u for u in url if not self.redis.sismember("urls", u)]
        return url if not self.redis.sismember("urls", url) else []
