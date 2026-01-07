import yaml
import logging
from pathlib import Path
from radar.scraping.emploi_territorial import EmploiTerritorialClient
from radar.etl.normalizer import normalize_emploi_territorial
from radar.utils.io import save_jsonl, save_csv

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def main():
    with open("src/radar/config/queries.yaml", "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)

    keywords = config.get("data_ia", [])
    scrap_cfg = config.get("scraping", {})

    max_p = scrap_cfg.get("max_pages_emploi_territorial", 50)
    familles = scrap_cfg.get("et_famille_metiers", "A7,A1")

    client = EmploiTerritorialClient()
    logger.info(f"Démarrage ET | Pages: {max_p} | Familles: {familles}")

    raw_data = client.fetch_all(queries=keywords, familles=familles, max_pages=max_p)

    if raw_data:
        save_jsonl(raw_data, Path("data/raw/emploi_territorial_raw.jsonl"))
        clean_data = normalize_emploi_territorial(raw_data)
        save_jsonl(clean_data, Path("data/processed/emploi_territorial_clean.jsonl"))
        save_csv(clean_data, Path("data/processed/emploi_territorial_clean.csv"))
        logger.info(f"✅ ET : {len(clean_data)} offres.")

if __name__ == "__main__":
    main()
