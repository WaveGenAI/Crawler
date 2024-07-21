""" 
Scraper module for making requests to the web
"""

from requests_html import AsyncHTMLSession
from typing import List, Callable


class WebScraper:
    """Scraper class for making requests to the web"""

    def __init__(self):
        self._asession = AsyncHTMLSession()

    async def get(self, url: List[str], callback: Callable = None) -> List:
        """Make a get request to the web

        Args:
            url (List[str]): a list of urls to make requests to
            callback (Callable, optional): a callback function to process the results. Defaults to None.

        Returns:
            List: a list of results
        """
        results = await self._asession.run(url)

        out = []
        for r in results:
            out.append(callback(r) if callback else r)

        return out
