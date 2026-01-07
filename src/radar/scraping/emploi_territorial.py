import requests
from bs4 import BeautifulSoup
import time
import logging
from typing import Any, Dict, List
from radar.scraping.base import BaseScraper

logger = logging.getLogger(__name__)

class EmploiTerritorialClient(BaseScraper):
    def __init__(self):
        self.session = requests.Session()
        self.base_url = "https://www.emploi-territorial.fr/emploi-mobilite/"
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
        }

    def fetch_all(self, queries: List[str], familles: str = "A7,A1", max_pages: int = 5) -> List[Dict[str, Any]]:
        all_results = []
        search_query = " ou ".join(queries)

        for page in range(1, max_pages + 1):
            # L'URL utilise maintenant la variable 'familles' venant du YAML
            url = f"{self.base_url}?adv-search={search_query}&search-fam-metier={familles}&page={page}"
            logger.info(f"ET : Scraping page {page} (Familles: {familles})")

            try:
                r = self.session.get(url, headers=self.headers, timeout=15)
                if r.status_code != 200: break

                soup = BeautifulSoup(r.text, 'html.parser')
                links = [f"https://www.emploi-territorial.fr{a['href'].split('?')[0]}" 
                        for a in soup.find_all('a', href=True) if '/offre/' in a['href']]

                if not links: break

                for link in list(set(links)):
                    detail = self._get_detail(link)
                    if detail:
                        all_results.append({
                            "id_offre": link.rstrip('/').split('/')[-1],
                            "url": link,
                            "titre": "Offre IT Territoriale",
                            "description_poste": detail,
                            "source": "Emploi Territorial"
                        })
                    time.sleep(0.3)
            except Exception as e:
                logger.error(f"Erreur page {page}: {e}")
                break
        return all_results

    def _get_detail(self, url):
        try:
            r = self.session.get(url, headers=self.headers, timeout=10)
            soup = BeautifulSoup(r.text, 'html.parser')
            detail = soup.find('div', class_='fiche-offre') or soup.find('main')
            return detail.get_text(separator=' ', strip=True) if detail else None
        except: return None
