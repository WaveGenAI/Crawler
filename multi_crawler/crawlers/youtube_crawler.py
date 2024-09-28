import json
import logging
import time
from concurrent.futures import ThreadPoolExecutor
from typing import Callable, Sequence

import requests

from ..models import Audio
from ..ytb_session import YtbSession
from .crawlers import BaseCrawler


class YoutubeCrawler(BaseCrawler):
    """Class to find and return URLs of Youtube videos based on search terms."""

    YOUTUBE_ENDPOINT = "https://www.youtube.com"

    def __init__(
        self,
        terms: Sequence[str],
        callback: Callable,
        process: bool = False,
        num_processes: int = 10,
    ):
        self._terms = terms
        self._callback = callback
        self._process = process
        self._num_processes = num_processes

        self.logging = logging.getLogger(__name__)
        self._ytb_sessions = {
            time.time(): YtbSession(
                {"quiet": True, "noprogress": True, "no_warnings": True}
            )
            for _ in range(num_processes)
        }

        # Create a thread pool with max 10 threads
        self.executor = ThreadPoolExecutor(max_workers=num_processes)
        self.futures = set()

    def _get_ytb_data(self, url):
        # get the oldest session
        session = self._ytb_sessions.pop(min(self._ytb_sessions.keys()))
        # append a new session
        self._ytb_sessions[time.time()] = session

        info = session.extract_info(url, download=False)

        if (
            "categories" in info
            and info["categories"] is not None
            and not "Music" in info["categories"]
        ):
            logging.info("Skipping non-music video: %s", info["title"])
            return

        logging.info("Found music video: %s", info["title"])
        audio = Audio(
            url=url,
            title=info["title"],
            author=info["channel"],
            description=info["description"],
            tags=info["tags"],
        )

        self._callback(audio)

    def _manage_futures(self):
        """Helper function to clean up completed futures and maintain a max of 10 threads."""
        # Check if any threads have finished and remove them
        completed_futures = {fut for fut in self.futures if fut.done()}
        for fut in completed_futures:
            fut.result()

            self.futures.remove(fut)

    def crawl(self, *args, **kwargs) -> None:
        """Find and return URLs of Youtube videos based on search terms."""

        nb_results = kwargs.get("nb_results", -1)

        results_nbm = 0
        next_page_token = None

        while results_nbm < nb_results or nb_results == -1:
            if next_page_token is None:
                results = self._get_list_by_keyword(self._terms)
            else:
                results = self._next_page(next_page_token)

            if "items" in results:
                if len(results["items"]) == 0:
                    break  # no more results

                for item in results["items"]:
                    url = f"{self.YOUTUBE_ENDPOINT}/watch?v={item['id']}"

                    # Ensure we don't have more than 10 active threads
                    while len(self.futures) > self._num_processes:
                        self._manage_futures()
                        time.sleep(0.1)  # Sleep briefly to avoid tight loop

                    future = self.executor.submit(self._get_ytb_data, url)
                    self.futures.add(future)

                    results_nbm += 1

            if "nextPage" in results:
                next_page_token = results["nextPage"]
            else:
                break

        self.logging.info("Found %d url.", results_nbm)

    def _get_youtube_init_data(self, url):
        init_data = {}
        api_token = None
        context = None

        try:
            response = requests.get(url)
            page_content = response.text

            yt_init_data = page_content.split("var ytInitialData =")

            if yt_init_data and len(yt_init_data) > 1:
                data = yt_init_data[1].split("</script>")[0].strip()[:-1]

                if "innertubeApiKey" in page_content:
                    api_token = (
                        page_content.split("innertubeApiKey")[1]
                        .strip()
                        .split(",")[0]
                        .split('"')[2]
                    )

                if "INNERTUBE_CONTEXT" in page_content:
                    context = json.loads(
                        page_content.split("INNERTUBE_CONTEXT")[1].strip()[2:-2]
                    )

                init_data = json.loads(data)
                return {
                    "initdata": init_data,
                    "apiToken": api_token,
                    "context": context,
                }
            else:
                print("cannot_get_init_data")
                raise Exception("cannot_get_init_data")

        except Exception as ex:
            print(ex)
            raise ex

    def _get_list_by_keyword(self, keyword):
        endpoint = f"{self.YOUTUBE_ENDPOINT}/results?search_query={keyword}&sp=EgIwAQ%253D%253D"

        try:
            page = self._get_youtube_init_data(endpoint)

            section_list_renderer = page["initdata"]["contents"][
                "twoColumnSearchResultsRenderer"
            ]["primaryContents"]["sectionListRenderer"]

            cont_token = {}
            items = []

            for content in section_list_renderer["contents"]:
                if "continuationItemRenderer" in content:
                    cont_token = content["continuationItemRenderer"][
                        "continuationEndpoint"
                    ]["continuationCommand"]["token"]
                elif "itemSectionRenderer" in content:
                    for item in content["itemSectionRenderer"]["contents"]:
                        video_render = item.get("videoRenderer")
                        if video_render and "videoId" in video_render:
                            items.append(self._video_render_func(item))

            api_token = page["apiToken"]
            context = page["context"]
            next_page_context = {"context": context, "continuation": cont_token}

            return {
                "items": items,
                "nextPage": {
                    "nextPageToken": api_token,
                    "nextPageContext": next_page_context,
                },
            }

        except Exception as ex:
            print(ex)
            raise ex

    def _next_page(self, next_page):
        endpoint = f"{self.YOUTUBE_ENDPOINT}/youtubei/v1/search?key={next_page['nextPageToken']}"

        try:
            response = requests.post(endpoint, json=next_page["nextPageContext"])
            page_data = response.json()

            item1 = page_data["onResponseReceivedCommands"][0][
                "appendContinuationItemsAction"
            ]
            items = []

            for conitem in item1["continuationItems"]:
                if "itemSectionRenderer" in conitem:
                    for item in conitem["itemSectionRenderer"]["contents"]:
                        video_render = item.get("videoRenderer")
                        if video_render and "videoId" in video_render:
                            items.append(self._video_render_func(item))
                elif "continuationItemRenderer" in conitem:
                    next_page["nextPageContext"]["continuation"] = conitem[
                        "continuationItemRenderer"
                    ]["continuationEndpoint"]["continuationCommand"]["token"]

            return {"items": items, "nextPage": next_page}

        except Exception as ex:
            print(ex)
            raise ex

    def _video_render_func(self, json_data):
        try:
            if json_data and "videoRenderer" in json_data:
                video_renderer = json_data["videoRenderer"]

                is_live = False
                if "badges" in video_renderer and video_renderer["badges"]:
                    badge = video_renderer["badges"][0].get("metadataBadgeRenderer")
                    if badge and badge.get("style") == "BADGE_STYLE_TYPE_LIVE_NOW":
                        is_live = True

                if "thumbnailOverlays" in video_renderer:
                    for item in video_renderer["thumbnailOverlays"]:
                        overlay = item.get("thumbnailOverlayTimeStatusRenderer")
                        if overlay and overlay.get("style") == "LIVE":
                            is_live = True

                return {
                    "id": video_renderer["videoId"],
                    "type": "video",
                    "thumbnail": video_renderer["thumbnail"],
                    "title": video_renderer["title"]["runs"][0]["text"],
                    "channelTitle": video_renderer.get("ownerText", {})
                    .get("runs", [{}])[0]
                    .get("text", ""),
                    "shortBylineText": video_renderer.get("shortBylineText", ""),
                    "length": video_renderer.get("lengthText", ""),
                    "isLive": is_live,
                }
            else:
                return {}

        except Exception as ex:
            raise ex
