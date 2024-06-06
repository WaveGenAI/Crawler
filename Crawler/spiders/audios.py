import re

import scrapy


class AudiosSpider(scrapy.Spider):
    name = "audios"
    start_urls = "https://musicforprogramming.net/seventy"
    match_audio_ext = (".mp3", ".ogg", ".wav", ".flac")

    def start_requests(self):
        yield scrapy.Request(
            self.start_urls,
            callback=self.parse,
            meta={
                "playwright": True,
                "playwright_include_page": True,
                "playwright_page_goto_kwargs": {
                    "wait_until": "networkidle",
                },
            },
        )

    async def get_links(self, response):
        page = response.meta["playwright_page"]
        links = await page.query_selector_all("a")

        full_links = []
        for link in links:
            link = await link.get_attribute("href")

            regex = re.compile(r".+(:\/\/)")
            if not regex.match(link):
                link = response.urljoin(link)

            full_links.append(link)

        return full_links

    async def parse(self, response):
        links = await self.get_links(response)

        for link in links:
            if link.endswith(self.match_audio_ext):
                yield {
                    "link": link,
                }

        for link in links:
            yield scrapy.Request(
                link,
                callback=self.parse,
                meta={
                    "playwright": True,
                    "playwright_include_page": True,
                    "playwright_page_goto_kwargs": {
                        "wait_until": "networkidle",
                    },
                },
            )
