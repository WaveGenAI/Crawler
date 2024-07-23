"""
Utils function
"""

import json
import urllib.parse


def process(file_name: str) -> None:
    """Class to process the json generated file

    Args:
        file_name (str): the file name to process
    """

    with open(file_name, encoding="utf-8") as file:
        data = json.load(file)

    unique_urls = set()
    unique_data = []

    for item in data:
        url = item["url"]
        if url not in unique_urls:
            unique_urls.add(url)
            unique_data.append(item)

    audio_files_count = len(unique_data)
    print(f"Number of unique musics : {audio_files_count}")

    with open(file_name, "w", encoding="utf-8") as outfile:
        json.dump(unique_data, outfile, indent=4)


def is_valid_url(url: str) -> bool:
    """Check if url is valid

    Args:
        url (str): the url to check

    Returns:
        bool: boolean that indicate if url is valid (true) or not
    """

    try:
        result = urllib.parse.urlparse(url)
        invalid_ascii = any(char.isascii() and not char.isprintable() for char in url)
        return all([result.scheme, result.netloc, not (invalid_ascii)])
    except AttributeError:
        return False
