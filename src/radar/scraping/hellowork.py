import time
import logging
import requests
from bs4 import BeautifulSoup
from typing import Any, Dict, List
from radar.scraping.base import BaseScraper

logger = logging.getLogger(__name__)

class HelloWorkClient(BaseScraper):
    def __init__(self):
        self.base_url = "https://www.hellowork.com"
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }

    def fetch_all(self, queries: List[str], max_pages: int = 3) -> List[Dict[str, Any]]:
        all_offers = []

        for q in queries:
            slug = q.lower().replace(" ", "-")
            logger.info(f"Recherche HelloWork : {q}")

            links_for_query = []

            for page in range(1, max_pages + 1):
                # Construction de l'URL avec pagination (?p=2, ?p=3...)
                url = f"{self.base_url}/fr-fr/emploi/metier_{slug}.html?p={page}"

                try:
                    logger.info(f"  -> Scraping page {page}...")
                    res = requests.get(url, headers=self.headers, timeout=10)
                    if res.status_code != 200:
                        break # Si la page n'existe pas, on passe au mot-clé suivant

                    soup = BeautifulSoup(res.text, "html.parser")

                    # Extraction des liens d'offres
                    page_links = []
                    for a in soup.find_all('a', href=True):
                        href = a['href']
                        if "/emplois/" in href and href.endswith(".html"):
                            full_url = self.base_url + href if href.startswith("/") else href
                            page_links.append(full_url)

                    if not page_links:
                        break # Plus de résultats trouvés

                    links_for_query.extend(page_links)
                    time.sleep(1) # Pause entre les pages de liste

                except Exception as e:
                    logger.error(f"Erreur sur {q} page {page}: {e}")
                    break

            # Nettoyage des doublons pour ce mot-clé
            links_for_query = list(set(links_for_query))
            logger.info(f"  -> Total : {len(links_for_query)} liens trouvés pour '{q}'")

            # Extraction du contenu de chaque offre
            for link in links_for_query:
                offer = self._parse_offer(link)
                if offer:
                    all_offers.append(offer)
                time.sleep(0.4) # Pause entre chaque offre

        return all_offers

    def _parse_offer(self, url: str) -> Dict[str, Any]:
        try:
            res = requests.get(url, headers=self.headers, timeout=10)
            if res.status_code != 200:
                return None

            soup = BeautifulSoup(res.text, "html.parser")

            # Extraction plus précise des champs
            title = soup.find("h1")
            company = soup.select_one("span[class*='company']") or soup.select_one("span[data-cy='companyName']")
            city = soup.select_one("span[class*='location']") or soup.select_one("span[data-cy='locationName']")

            return {
                "id": url.split("/")[-1].replace(".html", ""),
                "title": title.get_text(strip=True) if title else "Sans titre",
                "company": company.get_text(strip=True) if company else "Entreprise inconnue",
                "city": city.get_text(strip=True) if city else "France",
                "description": soup.get_text(separator=" ", strip=True)[500:3000],
                "link": url,
                "date": None
            }
        except:
            return None
