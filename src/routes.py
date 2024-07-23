""" 
Route for the crawler
"""

import re
import urllib.parse

from crawlee.basic_crawler import Router
from crawlee.beautifulsoup_crawler import BeautifulSoupCrawlingContext

from filter import Filter
from robots import RobotTXT
from utils import is_valid_url

router = Router[BeautifulSoupCrawlingContext]()
robots_parser = RobotTXT()
filter_domain = Filter()
REGEX = r"(https?:)?(\/\/)?(www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()!@:%_\+.~#?&\/\/=]*)\.(mp3|wav|ogg)"


@router.default_handler
async def default_handler(context: BeautifulSoupCrawlingContext) -> None:
    """Default handler where the result of each page is submit

    Args:
        context (BeautifulSoupCrawlingContext): the context of the crawler
    """

    url = context.request.url

    authorized = await robots_parser(
        url, context.log
    )  # get if robots.txt allow the crawl
    if not authorized:
        return

    context.log.info(f"Processing page: {url}")

    filter_domain.increment_domain(url)

    html_page = str(context.soup).replace(r"\/", "/")

    matches = re.finditer(REGEX, html_page)

    # get all audios links
    audio_links = [html_page[match.start() : match.end()] for match in matches]

    for link in audio_links:
        if link.startswith("//"):
            link = "https:" + link
        else:
            link = urllib.parse.urljoin(url, link)

        data = {"url": link, "src": url}

        context.log.info(f"Found audio link: {link}")
        await context.push_data(data)  # save the links
        filter_domain.valid_domain(url)  # reset the counter of the domain

    # check if keywords music, audio, sound are in the page
    keywords = ["music", "audio", "sound", "song", "artist"]
    text = context.soup.get_text(separator=" ", strip=True)

    if any(
        keyword in text.lower() for keyword in keywords
    ) and filter_domain.check_domain(url):
        requests = []

        nbm_links = 0  # limit the number of links added by a unique page
        for link in context.soup.select("a"):
            if nbm_links > 100:
                break

            if link.attrs.get("href") is not None:
                url = urllib.parse.urljoin(
                    context.request.url, link.attrs.get("href")
                ).strip()

                if not is_valid_url(url):
                    continue

                authorized = await robots_parser(
                    url, context.log, do_req=False
                )  # get if robots.txt allow the crawl
                if authorized or authorized is None:
                    requests.append(url)
                    nbm_links += 1

        await context.add_requests(requests)
