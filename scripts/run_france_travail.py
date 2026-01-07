import logging
import yaml
from pathlib import Path
from radar.scraping.france_travail import FranceTravailClient
from radar.etl.normalizer import normalize_france_travail
from radar.utils.io import save_jsonl, save_csv

# Configuration du logging
logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def load_keywords():
    """Charge les mots-clés depuis le fichier de configuration central."""
    config_path = Path("src/radar/config/queries.yaml")
    with open(config_path, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)
    # On utilise 'data_ia' car c'est le nom de la clé dans ton fichier yaml
    return config.get("data_ia", [])

def main():
    # Définition des chemins
    raw_path = Path("data/raw/france_travail_raw.jsonl")
    proc_path = Path("data/processed/france_travail_clean.jsonl")

    # 1. Initialisation du client
    logger.info("Initialisation du client France Travail...")
    client = FranceTravailClient()

    # 2. Chargement des requêtes depuis le YAML
    queries = load_keywords() # <--- Plus de liste en dur ici !
    logger.info(f"Lancement du scraping pour les requêtes du YAML : {queries}")

    # 3. Extraction (Scraping)
    raw_data = client.fetch_all(queries)

    if not raw_data:
        logger.error("Aucune donnée n'a pu être récupérée. Vérifiez vos identifiants .env ou le YAML.")
        return

    # 4. Sauvegarde des données brutes
    save_jsonl(raw_data, raw_path)

    # 5. Normalisation
    logger.info("Normalisation des données en cours...")
    clean_data = normalize_france_travail(raw_data)

    # 6. Sauvegarde des données propres
    save_jsonl(clean_data, proc_path)
    save_csv(clean_data, proc_path.with_suffix(".csv"))

    logger.info(f"✅ Terminé : {len(clean_data)} offres normalisées dans {proc_path}")

if __name__ == "__main__":
    main()
