
import duckdb
from pathlib import Path

# =========================
# Chemins
# =========================
DB_PATH = Path("data/db/radar.duckdb")
DB_PATH.parent.mkdir(parents=True, exist_ok=True)

# =========================
# Connexion DuckDB
# =========================
con = duckdb.connect(DB_PATH)

# =========================
# Dimensions géographiques
# =========================
con.execute("""
CREATE TABLE IF NOT EXISTS dim_region (
    region_id INTEGER PRIMARY KEY,
    nom_region TEXT,
    latitude DOUBLE,
    longitude DOUBLE
);
""")

con.execute("""
CREATE TABLE IF NOT EXISTS dim_departement (
    departement_id INTEGER PRIMARY KEY,
    code_departement TEXT,
    nom_departement TEXT,
    region_id INTEGER,
    FOREIGN KEY (region_id) REFERENCES dim_region(region_id)
);
""")

con.execute("""
CREATE TABLE IF NOT EXISTS dim_commune (
    commune_id INTEGER PRIMARY KEY,
    nom_commune TEXT,
    code_commune TEXT,
    departement_id INTEGER,
    latitude DOUBLE,
    longitude DOUBLE,
    FOREIGN KEY (departement_id) REFERENCES dim_departement(departement_id)
);
""")

# =========================
# Autres dimensions
# =========================
con.execute("""
CREATE TABLE IF NOT EXISTS dim_source (
    source_id INTEGER PRIMARY KEY,
    nom_source TEXT,
    type_source TEXT
);
""")

con.execute("""
CREATE TABLE IF NOT EXISTS dim_date (
    date_id INTEGER PRIMARY KEY,
    date DATE,
    jour INTEGER,
    mois INTEGER,
    annee INTEGER,
    semaine INTEGER,
    trimestre INTEGER
);
""")

con.execute("""
CREATE TABLE IF NOT EXISTS dim_metier (
    metier_id INTEGER PRIMARY KEY,
    nom_metier TEXT,
    mots_cles TEXT
);
""")

con.execute("""
CREATE TABLE IF NOT EXISTS dim_texte (
    texte_id INTEGER PRIMARY KEY,
    titre TEXT,
    texte_complet TEXT,
    texte_clean TEXT
);
""")

con.execute("""
CREATE TABLE IF NOT EXISTS dim_remote (
    remote_id INTEGER PRIMARY KEY,
    remote_type TEXT
);
""")

con.execute("""
CREATE TABLE IF NOT EXISTS dim_skill (
    skill_id INTEGER PRIMARY KEY,
    nom_skill TEXT,
    categorie TEXT,
    type_skill TEXT
);
""")

# =========================
# Table de faits
# =========================
con.execute("""
CREATE TABLE IF NOT EXISTS fact_offre (
    offre_id INTEGER PRIMARY KEY,
    source_id INTEGER,
    date_id INTEGER,
    commune_id INTEGER,
    metier_id INTEGER,
    texte_id INTEGER,
    remote_id INTEGER,
    url TEXT,
    type_contrat TEXT,
    salaire_min DOUBLE,
    salaire_max DOUBLE,
    longueur_texte INTEGER,
    hash_offre TEXT,
    FOREIGN KEY (source_id) REFERENCES dim_source(source_id),
    FOREIGN KEY (date_id) REFERENCES dim_date(date_id),
    FOREIGN KEY (commune_id) REFERENCES dim_commune(commune_id),
    FOREIGN KEY (metier_id) REFERENCES dim_metier(metier_id),
    FOREIGN KEY (texte_id) REFERENCES dim_texte(texte_id),
    FOREIGN KEY (remote_id) REFERENCES dim_remote(remote_id)
);
""")

# =========================
# Table de liaison compétences
# =========================
con.execute("""
CREATE TABLE IF NOT EXISTS bridge_offre_skill (
    offre_id INTEGER,
    skill_id INTEGER,
    importance DOUBLE,
    extraction_method TEXT,
    PRIMARY KEY (offre_id, skill_id),
    FOREIGN KEY (offre_id) REFERENCES fact_offre(offre_id),
    FOREIGN KEY (skill_id) REFERENCES dim_skill(skill_id)
);
""")

con.close()

print("✅ Base DuckDB initialisée :", DB_PATH.resolve())
