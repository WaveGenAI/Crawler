""" 
Base class for crawlers
"""

from abc import ABC, abstractmethod
from typing import Callable


class BaseCrawler(ABC):
    """Base class for crawlers."""

    @abstractmethod
    def crawl(self, *args, **kwargs) -> None:
        """
        Method to run the crawler
        """

    @abstractmethod
    def __init__(self, callback: Callable, *args, **kwargs):
        """Initialize the BaseCrawler object.

        Args:
            callback (Callable): the function to call with the URLs of the audio files
        """
        super().__init__()
