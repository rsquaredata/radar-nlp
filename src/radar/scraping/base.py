from abc import ABC, abstractmethod
from typing import Any, Dict, List

class BaseScraper(ABC):
    @abstractmethod
    def fetch_all(self, queries: List[str]) -> List[Dict[str, Any]]:
        """Méthode à implémenter pour récupérer les données brutes."""
        pass