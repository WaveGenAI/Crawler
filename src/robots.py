""" 
Class to respect robot.txt file
"""

import urllib.parse

import aiohttp
from protego import Protego


class RobotTXT:
    """Class to respect robot.txt file"""

    def __init__(self):
        self._robots = {}
        self._user_agent = ["*", "GPTBot", "WaveAICrawler"]

    async def __call__(self, url: str) -> bool:
        """Check if the url is allowed to be crawled

        Args:
            url (str): url to be checked

        Returns:
            bool: True if the url is allowed to be crawled, False otherwise
        """

        url_parse = urllib.parse.urlparse(url)
        robots_url = f"{url_parse.scheme}://{url_parse.netloc}/robots.txt"

        if robots_url not in self._robots:
            async with aiohttp.ClientSession() as session:
                async with session.get(robots_url) as response:
                    robots_content = await response.text()
                    self._robots[robots_url] = Protego.parse(robots_content)

        authorize = []
        for agent in self._user_agent:
            authorize.append(self._robots[robots_url].can_fetch(url, agent))

        if len(self._robots) > 1000:
            self._robots.popitem(last=False)

        return all(authorize)
