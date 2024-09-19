import os

from dotenv import load_dotenv

from multi_crawler import TorSession, YoutubeCrawler

load_dotenv(override=True)

terms = "music"
i = 0


def print_url(url: str):
    global i
    i += 1
    print(url, i)


crawlers = YoutubeCrawler(
    terms=terms, callback=print_url, session=TorSession(os.getenv("TOR_PSWD"))
)
crawlers.crawl(nb_results=10_000)
