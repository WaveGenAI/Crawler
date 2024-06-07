"""
A class to manage the crawling of a website
"""

import typing

from crawler.browser import Browser
from crawler.db_url import DBUrl
from crawler.data import Page


class Crawler:
    def __init__(self, reset_db: bool = False):
        self.browser = Browser(self._on_page_loaded)
        self.db_url = DBUrl(reset_db=reset_db)

    def _on_page_loaded(self, page: Page):
        """Callback called when a page is loaded

        Args:
            content (Page): the content of the page
        """

        print(page)

    def get(self, url: str):
        """Get the content of a page

        Args:
            url (str): the url to load
        """

        if not self.db_url.is_url_visited(url):
            self.db_url.add_url(url)
            self.browser.get(url)

    def crawl(self, start_url: typing.List[str]):
        """start crawling

        Args:
            start_url (typing.List[str]): the list of urls to start crawling
        """

        for url in start_url:
            self.get(url)

    def close(self):
        """
        Close the browser and the database and end the connection for the crawler
        """

        self.browser.close()
