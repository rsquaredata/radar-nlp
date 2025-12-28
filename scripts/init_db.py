from __future__ import annotations

from pathlib import Path
import sys

# === S'assurer que src/ est dans le PYTHONPATH ================================
REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = REPO_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

# === Imports projet ===========================================================
from radar.db.schema import init_database, DEFAULT_DB_PATH
from radar.db.io import (
    init_dim_source,
    init_dim_date,
    init_metier_hierarchy,
    init_dim_skill,
    init_dim_geo,
    init_dim_remote,
)


def main() -> None:
    print("Initialisation de la base RADAR...")

    # 1) Création du fichier DuckDB et des tables (DDL)
    init_database()
    print(f"Schéma créé / mis à jour dans : {DEFAULT_DB_PATH}")

    # 2) Peuple les dimensions de base
    print("Initialisation de dim_source...")
    init_dim_source()
    print("   → dim_source OK")

    print("Initialisation de dim_date...")
    init_dim_date(start_year=2020, end_year=2030)
    print("   → dim_date OK")

    print("Initialisation de la hiérarchie métiers (domaines / familles / métiers)...")
    init_metier_hierarchy()
    print("   → dim_domaine_metier / dim_famille_metier / dim_metier OK")

    print("Initialisation de dim_skill...")
    init_dim_skill()
    print("   → dim_skill OK")

    print("Initialisation des dimensions géographiques...")
    init_dim_geo()
    print("   → dim_pays / dim_region / dim_departement / dim_ville OK")

    print("Initialisation de dim_remote...")
    init_dim_remote()
    print("   → dim_remote OK")

    print("\nBase RADAR initialisée avec succès.")


if __name__ == "__main__":
    main()
