"""
This script is used to download the music files from the web archive.
"""

import argparse

from src.webarchive import ArchiveDownloader

argparser = argparse.ArgumentParser()
argparser.add_argument("--input", type=str, required=False, default="collections.txt")
argparser.add_argument("--output", type=str, required=False, default="musics.xml")
args = argparser.parse_args()

downloader = ArchiveDownloader(args.output)
ids = downloader.load_id_from_files(args.input)
downloader.search_and_extract_ids(ids)
