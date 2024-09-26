from typing import Any

import requests
from stem import Signal
from stem.control import Controller

from requests import Session


class Session:
    """
    Create a new session object.
    """

    def get_session(self) -> Session:
        return requests.Session()


class TorSession(Session):
    """Create a new session object with Tor proxy settings."""

    def __init__(self, pswd: str) -> None:
        super().__init__()
        self.__pswd = pswd

    def renew_connection(self) -> None:
        """Renew the Tor connection."""
        with Controller.from_port(port=9051) as controller:
            controller.authenticate(password=self.__pswd)
            controller.signal(Signal.NEWNYM)

    def get_session(self) -> Session:
        """Get a new session object with Tor proxy settings."""
        session = requests.Session()
        session.proxies = {
            "http": "socks5://127.0.0.1:9050",
            "https": "socks5://127.0.0.1:9050",
        }

        return session
