import re
import urllib.parse
from typing import Any, Callable, Dict, List, Sequence

from ..models import Audio
from ..session import Session
from .crawlers import BaseCrawler


class YoutubeCrawler(BaseCrawler):
    """
    Find and return URLs of Youtube videos based on search terms.
    """

    YT_SEARCH_URL = "https://www.youtube.com/youtubei/v1/search?prettyPrint=false"

    def __init__(
        self,
        terms: Sequence[str],
        callback: Callable,
        session: Session = Session,
        process: bool = False,
    ):
        """Create a new YoutubeCrawler object.

        Args:
            terms (Sequence[str]): the search terms
            callback (Callable): the function to call with the URLs of the videos
            session (Session, optional): the session to use to create request. Defaults to Session.
            process (bool, optional): whether to get description of the video. Defaults to False.
        """
        self._terms = urllib.parse.quote(terms)
        self._callback = callback
        self._session = session
        self._process = process

    @staticmethod
    def _get_description(content: str) -> str:
        """Find and return the description of a Youtube video.

        Args:
            content (str): the content of the Youtube video page

        Returns:
            str: the description of the video
        """

        description_match = re.search(
            r'attributedDescription":\{"content":"((?:\\.|[^"\\])*)"',
            content,
            re.DOTALL,
        )

        descr = ""
        if description_match:
            descr = description_match.group(1)

        return descr

    @staticmethod
    def _get_contents(result: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Find and return the contents of a Youtube search result.

        Args:
            result (Dict[str, Any]): the result of a Youtube search

        Returns:
            List[Dict[str, Any]]: the contents of the search result
        """

        # Check if the result contains the contents
        if "contents" in result:
            return result["contents"]["twoColumnSearchResultsRenderer"][
                "primaryContents"
            ]["sectionListRenderer"]["contents"]
        elif "onResponseReceivedCommands" in result:
            return result["onResponseReceivedCommands"][0][
                "appendContinuationItemsAction"
            ]["continuationItems"]
        else:
            return []

    def crawl(self, nb_results: int = float("inf")) -> None:
        """Find and return URLs of Youtube videos based on search terms.

        Args:
            nb_results (int): the number of results to return, Defaults to float("inf").

        Raises:
            ValueError: if nb_results is less than 1
        """

        if nb_results < 1:
            raise ValueError("Number of results must be 1 or greater")

        headers = {"Content-Type": "application/json"}

        data = {
            "context": {
                "client": {
                    "hl": "en",
                    "gl": "US",
                    "clientName": "WEB",
                    "clientVersion": "2.20231121.08.00",
                }
            },
            "query": self._terms,
            "params": "EgIwAQ%3D%3D",  # Creative Commons filter
        }

        continuation_token = None
        results_found = 0

        while results_found < nb_results:
            if continuation_token:
                data["continuation"] = continuation_token
                data["query"] = None

            session = self._session()
            response = session().post(self.YT_SEARCH_URL, headers=headers, json=data)

            response.raise_for_status()
            result = response.json()

            contents = self._get_contents(result)

            # Get the contents of the search result
            for content in contents:
                if results_found >= nb_results:
                    break
                if "itemSectionRenderer" in content:
                    items = content["itemSectionRenderer"]["contents"]
                    for item in items:
                        # Check if there are no more results
                        if "messageRenderer" in item:
                            if (
                                item["messageRenderer"]["text"]["runs"][0][
                                    "text"
                                ].strip()
                                == "No more results"
                            ):
                                return

                        if results_found >= nb_results:
                            break

                        if "videoRenderer" in item:
                            video_id = item["videoRenderer"].get("videoId")
                            if video_id:
                                # Get the video information
                                video_renderer = item["videoRenderer"]
                                video_url = (
                                    f"https://www.youtube.com/watch?v={video_id}"
                                )

                                title = video_renderer["title"]["runs"][0]["text"]
                                channel_name = video_renderer["ownerText"]["runs"][0][
                                    "text"
                                ]

                                if self._process:
                                    video_page = session().get(video_url)
                                    description = self._get_description(video_page.text)

                                    audio = Audio(
                                        url=video_url,
                                        title=title,
                                        author=channel_name,
                                        description=description,
                                    )
                                else:
                                    audio = Audio(
                                        url=video_url, title=title, author=channel_name
                                    )

                                # Call the callback function
                                self._callback(video_url, audio)
                                results_found += 1
                elif "continuationItemRenderer" in content:
                    continuation_token = content["continuationItemRenderer"][
                        "continuationEndpoint"
                    ]["continuationCommand"]["token"]

            if not continuation_token:
                break
