from __future__ import annotations

"""
Page 02_Carte - Visualisation cartographique des offres par région.

Cette page s'appuie sur :
- fact_offre
- dim_date
- dim_ville -> dim_departement -> dim_region
- dim_metier
- dim_source

Fonctionnalités :
- Filtres : période, métier, source (et éventuellement sous-ensemble de régions)
- Carte choroplèthe des régions françaises (nombre d'offres)
- Histogramme des régions (Top N par volume d'offres)
- Tableau récapitulatif + export CSV
"""

import datetime as dt
import json
from pathlib import Path

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
    Charge les valeurs nécessaires aux filtres :
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

    # Cas où la base n'a encore aucune offre
    if min_date is None or max_date is None:
        today = dt.date.today()
        min_date = max_date = today
    else:
        if isinstance(min_date, str):
            min_date = dt.date.fromisoformat(min_date)
        if isinstance(max_date, str):
            max_date = dt.date.fromisoformat(max_date)

    return regions, metiers, sources, min_date, max_date


# =========================
# GeoJSON des régions
# =========================

@st.cache_data(show_spinner=False)
def load_regions_geojson() -> dict:
    """
    Charge le GeoJSON des régions françaises.

    Hypothèse :
    - fichier : data/geo/regions_france.geojson
    - propriété identifiante : properties.code
      (cohérente avec dim_region.code_region)
    """
    geojson_path = Path("data/geo/regions_france.geojson")

    if not geojson_path.exists():
        # On signale l'erreur dans l'UI, mais on renvoie un dict vide
        st.error(
            f"Fichier GeoJSON introuvable : {geojson_path}. "
            "Vérifiez le chemin ou adaptez load_regions_geojson()."
        )
        return {}

    with geojson_path.open("r", encoding="utf-8") as f:
        data = json.load(f)

    return data


# =========================
# Données agrégées par région
# =========================

@st.cache_data(show_spinner=False)
def load_region_stats(
    selected_regions: list[str],
    selected_metiers: list[str],
    selected_sources: list[str],
    date_start: dt.date,
    date_end: dt.date,
):
    """
    Charge le nombre d'offres par région, avec éventuellement des filtres.

    Retourne un DataFrame avec au moins :
    - code_region
    - nom_region
    - nb_offres
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
        r.code_region,
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
    GROUP BY r.code_region, r.nom_region
    ORDER BY nb_offres DESC;
    """

    df = conn.execute(query).df()

    # On force code_region en string pour matcher le GeoJSON (properties.code est une string)
    if not df.empty:
        df["code_region"] = df["code_region"].astype(str)

    return df


# =========================
# UI principale
# =========================

def main() -> None:
    st.title("Carte des offres par région")

    st.markdown(
        """
Cette page propose une visualisation cartographique du volume d'offres
d'emploi par région, à partir des données de l'entrepôt RADAR.

Vous pouvez filtrer le corpus par **période**, **métier** et **source**, 
éventuellement restreindre à un sous-ensemble de régions, puis explorer :
- une carte choroplèthe des régions françaises (nombre d'offres) ;
- un histogramme des régions les plus représentées ;
- un tableau récapitulatif exportable.
"""
    )

    # --- Filtres ---
    regions, metiers, sources, min_date, max_date = load_filter_values()

    with st.sidebar:
        st.header("Filtres carte")

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

        selected_regions = st.multiselect(
            "Régions (optionnel)",
            options=regions,
            default=[],
            help="Permet de restreindre l'analyse à certaines régions."
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
            "Top N (histogramme régions)",
            min_value=5,
            max_value=30,
            value=10,
            step=5,
        )

    # --- Chargement des données ---
    with st.spinner("Chargement des données par région..."):
        df_regions = load_region_stats(
            selected_regions=selected_regions,
            selected_metiers=selected_metiers,
            selected_sources=selected_sources,
            date_start=date_start,
            date_end=date_end,
        )

    if df_regions.empty:
        st.warning("Aucune offre ne satisfait les filtres actuels.")
        return

    # --- Carte choroplèthe ---
    st.subheader("Carte des offres par région")

    regions_geojson = load_regions_geojson()
    if not regions_geojson:
        st.info(
            "Impossible d'afficher la carte : GeoJSON non disponible ou invalide. "
            "Vérifiez le chemin dans load_regions_geojson()."
        )
    else:
        # On suppose que :
        # - dim_region.code_region correspond à properties.code dans le GeoJSON
        # - df_regions['code_region'] contient ces codes (cast en string au-dessus)
        fig_map = px.choropleth(
            df_regions,
            geojson=regions_geojson,
            locations="code_region",
            featureidkey="properties.code",
            color="nb_offres",
            hover_name="nom_region",
            color_continuous_scale="Blues",
            labels={"nb_offres": "Nombre d'offres"},
            title="Nombre d'offres par région",
        )
        fig_map.update_geos(
            fitbounds="locations",
            visible=False,
        )
        fig_map.update_layout(
            margin={"r": 0, "t": 50, "l": 0, "b": 0},
        )
        st.plotly_chart(fig_map, use_container_width=True)

    st.markdown("---")

    # --- Histogramme top régions ---
    st.subheader("Top régions par nombre d'offres")

    df_top = df_regions.nlargest(top_n, "nb_offres").sort_values("nb_offres", ascending=True)

    fig_bar = px.bar(
        df_top,
        x="nb_offres",
        y="nom_region",
        orientation="h",
        labels={"nb_offres": "Nombre d'offres", "nom_region": "Région"},
        title="Régions les plus représentées dans le corpus filtré",
    )
    st.plotly_chart(fig_bar, use_container_width=True)

    # --- Tableau + export ---
    st.subheader("Tableau détaillé par région")

    st.dataframe(
        df_regions[["code_region", "nom_region", "nb_offres"]],
        use_container_width=True,
    )

    csv = df_regions.to_csv(index=False).encode("utf-8")
    st.download_button(
        "Télécharger les données par région (CSV)",
        data=csv,
        file_name="radar_regions_offres.csv",
        mime="text/csv",
    )


if __name__ == "__main__":
    main()
