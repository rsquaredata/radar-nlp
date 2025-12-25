import time
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


class RobustSession:
    def __init__(self, timeout: int = 20, retries: int = 3, backoff: float = 0.5):
        self.timeout = timeout
        self.s = requests.Session()

        retry = Retry(
            total=retries,
            backoff_factor=backoff,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["GET", "POST"],
        )

        adapter = HTTPAdapter(max_retries=retry)
        self.s.mount("http://", adapter)
        self.s.mount("https://", adapter)

    def get(self, url, **kwargs):
        return self.s.get(url, timeout=self.timeout, **kwargs)

    def post(self, url, **kwargs):
        return self.s.post(url, timeout=self.timeout, **kwargs)
