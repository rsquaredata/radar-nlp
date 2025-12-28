from pathlib import Path
import duckdb

from .schema import get_connection

def load_dim_pays(conn: duckdb.DuckDBPyConnection) -> None:
    """
    Insérer la France dans dim_pays.
    """
    conn.execute("""
        INSERT INTO dim_pays (pays_id, nom_pays, code_iso)
        VALUES (1, 'France', 'FR')
        ON CONFLICT (pays_id) DO NOTHING
    """)

def load_regions(conn: duckdb.DuckDBPyConnection, path_regions: Path) -> None:
    """
    Charger les régions depuis un CSV avec au moins :
    - code_region
    - nom_region
    """
    conn.execute(f"""
        CREATE OR REPLACE TEMPORARY TABLE tmp_regions AS
        SELECT
            row_number() OVER () AS region_id,
            '1'::INTEGER AS pays_id,
            code_region,
            nom_region
        FROM read_csv_auto('{path_regions}')
    """)

    conn.execute("""
        INSERT INTO dim_region (region_id, pays_id, nom_region, code_region)
        SELECT region_id, pays_id, nom_region, code_region
        FROM tmp_regions
    """)

def load_departements(conn: duckdb.DuckDBPyConnection, path_departements: Path) -> None:
    """
    Charger les départements depuis un CSV avec :
    - code_departement
    - nom_departement
    - code_region
    """
    conn.execute("""
        CREATE OR REPLACE TEMPORARY TABLE tmp_departements AS
        SELECT *
        FROM read_csv_auto($1)
    """, [str(path_departements)])

    # On fait un join avec dim_region pour récupérer region_id
    conn.execute("""
        INSERT INTO dim_departement (departement_id, region_id, nom_departement, code_departement)
        SELECT
            row_number() OVER () AS departement_id,
            r.region_id,
            d.nom_departement,
            d.code_departement
        FROM tmp_departements d
        JOIN dim_region r
          ON d.code_region = r.code_region;
    """)

def load_villes(conn: duckdb.DuckDBPyConnection, path_villes: Path) -> None:
    """
    Charger les villes depuis un CSV avec :
    - nom_ville
    - code_postal
    - code_departement
    - latitude
    - longitude
    """
    conn.execute("""
        CREATE OR REPLACE TEMPORARY TABLE tmp_villes AS
        SELECT *
        FROM read_csv_auto($1)
    """, [str(path_villes)])

    conn.execute("""
        INSERT INTO dim_ville (ville_id, departement_id, nom_ville, code_postal, latitude, longitude)
        SELECT
            row_number() OVER () AS ville_id,
            d.departement_id,
            v.nom_ville,
            v.code_postal,
            v.latitude,
            v.longitude
        FROM tmp_villes v
        JOIN dim_departement d
          ON v.code_departement = d.code_departement;
    """)

def load_all_geo(
    db_path: Path,
    path_regions: Path,
    path_departements: Path,
    path_villes: Path,
) -> None:
    conn = get_connection(db_path)
    load_dim_pays(conn)
    load_regions(conn, path_regions)
    load_departements(conn, path_departements)
    load_villes(conn, path_villes)
    conn.close()
