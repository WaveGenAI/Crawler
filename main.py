from crawler import Crawler

crawler = Crawler(reset_db=True)
crawler.crawl(["https://example.com"])
crawler.close()
