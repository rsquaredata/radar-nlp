import yaml
import logging
import requests
from bs4 import BeautifulSoup
import time
from pathlib import Path
from radar.utils.io import save_jsonl

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def main():
    # 1. Chargement de la config
    with open("src/radar/config/queries.yaml", "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)

    keywords = config.get("data_ia", [])
    search_query = " ou ".join(keywords)

    et_cfg = config.get("sources", {}).get("emploi_territorial", {})
    familles = et_cfg.get("et_famille_metiers", "A7,A1")
    max_pages = et_cfg.get("max_pages", 20000)

    base_url = "https://www.emploi-territorial.fr/emploi-mobilite/"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

    offers = []
    for page in range(1, max_pages + 1):
        url = f"{base_url}?adv-search={search_query}&search-fam-metier={familles}&page={page}"
        logger.info(f"Agent IA : Scraping page {page}/{max_pages}")

        try:
            r = requests.get(url, headers=headers, timeout=15)
            if r.status_code != 200: 
                logger.warning(f"Sortie : Status {r.status_code}")
                break

            soup = BeautifulSoup(r.text, "html.parser")
            rows = soup.select("tr[id^='O']")

            # Condition de sortie si la page est vide (Break)
            if not rows: 
                logger.info("Plus aucun résultat trouvé. Arrêt du scraping.")
                break

            for row in rows:
                link = row.select_one("a.lien-details-offre")
                if not link: continue

                offer_url = "https://www.emploi-territorial.fr" + link["href"]

                # Scraping du détail
                detail_r = requests.get(offer_url, headers=headers, timeout=10)
                detail_soup = BeautifulSoup(detail_r.text, "html.parser")
                main_div = detail_soup.select_one("div#contenuOffre, div.contenu-offre, main")

                description = ""
                if main_div:
                    for tag in main_div(["script", "style"]): tag.decompose()
                    description = main_div.get_text(separator=" ", strip=True)

                offers.append({
                    "titre": link.get_text(strip=True),
                    "url": offer_url,
                    "description": description,
                    "source": "Emploi Territorial (Mistral)"
                })
                time.sleep(0.2)

        except Exception as e:
            logger.error(f"Erreur fatale : {e}")
            break

    if offers:
        output_raw = Path("data/raw/emploi_territorial_mistral_raw.jsonl")
        save_jsonl(offers, output_raw)
        logger.info(f"✅ Terminé : {len(offers)} offres collectées.")

if __name__ == "__main__":
    main()
