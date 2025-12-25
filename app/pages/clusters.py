import streamlit as st
import pandas as pd
from config import DB_PATH
from db import query_df
from llm_mistral import mistral_label_cluster

st.title("🧠 Clusters — Interprétation")

meta = query_df(str(DB_PATH), "SELECT cluster, cluster_label, top_terms, n_docs FROM clusters_meta ORDER BY n_docs DESC")
st.dataframe(meta, use_container_width=True, hide_index=True)

st.divider()

cluster_id = st.selectbox("Choisir un cluster", meta["cluster"].tolist(), index=0)
row = meta[meta["cluster"] == cluster_id].iloc[0]
st.subheader(f"Cluster {cluster_id} — {row['cluster_label']} ({int(row['n_docs'])} docs)")
st.write("**Top terms (interprétable)**")
st.code(str(row["top_terms"])[:3000])

# exemples depuis offers_enriched
ex = query_df(
    str(DB_PATH),
    """
    SELECT title, employer, region, url
    FROM offers_enriched
    WHERE cluster = :c
    ORDER BY published_date DESC
    LIMIT 12
    """,
    params={"c": int(cluster_id)},
)
st.write("**Exemples d'offres**")
st.dataframe(ex, use_container_width=True, hide_index=True)

st.divider()
st.subheader("✨ Interprétation automatique (Mistral - optionnel)")

use_llm = st.checkbox("Activer Mistral (nécessite MISTRAL_API_KEY + pip install mistralai)", value=False)
if use_llm:
    # skills: si tu as skills_by_cluster.csv en DB, sinon on passe vide
    skills = []
    examples_titles = ex["title"].dropna().tolist()
    data, err = mistral_label_cluster(
        top_terms=str(row["top_terms"]),
        skills=skills,
        examples_titles=examples_titles,
    )
    if err:
        st.error(err)
    else:
        st.json(data)
        st.success("Interprétation générée (factuelle, basée sur top_terms/exemples).")
