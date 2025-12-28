from __future__ import annotations

import datetime as dt
from typing import Dict, List, Tuple

import duckdb
import pandas as pd
import plotly.express as px
import streamlit as st

from radar.db.schema import get_connection


"""
Page 05_Comparaison - Comparaison entre couples région / métier.

Cette page s'appuie sur :
- fact_offre
- dim_region
- dim_metier
- dim_date
- dim_source
- dim_texte
- fact_offre_skill
- dim_skill

Fonctionnalités :
- Choix d'un couple (Région A, Métier A) et (Région B, Métier B)
- Filtres globaux : période, source(s)
- Comparaison :
    - nombre d'offres
    - longueur moyenne des annonces
    - top compétences (skills) pour chaque couple
    - tableau comparatif des compétences
"""


# =========================
# Connexion & utilitaires
# =========================

@st.cache_resource(show_spinner=False)
def get_cached_connection() -> duckdb.DuckDBPyConnection:
    """Connexion DuckDB mise en cache côté Streamlit."""
    return get_connection()


def _quote_list(values: List[str]) -> str:
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
    - min / max date (période couverte dans fact_offre)
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
# Fonctions de comparaison
# =========================

def _build_base_where_clause(
    date_start: dt.date,
    date_end: dt.date,
    selected_sources: List[str],
) -> str:
    """
    Construit la partie commune du WHERE (période + source).
    """
    source_clause = ""
    if selected_sources:
        source_in = _quote_list(selected_sources)
        source_clause = f"AND s.nom_source IN ({source_in})"

    where = f"""
        WHERE d.date BETWEEN '{date_start}' AND '{date_end}'
          {source_clause}
    """
    return where


def _build_group_filter_clause(
    region: str | None,
    metier: str | None,
) -> str:
    """
    Construit la partie de filtre spécifique à un couple (région, métier).
    Si region ou metier est None, on ne filtre pas dessus.
    """
    clauses = []
    if region:
        clauses.append(f"r.nom_region = '{region.replace(\"'\", \"''\")}'")
    if metier:
        clauses.append(f"m.nom_metier = '{metier.replace(\"'\", \"''\")}'")

    if not clauses:
        return ""

    return "AND " + " AND ".join(clauses)


@st.cache_data(show_spinner=False)
def load_group_kpis(
    date_start: dt.date,
    date_end: dt.date,
    selected_sources: List[str],
    region: str | None,
    metier: str | None,
) -> Dict[str, float]:
    """
    Calcule quelques KPI pour un couple (région, métier) :
    - nb_offres
    - longueur moyenne du texte (caractères)
    """
    conn = get_cached_connection()

    base_where = _build_base_where_clause(date_start, date_end, selected_sources)
    group_clause = _build_group_filter_clause(region, metier)

    query = f"""
        SELECT
            COUNT(DISTINCT fo.offre_id) AS nb_offres,
            AVG(length(COALESCE(t.texte_clean, t.texte_complet))) AS len_moy
        FROM fact_offre fo
        JOIN dim_date d     USING(date_id)
        JOIN dim_ville v    USING(ville_id)
        JOIN dim_departement dp USING(departement_id)
        JOIN dim_region r   USING(region_id)
        JOIN dim_metier m   USING(metier_id)
        JOIN dim_source s   USING(source_id)
        LEFT JOIN dim_texte t USING(texte_id)
        {base_where}
          {group_clause}
    """

    row = conn.execute(query).fetchone()
    if row is None:
        return {"nb_offres": 0, "len_moy": None}

    nb_offres, len_moy = row
    return {
        "nb_offres": nb_offres or 0,
        "len_moy": len_moy,
    }


@st.cache_data(show_spinner=False)
def load_group_top_skills(
    date_start: dt.date,
    date_end: dt.date,
    selected_sources: List[str],
    region: str | None,
    metier: str | None,
    top_n: int = 20,
) -> pd.DataFrame:
    """
    Charge les top compétences pour un couple (région, métier).
    Retourne un DataFrame : nom_skill, freq.
    """
    conn = get_cached_connection()

    base_where = _build_base_where_clause(date_start, date_end, selected_sources)
    group_clause = _build_group_filter_clause(region, metier)

    query = f"""
        SELECT
            sk.nom_skill,
            COUNT(*) AS freq
        FROM fact_offre_skill fos
        JOIN dim_skill sk USING(skill_id)
        JOIN fact_offre fo USING(offre_id)
        JOIN dim_date d     USING(date_id)
        JOIN dim_ville v    USING(ville_id)
        JOIN dim_departement dp USING(departement_id)
        JOIN dim_region r   USING(region_id)
        JOIN dim_metier m   USING(metier_id)
        JOIN dim_source s   USING(source_id)
        {base_where}
          {group_clause}
        GROUP BY sk.nom_skill
        HAVING COUNT(*) > 0
        ORDER BY freq DESC
        LIMIT {int(top_n)};
    """

    df = conn.execute(query).df()
    return df


def _build_comparison_table(
    df_a: pd.DataFrame,
    df_b: pd.DataFrame,
    label_a: str,
    label_b: str,
) -> pd.DataFrame:
    """
    Construit un tableau comparatif des skills entre deux groupes.
    """
    df_a = df_a.rename(columns={"freq": f"freq_{label_a}"})
    df_b = df_b.rename(columns={"freq": f"freq_{label_b}"})

    df_merged = pd.merge(
        df_a,
        df_b,
        on="nom_skill",
        how="outer",
    ).fillna(0)

    df_merged["diff"] = df_merged[f"freq_{label_a}"] - df_merged[f"freq_{label_b}"]
    df_merged = df_merged.sort_values("diff", ascending=False)

    return df_merged


# =========================
# Page principale
# =========================

def main() -> None:
    st.title("Comparaison régions / métiers")

    st.markdown(
        """
Cette page permet de comparer deux couples **Région / Métier** sur plusieurs aspects :

- volume d'offres ;
- longueur moyenne des annonces ;
- compétences les plus fréquentes (skills) ;
- tableau comparatif des compétences entre les deux groupes.

Les filtres globaux (période, sources) s'appliquent aux deux groupes.
"""
    )

    regions, metiers, sources, min_date, max_date = load_filter_values()

    # --- Filtres globaux ---
    with st.sidebar:
        st.header("Filtres globaux")

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

        top_n_skills = st.slider(
            "Nombre de compétences à afficher",
            min_value=5,
            max_value=50,
            value=20,
            step=5,
        )

        st.caption(
            "Les filtres s'appliquent de manière identique aux deux groupes (A et B)."
        )

    # --- Sélecteurs groupes A / B ---
    st.subheader("Sélection des deux groupes à comparer")

    col_a, col_b = st.columns(2)

    with col_a:
        st.markdown("### Groupe A")
        region_a = st.selectbox(
            "Région A",
            options=["(Toutes)"] + regions,
            index=0,
            key="region_a",
        )
        metier_a = st.selectbox(
            "Métier A",
            options=["(Tous)"] + metiers,
            index=0,
            key="metier_a",
        )

    with col_b:
        st.markdown("### Groupe B")
        region_b = st.selectbox(
            "Région B",
            options=["(Toutes)"] + regions,
            index=0,
            key="region_b",
        )
        metier_b = st.selectbox(
            "Métier B",
            options=["(Tous)"] + metiers,
            index=0,
            key="metier_b",
        )

    # Normalisation des valeurs (None si "(Toutes)" / "(Tous)")
    region_a_val = None if region_a == "(Toutes)" else region_a
    metier_a_val = None if metier_a == "(Tous)" else metier_a
    region_b_val = None if region_b == "(Toutes)" else region_b
    metier_b_val = None if metier_b == "(Tous)" else metier_b

    label_a = "A"
    label_b = "B"

    # --- KPI de base ---
    st.subheader("Indicateurs de base")

    kpi_a = load_group_kpis(
        date_start=date_start,
        date_end=date_end,
        selected_sources=selected_sources,
        region=region_a_val,
        metier=metier_a_val,
    )
    kpi_b = load_group_kpis(
        date_start=date_start,
        date_end=date_end,
        selected_sources=selected_sources,
        region=region_b_val,
        metier=metier_b_val,
    )

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### Groupe A")
        st.write(f"Région : **{region_a}**")
        st.write(f"Métier : **{metier_a}**")
        st.metric("Nombre d'offres", f"{kpi_a['nb_offres']}")
        if kpi_a["len_moy"] is not None:
            st.metric(
                "Longueur moyenne de l'annonce (caractères)",
                f"{kpi_a['len_moy']:.0f}",
            )
        else:
            st.write("Longueur moyenne de l'annonce : N/A")

    with col2:
        st.markdown("#### Groupe B")
        st.write(f"Région : **{region_b}**")
        st.write(f"Métier : **{metier_b}**")
        st.metric("Nombre d'offres", f"{kpi_b['nb_offres']}")
        if kpi_b["len_moy"] is not None:
            st.metric(
                "Longueur moyenne de l'annonce (caractères)",
                f"{kpi_b['len_moy']:.0f}",
            )
        else:
            st.write("Longueur moyenne de l'annonce : N/A")

    if kpi_a["nb_offres"] == 0 and kpi_b["nb_offres"] == 0:
        st.warning(
            "Aucune offre trouvée pour les deux groupes avec les filtres actuels."
        )
        return

    st.markdown("---")

    # --- Comparaison des compétences ---
    st.subheader("Comparaison des compétences (skills)")

    with st.spinner("Chargement des compétences pour les deux groupes..."):
        df_skills_a = load_group_top_skills(
            date_start=date_start,
            date_end=date_end,
            selected_sources=selected_sources,
            region=region_a_val,
            metier=metier_a_val,
            top_n=top_n_skills,
        )
        df_skills_b = load_group_top_skills(
            date_start=date_start,
            date_end=date_end,
            selected_sources=selected_sources,
            region=region_b_val,
            metier=metier_b_val,
            top_n=top_n_skills,
        )

    col_sa, col_sb = st.columns(2)

    with col_sa:
        st.markdown("#### Top compétences – Groupe A")
        if df_skills_a.empty:
            st.info("Aucune compétence trouvée pour le groupe A.")
        else:
            fig_a = px.bar(
                df_skills_a.sort_values("freq", ascending=True),
                x="freq",
                y="nom_skill",
                orientation="h",
                labels={"freq": "Fréquence", "nom_skill": "Compétence"},
                title="Top compétences (A)",
            )
            st.plotly_chart(fig_a, use_container_width=True)

    with col_sb:
        st.markdown("#### Top compétences – Groupe B")
        if df_skills_b.empty:
            st.info("Aucune compétence trouvée pour le groupe B.")
        else:
            fig_b = px.bar(
                df_skills_b.sort_values("freq", ascending=True),
                x="freq",
                y="nom_skill",
                orientation="h",
                labels={"freq": "Fréquence", "nom_skill": "Compétence"},
                title="Top compétences (B)",
            )
            st.plotly_chart(fig_b, use_container_width=True)

    # Tableau comparatif
    st.markdown("#### Tableau comparatif des compétences")

    if df_skills_a.empty and df_skills_b.empty:
        st.info("Aucune compétence à comparer pour les deux groupes.")
    else:
        df_comp = _build_comparison_table(
            df_a=df_skills_a,
            df_b=df_skills_b,
            label_a=label_a,
            label_b=label_b,
        )
        st.dataframe(
            df_comp,
            use_container_width=True,
        )

        st.caption(
            "La colonne `diff` est positive lorsque la compétence est plus fréquente dans le groupe A "
            "que dans le groupe B, et négative dans le cas contraire."
        )

        csv_comp = df_comp.to_csv(index=False).encode("utf-8")
        st.download_button(
            "Télécharger le tableau comparatif (CSV)",
            data=csv_comp,
            file_name="radar_comparaison_skills_A_vs_B.csv",
            mime="text/csv",
        )


if __name__ == "__main__":
    main()
