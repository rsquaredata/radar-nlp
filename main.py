from __future__ import annotations

"""
Page principale - Vue d'ensemble du marché des offres d'emploi RADAR.

Cette page s'appuie sur :
- fact_offre
- dim_date
- dim_ville -> dim_departement -> dim_region
- dim_metier
- dim_source

Fonctionnalités :
- Filtres globaux : période, région, métier
- Indicateurs clés (nb d'offres, nb de régions couvertes, nb de métiers, nb de sources)
- Évolution temporelle des offres
- Top régions par volume d'offres
- Top métiers par volume d'offres
"""

import datetime as dt

import duckdb
import pandas as pd
import plotly.express as px
import streamlit as st

from radar.db.schema import get_connection


# =========================
# Connexion & utilitaires
# =========================

@st.cache_resource(show_spinner=False)
def get_cached_connection() -> duckdb.DuckDBPyConnection:
    """Connexion DuckDB mise en cache côté Streamlit."""
    return get_connection()


def _quote_list(values: list[str]) -> str:
    """Construit une liste de valeurs SQL-safe pour un IN (...) simple."""
    if not values:
        return ""
    escaped = [v.replace("'", "''") for v in values]
    return ", ".join(f"'{v}'" for v in escaped)


# =========================
# Chargement des filtres
# =========================

@st.cache_data(show_spinner=False)
def load_filter_values():
    """
    Charge les valeurs nécessaires aux filtres globaux :
    - liste des régions
    - liste des métiers
    - liste des sources
    - min / max date (période couverte)
    """
    conn = get_cached_connection()

    regions = conn.execute(
        """
        SELECT DISTINCT nom_region
        FROM dim_region
        ORDER BY nom_region;
        """
    ).df()["nom_region"].tolist()

    metiers = conn.execute(
        """
        SELECT DISTINCT nom_metier
        FROM dim_metier
        ORDER BY nom_metier;
        """
    ).df()["nom_metier"].tolist()

    sources = conn.execute(
        """
        SELECT DISTINCT nom_source
        FROM dim_source
        ORDER BY nom_source;
        """
    ).df()["nom_source"].tolist()

    date_bounds = conn.execute(
        """
        SELECT 
            MIN(d.date) AS min_date,
            MAX(d.date) AS max_date
        FROM fact_offre fo
        JOIN dim_date d USING(date_id);
        """
    ).fetchone()

    min_date, max_date = date_bounds
    if isinstance(min_date, str):
        min_date = dt.date.fromisoformat(min_date)
    if isinstance(max_date, str):
        max_date = dt.date.fromisoformat(max_date)

    return regions, metiers, sources, min_date, max_date


# =========================
# Chargement des données agrégées
# =========================

@st.cache_data(show_spinner=False)
def load_global_kpis(
    selected_regions: list[str],
    selected_metiers: list[str],
    selected_sources: list[str],
    date_start: dt.date,
    date_end: dt.date,
) -> dict:
    """
    Charge les indicateurs globaux :
    - nb_offres
    - nb_regions
    - nb_metiers
    - nb_sources
    """
    conn = get_cached_connection()

    region_clause = ""
    if selected_regions:
        region_in = _quote_list(selected_regions)
        region_clause = f"AND r.nom_region IN ({region_in})"

    metier_clause = ""
    if selected_metiers:
        metier_in = _quote_list(selected_metiers)
        metier_clause = f"AND m.nom_metier IN ({metier_in})"

    source_clause = ""
    if selected_sources:
        source_in = _quote_list(selected_sources)
        source_clause = f"AND s.nom_source IN ({source_in})"

    query = f"""
    SELECT
        COUNT(DISTINCT fo.offre_id)      AS nb_offres,
        COUNT(DISTINCT r.region_id)      AS nb_regions,
        COUNT(DISTINCT m.metier_id)      AS nb_metiers,
        COUNT(DISTINCT s.source_id)      AS nb_sources
    FROM fact_offre fo
    JOIN dim_date d       USING(date_id)
    JOIN dim_ville v      USING(ville_id)
    JOIN dim_departement dp USING(departement_id)
    JOIN dim_region r     USING(region_id)
    JOIN dim_metier m     USING(metier_id)
    JOIN dim_source s     USING(source_id)
    WHERE d.date BETWEEN '{date_start}' AND '{date_end}'
      {region_clause}
      {metier_clause}
      {source_clause};
    """

    row = conn.execute(query).fetchone()
    if row is None:
        return {
            "nb_offres": 0,
            "nb_regions": 0,
            "nb_metiers": 0,
            "nb_sources": 0,
        }

    nb_offres, nb_regions, nb_metiers, nb_sources = row
    return {
        "nb_offres": nb_offres or 0,
        "nb_regions": nb_regions or 0,
        "nb_metiers": nb_metiers or 0,
        "nb_sources": nb_sources or 0,
    }


@st.cache_data(show_spinner=False)
def load_timeseries_offres(
    selected_regions: list[str],
    selected_metiers: list[str],
    selected_sources: list[str],
    date_start: dt.date,
    date_end: dt.date,
):
    """
    Charge l'évolution temporelle du nombre d'offres (agrégation par mois).
    """
    conn = get_cached_connection()

    region_clause = ""
    if selected_regions:
        region_in = _quote_list(selected_regions)
        region_clause = f"AND r.nom_region IN ({region_in})"

    metier_clause = ""
    if selected_metiers:
        metier_in = _quote_list(selected_metiers)
        metier_clause = f"AND m.nom_metier IN ({metier_in})"

    source_clause = ""
    if selected_sources:
        source_in = _quote_list(selected_sources)
        source_clause = f"AND s.nom_source IN ({source_in})"

    query = f"""
    SELECT
        DATE_TRUNC('month', d.date)::DATE AS mois,
        COUNT(DISTINCT fo.offre_id)       AS nb_offres
    FROM fact_offre fo
    JOIN dim_date d       USING(date_id)
    JOIN dim_ville v      USING(ville_id)
    JOIN dim_departement dp USING(departement_id)
    JOIN dim_region r     USING(region_id)
    JOIN dim_metier m     USING(metier_id)
    JOIN dim_source s     USING(source_id)
    WHERE d.date BETWEEN '{date_start}' AND '{date_end}'
      {region_clause}
      {metier_clause}
      {source_clause}
    GROUP BY mois
    ORDER BY mois;
    """

    return conn.execute(query).df()


@st.cache_data(show_spinner=False)
def load_top_regions(
    selected_regions: list[str],
    selected_metiers: list[str],
    selected_sources: list[str],
    date_start: dt.date,
    date_end: dt.date,
    top_n: int = 10,
):
    """
    Charge les top régions par nombre d'offres.
    """
    conn = get_cached_connection()

    region_clause = ""
    if selected_regions:
        region_in = _quote_list(selected_regions)
        region_clause = f"AND r.nom_region IN ({region_in})"

    metier_clause = ""
    if selected_metiers:
        metier_in = _quote_list(selected_metiers)
        metier_clause = f"AND m.nom_metier IN ({metier_in})"

    source_clause = ""
    if selected_sources:
        source_in = _quote_list(selected_sources)
        source_clause = f"AND s.nom_source IN ({source_in})"

    query = f"""
    SELECT
        r.nom_region,
        COUNT(DISTINCT fo.offre_id) AS nb_offres
    FROM fact_offre fo
    JOIN dim_date d       USING(date_id)
    JOIN dim_ville v      USING(ville_id)
    JOIN dim_departement dp USING(departement_id)
    JOIN dim_region r     USING(region_id)
    JOIN dim_metier m     USING(metier_id)
    JOIN dim_source s     USING(source_id)
    WHERE d.date BETWEEN '{date_start}' AND '{date_end}'
      {region_clause}
      {metier_clause}
      {source_clause}
    GROUP BY r.nom_region
    ORDER BY nb_offres DESC
    LIMIT {int(top_n)};
    """

    return conn.execute(query).df()


@st.cache_data(show_spinner=False)
def load_top_metiers(
    selected_regions: list[str],
    selected_metiers: list[str],
    selected_sources: list[str],
    date_start: dt.date,
    date_end: dt.date,
    top_n: int = 10,
):
    """
    Charge les top métiers par nombre d'offres.
    """
    conn = get_cached_connection()

    region_clause = ""
    if selected_regions:
        region_in = _quote_list(selected_regions)
        region_clause = f"AND r.nom_region IN ({region_in})"

    metier_clause = ""
    if selected_metiers:
        metier_in = _quote_list(selected_metiers)
        metier_clause = f"AND m.nom_metier IN ({metier_in})"

    source_clause = ""
    if selected_sources:
        source_in = _quote_list(selected_sources)
        source_clause = f"AND s.nom_source IN ({source_in})"

    query = f"""
    SELECT
        m.nom_metier,
        COUNT(DISTINCT fo.offre_id) AS nb_offres
    FROM fact_offre fo
    JOIN dim_date d       USING(date_id)
    JOIN dim_ville v      USING(ville_id)
    JOIN dim_departement dp USING(departement_id)
    JOIN dim_region r     USING(region_id)
    JOIN dim_metier m     USING(metier_id)
    JOIN dim_source s     USING(source_id)
    WHERE d.date BETWEEN '{date_start}' AND '{date_end}'
      {region_clause}
      {metier_clause}
      {source_clause}
    GROUP BY m.nom_metier
    ORDER BY nb_offres DESC
    LIMIT {int(top_n)};
    """

    return conn.execute(query).df()


# =========================
# UI principale
# =========================

def main() -> None:
    st.title("Vue d'ensemble du marché (RADAR)")

    st.markdown(
        """
Cette page fournit une vue globale des offres d'emploi présentes dans l'entrepôt RADAR.

Vous pouvez filtrer le corpus par **période**, **région**, **métier** et **source**,
puis observer :
- des indicateurs de synthèse (nombre d'offres, de régions, de métiers, de sources) ;
- l'évolution temporelle du volume d'offres ;
- les régions et métiers les plus représentés.
"""
    )

    # --- Filtres globaux ---
    regions, metiers, sources, min_date, max_date = load_filter_values()

    with st.sidebar:
        st.header("Filtres globaux")

        selected_regions = st.multiselect(
            "Régions",
            options=regions,
            default=[],
            help="Si aucun choix, toutes les régions sont conservées."
        )

        selected_metiers = st.multiselect(
            "Métiers",
            options=metiers,
            default=[],
            help="Si aucun choix, tous les métiers sont conservés."
        )

        selected_sources = st.multiselect(
            "Sources",
            options=sources,
            default=[],
            help="Si aucun choix, toutes les sources sont conservées."
        )

        date_range = st.date_input(
            "Période",
            value=(min_date, max_date),
            min_value=min_date,
            max_value=max_date,
        )
        if isinstance(date_range, tuple):
            date_start, date_end = date_range
        else:
            date_start, date_end = min_date, max_date

        st.markdown("---")

        top_n = st.slider(
            "Top N (régions / métiers)",
            min_value=5,
            max_value=30,
            value=10,
            step=5,
        )

    # --- KPIs globaux ---
    with st.spinner("Calcul des indicateurs globaux..."):
        kpis = load_global_kpis(
            selected_regions=selected_regions,
            selected_metiers=selected_metiers,
            selected_sources=selected_sources,
            date_start=date_start,
            date_end=date_end,
        )

    nb_offres = kpis["nb_offres"]
    nb_regions = kpis["nb_regions"]
    nb_metiers = kpis["nb_metiers"]
    nb_sources = kpis["nb_sources"]

    if nb_offres == 0:
        st.warning("Aucune offre ne satisfait les filtres actuels.")
        return

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Offres", f"{nb_offres}")
    col2.metric("Régions", f"{nb_regions}")
    col3.metric("Métiers", f"{nb_metiers}")
    col4.metric("Sources", f"{nb_sources}")

    st.markdown("---")

    # --- Évolution temporelle ---
    st.subheader("Évolution temporelle du nombre d'offres")

    with st.spinner("Chargement des séries temporelles..."):
        df_ts = load_timeseries_offres(
            selected_regions=selected_regions,
            selected_metiers=selected_metiers,
            selected_sources=selected_sources,
            date_start=date_start,
            date_end=date_end,
        )

    if df_ts.empty:
        st.info("Pas de données temporelles disponibles pour les filtres actuels.")
    else:
        fig_ts = px.line(
            df_ts,
            x="mois",
            y="nb_offres",
            labels={"mois": "Mois", "nb_offres": "Nombre d'offres"},
            title="Volume d'offres par mois",
        )
        fig_ts.update_layout(xaxis=dict(dtick="M1", tickformat="%Y-%m"))
        st.plotly_chart(fig_ts, use_container_width=True)

    st.markdown("---")

    # --- Top régions ---
    st.subheader("Top régions par nombre d'offres")

    with st.spinner("Chargement des régions..."):
        df_regions = load_top_regions(
            selected_regions=selected_regions,
            selected_metiers=selected_metiers,
            selected_sources=selected_sources,
            date_start=date_start,
            date_end=date_end,
            top_n=top_n,
        )

    if df_regions.empty:
        st.info("Aucune région ne ressort avec les filtres actuels.")
    else:
        fig_reg = px.bar(
            df_regions.sort_values("nb_offres", ascending=True),
            x="nb_offres",
            y="nom_region",
            orientation="h",
            labels={"nb_offres": "Nombre d'offres", "nom_region": "Région"},
            title="Top régions (par volume d'offres)",
        )
        st.plotly_chart(fig_reg, use_container_width=True)

    # --- Top métiers ---
    st.subheader("Top métiers par nombre d'offres")

    with st.spinner("Chargement des métiers..."):
        df_metiers = load_top_metiers(
            selected_regions=selected_regions,
            selected_metiers=selected_metiers,
            selected_sources=selected_sources,
            date_start=date_start,
            date_end=date_end,
            top_n=top_n,
        )

    if df_metiers.empty:
        st.info("Aucun métier ne ressort avec les filtres actuels.")
    else:
        fig_met = px.bar(
            df_metiers.sort_values("nb_offres", ascending=True),
            x="nb_offres",
            y="nom_metier",
            orientation="h",
            labels={"nb_offres": "Nombre d'offres", "nom_metier": "Métier"},
            title="Top métiers (par volume d'offres)",
        )
        st.plotly_chart(fig_met, use_container_width=True)

    # Optionnel : affichage des tables
    with st.expander("Afficher les données agrégées (régions & métiers)"):
        st.markdown("**Top régions**")
        st.dataframe(df_regions, use_container_width=True)
        st.markdown("**Top métiers**")
        st.dataframe(df_metiers, use_container_width=True)


if __name__ == "__main__":
    main()
