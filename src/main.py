import asyncio

from crawlee.playwright_crawler import PlaywrightCrawler
from crawlee.beautifulsoup_crawler import BeautifulSoupCrawler

from routes import router


async def main() -> None:
    crawler = BeautifulSoupCrawler(
        request_handler=router,
    )

    await crawler.run(
        ["https://freemusicarchive.org/member/meghan-admin/meet-the-exploding-pea-mix/"]
    )


if __name__ == "__main__":
    asyncio.run(main())