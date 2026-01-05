import time
from typing import Optional
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


class RobustSession(requests.Session):
    """
    Session HTTP avec retry automatique et gestion d'erreurs robuste.
    """
    
    def __init__(
        self,
        retries: int = 3,
        backoff_factor: float = 0.5,
        status_forcelist: tuple = (500, 502, 504),
        timeout: int = 30,
    ):
        super().__init__()
        
        self.timeout = timeout
        
        # Configuration retry
        retry_strategy = Retry(
            total=retries,
            backoff_factor=backoff_factor,
            status_forcelist=status_forcelist,
            allowed_methods=["HEAD", "GET", "OPTIONS", "POST"],
        )
        
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.mount("http://", adapter)
        self.mount("https://", adapter)
    
    def get(self, url: str, **kwargs):
        """GET avec timeout par défaut"""
        if 'timeout' not in kwargs:
            kwargs['timeout'] = self.timeout
        return super().get(url, **kwargs)
    
    def post(self, url: str, **kwargs):
        """POST avec timeout par défaut"""
        if 'timeout' not in kwargs:
            kwargs['timeout'] = self.timeout
        return super().post(url, **kwargs)