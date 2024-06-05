from pathlib import Path

import scrapy


class AudiosSpider(scrapy.Spider):
    name = "audios"
    start_urls = []

    def parse(self, response):
        pass
