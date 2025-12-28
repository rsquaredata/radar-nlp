from __future__ import annotations

import json
from pathlib import Path

from radar.scraping.emploi_territorial import scrape_emploi_territorial


OUT_DIR = Path("data/raw/emploi_territorial/")
OUT_DIR.mkdir(parents=True, exist_ok=True)


def main():
    print("Scraping Emploi-Territorial...")

    jobs = scrape_emploi_territorial(
        mots_cles="data",
        max_pages=10,
    )

    out_path = OUT_DIR / "emploi_territorial.jsonl"

    with out_path.open("w", encoding="utf-8") as f:
        for job in jobs:
            f.write(job.to_json() + "\n")

    print(f"Scraping terminé : {len(jobs)} offres")
    print(f"Fichier écrit dans : {out_path}")


if __name__ == "__main__":
    main()
