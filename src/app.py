from __future__ import annotations

import re
import sqlite3
from pathlib import Path
from typing import Optional, Tuple

import pandas as pd
import plotly.express as px
import streamlit as st

# Optional (table avancée)
try:
    from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode
    HAS_AGGRID = True
except Exception:
    HAS_AGGRID = False


# -----------------------------
# UI CONFIG
# -----------------------------
st.set_page_config(
    page_title="Job Mining Dashboard",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
)

CUSTOM_CSS = """
<style>
/* Global */
.block-container { padding-top: 1.2rem; padding-bottom: 1.5rem; }
[data-testid="stHeader"] { background: rgba(0,0,0,0); }
h1, h2, h3 { letter-spacing: -0.02em; }
.small-muted { color: rgba(120,120,120,0.9); font-size: 0.9rem; }
.kpi-card {
  padding: 14px 16px; border-radius: 16px;
  border: 1px solid rgba(120,120,120,0.18);
  background: linear-gradient(135deg, rgba(120,120,120,0.08), rgba(80,80,80,0.03));
}
.badge {
  display:inline-block; padding: 2px 10px; border-radius: 999px;
  border: 1px solid rgba(120,120,120,0.25);
  font-size: 12px; margin-right: 6px;
}
.hr { border-top: 1px solid rgba(120,120,120,0.18); margin: 0.8rem 0; }
.sidebar-title { font-weight:700; font-size:1.05rem; margin-bottom: 0.25rem; }
.navpill {
  padding: 8px 12px; border-radius: 999px;
  border: 1px solid rgba(120,120,120,0.22);
  background: rgba(120,120,120,0.06);
}
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


# -----------------------------
# PATHS (adapt if needed)
# -----------------------------
DEFAULT_DB = Path("../data/offers.sqlite")
DEFAULT_CLUSTERED = Path("../data/clustered_k25_final.csv")  # optionnel
DEFAULT_SKILLS_BY_CLUSTER = Path("../data/skills_by_cluster.csv")  # optionnel
DEFAULT_TERMS_BY_CLUSTER = Path("../data/top_terms_by_cluster.csv")  # optionnel


# -----------------------------
# HELPERS
# -----------------------------
def safe_read_csv(path: Path) -> Optional[pd.DataFrame]:
    if path and path.exists():
        try:
            return pd.read_csv(path)
        except Exception:
            return None
    return None


@st.cache_data(show_spinner=False)
def load_sqlite_offers(db_path: str) -> pd.DataFrame:
    if not Path(db_path).exists():
        return pd.DataFrame()

    con = sqlite3.connect(db_path)
    try:
        # table offers (from your loader)
        df = pd.read_sql_query("SELECT * FROM offers", con)
    finally:
        con.close()

    # Normalize common columns
    for col in ["title", "employer", "location", "contract_type", "salary", "source", "url", "raw_text"]:
        if col in df.columns:
            df[col] = df[col].astype(str).replace({"nan": ""})

    # Some datasets may use different column names
    if "uid" not in df.columns:
        # attempt to build uid
        if "source" in df.columns and "offer_id" in df.columns:
            df["uid"] = df["source"].astype(str) + "::" + df["offer_id"].astype(str)
        else:
            df["uid"] = df.index.astype(str)

    return df


@st.cache_data(show_spinner=False)
def load_clustered_csv(path: str) -> pd.DataFrame:
    p = Path(path)
    if not p.exists():
        return pd.DataFrame()
    df = pd.read_csv(p)
    return df


def enrich_with_clusters(offers: pd.DataFrame, clustered: pd.DataFrame) -> pd.DataFrame:
    """
    Merge offers with clustered CSV when possible.
    We try uid, else url.
    """
    if offers.empty or clustered.empty:
        return offers

    # Identify columns
    c_uid = "uid" if "uid" in clustered.columns else None
    c_url = "url" if "url" in clustered.columns else None

    # cluster column might be "cluster" or "cluster_id"
    cluster_col = None
    for c in ["cluster", "cluster_id"]:
        if c in clustered.columns:
            cluster_col = c
            break

    label_col = None
    for c in ["cluster_label", "label"]:
        if c in clustered.columns:
            label_col = c
            break

    keep_cols = []
    if c_uid: keep_cols.append(c_uid)
    if c_url and c_url not in keep_cols: keep_cols.append(c_url)
    if cluster_col: keep_cols.append(cluster_col)
    if label_col and label_col not in keep_cols: keep_cols.append(label_col)

    if not keep_cols or not cluster_col:
        return offers

    csmall = clustered[keep_cols].copy()

    # Merge priority: uid > url
    out = offers.copy()
    if c_uid and "uid" in out.columns:
        out = out.merge(csmall, how="left", left_on="uid", right_on=c_uid, suffixes=("", "_c"))
    elif c_url and "url" in out.columns:
        out = out.merge(csmall, how="left", left_on="url", right_on=c_url, suffixes=("", "_c"))

    # Harmonize names
    if cluster_col and cluster_col in out.columns:
        out.rename(columns={cluster_col: "cluster"}, inplace=True)
    if label_col and label_col in out.columns:
        out.rename(columns={label_col: "cluster_label"}, inplace=True)

    # Cleanup duplicate keys
    for col in [c_uid, c_url]:
        if col and col in out.columns and col not in ["uid", "url"]:
            out.drop(columns=[col], inplace=True)

    return out


def contains_any(text: str, keywords: list[str]) -> bool:
    t = (text or "").lower()
    return any((k.lower() in t) for k in keywords if k and k.strip())


def clean_url(url: str) -> str:
    url = (url or "").strip()
    return url


def apply_filters(df: pd.DataFrame,
                  q: str,
                  sources: list[str],
                  contract_types: list[str],
                  clusters: list[int],
                  remote_only: bool,
                  min_text_len: int) -> pd.DataFrame:
    out = df.copy()

    # Basic robustness
    for c in ["source", "contract_type", "cluster_label", "title", "employer", "location", "url"]:
        if c in out.columns:
            out[c] = out[c].fillna("").astype(str)

    if "raw_text" in out.columns:
        out["raw_text"] = out["raw_text"].fillna("").astype(str)
    else:
        out["raw_text"] = ""

    if min_text_len > 0:
        out = out[out["raw_text"].str.len() >= min_text_len]

    if sources:
        out = out[out["source"].isin(sources)]

    if contract_types:
        out = out[out["contract_type"].isin(contract_types)]

    if clusters and "cluster" in out.columns:
        out = out[out["cluster"].isin(clusters)]

    if remote_only:
        # try common fields
        if "remote" in out.columns:
            out = out[out["remote"].astype(str).str.lower().isin(["yes", "true", "1"])]
        else:
            # fallback: detect in text
            out = out[out["raw_text"].str.contains(r"télétravail|remote|hybrid|hybride", case=False, regex=True)]

    if q.strip():
        qq = q.strip().lower()
        mask = (
            out["title"].str.lower().str.contains(qq, na=False)
            | out["employer"].str.lower().str.contains(qq, na=False)
            | out["location"].str.lower().str.contains(qq, na=False)
            | out["raw_text"].str.lower().str.contains(qq, na=False)
        )
        out = out[mask]

    return out


def make_download(df: pd.DataFrame, filename: str, label: str):
    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button(label=label, data=csv, file_name=filename, mime="text/csv")


# -----------------------------
# SIDEBAR / NAV
# -----------------------------
st.sidebar.markdown('<div class="sidebar-title">🧠 Job Mining</div>', unsafe_allow_html=True)
st.sidebar.caption("France Travail • HelloWork • Adzuna • (Clusters K=25)")

db_path = st.sidebar.text_input("Chemin SQLite", value=str(DEFAULT_DB))
clustered_path = st.sidebar.text_input("Chemin CSV clusterisé (optionnel)", value=str(DEFAULT_CLUSTERED))

st.sidebar.markdown('<div class="hr"></div>', unsafe_allow_html=True)

PAGES = [
    ("🏠 Overview", "overview"),
    ("📋 Toutes les offres", "offers"),
    ("🧩 Clusters", "clusters"),
    ("🛠️ Skills & Outils", "skills"),
    ("🔎 Recherche avancée", "search"),
    ("⚙️ Qualité & Debug", "debug"),
]
page_label = st.sidebar.radio("Navigation", [p[0] for p in PAGES], index=0)
page = dict(PAGES)[page_label]

st.sidebar.markdown('<div class="hr"></div>', unsafe_allow_html=True)
st.sidebar.caption("Astuce: charge d’abord SQLite. Ajoute ensuite le CSV clusterisé pour enrichir l’analyse.")


# -----------------------------
# LOAD DATA
# -----------------------------
offers_df = load_sqlite_offers(db_path)
clustered_df = load_clustered_csv(clustered_path) if clustered_path else pd.DataFrame()
df = enrich_with_clusters(offers_df, clustered_df)

# Ensure URL clickable
if "url" in df.columns:
    df["url"] = df["url"].astype(str).apply(clean_url)

# Offer "apply_url"
# If you have a dedicated apply_url column, we use it; else url acts as apply_url.
if "apply_url" not in df.columns:
    df["apply_url"] = df["url"] if "url" in df.columns else ""


# -----------------------------
# COMMON FILTER CHOICES
# -----------------------------
sources_all = sorted([s for s in df["source"].dropna().unique().tolist()]) if "source" in df.columns else []
contract_all = sorted([c for c in df["contract_type"].dropna().unique().tolist() if str(c).strip()]) if "contract_type" in df.columns else []
clusters_all = sorted([int(x) for x in df["cluster"].dropna().unique().tolist()]) if "cluster" in df.columns else []


# -----------------------------
# PAGE: OVERVIEW
# -----------------------------
if page == "overview":
    st.title("🧠 Job Mining Dashboard")
    st.caption("Une vue moderne et actionnable de toutes tes offres (SQLite) + analyse text-mining (clusters).")

    if df.empty:
        st.error("Aucune donnée chargée. Vérifie le chemin vers offers.sqlite.")
        st.stop()

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown('<div class="kpi-card">', unsafe_allow_html=True)
        st.metric("Offres", f"{len(df):,}".replace(",", " "))
        st.markdown("</div>", unsafe_allow_html=True)
    with c2:
        st.markdown('<div class="kpi-card">', unsafe_allow_html=True)
        st.metric("Sources", f"{df['source'].nunique() if 'source' in df.columns else 0}")
        st.markdown("</div>", unsafe_allow_html=True)
    with c3:
        st.markdown('<div class="kpi-card">', unsafe_allow_html=True)
        n_urls = df["url"].astype(str).str.len().gt(0).sum() if "url" in df.columns else 0
        st.metric("URLs", f"{n_urls:,}".replace(",", " "))
        st.markdown("</div>", unsafe_allow_html=True)
    with c4:
        st.markdown('<div class="kpi-card">', unsafe_allow_html=True)
        st.metric("Clusters", f"{df['cluster'].nunique() if 'cluster' in df.columns else 0}")
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown('<div class="hr"></div>', unsafe_allow_html=True)

    left, right = st.columns([1.2, 1])
    with left:
        st.subheader("Répartition par source")
        if "source" in df.columns:
            src = df["source"].value_counts().reset_index()
            src.columns = ["source", "n"]
            fig = px.bar(src, x="source", y="n")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Colonne 'source' non trouvée.")

    with right:
        st.subheader("Top localisations")
        if "location" in df.columns:
            loc = df["location"].fillna("").astype(str)
            loc = loc[loc.str.len().gt(0)]
            top = loc.value_counts().head(12).reset_index()
            top.columns = ["location", "n"]
            fig2 = px.bar(top, x="n", y="location", orientation="h")
            st.plotly_chart(fig2, use_container_width=True)
        else:
            st.info("Colonne 'location' non trouvée.")

    st.markdown('<div class="hr"></div>', unsafe_allow_html=True)
    st.subheader("Actions rapides")
    colA, colB, colC = st.columns(3)
    with colA:
        st.write("📋 Voir toutes les offres")
        st.caption("Table filtrable + lien pour postuler")
        if st.button("Ouvrir la liste", use_container_width=True):
            st.session_state["_nav"] = "offers"
            st.rerun()
    with colB:
        st.write("🧩 Explorer les clusters")
        st.caption("Top termes + exemples + tailles")
        if st.button("Ouvrir clusters", use_container_width=True):
            st.session_state["_nav"] = "clusters"
            st.rerun()
    with colC:
        st.write("🛠️ Skills")
        st.caption("Compétences par cluster")
        if st.button("Ouvrir skills", use_container_width=True):
            st.session_state["_nav"] = "skills"
            st.rerun()

    # quick nav hook
    if st.session_state.get("_nav"):
        # emulate nav (streamlit doesn't allow direct change of radio)
        st.info("Utilise la sidebar pour naviguer (Overview / Offres / Clusters / Skills).")
        st.session_state["_nav"] = None


# -----------------------------
# PAGE: ALL OFFERS
# -----------------------------
elif page == "offers":
    st.title("📋 Toutes les offres")
    if df.empty:
        st.error("Aucune donnée chargée.")
        st.stop()

    # Filters row
    f1, f2, f3, f4, f5 = st.columns([1.4, 1, 1, 1, 1])
    with f1:
        q = st.text_input("Recherche (titre, entreprise, lieu, texte)", value="")
    with f2:
        src_sel = st.multiselect("Source", options=sources_all, default=[])
    with f3:
        ct_sel = st.multiselect("Contrat", options=contract_all, default=[])
    with f4:
        cl_sel = st.multiselect("Cluster", options=clusters_all, default=[])
    with f5:
        remote_only = st.toggle("Remote only", value=False)

    min_len = st.slider("Taille min texte (raw_text)", 0, 5000, 0, 100)

    filtered = apply_filters(df, q, src_sel, ct_sel, cl_sel, remote_only, min_len)

    st.caption(f"Résultats: **{len(filtered):,}** offres".replace(",", " "))

    make_download(filtered, "offers_filtered.csv", "⬇️ Télécharger CSV filtré")

    # Display table with clickable links
    show_cols = [c for c in [
        "uid", "source", "title", "employer", "location",
        "contract_type", "salary", "cluster", "cluster_label",
        "url", "apply_url"
    ] if c in filtered.columns]

    view = filtered[show_cols].copy()

    # Make clickable links in Streamlit: use markdown links column
    def to_link(u: str) -> str:
        u = str(u or "").strip()
        if not u:
            return ""
        return f"[Postuler]({u})"

    if "apply_url" in view.columns:
        view["postuler"] = view["apply_url"].apply(to_link)
        # Hide raw apply_url from display
        if "apply_url" in view.columns:
            view.drop(columns=["apply_url"], inplace=True)

    # Use AgGrid if available
    if HAS_AGGRID:
        gb = GridOptionsBuilder.from_dataframe(view)
        gb.configure_pagination(paginationAutoPageSize=False, paginationPageSize=25)
        gb.configure_default_column(filter=True, sortable=True, resizable=True)
        gb.configure_column("postuler", headerName="Postuler", cellRenderer="markdownRenderer")
        gridOptions = gb.build()

        AgGrid(
            view,
            gridOptions=gridOptions,
            update_mode=GridUpdateMode.NO_UPDATE,
            allow_unsafe_jscode=True,
            fit_columns_on_grid_load=True,
            theme="streamlit",
            height=620,
        )
    else:
        st.info("Pour une table plus avancée, installe `streamlit-aggrid` (optionnel).")
        st.dataframe(view, use_container_width=True, height=620)

    st.markdown('<div class="hr"></div>', unsafe_allow_html=True)

    st.subheader("📰 Aperçu d’une offre")
    if len(filtered) > 0:
        pick_idx = st.number_input("Index ligne (dans la table filtrée)", min_value=0, max_value=len(filtered)-1, value=0)
        row = filtered.iloc[int(pick_idx)].to_dict()

        left, right = st.columns([1.7, 1])
        with left:
            st.markdown(f"### {row.get('title','')}")
            st.write(f"**Entreprise :** {row.get('employer','')}")
            st.write(f"**Lieu :** {row.get('location','')}")
            st.write(f"**Contrat :** {row.get('contract_type','')}")
            st.write(f"**Salaire :** {row.get('salary','')}")
            if "cluster_label" in row and row.get("cluster_label"):
                st.write(f"**Cluster :** {row.get('cluster')} — {row.get('cluster_label')}")
            st.markdown(f"➡️ **Lien :** {row.get('url','')}")
            st.markdown(f"✅ **Postuler :** {row.get('apply_url','')}")
        with right:
            st.markdown("### Texte (extrait)")
            txt = (row.get("raw_text") or "")[:1200]
            st.text_area("raw_text", value=txt, height=360)
    else:
        st.warning("Aucune offre après filtres.")


# -----------------------------
# PAGE: CLUSTERS
# -----------------------------
elif page == "clusters":
    st.title("🧩 Clusters")
    if "cluster" not in df.columns:
        st.warning("Aucune colonne 'cluster' trouvée. Charge `clustered_k25_final.csv` ou applique les labels.")
        st.stop()

    # cluster sizes
    sizes = df["cluster"].value_counts().reset_index()
    sizes.columns = ["cluster", "n_offers"]
    sizes = sizes.sort_values("cluster")

    st.subheader("Taille des clusters")
    fig = px.bar(sizes, x="cluster", y="n_offers")
    st.plotly_chart(fig, use_container_width=True)

    st.markdown('<div class="hr"></div>', unsafe_allow_html=True)

    # choose cluster
    cid = st.selectbox("Choisir un cluster", options=sorted(df["cluster"].dropna().unique().tolist()))
    sub = df[df["cluster"] == cid].copy()

    col1, col2, col3 = st.columns([1.2, 1.2, 1])
    with col1:
        st.markdown('<div class="kpi-card">', unsafe_allow_html=True)
        st.metric("Offres dans cluster", f"{len(sub):,}".replace(",", " "))
        st.markdown("</div>", unsafe_allow_html=True)
    with col2:
        label = ""
        if "cluster_label" in sub.columns:
            label = sub["cluster_label"].dropna().astype(str).head(1).tolist()
            label = label[0] if label else ""
        st.markdown('<div class="kpi-card">', unsafe_allow_html=True)
        st.metric("Label", label if label else "(non labellisé)")
        st.markdown("</div>", unsafe_allow_html=True)
    with col3:
        top_sources = sub["source"].value_counts().head(3).to_dict() if "source" in sub.columns else {}
        st.markdown('<div class="kpi-card">', unsafe_allow_html=True)
        st.write("Top sources")
        st.caption(" • ".join([f"{k}:{v}" for k, v in top_sources.items()]) if top_sources else "-")
        st.markdown("</div>", unsafe_allow_html=True)

    # terms & skills tables if available
    terms = safe_read_csv(DEFAULT_TERMS_BY_CLUSTER)
    skills = safe_read_csv(DEFAULT_SKILLS_BY_CLUSTER)

    a, b = st.columns(2)
    with a:
        st.subheader("Top termes (si dispo)")
        if terms is not None and "cluster" in terms.columns:
            st.dataframe(terms[terms["cluster"] == cid], use_container_width=True, height=260)
        else:
            st.info("Fichier `top_terms_by_cluster.csv` non trouvé ou mauvais format.")
    with b:
        st.subheader("Skills (si dispo)")
        if skills is not None and "cluster" in skills.columns:
            st.dataframe(skills[skills["cluster"] == cid], use_container_width=True, height=260)
        else:
            st.info("Fichier `skills_by_cluster.csv` non trouvé ou mauvais format.")

    st.markdown('<div class="hr"></div>', unsafe_allow_html=True)
    st.subheader("Offres (extraits)")
    cols = [c for c in ["title", "employer", "location", "contract_type", "salary", "url"] if c in sub.columns]
    st.dataframe(sub[cols].head(200), use_container_width=True, height=520)

    make_download(sub, f"cluster_{cid}.csv", f"⬇️ Télécharger ce cluster (cluster={cid})")


# -----------------------------
# PAGE: SKILLS
# -----------------------------
elif page == "skills":
    st.title("🛠️ Skills & Outils")
    skills = safe_read_csv(DEFAULT_SKILLS_BY_CLUSTER)
    terms = safe_read_csv(DEFAULT_TERMS_BY_CLUSTER)

    if skills is None and terms is None:
        st.warning("Je ne trouve ni `skills_by_cluster.csv` ni `top_terms_by_cluster.csv` dans ../data.")
        st.info("Tu peux quand même exploiter les clusters via l’onglet Clusters.")
        st.stop()

    left, right = st.columns(2)
    with left:
        st.subheader("Skills par cluster")
        if skills is not None:
            st.dataframe(skills, use_container_width=True, height=640)
            make_download(skills, "skills_by_cluster.csv", "⬇️ Télécharger skills_by_cluster.csv")
        else:
            st.info("skills_by_cluster.csv non disponible.")

    with right:
        st.subheader("Top termes TF-IDF par cluster")
        if terms is not None:
            st.dataframe(terms, use_container_width=True, height=640)
            make_download(terms, "top_terms_by_cluster.csv", "⬇️ Télécharger top_terms_by_cluster.csv")
        else:
            st.info("top_terms_by_cluster.csv non disponible.")


# -----------------------------
# PAGE: ADVANCED SEARCH
# -----------------------------
elif page == "search":
    st.title("🔎 Recherche avancée")
    if df.empty:
        st.error("Aucune donnée chargée.")
        st.stop()

    st.caption("Ici tu peux faire des requêtes style *mini-moteur de recherche*.")

    query = st.text_input("Mots-clés (ex: python AND spark OR databricks)", value="python AND (spark OR databricks)")
    limit = st.slider("Nombre max de résultats", 50, 5000, 300, 50)

    def parse_bool_query(q: str) -> Tuple[list[str], list[str]]:
        # ultra simple: tokens >= 2 chars
        tokens = re.findall(r"[A-Za-zÀ-ÖØ-öø-ÿ0-9\+\#\.\-]{2,}", q)
        tokens = [t.lower() for t in tokens if t.lower() not in {"and", "or", "not"}]
        # return must-have / any-have (naive)
        must = []
        any_ = []
        if "and" in q.lower():
            must = tokens
        else:
            any_ = tokens
        return must, any_

    must, any_ = parse_bool_query(query)

    base = df.copy()
    text = (
        base.get("title", "").astype(str) + " " +
        base.get("employer", "").astype(str) + " " +
        base.get("location", "").astype(str) + " " +
        base.get("raw_text", "").astype(str)
    ).str.lower()

    if must:
        mask = pd.Series(True, index=base.index)
        for t in must:
            mask &= text.str.contains(re.escape(t), na=False)
        res = base[mask]
    elif any_:
        mask = pd.Series(False, index=base.index)
        for t in any_:
            mask |= text.str.contains(re.escape(t), na=False)
        res = base[mask]
    else:
        res = base

    res = res.head(limit)
    st.caption(f"Résultats: **{len(res)}** (limit={limit})")

    cols = [c for c in ["source","title","employer","location","contract_type","salary","cluster","cluster_label","url"] if c in res.columns]
    st.dataframe(res[cols], use_container_width=True, height=620)
    make_download(res, "search_results.csv", "⬇️ Télécharger résultats")


# -----------------------------
# PAGE: DEBUG / QUALITY
# -----------------------------
elif page == "debug":
    st.title("⚙️ Qualité & Debug")
    st.caption("Pour comprendre ce que Streamlit lit réellement et détecter les colonnes disponibles.")

    st.subheader("Fichiers")
    st.write("SQLite:", db_path, "✅" if Path(db_path).exists() else "❌ introuvable")
    st.write("CSV clusterisé:", clustered_path, "✅" if Path(clustered_path).exists() else "❌ (optionnel)")

    st.markdown('<div class="hr"></div>', unsafe_allow_html=True)
    st.subheader("Colonnes détectées (SQLite -> offers)")
    st.write(list(offers_df.columns))

    st.subheader("Colonnes après enrichissement clusters")
    st.write(list(df.columns))

    st.markdown('<div class="hr"></div>', unsafe_allow_html=True)
    st.subheader("Échantillon (10 lignes)")
    st.dataframe(df.head(10), use_container_width=True)

    st.markdown('<div class="hr"></div>', unsafe_allow_html=True)
    st.subheader("Stats manquants")
    missing = pd.DataFrame({
        "col": df.columns,
        "missing_%": (df.isna().mean() * 100).round(2).values
    }).sort_values("missing_%", ascending=False)
    st.dataframe(missing, use_container_width=True, height=520)
