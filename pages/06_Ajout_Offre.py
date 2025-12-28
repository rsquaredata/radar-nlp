from __future__ import annotations

"""
Page 06_Ajout_Offre – Ajout interactif d'une offre dans RADAR à partir d'une URL.

Fonctionnement prévu :
- l'utilisateur colle une URL d'offre (Indeed, Apec, Jooble, ...),
- la source est détectée automatiquement (avec possibilité de forcer),
- on appelle le scraper / client API correspondant,
- on passe le résultat dans process_offre() pour générer les variables structurées,
- on appelle upsert_offre_complete() pour insérer / mettre à jour l'offre dans DuckDB,
- on affiche un récapitulatif et un message de succès.
"""

import re
from typing import Dict, Optional, Tuple
from urllib.parse import urlparse

import duckdb
import streamlit as st

from radar.db.schema import get_connection

# 🧩 À adapter selon ton projet réel :
# (si les chemins ne sont pas bons, tu modifies juste ces imports)
try:
    from radar.scraping.indeed import fetch_indeed_offer
except ImportError:  # fallback symbolique pour éviter que la page crashe
    fetch_indeed_offer = None  # type: ignore

try:
    from radar.scraping.apec import fetch_apec_offer
except ImportError:
    fetch_apec_offer = None  # type: ignore

try:
    from radar.scraping.jooble import fetch_jooble_offer
except ImportError:
    fetch_jooble_offer = None  # type: ignore

try:
    from radar.pipeline.process_offre import process_offre
except ImportError:
    process_offre = None  # type: ignore

try:
    from radar.db.io import upsert_offre_complete
except ImportError:
    upsert_offre_complete = None  # type: ignore


# =========================
# Connexion DB
# =========================

@st.cache_resource(show_spinner=False)
def get_cached_connection() -> duckdb.DuckDBPyConnection:
    """Connexion DuckDB mise en cache côté Streamlit."""
    return get_connection()


# =========================
# Détection de la source
# =========================

def detect_source_from_url(url: str) -> Optional[str]:
    """
    Détecte la source à partir du host de l'URL.
    Retourne l'un de : 'Indeed', 'Apec', 'Jooble', ou None si inconnu.
    """
    try:
        parsed = urlparse(url)
        host = parsed.netloc.lower()
    except Exception:
        return None

    if "indeed" in host:
        return "Indeed"
    if "apec" in host:
        return "Apec"
    if "jooble" in host:
        return "Jooble"
    return None


def get_scraper_for_source(source: str):
    """
    Retourne la fonction de scraping adaptée à la source.
    Lève une ValueError si la source n'est pas supportée ou si le scraper manque.
    """
    if source == "Indeed":
        if fetch_indeed_offer is None:
            raise ValueError("Scraper Indeed non disponible (fetch_indeed_offer introuvable).")
        return fetch_indeed_offer

    if source == "Apec":
        if fetch_apec_offer is None:
            raise ValueError("Scraper Apec non disponible (fetch_apec_offer introuvable).")
        return fetch_apec_offer

    if source == "Jooble":
        if fetch_jooble_offer is None:
            raise ValueError("Client Jooble non disponible (fetch_jooble_offer introuvable).")
        return fetch_jooble_offer

    raise ValueError(f"Source non supportée : {source}")


# =========================
# Pipeline d'ajout d'offre
# =========================

def add_offer_from_url(
    url: str,
    source: str,
    conn: duckdb.DuckDBPyConnection,
) -> Tuple[Dict, Dict]:
    """
    Exécute le pipeline complet :
    - scraping / API pour récupérer raw_job,
    - process_offre(raw_job) -> offre_nlp,
    - upsert_offre_complete(offre_nlp) dans DuckDB.

    Retourne (raw_job, offre_nlp) pour affichage éventuel.
    """
    if process_offre is None:
        raise RuntimeError("process_offre() est introuvable. Vérifie l'import radar.pipeline.process_offre.")

    if upsert_offre_complete is None:
        raise RuntimeError("upsert_offre_complete() est introuvable. Vérifie l'import radar.db.io.")

    scraper = get_scraper_for_source(source)

    # 1. Scraping / API
    raw_job = scraper(url)
    if raw_job is None:
        raise RuntimeError("Le scraper n'a rien retourné (raw_job est vide ou None).")

    # 2. Traitement NLP / enrichissement
    offre_nlp = process_offre(raw_job)
    if offre_nlp is None:
        raise RuntimeError("process_offre() n'a rien retourné (offre_nlp est vide ou None).")

    # 3. Insertion en base
    # Selon ton implémentation réelle : avec ou sans connexion en paramètre
    try:
        upsert_offre_complete(conn, offre_nlp)  # type: ignore[arg-type]
    except TypeError:
        # fallback si ta fonction ne prend pas de connexion
        upsert_offre_complete(offre_nlp)  # type: ignore[call-arg]

    return raw_job, offre_nlp


# =========================
# UI principale
# =========================

def main() -> None:
    st.title("➕ Ajouter une nouvelle offre")

    st.markdown(
        """
Cette page permet d'ajouter **manuellement** une offre au corpus RADAR
à partir d'une simple URL (Indeed, Apec, Jooble, ...).

Pipeline :
1. détection / sélection de la source ;
2. scraping ou appel API pour récupérer l'offre brute ;
3. passage dans `process_offre()` pour extraire les variables structurées ;
4. insertion / mise à jour dans la base via `upsert_offre_complete()`.
"""
    )

    conn = get_cached_connection()

    st.markdown("### 1. Saisie de l'URL")

    url = st.text_input("URL de l'offre", placeholder="https://...")

    auto_source = detect_source_from_url(url) if url else None

    st.markdown("### 2. Source de l'offre")

    source_options = ["Indeed", "Apec", "Jooble"]
    default_index = 0

    if auto_source in source_options:
        default_index = source_options.index(auto_source)

    source = st.selectbox(
        "Source (détectée automatiquement si possible)",
        options=source_options,
        index=default_index,
        help=(
            "La source est suggérée à partir du domaine de l'URL, "
            "mais vous pouvez la modifier manuellement."
        ),
    )

    st.markdown("### 3. Scraper et ajouter dans l'entrepôt")

    if st.button("Scraper & ajouter l'offre", type="primary", use_container_width=True):
        if not url:
            st.error("Merci de renseigner une URL d'offre.")
            return

        with st.spinner(f"Scraping de l'offre depuis {source}..."):
            try:
                raw_job, offre_nlp = add_offer_from_url(url, source, conn)
            except Exception as e:
                st.error(
                    "Une erreur est survenue lors de l'ajout de l'offre. "
                    "Vérifiez les logs et l'implémentation des scrapers / process_offre()."
                )
                st.exception(e)
                return

        st.success("Offre ajoutée (ou mise à jour) avec succès dans l'entrepôt RADAR.")

        with st.expander("Voir les données brutes (raw_job)"):
            st.json(raw_job)

        with st.expander("Voir l'offre enrichie (offre_nlp)"):
            st.json(offre_nlp)

        st.info(
            "L'offre est désormais disponible dans fact_offre (et tables associées), "
            "et sera visible dans les autres pages (vue globale, carte, compétences, NLP, comparaison)."
        )


if __name__ == "__main__":
    main()
