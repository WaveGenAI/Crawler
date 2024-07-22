"""
Utils function
"""

import urllib.parse


def is_valid_url(url: str) -> bool:
    """Check if url is valid

    Args:
        url (str): the url to check

    Returns:
        bool: boolean that indicate if url is valid (true) or not
    """

    try:
        result = urllib.parse.urlparse(url)
        return all([result.scheme, result.netloc])
    except AttributeError:
        return False
