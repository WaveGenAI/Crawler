import logging
import subprocess
import time
from queue import Queue
from threading import Thread

import yt_dlp


class YtbDLSession:
    """
    Class to manage a YouTube-DL session with a pool of tokens.
    """

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
            ["./multi_crawler/scripts/poo_gen.sh"],
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

    def extract_info(self, url) -> dict:
        """
        Extracts info from a given URL using the YouTube-DL session.
        args:
            url: URL to extract info from.
        returns:
            dict: Extracted info from the URL.
        """

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
