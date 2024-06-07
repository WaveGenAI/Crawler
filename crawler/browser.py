"""
A module to manage the playwright browser in an asyncio context
"""

import asyncio
import typing

from playwright.async_api import async_playwright
from crawler.data import Page


class Browser:
    def __init__(self, callback: typing.Callable):
        """Initialize the browser

        Args:
            callback (typing.Callable): a function to call when a page is loaded
        """

        self._browser = None
        self._callback = callback
        self._asyncio_loop = (
            asyncio.new_event_loop()
        )  # set the event loop that will be used by the browser
        asyncio.set_event_loop(self._asyncio_loop)

        self._asyncio_loop.run_until_complete(self._launch())
        self._tasks = []  # Store the tasks to close them later

    async def _launch(self):
        """Launch the browser"""

        self._playwright = (
            await async_playwright().__aenter__()
        )  # just like the `with function` but in async (called manually)

        self._browser = await self._playwright.chromium.launch()

    async def _close(self):
        """Close the browser and playwright"""
        if self._browser is not None:
            await self._browser.close()

    @property
    def queue_size(self):
        """Get the size of the queue"""
        return len(self._tasks)

    async def _get_content(self, url: str):
        """Get the content of a page

        Args:
            url (str): the url to load

        Returns:
            str: the content of the page
        """

        page = await self._browser.new_page()
        await page.goto(url)

        # Wait for the page to load
        await page.wait_for_load_state("domcontentloaded")

        content = await page.content()
        await page.close()

        page = Page(url, content)
        self._callback(page)

    def get(self, url: str):
        """Load a page in the browser

        Args:
            url (str): the url to load
        """

        loop = self._asyncio_loop
        task = loop.create_task(self._get_content(url))
        self._tasks.append(task)

        self._tasks = [task for task in self._tasks if not task.done()]

    def close(self):
        """Close the browser and the asyncio loop"""

        asyncio.set_event_loop(self._asyncio_loop)
        loop = self._asyncio_loop

        loop.run_until_complete(asyncio.gather(*self._tasks))
        loop.run_until_complete(self._close())

        loop.close()
