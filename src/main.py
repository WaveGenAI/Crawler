"""
main script for the crawler
"""

import asyncio

from crawlee.beautifulsoup_crawler import BeautifulSoupCrawler

from routes import router
from utils import process
import argparse

parser = argparse.ArgumentParser(description="Crawl the web to find audio files")

parser.add_argument(
    "-o",
    "--output",
    type=str,
    default="results.json",
    help="output file name",
)

parser.add_argument(
    "-m",
    "--max_requests",
    type=int,
    default=1_000_000,
    help="maximum number of requests per crawl",
)

parser.add_argument(
    "-u",
    "--urls",
    type=str,
    nargs="+",
    default=["https://freemusicarchive.org"],
    help="list of urls to start the crawl",
)
args = parser.parse_args()


async def main() -> None:
    """
    Function to launch the crawler
    """

    crawler = BeautifulSoupCrawler(
        request_handler=router, max_requests_per_crawl=args.max_requests
    )

    await crawler.run(args.urls)
    await crawler.export_data(args.output)
    process(args.output)


if __name__ == "__main__":
    asyncio.run(main())
