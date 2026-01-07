import logging
from pathlib import Path
from radar.scraping.france_travail import FranceTravailClient
# Importe ici tes autres clients quand ils seront prêts (ET, etc.)
from radar.etl.normalizer import normalize_france_travail
from radar.utils.io import save_jsonl

# Configurer le logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    # 1. Initialisation
    client_ft = FranceTravailClient()

    # 2. Définition des recherches (pourrait être chargé depuis config/queries.yaml)
    queries = ["Data Scientist", "Analyste de données", "Intelligence Artificielle"]

    # 3. Pipeline France Travail
    logger.info("Début du pipeline France Travail...")
    raw_ft = client_ft.fetch_all(queries)

    if raw_ft:
        # On sauvegarde le brut
        save_jsonl(raw_ft, Path("data/raw/france_travail_raw.jsonl"))

        # On normalise
        clean_ft = normalize_france_travail(raw_ft)

        # On sauvegarde le final (on pourra concaténer avec les autres sources ici)
        save_jsonl(clean_ft, Path("data/processed/offers_merged.jsonl"))
        logger.info(f"Ingestion FT réussie : {len(clean_ft)} offres traitées.")
    else:
        logger.warning("Aucune donnée récupérée pour France Travail.")

if __name__ == "__main__":
    main()