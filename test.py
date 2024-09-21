from multi_crawler import ArchiveCrawler, CSVExporter, Session, YoutubeCrawler

i = 0


def print_url(url: str, **kwargs):
    global i
    i += 1
    print(url, i, kwargs.get("title"))


exporter = CSVExporter("results.csv", "URL", overwrite=True)
crawlers = ArchiveCrawler("ultra-japanese-sound-collection", callback=print_url)
# crawlers = YoutubeCrawler("phonk", callback=exporter, session=Session)

crawlers.crawl()
