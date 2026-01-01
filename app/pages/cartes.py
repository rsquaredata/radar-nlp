from __future__ import annotations

import streamlit as st
import pandas as pd

from components import inject_premium_css, top_navbar
from config import DB_PATH, DEFAULT_TABLE
from db import query_df
from geo import fig_jobs_map
from charts import kpis


# =========================
# 1) CSS + NAVBAR
# =========================
inject_premium_css()
top_navbar(active="Carte")


# =========================
# 2) Chargement des données
# =========================
df = query_df(str(DB_PATH), f"SELECT * FROM {DEFAULT_TABLE}")

if df.empty:
    st.error("Aucune donnée disponible pour la carte.")
    st.stop()

if "lat" not in df.columns or "lon" not in df.columns:
    st.error("Les colonnes 'lat' et 'lon' sont absentes de la table. Impossible d’afficher la carte.")
    st.stop()


# =========================
# 3) HERO / ENTÊTE
# =========================
st.markdown(
    """
<div style="
  display:flex;
  flex-direction:column;
  gap:.4rem;
  padding:1.1rem 1.4rem;
  border-radius:18px;
  border:1px solid rgba(148,163,184,.35);
  background:radial-gradient(circle at 0 0,rgba(59,130,246,.14),rgba(15,23,42,.96));
  box-shadow:0 18px 40px rgba(15,23,42,.75);
  margin-bottom: 1rem;
">
  <div style="font-size:1.05rem;opacity:.9;">🗺️ CARTE</div>
  <div style="font-size:1.6rem;font-weight:800;letter-spacing:.04em;">
    Cartographie des offres d’emploi Data & IA
  </div>
  <div style="font-size:.9rem;opacity:.85;max-width:860px;">
    Visualise la distribution géographique des offres multi-sources.
    La carte est interactive : zoom, déplacement, survol des points pour voir
    le détail des offres (titre, employeur, région, source, etc.).
  </div>
</div>
""",
    unsafe_allow_html=True,
)


# =========================
# 4) FILTRES
# =========================
st.markdown("#### 🎯 Filtres carte")

col1, col2, col3 = st.columns([1.2, 1.1, 1.1])

with col1:
    regions = sorted(df["region"].dropna().unique()) if "region" in df.columns else []
    region_sel = st.multiselect(
        "Région",
        options=regions,
        default=regions,
        placeholder="Choisis une ou plusieurs régions",
    )

with col2:
    sources = sorted(df["source"].dropna().unique()) if "source" in df.columns else []
    source_sel = st.multiselect(
        "Source",
        options=sources,
        default=sources,
        placeholder="France Travail, HelloWork, Adzuna…",
    )

with col3:
    clusters_labels = (
        sorted(df["cluster_label"].dropna().unique())
        if "cluster_label" in df.columns
        else []
    )
    cluster_sel = st.multiselect(
        "Cluster (famille de poste)",
        options=clusters_labels,
        default=clusters_labels,  # on garde tout par défaut
        placeholder="Filtrer par cluster de métier",
    )

col4, col5 = st.columns([1.3, 1])

with col4:
    color_mode = st.radio(
        "Coloriser les points par :",
        options=["Cluster métier", "Région", "Source"],
        horizontal=True,
    )

with col5:
    remote_filter = st.radio(
        "Télétravail",
        options=["Tous", "Télétravail uniquement", "Sans télétravail"],
        horizontal=True,
    )

col6, col7 = st.columns([1.2, 1])

with col6:
    nb_points_max = st.slider(
        "Nombre max. de points à afficher sur la carte (échantillonnage si nécessaire)",
        min_value=100,
        max_value=10000,
        value=3000,
        step=100,
    )

with col7:
    zoom_default = st.slider(
        "Niveau de zoom par défaut",
        min_value=3,
        max_value=8,
        value=5,
    )


# =========================
# 5) Application des filtres
# =========================
df_map = df.copy()

# Ne garder que les géocodées
df_map["lat"] = pd.to_numeric(df_map["lat"], errors="coerce")
df_map["lon"] = pd.to_numeric(df_map["lon"], errors="coerce")
df_map = df_map.dropna(subset=["lat", "lon"])

total_geo_before = len(df_map)

if region_sel and "region" in df_map.columns:
    df_map = df_map[df_map["region"].isin(region_sel)]

if source_sel and "source" in df_map.columns:
    df_map = df_map[df_map["source"].isin(source_sel)]

if cluster_sel and "cluster_label" in df_map.columns and len(cluster_sel) > 0:
    df_map = df_map[df_map["cluster_label"].isin(cluster_sel)]

if "remote_label" in df_map.columns:
    if remote_filter == "Télétravail uniquement":
        df_map = df_map[df_map["remote_label"].str.contains("télétravail", case=False, na=False)]
    elif remote_filter == "Sans télétravail":
        df_map = df_map[~df_map["remote_label"].str.contains("télétravail", case=False, na=False)]

total_geo_after = len(df_map)

st.caption(
    f"📌 Offres géolocalisées avant filtres : **{total_geo_before}** — "
    f"après filtres : **{total_geo_after}**"
)

if df_map.empty:
    st.warning("Aucune offre géolocalisée ne correspond aux filtres sélectionnés.")
    st.stop()

# Échantillonnage si trop de points
if total_geo_after > nb_points_max:
    df_map = df_map.sample(nb_points_max, random_state=42)
    sampled = True
else:
    sampled = False

# Colonne pour la couleur
if color_mode == "Cluster métier":
    color_by = "cluster_label"
elif color_mode == "Région":
    color_by = "region"
else:
    color_by = "source"

if sampled:
    caption_points = (
        f"Points affichés sur la carte : **{len(df_map)}** "
        f"(corpus filtré : {total_geo_after} offres géolocalisées ; "
        f"échantillonnage appliqué.)"
    )
else:
    caption_points = (
        f"Points affichés sur la carte : **{len(df_map)}** "
        f"(corpus filtré : {total_geo_after} offres géolocalisées ; "
        f"sans échantillonnage.)"
    )

st.caption(caption_points)


# =========================
# 6) KPIs + MINI-LÉGENDE
# =========================
stats = kpis(df_map)
col_k1, col_k2, col_k3, col_k4 = st.columns(4)
col_k1.metric("Offres géolocalisées", stats["Offres"])
col_k2.metric("Régions couvertes", stats["Régions"])
col_k3.metric("Clusters (familles)", stats["Clusters"])
col_k4.metric("Sources", stats["Sources"])

st.markdown("---")
st.markdown("##### 🧾 Mini-légende")

group_col = color_by if color_by in df_map.columns else None
if group_col:
    counts = (
        df_map.groupby(group_col)
        .size()
        .sort_values(ascending=False)
        .head(8)
    )
    total = len(df_map)
    legend_lines = []
    for name, cnt in counts.items():
        label = str(name) if name not in [None, "", "nan"] else "Non renseigné"
        pct = (cnt / total) * 100 if total > 0 else 0
        legend_lines.append(f"- **{label}** : {cnt} offres (~{pct:0.1f} %)")
    st.markdown("\n".join(legend_lines))
else:
    st.caption("Impossible de calculer la légende pour ce mode de couleur.")

st.markdown("---")


# =========================
# 7) CARTE INTERACTIVE
# =========================
st.subheader("🗺️ Carte interactive des offres")

fig = fig_jobs_map(df_map, color_by=color_by, zoom=zoom_default, height=650)

if fig is None:
    st.warning("Impossible de construire la carte (problème de géolocalisation).")
else:
    st.plotly_chart(
        fig,
        use_container_width=True,
        config={
            "scrollZoom": True,
            "displayModeBar": True,
        },
    )

    st.caption(
        "💡 Astuce : zoom avec la molette, déplacement par clic-drag, "
        "et survol des points pour voir le détail de l’offre."
    )
