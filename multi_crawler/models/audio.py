from typing import List

from pydantic import BaseModel


class Audio(BaseModel):
    """
    Audio model
    """

    url: str
    title: str = None
    author: str = None
    description: str = None
    genre: str = None
    album: str = None
    tags: List[str] = None
