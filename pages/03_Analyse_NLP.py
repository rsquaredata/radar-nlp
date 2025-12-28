from __future__ import annotations

from typing import Tuple

import duckdb
import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st
from sklearn.cluster import KMeans
from sklearn.decomposition import LatentDirichletAllocation, TruncatedSVD
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer

from radar.db.schema import get_connection


"""
Page 03_Analyse_NLP - Analyse textuelle des offres d'emploi.

Cette page s'appuie sur :
- fact_offre
- dim_texte
- dim_date
- dim_ville -> dim_departement -> dim_region
- dim_metier
- dim_source

Fonctionnalités :
- Filtres globaux : période, région, métier, source
- Échantillonnage d'un corpus de textes (dim_texte)
- LDA (topics) avec affichage des top mots par thème
- Clustering K-Means sur TF-IDF + exploration des textes par cluster
- Projection 2D des documents (SVD/LSA) colorée par cluster ou topic dominant
"""


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
# Filtres globaux & chargement corpus
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
        today = pd.Timestamp.today().date()
        min_date = max_date = today
    else:
        if isinstance(min_date, str):
            min_date = pd.to_datetime(min_date).date()
        if isinstance(max_date, str):
            max_date = pd.to_datetime(max_date).date()

    return regions, metiers, sources, min_date, max_date


@st.cache_data(show_spinner=False)
def load_text_sample(
    selected_regions: list[str],
    selected_metiers: list[str],
    selected_sources: list[str],
    date_start,
    date_end,
    max_docs: int = 500,
    min_len: int = 100,
) -> pd.DataFrame:
    """
    Charge un échantillon de textes depuis dim_texte, en tenant compte des filtres.

    Le corpus est construit à partir de fact_offre, puis relié à dim_texte :
    - filtres région / métier / source / période
    - filtre sur longueur minimale du texte
    - limite max_docs
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
            t.texte_id,
            COALESCE(t.texte_clean, t.texte_complet) AS texte
        FROM fact_offre fo
        JOIN dim_texte t   USING(texte_id)
        JOIN dim_date d    USING(date_id)
        JOIN dim_ville v   USING(ville_id)
        JOIN dim_departement dp USING(departement_id)
        JOIN dim_region r  USING(region_id)
        JOIN dim_metier m  USING(metier_id)
        JOIN dim_source s  USING(source_id)
        WHERE d.date BETWEEN '{date_start}' AND '{date_end}'
          {region_clause}
          {metier_clause}
          {source_clause}
          AND t.texte_complet IS NOT NULL
          AND length(COALESCE(t.texte_clean, t.texte_complet)) >= {int(min_len)}
        LIMIT {int(max_docs)}
    """
    df = conn.execute(query).fetchdf()
    df = df.dropna(subset=["texte"])
    return df


# =========================
# LDA
# =========================

@st.cache_data(show_spinner=False)
def compute_lda(
    texts: list[str],
    n_topics: int = 8,
    max_features: int = 5000,
    random_state: int = 42,
) -> Tuple[LatentDirichletAllocation, CountVectorizer, np.ndarray]:
    """
    Calcule une LDA simple sur une liste de textes.
    Retourne : (lda_model, vectorizer, doc_topic_matrix)
    """
    vectorizer = CountVectorizer(
        max_features=max_features,
        stop_words="english",  # TODO: remplacer/compléter avec des stopwords FR
    )
    X = vectorizer.fit_transform(texts)

    lda = LatentDirichletAllocation(
        n_components=n_topics,
        learning_method="batch",
        random_state=random_state,
    )
    doc_topic = lda.fit_transform(X)
    return lda, vectorizer, doc_topic


def format_topics(
    lda: LatentDirichletAllocation,
    vectorizer: CountVectorizer,
    n_top_words: int = 10,
) -> pd.DataFrame:
    """
    Retourne un DataFrame avec les top mots par topic.
    """
    feature_names = np.array(vectorizer.get_feature_names_out())
    topics = []
    for topic_idx, topic in enumerate(lda.components_):
        top_indices = topic.argsort()[::-1][:n_top_words]
        top_words = feature_names[top_indices]
        topics.append(
            {
                "topic": topic_idx,
                "top_words": ", ".join(top_words),
            }
        )
    return pd.DataFrame(topics)


# =========================
# TF-IDF + KMeans + 2D
# =========================

@st.cache_data(show_spinner=False)
def compute_tfidf(
    texts: list[str],
    max_features: int = 5000,
) -> Tuple[TfidfVectorizer, np.ndarray]:
    """
    Calcule une représentation TF-IDF des textes.
    """
    vectorizer = TfidfVectorizer(
        max_features=max_features,
        stop_words="english",  # TODO: stopwords FR
    )
    X = vectorizer.fit_transform(texts)
    return vectorizer, X


@st.cache_data(show_spinner=False)
def compute_kmeans(
    X,
    n_clusters: int = 8,
    random_state: int = 42,
) -> np.ndarray:
    """
    Applique K-Means sur la matrice TF-IDF.
    Retourne les labels de cluster.
    """
    if X.shape[0] < n_clusters:
        # Pas assez de docs pour autant de clusters
        n_clusters = max(2, X.shape[0] // 2) if X.shape[0] >= 2 else 1

    if n_clusters < 2:
        # Cas extrême : très peu de documents
        return np.zeros(X.shape[0], dtype=int)

    km = KMeans(
        n_clusters=n_clusters,
        random_state=random_state,
        n_init="auto",
    )
    labels = km.fit_predict(X)
    return labels


@st.cache_data(show_spinner=False)
def compute_2d_projection(X, random_state: int = 42) -> np.ndarray:
    """
    Projette la matrice TF-IDF en 2D avec SVD (LSA).
    TODO: éventuellement remplacer par UMAP plus tard.
    """
    svd = TruncatedSVD(n_components=2, random_state=random_state)
    coords_2d = svd.fit_transform(X)
    return coords_2d


# =========================
# Page principale
# =========================

def main() -> None:
    st.title("Analyse NLP des offres")

    st.markdown(
        """
Cette page propose une exploration textuelle des offres d'emploi du corpus RADAR.

Le pipeline est le suivant :
- sélection d'un **corpus filtré** (région, métier, source, période) ;
- constitution d'un échantillon de textes (dim_texte) ;
- analyses :
  - **LDA** pour extraire des thèmes (topics) ;
  - **K-Means sur TF-IDF** pour regrouper les offres ;
  - **projection 2D** pour visualiser les documents.
"""
    )

    # --- Filtres globaux (comme les autres pages) ---
    regions, metiers, sources, min_date, max_date = load_filter_values()

    with st.sidebar:
        st.header("Filtres corpus")

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

        max_docs = st.slider(
            "Nombre max de documents analysés",
            min_value=100,
            max_value=5000,
            value=500,
            step=100,
        )

        min_len = st.slider(
            "Longueur minimale du texte (caractères)",
            min_value=20,
            max_value=2000,
            value=200,
            step=50,
        )

        st.markdown("---")

        n_topics = st.slider(
            "Nombre de topics (LDA)",
            min_value=3,
            max_value=20,
            value=8,
            step=1,
        )

        n_clusters = st.slider(
            "Nombre de clusters (K-Means)",
            min_value=2,
            max_value=20,
            value=8,
            step=1,
        )

        st.caption("Les calculs sont faits sur un échantillon filtré d'offres.")

    # --- Chargement du corpus ---
    with st.spinner("Chargement des textes depuis la base..."):
        df_texts = load_text_sample(
            selected_regions=selected_regions,
            selected_metiers=selected_metiers,
            selected_sources=selected_sources,
            date_start=date_start,
            date_end=date_end,
            max_docs=max_docs,
            min_len=min_len,
        )

    if df_texts.empty:
        st.warning(
            "Aucun texte ne satisfait les filtres actuels "
            "(période / région / métier / source / longueur minimale)."
        )
        return

    st.write(f"Corpus analysé : **{len(df_texts)}** documents.")

    texts = df_texts["texte"].astype(str).tolist()

    # On pré-calcul TF-IDF ici pour le réutiliser dans les onglets
    with st.spinner("Préparation des représentations TF-IDF..."):
        tfidf_vec, X_tfidf = compute_tfidf(texts, max_features=5000)

    # Tabs LDA / Clustering / Projection
    tab_lda, tab_cluster, tab_2d = st.tabs(
        ["LDA (Topics)", "Clustering K-Means", "Projection 2D"]
    )

    # ======== LDA ========
    with tab_lda:
        st.subheader("LDA – Thèmes des offres")

        with st.spinner("Calcul LDA en cours..."):
            lda_model, cv, doc_topic = compute_lda(
                texts,
                n_topics=n_topics,
                max_features=5000,
            )
            df_topics = format_topics(lda_model, cv, n_top_words=10)

        st.write("Top mots par topic :")
        st.dataframe(
            df_topics,
            use_container_width=True,
            hide_index=True,
        )

        # Répartition globale des topics
        topic_distribution = doc_topic.mean(axis=0)
        df_topic_dist = pd.DataFrame(
            {
                "topic": list(range(len(topic_distribution))),
                "poids_moyen": topic_distribution,
            }
        )

        st.write("Importance moyenne de chaque topic :")
        st.bar_chart(
            df_topic_dist.set_index("topic")["poids_moyen"]
        )

    # ======== Clustering K-Means ========
    with tab_cluster:
        st.subheader("Clustering des offres (K-Means sur TF-IDF)")

        with st.spinner("Clustering K-Means en cours..."):
            labels = compute_kmeans(X_tfidf, n_clusters=n_clusters)

        df_clusters = df_texts.copy()
        df_clusters["cluster"] = labels

        st.write("Répartition des documents par cluster :")
        st.bar_chart(
            df_clusters["cluster"].value_counts().sort_index()
        )

        st.write("Aperçu des textes par cluster :")
        cluster_to_show = st.selectbox(
            "Cluster à afficher",
            options=sorted(df_clusters["cluster"].unique().tolist()),
        )

        df_sample = df_clusters[df_clusters["cluster"] == cluster_to_show].head(10)
        for _, row in df_sample.iterrows():
            st.markdown(f"**Texte ID {row['texte_id']} – cluster {row['cluster']}**")
            st.write(row["texte"][:500] + "…")
            st.markdown("---")

    # ======== Projection 2D ========
    with tab_2d:
        st.subheader("Visualisation 2D des documents")

        color_option = st.radio(
            "Coloration des points",
            options=["Topic dominant", "Cluster K-Means"],
            index=0,
        )

        with st.spinner("Calcul projection 2D + labels en cours..."):
            coords_2d = compute_2d_projection(X_tfidf)
            labels_km = compute_kmeans(X_tfidf, n_clusters=n_clusters)
            lda_model, cv, doc_topic = compute_lda(
                texts,
                n_topics=n_topics,
                max_features=5000,
            )

        df_vis = df_texts.copy()
        df_vis["x"] = coords_2d[:, 0]
        df_vis["y"] = coords_2d[:, 1]
        df_vis["cluster"] = labels_km
        df_vis["topic_dominant"] = doc_topic.argmax(axis=1)

        if color_option == "Cluster K-Means":
            color_col = "cluster"
        else:
            color_col = "topic_dominant"

        fig = px.scatter(
            df_vis,
            x="x",
            y="y",
            color=color_col,
            hover_data=["texte_id"],
            title="Projection 2D des documents",
            height=700,
        )
        st.plotly_chart(fig, use_container_width=True)

        st.caption(
            "Projection 2D basée sur une réduction de dimension (SVD/LSA) des vecteurs TF-IDF. "
            "Coloration par cluster K-Means ou topic LDA dominant."
        )


if __name__ == "__main__":
    main()
