"""
main script for the crawler
"""

import asyncio

from crawlee.beautifulsoup_crawler import BeautifulSoupCrawler

from routes import router
from utils import process


async def main() -> None:
    """
    Function to launch the crawler
    """

    crawler = BeautifulSoupCrawler(
        request_handler=router,
    )

    await crawler.run(["https://freemusicarchive.org"])
    await crawler.export_data("results.json")
    process("results.json")


if __name__ == "__main__":
    asyncio.run(main())
