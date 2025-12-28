from pathlib import Path
import duckdb

# Fichier DuckDB par défaut
DEFAULT_DB_PATH = Path("data/db/radar.duckdb")

SCHEMA_SQL = """
-- ===========
-- Dimensions géographiques (snowflake)
-- ===========

CREATE TABLE IF NOT EXISTS dim_pays (
    pays_id     INTEGER PRIMARY KEY,
    nom_pays    VARCHAR NOT NULL,
    code_iso    VARCHAR NOT NULL
);

CREATE TABLE IF NOT EXISTS dim_region (
    region_id   INTEGER PRIMARY KEY,
    pays_id     INTEGER NOT NULL,
    nom_region  VARCHAR NOT NULL,
    code_region VARCHAR,
    FOREIGN KEY (pays_id) REFERENCES dim_pays(pays_id)
);

CREATE TABLE IF NOT EXISTS dim_departement (
    departement_id   INTEGER PRIMARY KEY,
    region_id        INTEGER NOT NULL,
    nom_departement  VARCHAR NOT NULL,
    code_departement VARCHAR NOT NULL,
    FOREIGN KEY (region_id) REFERENCES dim_region(region_id)
);

CREATE TABLE IF NOT EXISTS dim_ville (
    ville_id        INTEGER PRIMARY KEY,
    departement_id  INTEGER NOT NULL,
    nom_ville       VARCHAR NOT NULL,
    code_postal     VARCHAR,
    latitude        DOUBLE,
    longitude       DOUBLE,
    FOREIGN KEY (departement_id) REFERENCES dim_departement(departement_id)
);

-- ===========
-- Dimensions métiers (snowflake)
-- ===========

CREATE TABLE IF NOT EXISTS dim_domaine_metier (
    domaine_id  INTEGER PRIMARY KEY,
    nom_domaine VARCHAR NOT NULL
);

CREATE TABLE IF NOT EXISTS dim_famille_metier (
    famille_id  INTEGER PRIMARY KEY,
    domaine_id  INTEGER NOT NULL,
    nom_famille VARCHAR NOT NULL,
    FOREIGN KEY (domaine_id) REFERENCES dim_domaine_metier(domaine_id)
);

CREATE TABLE IF NOT EXISTS dim_metier (
    metier_id   INTEGER PRIMARY KEY,
    famille_id  INTEGER NOT NULL,
    nom_metier  VARCHAR NOT NULL,
    mots_cles   VARCHAR,
    FOREIGN KEY (famille_id) REFERENCES dim_famille_metier(famille_id)
);

-- ===========
-- Autres dimensions
-- ===========

CREATE TABLE IF NOT EXISTS dim_source (
    source_id  INTEGER PRIMARY KEY,
    nom_source VARCHAR NOT NULL,
    secteur    VARCHAR
);

CREATE TABLE IF NOT EXISTS dim_date (
    date_id   INTEGER PRIMARY KEY, -- ex: 20251201
    date      DATE NOT NULL,
    annee     INTEGER,
    mois      INTEGER,
    jour      INTEGER,
    semaine   INTEGER,
    trimestre INTEGER
);

CREATE TABLE IF NOT EXISTS dim_texte (
    texte_id      INTEGER PRIMARY KEY,
    titre         VARCHAR,
    missions      VARCHAR,
    profil        VARCHAR,
    competences   VARCHAR,
    remuneration  VARCHAR,
    texte_complet VARCHAR,
    texte_clean   VARCHAR
);

CREATE TABLE IF NOT EXISTS dim_skill (
    skill_id   INTEGER PRIMARY KEY,
    nom_skill  VARCHAR NOT NULL,
    categorie  VARCHAR -- langage, outil BI, concept, soft-skill...
);

-- ===========
-- Dimension télétravail
-- ===========

CREATE TABLE IF NOT EXISTS dim_remote (
    remote_id    INTEGER PRIMARY KEY,
    remote_type  VARCHAR NOT NULL, -- on-site, hybride, remote
    jours_remote INTEGER,          -- 0 à 5
    description  VARCHAR
);

-- ===========
-- Table de faits
-- ===========

CREATE TABLE IF NOT EXISTS fact_offre (
    offre_id        INTEGER PRIMARY KEY,
    source_id       INTEGER NOT NULL,
    date_id         INTEGER NOT NULL,
    ville_id        INTEGER NOT NULL,
    metier_id       INTEGER NOT NULL,
    texte_id        INTEGER NOT NULL,
    remote_id       INTEGER,       -- nullable si info absente
    url             VARCHAR,
    type_contrat    VARCHAR,
    niveau_etude    VARCHAR,
    salaire_min     DOUBLE,
    salaire_max     DOUBLE,
    salaire_brut_net_flag VARCHAR, -- 'BRUT', 'NET', NULL si inconnu
    longueur_texte  INTEGER,
    hash_offre      VARCHAR,
    FOREIGN KEY (source_id) REFERENCES dim_source(source_id),
    FOREIGN KEY (date_id)   REFERENCES dim_date(date_id),
    FOREIGN KEY (ville_id)  REFERENCES dim_ville(ville_id),
    FOREIGN KEY (metier_id) REFERENCES dim_metier(metier_id),
    FOREIGN KEY (texte_id)  REFERENCES dim_texte(texte_id),
    FOREIGN KEY (remote_id) REFERENCES dim_remote(remote_id)
);

-- ===========
-- Table de bridge offre <-> skills (N-N)
-- ===========

CREATE TABLE IF NOT EXISTS bridge_offre_skill (
    offre_id   INTEGER NOT NULL,
    skill_id   INTEGER NOT NULL,
    importance DOUBLE, -- score ou poids si tu en calcules un
    PRIMARY KEY (offre_id, skill_id),
    FOREIGN KEY (offre_id) REFERENCES fact_offre(offre_id),
    FOREIGN KEY (skill_id) REFERENCES dim_skill(skill_id)
);

-- ===========
-- Index utiles
-- ===========

CREATE INDEX IF NOT EXISTS idx_fact_offre_hash
    ON fact_offre(hash_offre);

CREATE INDEX IF NOT EXISTS idx_fact_offre_url
    ON fact_offre(url);

CREATE INDEX IF NOT EXISTS idx_fact_offre_ville
    ON fact_offre(ville_id);

CREATE INDEX IF NOT EXISTS idx_fact_offre_metier
    ON fact_offre(metier_id);

CREATE INDEX IF NOT EXISTS idx_fact_offre_remote
    ON fact_offre(remote_id);
"""


def get_connection(db_path: Path | None = None) -> duckdb.DuckDBPyConnection:
    """
    Retourne une connexion DuckDB sur le fichier radar.duckdb.
    Crée le dossier parent si nécessaire.
    """
    if db_path is None:
        db_path = DEFAULT_DB_PATH

    db_path = Path(db_path)
    db_path.parent.mkdir(parents=True, exist_ok=True)

    conn = duckdb.connect(str(db_path))
    return conn


def create_schema(conn: duckdb.DuckDBPyConnection) -> None:
    """
    Exécute le script SQL de création des tables.
    """
    conn.execute(SCHEMA_SQL)


def init_database(db_path: Path | None = None) -> None:
    """
    Initialise complètement la base avec le schéma RADAR.
    """
    conn = get_connection(db_path)
    create_schema(conn)
    conn.close()


if __name__ == "__main__":
    init_database()
    print(f"Base RADAR initialisée dans {DEFAULT_DB_PATH}")
