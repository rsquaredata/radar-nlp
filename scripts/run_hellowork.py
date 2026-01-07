import logging
import yaml
from pathlib import Path
from radar.scraping.hellowork import HelloWorkClient
from radar.etl.normalizer import normalize_hellowork
from radar.utils.io import save_jsonl, save_csv

# Configuration du logging
logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def load_keywords():
    """Charge les mots-clés métiers depuis queries.yaml."""
    config_path = Path("src/radar/config/queries.yaml")
    with open(config_path, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)
    # On cible 'data_ia' car c'est le nom dans ton fichier
    return config.get("data_ia", [])

def main():
    # 1. Configuration des chemins
    raw_path = Path("data/raw/hellowork_raw.jsonl")
    proc_path = Path("data/processed/hellowork_clean.jsonl")

    # 2. Chargement des mots-clés via la config centralisée
    keywords = load_keywords()

    if not keywords:
        logger.error("Aucun mot-clé trouvé dans queries.yaml (clé 'data_ia')")
        return

    # 3. Initialisation du client
    client = HelloWorkClient()

    logger.info(f"Lancement du scraping HelloWork pour : {keywords}")

    # 4. Extraction
    raw_data = client.fetch_all(keywords)

    if not raw_data:
        logger.warning("Aucune donnée récupérée pour HelloWork.")
        return

    # 5. Sauvegarde du brut
    save_jsonl(raw_data, raw_path)

    # 6. Normalisation
    logger.info("Normalisation des données HelloWork...")
    clean_data = normalize_hellowork(raw_data)

    # 7. Sauvegarde des données propres
    save_jsonl(clean_data, proc_path)
    save_csv(clean_data, proc_path.with_suffix(".csv"))

    logger.info(f"✅ Terminé : {len(clean_data)} offres HelloWork traitées et normalisées.")

if __name__ == "__main__":
    main()
