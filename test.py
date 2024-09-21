import os

from dotenv import load_dotenv

from multi_crawler import Session, YoutubeCrawler

load_dotenv(override=True)

terms = "phonk"
i = 0


def print_url(url: str):
    global i
    i += 1
    print(url, i)


crawlers = YoutubeCrawler(terms=terms, callback=print_url, session=Session)

crawlers.crawl(nb_results=float("inf"))
