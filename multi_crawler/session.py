from typing import Any

import requests
from stem import Signal
from stem.control import Controller


class Session:
    """
    Create a new session object.
    """

    def __call__(self) -> Any:
        return requests.Session()


class TorSession(Session):
    """Create a new session object with Tor proxy settings."""

    def __init__(self, pswd: str) -> None:
        super().__init__()
        self.__pswd = pswd

    def _renew_connection(self) -> None:
        with Controller.from_port(port=9051) as controller:
            controller.authenticate(password=self.__pswd)
            controller.signal(Signal.NEWNYM)

    def __call__(self) -> Any:
        self._renew_connection()
        session = requests.Session()
        session.proxies = {
            "http": "socks5://127.0.0.1:9050",
            "https": "socks5://127.0.0.1:9050",
        }

        return session
