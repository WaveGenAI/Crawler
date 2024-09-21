from multi_crawler import CSVExporter, Session, YoutubeCrawler


i = 0


def print_url(url: str):
    global i
    i += 1
    print(url, i)


exporter = CSVExporter("results.csv", "URL", overwrite=True)
crawlers = YoutubeCrawler("phonk", callback=exporter, session=Session)

crawlers.crawl()
