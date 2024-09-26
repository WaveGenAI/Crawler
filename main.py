import argparse
import logging
import os

from dotenv import load_dotenv

from multi_crawler import (
    ArchiveCrawler,
    CSVExporter,
    Session,
    TorSession,
    YoutubeCrawler,
)

logging.basicConfig(level=logging.INFO)
load_dotenv(override=True)

if __name__ == "__main__":
    argparser = argparse.ArgumentParser(
        prog="multi_crawler",
        description="Utility to crawl audio files from the internet using webarhive.org and youtube.com",
    )
    argparser.add_argument(
        "--input",
        type=str,
        required=True,
        help="Input file with search terms from youtube or collection name from archive.org",
    )
    argparser.add_argument(
        "--csv",
        required=True,
        action="store_true",
        help="Output file in CSV format",
    )
    argparser.add_argument(
        "--overwrite",
        action="store_true",
        help="Overwrite the csv file if it exists",
    )
    argparser.add_argument(
        "--file_name",
        type=str,
        help="Name of the output file",
        required=False,
    )
    argparser.add_argument(
        "--tor_proxy",
        action="store_true",
        help="Use Tor proxy to make requests on youtube",
        default=False,
    )

    args = argparser.parse_args()

    if args.csv and args.file_name is None:
        raise ValueError("Please provide the name of the output file using --file_name")

    exporter = CSVExporter(args.file_name, overwrite=args.overwrite)

    with open(args.input, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            logging.info("Processing line: %s", line)

            session = (
                TorSession(os.getenv("TOR_PASSWORD")) if args.tor_proxy else Session()
            )
            if line.startswith("youtube:"):
                crawlers = YoutubeCrawler(
                    line.split(" ", 1)[1],
                    callback=exporter,
                    session=session,
                )
            else:
                crawlers = ArchiveCrawler(line.split(" ", 1)[1], callback=exporter)
            crawlers.crawl()
