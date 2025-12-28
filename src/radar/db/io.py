from __future__ import annotations

from datetime import date
from pathlib import Path
from typing import Optional, Iterable

import csv
import duckdb
import hashlib

from radar.db.schema import get_connection

# =============================================================================
# CONSTANTES DE CHEMIN
# =============================================================================

# data/static/ : référentiels métiers, skills, etc.
STATIC_DIR = Path(__file__).resolve().parents[3] / "data" / "static"

# data/raw/ : fichier géographique brut
GEO_CSV_PATH = (
    Path(__file__).resolve().parents[3]
    / "data"
    / "raw"
    / "20230823-communes-departement-region.csv"
)

# =============================================================================
# DIMENSIONS SIMPLES
# =============================================================================


def init_dim_source() -> None:
    """
    Remplit dim_source avec quelques sources standard.
    Idempotent : ne réinsère pas si déjà présent.
    """
    conn = get_connection()

    sources = [
        (1, "Indeed", "privé"),
        (2, "APEC", "privé"),
        (3, "Jooble", "privé"),
        (4, "Welcome to the Jungle", "privé"),
        (5, "Emploi-Territorial", "public"),
        (6, "Emploi-Public", "public"),
    ]

    for source_id, nom_source, secteur in sources:
        conn.execute(
            """
            INSERT INTO dim_source (source_id, nom_source, secteur)
            SELECT ?, ?, ?
            WHERE NOT EXISTS (
                SELECT 1 FROM dim_source WHERE source_id = ?
            );
        """,
            (source_id, nom_source, secteur, source_id),
        )

    conn.close()


def init_dim_date(start_year: int = 2020, end_year: int = 2030) -> None:
    """
    Remplit dim_date avec un calendrier YYYY-MM-DD entre start_year et end_year (inclus).
    """
    conn = get_connection()

    conn.execute(
        f"""
        INSERT INTO dim_date (date_id, date, annee, mois, jour, semaine, trimestre)
        SELECT
            CAST(strftime(date_range, '%Y%m%d') AS INTEGER) AS date_id,
            date_range::DATE AS date,
            EXTRACT(YEAR FROM date_range) AS annee,
            EXTRACT(MONTH FROM date_range) AS mois,
            EXTRACT(DAY FROM date_range) AS jour,
            EXTRACT(ISODOW FROM date_range) AS semaine,
            ((EXTRACT(MONTH FROM date_range) - 1) / 3 + 1)::INTEGER AS trimestre
        FROM (
            SELECT range AS date_range
            FROM range(
                DATE '{start_year}-01-01',
                DATE '{end_year}-12-31',
                INTERVAL 1 DAY
            )
        )
        WHERE NOT EXISTS (
            SELECT 1 FROM dim_date d WHERE d.date = date_range
        );
    """
    )

    conn.close()


# =============================================================================
# DIMENSION METIERS : domaine / famille / métier
# =============================================================================


def init_metier_hierarchy() -> None:
    """
    Remplit dim_domaine_metier, dim_famille_metier, dim_metier à partir de data/static/metiers.csv.
    """
    path = STATIC_DIR / "metiers.csv"

    if not path.exists():
        raise FileNotFoundError(f"Fichier référentiel métiers introuvable : {path}")

    conn = get_connection()

    with path.open("r", encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter=";")
        rows = list(reader)

    # 1) domaines
    domaines = {int(r["domaine_id"]): r["nom_domaine"] for r in rows}

    for domaine_id, nom_domaine in domaines.items():
        conn.execute(
            """
            INSERT INTO dim_domaine_metier (domaine_id, nom_domaine)
            SELECT ?, ?
            WHERE NOT EXISTS (
                SELECT 1 FROM dim_domaine_metier WHERE domaine_id = ?
            );
        """,
            (domaine_id, nom_domaine, domaine_id),
        )

    # 2) familles
    familles = {
        int(r["famille_id"]): (int(r["domaine_id"]), r["nom_famille"]) for r in rows
    }

    for famille_id, (domaine_id, nom_famille) in familles.items():
        conn.execute(
            """
            INSERT INTO dim_famille_metier (famille_id, domaine_id, nom_famille)
            SELECT ?, ?, ?
            WHERE NOT EXISTS (
                SELECT 1 FROM dim_famille_metier WHERE famille_id = ?
            );
        """,
            (famille_id, domaine_id, nom_famille, famille_id),
        )

    # 3) métiers
    for row in rows:
        metier_id = int(row["metier_id"])
        famille_id = int(row["famille_id"])
        nom_metier = row["nom_metier"]
        mots_cles = row.get("mots_cles", "")

        conn.execute(
            """
            INSERT INTO dim_metier (metier_id, famille_id, nom_metier, mots_cles)
            SELECT ?, ?, ?, ?
            WHERE NOT EXISTS (
                SELECT 1 FROM dim_metier WHERE metier_id = ?
            );
        """,
            (metier_id, famille_id, nom_metier, mots_cles, metier_id),
        )

    conn.close()


# =============================================================================
# DIMENSION SKILLS
# =============================================================================


def init_dim_skill() -> None:
    """
    Remplit dim_skill à partir de data/static/skills.csv.
    """
    path = STATIC_DIR / "skills.csv"
    if not path.exists():
        raise FileNotFoundError(f"Fichier référentiel skills introuvable : {path}")

    conn = get_connection()

    with path.open("r", encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter=";")
        for row in reader:
            skill_id = int(row["skill_id"])
            nom_skill = row["nom_skill"]
            categorie = row.get("categorie", None)

            conn.execute(
                """
                INSERT INTO dim_skill (skill_id, nom_skill, categorie)
                SELECT ?, ?, ?
                WHERE NOT EXISTS (
                    SELECT 1 FROM dim_skill WHERE skill_id = ?
                );
            """,
                (skill_id, nom_skill, categorie, skill_id),
            )

    conn.close()


# =============================================================================
# DIMENSION REMOTE
# =============================================================================


def init_dim_remote() -> None:
    """
    Remplit dim_remote avec 6 cas :
    1 – 0j TT  (on-site)
    2 – 1j TT  (hybride)
    3 – 2j TT  (hybride)
    4 – 3j TT  (hybride)
    5 – 4j TT  (hybride)
    6 – 5j TT  (remote)
    """
    conn = get_connection()

    remote_values = [
        (1, "on-site", 0, "Aucun télétravail (0 jour/semaine)"),
        (2, "hybride", 1, "Télétravail partiel (1 jour/semaine)"),
        (3, "hybride", 2, "Télétravail partiel (2 jours/semaine)"),
        (4, "hybride", 3, "Télétravail partiel (3 jours/semaine)"),
        (5, "hybride", 4, "Télétravail majoritaire (4 jours/semaine)"),
        (6, "remote", 5, "Télétravail total (5 jours/semaine)"),
    ]

    for remote_id, remote_type, jours_remote, desc in remote_values:
        conn.execute(
            """
            INSERT INTO dim_remote (remote_id, remote_type, jours_remote, description)
            SELECT ?, ?, ?, ?
            WHERE NOT EXISTS (
                SELECT 1 FROM dim_remote WHERE remote_id = ?
            );
        """,
            (remote_id, remote_type, jours_remote, desc, remote_id),
        )

    conn.close()


# mapping par défaut si on n’a que remote_type
REMOTE_DEFAULT = {
    "on-site": 1,
    "hybride": 3,  # par défaut 2j TT
    "remote": 6,   # full remote
}


def resolve_remote_id(offre: dict) -> Optional[int]:
    """
    Retourne un remote_id cohérent à partir de :
    - offre["jours_remote"] (int, nombre de jours TT/semaine), si dispo
    - sinon offre["remote_type"] ('on-site' / 'hybride' / 'remote')

    Si rien n'est indiqué → None.
    """
    jours = offre.get("jours_remote")
    if isinstance(jours, int):
        if jours <= 0:
            return 1
        elif jours == 1:
            return 2
        elif jours == 2:
            return 3
        elif jours == 3:
            return 4
        elif jours == 4:
            return 5
        else:
            return 6

    remote_type = offre.get("remote_type")
    if remote_type is None:
        return None

    return REMOTE_DEFAULT.get(remote_type, None)


# =============================================================================
# DIMENSIONS GEO
# =============================================================================


def init_dim_geo() -> None:
    """
    Initialise dim_pays / dim_region / dim_departement / dim_ville à partir de GEO_CSV_PATH.
    """
    if not GEO_CSV_PATH.exists():
        raise FileNotFoundError(f"Fichier géo introuvable : {GEO_CSV_PATH}")

    conn = get_connection()

    # Pays = France
    conn.execute(
        """
        INSERT INTO dim_pays (pays_id, nom_pays, code_iso)
        SELECT 1, 'France', 'FR'
        WHERE NOT EXISTS (SELECT 1 FROM dim_pays WHERE pays_id = 1);
    """
    )

    # staging CSV
    conn.execute(
        """
        CREATE OR REPLACE TEMPORARY TABLE stg_geo AS
        SELECT * FROM read_csv_auto(?, HEADER=TRUE);
    """,
        [str(GEO_CSV_PATH)],
    )

    # régions
    conn.execute(
        """
        INSERT INTO dim_region (region_id, pays_id, nom_region, code_region)
        SELECT
            CAST(s.code_region AS INTEGER),
            1,
            s.nom_region,
            s.code_region
        FROM (
            SELECT DISTINCT code_region, nom_region
            FROM stg_geo
            WHERE code_region IS NOT NULL
        ) s
        WHERE NOT EXISTS (
            SELECT 1 FROM dim_region r WHERE r.code_region = s.code_region
        );
    """
    )

    # départements
    conn.execute(
        """
        INSERT INTO dim_departement (departement_id, region_id, nom_departement, code_departement)
        SELECT
            (SELECT COALESCE(MAX(departement_id), 0) FROM dim_departement)
            + ROW_NUMBER() OVER (ORDER BY s.code_departement),
            r.region_id,
            s.nom_departement,
            s.code_departement
        FROM (
            SELECT DISTINCT code_departement, nom_departement, code_region
            FROM stg_geo
            WHERE code_departement IS NOT NULL
        ) s
        JOIN dim_region r ON r.code_region = s.code_region
        WHERE NOT EXISTS (
            SELECT 1 FROM dim_departement d WHERE d.code_departement = s.code_departement
        );
    """
    )

    # villes
    conn.execute(
        """
        INSERT INTO dim_ville (ville_id, departement_id, nom_ville, code_postal, latitude, longitude)
        SELECT
            (SELECT COALESCE(MAX(ville_id), 0) FROM dim_ville)
            + ROW_NUMBER() OVER (ORDER BY s.code_commune_INSEE, s.code_postal),
            d.departement_id,
            s.nom_commune_complet,
            s.code_postal,
            s.latitude::DOUBLE,
            s.longitude::DOUBLE
        FROM (
            SELECT DISTINCT
                code_commune_INSEE,
                nom_commune_complet,
                code_postal,
                code_departement,
                latitude,
                longitude
            FROM stg_geo
            WHERE code_commune_INSEE IS NOT NULL
        ) s
        JOIN dim_departement d ON d.code_departement = s.code_departement
        WHERE NOT EXISTS (
            SELECT 1
            FROM dim_ville v
            WHERE v.nom_ville = s.nom_commune_complet
              AND v.code_postal = s.code_postal
        );
    """
    )

    conn.close()


# =============================================================================
# HELPERS DIMENSIONS
# =============================================================================


def get_source_id(conn: duckdb.DuckDBPyConnection, source_name: str) -> int:
    row = conn.execute(
        "SELECT source_id FROM dim_source WHERE nom_source = ?",
        [source_name],
    ).fetchone()

    if row is None:
        raise ValueError(f"Source inconnue : {source_name}")

    return row[0]


def get_date_id(conn: duckdb.DuckDBPyConnection, d: date) -> int:
    row = conn.execute(
        "SELECT date_id FROM dim_date WHERE date = ?",
        [d],
    ).fetchone()

    if row is None:
        raise ValueError(f"Date {d} absente de dim_date. Lance init_dim_date.")
    return row[0]


def find_ville_id(
    conn: duckdb.DuckDBPyConnection,
    nom_ville: str,
    code_postal: Optional[str],
) -> Optional[int]:
    if code_postal:
        q = """
            SELECT ville_id FROM dim_ville
            WHERE lower(nom_ville) = lower(?)
              AND code_postal = ?
            LIMIT 1;
        """
        params = [nom_ville, code_postal]
    else:
        q = """
            SELECT ville_id FROM dim_ville
            WHERE lower(nom_ville) = lower(?)
            LIMIT 1;
        """
        params = [nom_ville]

    row = conn.execute(q, params).fetchone()
    return row[0] if row else None


# =============================================================================
# INSERT TEXTE
# =============================================================================


def insert_texte_with_conn(
    conn: duckdb.DuckDBPyConnection,
    titre: Optional[str],
    missions: Optional[str],
    profil: Optional[str],
    competences: Optional[str],
    remuneration: Optional[str],
    texte_complet: str,
    texte_clean: Optional[str],
) -> int:
    next_id = conn.execute(
        "SELECT COALESCE(MAX(texte_id), 0) + 1 FROM dim_texte"
    ).fetchone()[0]

    conn.execute(
        """
        INSERT INTO dim_texte (
            texte_id, titre, missions, profil, competences,
            remuneration, texte_complet, texte_clean
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?);
    """,
        (
            next_id,
            titre,
            missions,
            profil,
            competences,
            remuneration,
            texte_complet,
            texte_clean,
        ),
    )

    return next_id


def insert_texte(
    titre: Optional[str],
    missions: Optional[str],
    profil: Optional[str],
    competences: Optional[str],
    remuneration: Optional[str],
    texte_complet: str,
    texte_clean: Optional[str],
) -> int:
    conn = get_connection()
    texte_id = insert_texte_with_conn(
        conn,
        titre=titre,
        missions=missions,
        profil=profil,
        competences=competences,
        remuneration=remuneration,
        texte_complet=texte_complet,
        texte_clean=texte_clean,
    )
    conn.close()
    return texte_id


# =============================================================================
# FACT_OFFRE + SKILLS
# =============================================================================


def upsert_fact_offre_raw(
    conn: duckdb.DuckDBPyConnection,
    source_id: int,
    date_id: int,
    ville_id: int,
    metier_id: int,
    texte_id: int,
    remote_id: Optional[int],
    url: Optional[str],
    type_contrat: Optional[str],
    niveau_etude: Optional[str],
    salaire_min: Optional[float],
    salaire_max: Optional[float],
    salaire_brut_net_flag: Optional[str],
    longueur_texte: Optional[int],
    hash_offre: str,
) -> int:
    row = conn.execute(
        "SELECT offre_id FROM fact_offre WHERE hash_offre = ?;",
        [hash_offre],
    ).fetchone()

    if row:
        offre_id = row[0]
        conn.execute(
            """
            UPDATE fact_offre
            SET source_id = ?, date_id = ?, ville_id = ?,
                metier_id = ?, texte_id = ?, remote_id = ?,
                url = ?, type_contrat = ?, niveau_etude = ?,
                salaire_min = ?, salaire_max = ?, salaire_brut_net_flag = ?,
                longueur_texte = ?
            WHERE offre_id = ?;
        """,
            [
                source_id,
                date_id,
                ville_id,
                metier_id,
                texte_id,
                remote_id,
                url,
                type_contrat,
                niveau_etude,
                salaire_min,
                salaire_max,
                salaire_brut_net_flag,
                longueur_texte,
                offre_id,
            ],
        )
    else:
        offre_id = conn.execute(
            "SELECT COALESCE(MAX(offre_id), 0) + 1 FROM fact_offre"
        ).fetchone()[0]

        conn.execute(
            """
            INSERT INTO fact_offre (
                offre_id, source_id, date_id, ville_id, metier_id, texte_id,
                remote_id, url, type_contrat, niveau_etude,
                salaire_min, salaire_max, salaire_brut_net_flag,
                longueur_texte, hash_offre
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
        """,
            [
                offre_id,
                source_id,
                date_id,
                ville_id,
                metier_id,
                texte_id,
                remote_id,
                url,
                type_contrat,
                niveau_etude,
                salaire_min,
                salaire_max,
                salaire_brut_net_flag,
                longueur_texte,
                hash_offre,
            ],
        )

    return offre_id


def upsert_offre_skills(
    conn: duckdb.DuckDBPyConnection,
    offre_id: int,
    skill_scores: Iterable[tuple[int, float]],
) -> None:
    """
    Met à jour bridge_offre_skill pour une offre.
    """
    conn.execute("DELETE FROM bridge_offre_skill WHERE offre_id = ?;", [offre_id])

    for skill_id, importance in skill_scores:
        conn.execute(
            """
            INSERT INTO bridge_offre_skill (offre_id, skill_id, importance)
            VALUES (?, ?, ?);
        """,
            [offre_id, skill_id, importance],
        )


def upsert_offre_complete(offre: dict) -> int:
    """
    Prend une offre pré-traitée (scraping + NLP) et alimente :
    - dim_texte
    - fact_offre
    - bridge_offre_skill
    """
    conn = get_connection()

    # 1) Dimensions
    source_id = get_source_id(conn, offre["source_name"])
    date_id = get_date_id(conn, offre["date_publication"])

    ville_id = find_ville_id(
        conn,
        offre["ville_nom"],
        offre.get("code_postal"),
    )
    if ville_id is None:
        conn.close()
        raise ValueError(
            f"Ville inconnue : {offre['ville_nom']} / {offre.get('code_postal')}"
        )

    metier_id = offre["metier_id"]

    # 2) Texte
    t = offre["texte"]
    texte_id = insert_texte_with_conn(
        conn,
        titre=t.get("titre"),
        missions=t.get("missions"),
        profil=t.get("profil"),
        competences=t.get("competences"),
        remuneration=t.get("remuneration"),
        texte_complet=t["texte_complet"],
        texte_clean=t.get("texte_clean"),
    )

    # 3) Remote
    remote_id = resolve_remote_id(offre)

    # 4) Hash
    hash_offre = offre.get("hash_offre")
    if not hash_offre:
        h = hashlib.sha256()
        h.update((offre.get("url", "") + t["texte_complet"]).encode("utf-8"))
        hash_offre = h.hexdigest()

    longueur_texte = len(t["texte_complet"]) if t.get("texte_complet") else None

    # 5) Upsert fact_offre
    offre_id = upsert_fact_offre_raw(
        conn=conn,
        source_id=source_id,
        date_id=date_id,
        ville_id=ville_id,
        metier_id=metier_id,
        texte_id=texte_id,
        remote_id=remote_id,
        url=offre.get("url"),
        type_contrat=offre.get("type_contrat"),
        niveau_etude=offre.get("niveau_etude"),
        salaire_min=offre.get("salaire_min"),
        salaire_max=offre.get("salaire_max"),
        salaire_brut_net_flag=offre.get("salaire_brut_net_flag"),
        longueur_texte=longueur_texte,
        hash_offre=hash_offre,
    )

    # 6) Skills
    skill_scores: list[tuple[int, float]] = []
    for skill in offre.get("skills", []):
        if isinstance(skill[0], int):
            # (skill_id, importance)
            skill_scores.append((skill[0], skill[1]))
        else:
            # TODO: lookup nom_skill -> skill_id si skill[0] est str
            pass

    if skill_scores:
        upsert_offre_skills(conn, offre_id, skill_scores)

    conn.close()
    return offre_id
