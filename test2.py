import re

import requests

s = requests.Session()
r = s.get("https://www.youtube.com/watch?v=o1A5hQZyuC4")


def _get_description(content):
    description_match = re.search(
        r'attributedDescription":\{"content":"((?:[^"\\]|\\.)*?)"',
        content,
        re.DOTALL,
    )

    descr = ""
    if description_match:
        descr = description_match.group(1)

    return descr


print(_get_description(r.text))
