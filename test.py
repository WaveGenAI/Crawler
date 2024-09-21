from multi_crawler import ArchiveCrawler, CSVExporter, Session, YoutubeCrawler
from multi_crawler.models import Audio

exporter = CSVExporter("results.csv", overwrite=True, *list(Audio.model_fields.keys()))
# crawlers = ArchiveCrawler("ultra-japanese-sound-collection", callback=print_url)
crawlers = YoutubeCrawler("phonk", callback=exporter, session=Session)

crawlers.crawl()
