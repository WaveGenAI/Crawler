from multi_crawler import ArchiveCrawler, CSVExporter, Session, YoutubeCrawler
from multi_crawler.models import Audio

i = 0


def print_url(url: str, audio):
    global i
    i += 1
    print(url, i)


exporter = CSVExporter("results.csv", overwrite=True, *list(Audio.model_fields.keys()))
# crawlers = ArchiveCrawler("ultra-japanese-sound-collection", callback=print_url)
crawlers = YoutubeCrawler("phonk", callback=print_url, session=Session, process=False)

crawlers.crawl()
