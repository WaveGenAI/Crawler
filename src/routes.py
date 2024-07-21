import re
import urllib.parse

from crawlee.basic_crawler import Router
from crawlee.beautifulsoup_crawler import BeautifulSoupCrawlingContext
from crawlee.playwright_crawler import PlaywrightCrawlingContext

router = Router[PlaywrightCrawlingContext]()

regex = r"https?:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()!@:%_\+.~#?&\/\/=]*)\.(mp3|wav|ogg)"


@router.default_handler
async def default_handler(context: BeautifulSoupCrawlingContext) -> None:
    url = context.request.url
    html_page = str(context.soup).replace("\/", "/")

    matches = re.finditer(regex, html_page)

    audio_links = [html_page[match.start() : match.end()] for match in matches]

    for link in audio_links:
        link = urllib.parse.urljoin(url, link)

        data = {
            "url": link,
            "label": "audio",
        }

        await context.push_data(data)

    await context.enqueue_links(strategy="all")
