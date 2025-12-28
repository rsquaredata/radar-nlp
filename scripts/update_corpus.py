from __future__ import annotations

import json
import argparse
from pathlib import Path

from radar.nlp.preprocess_offre import process_offre
from radar.db.io import upsert_offre_complete


def list_jsonl_files(raw_root: Path) -> list[Path]:
    """
    Retourne tous les fichiers .jsonl présents dans data/raw/**.
    """
    return sorted(raw_root.glob("**/*.jsonl"))


def process_file(jsonl_path: Path) -> dict:
    """
    Traite un fichier JSONL complet :
    - lit tous les raw_job
    - applique process_offre()
    - insère/upsert en DB
    Retourne les stats du fichier.
    """
    print(f"\n📄 Traitement du fichier : {jsonl_path}")

    total = 0
    success = 0
    errors = 0

    with jsonl_path.open("r", encoding="utf-8") as f:
        for line in f:
            total += 1

            try:
                raw_job = json.loads(line)

                # Étape 2 : NLP / prétraitement
                offre_nlp = process_offre(raw_job)

                # Étape 3 : DB / upsert
                upsert_offre_complete(offre_nlp)

                success += 1

            except Exception as e:
                print(f" ❌ Erreur sur une offre : {e}")
                errors += 1

    return {
        "fichier": str(jsonl_path),
        "total": total,
        "success": success,
        "errors": errors,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--raw-dir",
        default="data/raw",
        help="Dossier contenant les fichiers JSONL scrapés",
    )
    args = parser.parse_args()

    raw_root = Path(args.raw_dir)
    if not raw_root.exists():
        raise FileNotFoundError(f"Dossier introuvable : {raw_root}")

    jsonl_files = list_jsonl_files(raw_root)

    if not jsonl_files:
        print("❗ Aucun fichier JSONL trouvé dans data/raw/.")
        return

    print(f"🟦 {len(jsonl_files)} fichiers JSONL trouvés.")

    global_total = 0
    global_success = 0
    global_errors = 0

    for jsonl_file in jsonl_files:
        stats = process_file(jsonl_file)
        global_total += stats["total"]
        global_success += stats["success"]
        global_errors += stats["errors"]

        print(
            f" ✔️ Fichier {jsonl_file.name} : "
            f"{stats['success']}/{stats['total']} OK, "
            f"{stats['errors']} erreurs"
        )

    print("\n==============================================================")
    print("📊 Résumé global ingestion")
    print("--------------------------------------------------------------")
    print(f"🔵 Offres totales lues :       {global_total}")
    print(f"🟢 Offres insérées/majus :    {global_success}")
    print(f"🔴 Offres en erreur :         {global_errors}")
    print("==============================================================\n")

    print("Terminé 👍")


if __name__ == "__main__":
    main()
