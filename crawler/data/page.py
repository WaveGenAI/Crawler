from dataclasses import dataclass


@dataclass
class Page:
    """
    Class that represents a web page.
    """

    url: str
    content: str
