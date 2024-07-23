import logging
import urllib.parse

import aiohttp
from cachetools import LRUCache
from protego import Protego


class RobotTXT:
    """Class to respect robot.txt file"""

    def __init__(self, cache_size: int = 5000):
        self._robots = LRUCache(maxsize=cache_size)
        self._user_agent = ["gptbot", "waveaicrawler"]  # lower case

    async def _fetch_robots_txt(self, robots_url: str) -> Protego:
        """Fetch the robots.txt file

        Args:
            robots_url (str): url of the robots.txt file

        Returns:
            Protego: parser of the robots.txt file
        """

        async with aiohttp.ClientSession() as session:
            async with session.get(robots_url, timeout=5) as response:
                robots_content = await response.text()
                return Protego.parse(robots_content)

    async def __call__(self, url: str, log: logging.Logger = None) -> bool:
        """Check if the url is allowed to be crawled

        Args:
            url (str): url to be checked
            log (logging.Logger, optional): logger to log the result. Defaults to None.

        Returns:
            bool: True if the url is allowed to be crawled, False otherwise
        """

        url_parse = urllib.parse.urlparse(url)
        robots_url = f"{url_parse.scheme}://{url_parse.netloc}/robots.txt"

        if robots_url not in self._robots:
            if log is not None:
                log.info(f"Fetching robots.txt from {robots_url}")

            try:
                robots_parser = await self._fetch_robots_txt(robots_url)
                self._robots[robots_url] = robots_parser
            except Exception as e:  # pylint: disable=broad-except
                robots_parser = Protego.parse("User-agent: *\nDisallow: /")
                self._robots[robots_url] = robots_parser

                if log is not None:
                    log.error(f"Error fetching robots.txt from {robots_url}: {e}")

        robots_parser = self._robots[robots_url]
        authorize = robots_parser.can_fetch(url, "*")
        for agent in self._user_agent:
            if agent in robots_parser._user_agents:
                authorize = robots_parser.can_fetch(url, agent)

        return authorize
