""" 
Class to respect robot.txt file
"""

import asyncio
import logging
import urllib.parse

import aiohttp
from protego import Protego


class RobotTXT:
    """Class to respect robot.txt file"""

    def __init__(self):
        self._robots = {}
        self._user_agent = ["*", "GPTBot", "WaveAICrawler"]

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
                async with aiohttp.ClientSession() as session:
                    async with session.get(robots_url) as response:
                        robots_content = await response.text()
                        self._robots[robots_url] = Protego.parse(robots_content)
            except (
                aiohttp.ClientError,
                asyncio.exceptions.CancelledError,
                asyncio.exceptions.TimeoutError,
            ):
                self._robots[robots_url] = Protego.parse("User-agent: *\nDisallow: /")

        authorize = []
        for agent in self._user_agent:
            authorize.append(self._robots[robots_url].can_fetch(url, agent))

        if len(self._robots) > 1000:
            older_keys = list(self._robots.keys())[-1]
            self._robots.pop(older_keys)

            if log is not None:
                log.info(f"Removing robots.txt for {robots_url}")

        return all(authorize)
