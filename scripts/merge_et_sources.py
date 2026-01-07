import pandas as pd
from pathlib import Path
import logging
import json

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def merge_sources():
    std_path = Path("data/processed/emploi_territorial_clean.jsonl")
    mistral_raw_path = Path("data/raw/emploi_territorial_mistral_raw.jsonl")
    output_path = Path("data/processed/emploi_territorial_mistral_clean.jsonl")

    if not std_path.exists() or not mistral_raw_path.exists():
        logger.error("Fichiers sources manquants.")
        return

    # 1. Charger les URLs existantes pour dédupliquer
    existing_urls = set()
    with open(std_path, 'r', encoding='utf-8') as f:
        for line in f:
            try: existing_urls.add(json.loads(line)['url'])
            except: continue

    # 2. Charger Mistral
    mistral_data = []
    with open(mistral_raw_path, 'r', encoding='utf-8') as f:
        for line in f:
            try: mistral_data.append(json.loads(line))
            except: continue

    # 3. Filtrage et Alignement (Normalisation)
    final_mistral = []
    for o in mistral_data:
        if o['url'] not in existing_urls:
            # On aligne EXACTEMENT sur les colonnes du Standard
            final_mistral.append({
                "id_offre": o['url'].rstrip('/').split('/')[-1], # On extrait l'ID de l'URL
                "source": "Emploi Territorial (Mistral)",
                "titre": o['titre'],
                "description": o['description'], # Aligné sur 'Standard'
                "date_publication": None,        # Information non disponible
                "lieu_nom": "Inconnu",           # Aligné sur 'Standard'
                "code_postal": None,
                "entreprise": "Collectivité Territoriale",
                "type_contrat": "Non précisé",
                "url": o['url']
            })
            # On ajoute l'URL au set pour éviter les doublons internes à Mistral
            existing_urls.add(o['url'])

    # 4. Sauvegarde
    with open(output_path, 'w', encoding='utf-8') as f:
        for entry in final_mistral:
            f.write(json.dumps(entry, ensure_ascii=False) + '\n')

    logger.info(f"✅ Normalisation terminée : {len(final_mistral)} nouvelles offres au format standard.")

if __name__ == "__main__":
    merge_sources()
