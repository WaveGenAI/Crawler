""" 
Route for the crawler
"""

import re
import urllib.parse

from crawlee.basic_crawler import Router
from crawlee.beautifulsoup_crawler import BeautifulSoupCrawlingContext

from robots import RobotTXT
from utils import is_valid_url

router = Router[BeautifulSoupCrawlingContext]()
robots_parser = RobotTXT()
regex = r"(https?:\/\/)?(www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()!@:%_\+.~#?&\/\/=]*)\.(mp3|wav|ogg)"


@router.default_handler
async def default_handler(context: BeautifulSoupCrawlingContext) -> None:
    """Default handler where the result of each page is submit

    Args:
        context (BeautifulSoupCrawlingContext): the context of the crawler
    """

    context.log.info(f"Processing page: {context.request.url}")

    url = context.request.url
    html_page = str(context.soup).replace(r"\/", "/")

    matches = re.finditer(regex, html_page)

    # get all audios links
    audio_links = [html_page[match.start() : match.end()] for match in matches]

    for link in audio_links:
        link = urllib.parse.urljoin(url, link)

        data = {"url": link, "src": url}

        context.log.info(f"Found audio link: {link}")
        await context.push_data(data)  # save the links

    # get all links in the page
    requests = []
    for link in context.soup.select("a"):
        if link.attrs.get("href") is not None:
            url = urllib.parse.urljoin(context.request.url, link.attrs.get("href"))

            if not is_valid_url(url):
                continue

            authorized = await robots_parser(
                url, context.log
            )  # get if robots.txt allow the crawl
            if authorized:
                url_trunk = url.split("?")[0].split("#")[0]

                requests.append(url_trunk)

    await context.add_requests(requests)
