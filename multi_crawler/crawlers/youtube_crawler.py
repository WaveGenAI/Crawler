import json
import logging
import subprocess
import time
from concurrent.futures import ThreadPoolExecutor
from queue import Queue
from threading import Thread
from typing import Callable, Sequence

import yt_dlp

from ..models import Audio
from ..session import Session, TorSession
from .crawlers import BaseCrawler


class YtbDLSession:
    def __init__(self, is_tor_session: bool, po_token_reserve: int = 5, session=None):
        self.is_tor_session = is_tor_session
        self.po_token_queue = Queue()
        self.ytb_dl = None
        self.po_token_reserve = po_token_reserve
        self.token_generator_thread = Thread(
            target=self._token_generator_worker, daemon=True
        )
        self._session = session
        self.token_generator_thread.start()

    def _token_generator_worker(self):
        while True:
            if self.po_token_queue.qsize() < self.po_token_reserve:
                new_token = self._generate_poo()
                self.po_token_queue.put(new_token)
            else:
                time.sleep(1)  # Sleep to avoid constant CPU usage

    def _create_ytb_dl(self):
        settings = {
            "proxy": "socks5://127.0.0.1:9050" if self.is_tor_session else None,
            "po_token": f"web+{self._get_po_token()}",
            "nocheckcertificate": True,
            "quiet": True,
            "noprogress": True,
        }
        self.ytb_dl = yt_dlp.YoutubeDL(settings)

    def _get_po_token(self):
        if len(self.po_token_queue.queue) == 0:
            logging.warning("No poo token available. Waiting...")

        while len(self.po_token_queue.queue) == 0:
            time.sleep(1)

        return self.po_token_queue.get()

    def _generate_poo(self):
        logging.info("Generating poo token")
        result = subprocess.run(
            ["./poo_gen.sh"],
            capture_output=True,
            text=True,
            check=True,
        )

        result = result.stdout.strip()

        if "warning" in result:
            logging.warning("Failed to generate poo token. Retrying...")
            return self._generate_poo()

        poo_token = result.split("po_token: ")[1].split("\n")[0]
        logging.info("Generated poo token: %s", poo_token[:10] + "...")
        return poo_token.strip()

    def extract_info(self, url):
        logging.info("Extracting info from %s", url)
        if self.ytb_dl is None:
            self._create_ytb_dl()

        try:
            return self.ytb_dl.extract_info(url, download=False)
        except yt_dlp.utils.DownloadError:
            logging.warning("YouTube bot detection triggered. Updating session...")
            if self.is_tor_session:
                self._session.renew_connection()

            self._create_ytb_dl()
            return self.extract_info(url)


class YoutubeCrawler(BaseCrawler):
    """Class to find and return URLs of Youtube videos based on search terms."""

    YOUTUBE_ENDPOINT = "https://www.youtube.com"

    def __init__(
        self,
        terms: Sequence[str],
        callback: Callable,
        session: Session = Session,
        process: bool = False,
    ):
        self._terms = terms
        self._callback = callback
        self._session = session
        self._process = process

        self.logging = logging.getLogger(__name__)

        self._nbm_requests = 0

        self.ytb_dl_session = YtbDLSession(
            isinstance(self._session, TorSession), session=self._session
        )

        # Create a thread pool with max 10 threads
        self.executor = ThreadPoolExecutor(max_workers=10)
        self.futures = set()

    def _get_ytb_data(self, url):
        info = self.ytb_dl_session.extract_info(url)

        if not "Music" in info["categories"]:
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
                    while len(self.futures) >= 10:
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
            response = self._session.get_session().get(url)
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
            response = self._session.get_session().post(
                endpoint, json=next_page["nextPageContext"]
            )
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
