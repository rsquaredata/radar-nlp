"""
Page 04_Competences – Analyse des compétences demandées dans les offres.

Cette page s'appuie sur :
- fact_offre
- fact_offre_skill
- dim_skill
- dim_ville -> dim_departement -> dim_region
- dim_metier
- dim_date

Fonctionnalités :
- Filtres région, métier, période
- Top compétences (barplot horizontal)
- Répartition par région pour une compétence sélectionnée
- Tableau détaillé + export CSV
"""

import datetime as dt

import duckdb
import pandas as pd
import plotly.express as px
import streamlit as st

from radar.db.schema import get_connection


# =========================
# Utils / cache
# =========================

@st.cache_resource(show_spinner=False)
def get_cached_connection():
    """Connexion DuckDB mise en cache côté Streamlit."""
    return get_connection()  # utilise DEFAULT_DB_PATH interne


@st.cache_data(show_spinner=False)
def load_filter_values():
    """
    Charge les valeurs nécessaires aux filtres :
    - liste des régions
    - liste des métiers
    - min / max date
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

    # Période observée (à partir de dim_date + fact_offre)
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

    return regions, metiers, min_date, max_date


def _quote_list(values):
    """Construit une liste de valeurs SQL-safe pour un IN (...) simple."""
    if not values:
        return ""
    escaped = [v.replace("'", "''") for v in values]
    return ", ".join(f"'{v}'" for v in escaped)


@st.cache_data(show_spinner=False)
def load_skills_stats(
    selected_regions,
    selected_metiers,
    date_start,
    date_end,
    min_freq=10,
    top_n=30,
):
    """
    Charge les stats globales de compétences en fonction des filtres.
    Retourne un DataFrame avec :
      nom_skill, freq, freq_normalisee, nb_offres, regions_count, metiers_count
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

    query = f"""
    WITH filtered_offres AS (
        SELECT 
            fo.offre_id,
            r.nom_region,
            m.nom_metier
        FROM fact_offre fo
        JOIN dim_ville v       USING(ville_id)
        JOIN dim_departement d USING(departement_id)
        JOIN dim_region r      USING(region_id)
        JOIN dim_metier m      USING(metier_id)
        JOIN dim_date dd       USING(date_id)
        WHERE dd.date BETWEEN '{date_start}' AND '{date_end}'
        {region_clause}
        {metier_clause}
    ),
    skill_counts AS (
        SELECT
            sk.skill_id,
            sk.nom_skill,
            COUNT(*) AS freq,
            COUNT(DISTINCT fo.offre_id) AS nb_offres
        FROM fact_offre_skill fos
        JOIN dim_skill sk USING(skill_id)
        JOIN filtered_offres fo USING(offre_id)
        GROUP BY sk.skill_id, sk.nom_skill
    ),
    skill_regions AS (
        SELECT 
            sk.skill_id,
            COUNT(DISTINCT fo.nom_region) AS regions_count
        FROM fact_offre_skill fos
        JOIN dim_skill sk USING(skill_id)
        JOIN filtered_offres fo USING(offre_id)
        GROUP BY sk.skill_id
    ),
    skill_metiers AS (
        SELECT
            sk.skill_id,
            COUNT(DISTINCT fo.nom_metier) AS metiers_count
        FROM fact_offre_skill fos
        JOIN dim_skill sk USING(skill_id)
        JOIN filtered_offres fo USING(offre_id)
        GROUP BY sk.skill_id
    )
    SELECT
        sc.skill_id,
        sc.nom_skill,
        sc.freq,
        sc.nb_offres,
        sr.regions_count,
        sm.metiers_count
    FROM skill_counts sc
    LEFT JOIN skill_regions sr USING(skill_id)
    LEFT JOIN skill_metiers sm USING(skill_id)
    WHERE sc.freq >= {int(min_freq)}
    ORDER BY sc.freq DESC
    LIMIT {int(top_n)};
    """

    df = conn.execute(query).df()

    if not df.empty:
        total = df["freq"].sum()
        df["freq_normalisee"] = df["freq"] / total
    else:
        df["freq_normalisee"] = []

    return df


@st.cache_data(show_spinner=False)
def load_skill_by_region(
    skill_name,
    selected_regions,
    selected_metiers,
    date_start,
    date_end,
):
    """
    Charge la répartition d'une compétence donnée par région.
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

    query = f"""
    SELECT
        r.nom_region,
        COUNT(*) AS freq
    FROM fact_offre_skill fos
    JOIN dim_skill sk USING(skill_id)
    JOIN fact_offre fo USING(offre_id)
    JOIN dim_ville v       USING(ville_id)
    JOIN dim_departement d USING(departement_id)
    JOIN dim_region r      USING(region_id)
    JOIN dim_metier m      USING(metier_id)
    JOIN dim_date dd       USING(date_id)
    WHERE sk.nom_skill = '{skill_name.replace("'", "''")}'
      AND dd.date BETWEEN '{date_start}' AND '{date_end}'
      {region_clause}
      {metier_clause}
    GROUP BY r.nom_region
    ORDER BY freq DESC;
    """

    return conn.execute(query).df()


# =========================
# UI principale
# =========================

def main():
    st.title("🧠 Analyse des compétences demandées")

    st.markdown(
        """
Cette page permet d'analyser les compétences les plus demandées dans les offres
d'emploi présentes dans l'entrepôt RADAR.

Vous pouvez filtrer par région, par métier et par période, puis explorer :
- les compétences les plus fréquentes ;
- leur dispersion géographique ;
- un tableau détaillé exportable.
"""
    )

    # --- Filtres ---
    regions, metiers, min_date, max_date = load_filter_values()

    with st.sidebar:
        st.header("Filtres")

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

        date_range = st.date_input(
            "Période",
            value=(min_date, max_date),
            min_value=min_date,
            max_value=max_date,
        )
        if isinstance(date_range, tuple):
            date_start, date_end = date_range
        else:
            date_start, date_end = min_date, max_date  # fallback

        st.markdown("---")

        min_freq = st.number_input(
            "Fréquence minimale",
            min_value=1,
            max_value=1000,
            value=10,
            step=1,
            help="Compétences apparaissant moins souvent sont filtrées."
        )

        top_n = st.slider(
            "Nombre de compétences à afficher",
            min_value=5,
            max_value=50,
            value=20,
            step=5,
        )

    # --- Données principales ---
    with st.spinner("Chargement des statistiques de compétences..."):
        df_skills = load_skills_stats(
            selected_regions=selected_regions,
            selected_metiers=selected_metiers,
            date_start=date_start,
            date_end=date_end,
            min_freq=min_freq,
            top_n=top_n,
        )

    if df_skills.empty:
        st.warning("Aucune compétence ne satisfait les filtres actuels.")
        return

    # --- Graphique top compétences ---
    st.subheader("Top compétences demandées")

    fig = px.bar(
        df_skills.sort_values("freq", ascending=True),
        x="freq",
        y="nom_skill",
        orientation="h",
        labels={"freq": "Fréquence", "nom_skill": "Compétence"},
        title="Compétences les plus fréquentes (dans le corpus filtré)",
    )
    st.plotly_chart(fig, use_container_width=True)

    # --- Détails pour une compétence sélectionnée ---
    st.subheader("Répartition géographique pour une compétence")

    selected_skill = st.selectbox(
        "Choisir une compétence",
        options=df_skills["nom_skill"].tolist(),
        index=0,
    )

    df_skill_region = load_skill_by_region(
        skill_name=selected_skill,
        selected_regions=selected_regions,
        selected_metiers=selected_metiers,
        date_start=date_start,
        date_end=date_end,
    )

    if df_skill_region.empty:
        st.info("Pas de répartition régionale disponible pour cette compétence avec les filtres actuels.")
    else:
        fig_reg = px.bar(
            df_skill_region,
            x="nom_region",
            y="freq",
            labels={
                "nom_region": "Région",
                "freq": f"Nombre d'occurrences de {selected_skill}",
            },
            title=f"Répartition de « {selected_skill} » par région",
        )
        fig_reg.update_xaxes(tickangle=45)
        st.plotly_chart(fig_reg, use_container_width=True)

    # --- Tableau détaillé + export ---
    st.subheader("Tableau détaillé")

    st.dataframe(
        df_skills[
            [
                "nom_skill",
                "freq",
                "freq_normalisee",
                "nb_offres",
                "regions_count",
                "metiers_count",
            ]
        ],
        use_container_width=True,
    )

    csv = df_skills.to_csv(index=False).encode("utf-8")
    st.download_button(
        "Télécharger les résultats (CSV)",
        data=csv,
        file_name="radar_competences.csv",
        mime="text/csv",
    )


if __name__ == "__main__":
    main()
