from __future__ import annotations

import textwrap
import streamlit as st

from components import inject_premium_css, top_navbar
from config import DB_PATH, DEFAULT_TABLE, MAX_ROWS_TABLE
from db import query_df


# =========================
# CONFIGURATION PAGE WIDE
# =========================
st.set_page_config(layout="wide", page_title="Offres d'Emploi", page_icon="💼")

inject_premium_css()
top_navbar(active="Dashboard")

# CSS avec page pleine largeur et background élégant
st.markdown("""
<style>
    /* Forcer la largeur complète */
    .main .block-container {
        max-width: 100% !important;
        padding-left: 3rem !important;
        padding-right: 3rem !important;
        padding-top: 2rem !important;
    }
    
    /* Background dégradé élégant pour toute la page */
    .main {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    
    /* Section principale avec fond clair */
    .main > div {
        background: #f8f9fc;
        min-height: 100vh;
    }
    
    /* Champs de formulaire bien visibles */
    .stTextInput > div > div > input {
        background-color: white !important;
        border: 2px solid #e5e7eb !important;
        border-radius: 12px !important;
        padding: 0.75rem 1rem !important;
        font-size: 1rem !important;
        color: #1f2937 !important;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #6366f1 !important;
        box-shadow: 0 0 0 4px rgba(99, 102, 241, 0.15) !important;
    }
    
    .stSelectbox > div > div > select {
        background-color: white !important;
        border: 2px solid #e5e7eb !important;
        border-radius: 12px !important;
        padding: 0.75rem 1rem !important;
        font-size: 1rem !important;
        color: #1f2937 !important;
    }
    
    /* Labels en noir */
    .stTextInput > label, .stSelectbox > label {
        color: #1f2937 !important;
        font-weight: 700 !important;
        font-size: 1rem !important;
    }
    
    /* Cartes d'offres avec fond blanc éclatant */
    div[data-testid="column"] > div > div {
        background-color: white;
        border-radius: 16px;
        padding: 2rem;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
        border: 1px solid #e5e7eb;
    }
    
    /* Boutons stylisés */
    .stButton > button {
        background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%) !important;
        color: white !important;
        border: none !important;
        padding: 0.75rem 2rem !important;
        border-radius: 12px !important;
        font-weight: 700 !important;
        font-size: 1rem !important;
        box-shadow: 0 4px 15px rgba(99, 102, 241, 0.4) !important;
        transition: all 0.3s ease !important;
        width: 100% !important;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 30px rgba(99, 102, 241, 0.5) !important;
    }
    
    /* Dividers */
    hr {
        margin: 2rem 0;
        border: none;
        height: 1px;
        background: #e5e7eb;
    }
    
    /* Forcer le texte visible dans les cartes */
    .main h1, .main h2, .main h3, .main h4, .main h5, .main h6 {
        color: #111827 !important;
    }
    
    .main p, .main span, .main div {
        color: #374151 !important;
    }
    
    .stMarkdown {
        color: #1f2937 !important;
    }
    
    /* Caption bien visible */
    .element-container .caption {
        color: #6b7280 !important;
    }
    
    /* Info boxes - bien visibles */
    .stAlert {
        background-color: #f0f9ff !important;
        border-left: 4px solid #3b82f6 !important;
        border-radius: 8px !important;
        padding: 1rem !important;
        color: #1e293b !important;
    }
    
    .stAlert p {
        color: #1e293b !important;
        font-size: 0.95rem !important;
        line-height: 1.6 !important;
    }
</style>
""", unsafe_allow_html=True)


# =========================
# 2) HEADER PLEINE LARGEUR
# =========================
st.markdown("""
<div style="background: linear-gradient(135deg, #667eea 0%, #8b5cf6 50%, #d946ef 100%);
            padding: 3rem 2rem;
            border-radius: 20px;
            margin-bottom: 2rem;
            box-shadow: 0 20px 60px rgba(99, 102, 241, 0.4);
            text-align: center;">
    <h1 style="color: white; font-size: 3.5rem; font-weight: 900; margin: 0; text-shadow: 0 2px 20px rgba(0, 0, 0, 0.3);">
        💼 Offres d'Emploi
    </h1>
    <p style="color: white; font-size: 1.4rem; margin: 1rem 0 0 0; font-weight: 500;">
        Trouvez votre prochaine opportunité professionnelle
    </p>
</div>
""", unsafe_allow_html=True)


# =========================
# 3) FILTRES SUR TOUTE LA LARGEUR
# =========================
st.markdown("## 🔍 Recherche d'offres")

col1, col2, col3 = st.columns(3)

with col1:
    q = st.text_input("🔎 Mots-clés", value="", placeholder="Titre, entreprise...")

with col2:
    region = st.text_input("📍 Région", value="", placeholder="Ex: Île-de-France")

with col3:
    remote = st.selectbox("🏠 Télétravail", ["Tous", "Oui", "Non", "Non précisé"], index=0)

# Mapping
remote_map = {"Tous": "(tous)", "Oui": "yes", "Non": "no", "Non précisé": "unknown"}
remote_value = remote_map[remote]

# Requête SQL
where = []
params: dict[str, object] = {}

if q.strip():
    where.append("(title LIKE :q OR employer LIKE :q OR raw_text LIKE :q)")
    params["q"] = f"%{q.strip()}%"

if region.strip():
    where.append("region = :region")
    params["region"] = region.strip()

if remote_value != "(tous)":
    where.append("remote = :remote")
    params["remote"] = remote_value

sql = f"SELECT * FROM {DEFAULT_TABLE}"
if where:
    sql += " WHERE " + " AND ".join(where)
sql += " ORDER BY published_date DESC LIMIT :lim"
params["lim"] = MAX_ROWS_TABLE

df = query_df(str(DB_PATH), sql, params=params)


# =========================
# 4) STATISTIQUES PLEINE LARGEUR
# =========================
st.markdown("---")

stat_col1, stat_col2, stat_col3 = st.columns(3)

with stat_col1:
    st.markdown(f"""
    <div style="background: white;
                padding: 2.5rem;
                border-radius: 20px;
                box-shadow: 0 10px 40px rgba(0, 0, 0, 0.1);
                border: 2px solid #e5e7eb;
                text-align: center;">
        <div style="font-size: 4rem;
                    font-weight: 900;
                    background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
                    -webkit-background-clip: text;
                    -webkit-text-fill-color: transparent;
                    margin-bottom: 0.5rem;">
            {len(df)}
        </div>
        <div style="color: #6b7280;
                    font-size: 1.1rem;
                    font-weight: 700;
                    text-transform: uppercase;
                    letter-spacing: 1px;">
            Offres trouvées
        </div>
    </div>
    """, unsafe_allow_html=True)

with stat_col2:
    st.markdown(f"""
    <div style="background: white;
                padding: 2.5rem;
                border-radius: 20px;
                box-shadow: 0 10px 40px rgba(0, 0, 0, 0.1);
                border: 2px solid #e5e7eb;
                text-align: center;">
        <div style="font-size: 4rem;
                    font-weight: 900;
                    background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
                    -webkit-background-clip: text;
                    -webkit-text-fill-color: transparent;
                    margin-bottom: 0.5rem;">
            {df['employer'].nunique() if 'employer' in df.columns and not df.empty else 0}
        </div>
        <div style="color: #6b7280;
                    font-size: 1.1rem;
                    font-weight: 700;
                    text-transform: uppercase;
                    letter-spacing: 1px;">
            Entreprises
        </div>
    </div>
    """, unsafe_allow_html=True)

with stat_col3:
    st.markdown(f"""
    <div style="background: white;
                padding: 2.5rem;
                border-radius: 20px;
                box-shadow: 0 10px 40px rgba(0, 0, 0, 0.1);
                border: 2px solid #e5e7eb;
                text-align: center;">
        <div style="font-size: 4rem;
                    font-weight: 900;
                    background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
                    -webkit-background-clip: text;
                    -webkit-text-fill-color: transparent;
                    margin-bottom: 0.5rem;">
            {df['region'].nunique() if 'region' in df.columns and not df.empty else 0}
        </div>
        <div style="color: #6b7280;
                    font-size: 1.1rem;
                    font-weight: 700;
                    text-transform: uppercase;
                    letter-spacing: 1px;">
            Régions
        </div>
    </div>
    """, unsafe_allow_html=True)


if df.empty:
    st.warning("🔍 Aucune offre ne correspond à votre recherche. Essayez avec d'autres critères.")
    st.stop()


# =========================
# 5) AFFICHAGE DES OFFRES EN GRILLE
# =========================
st.markdown("---")
st.markdown("## 📋 Offres disponibles")

def render_job_card(row, index: int) -> None:
    """Affiche une carte d'offre élégante"""
    
    # Extraction des données
    title = row.get("title", "Titre non renseigné")
    employer = row.get("employer", "Employeur non renseigné")
    city = row.get("city", "")
    region_val = row.get("region", "")
    contract = row.get("contract_type", "") or row.get("contract", "")
    remote_label = row.get("remote", "") or row.get("remote_label", "")
    salary = row.get("salary_str", "") or row.get("salary", "")
    cluster = row.get("cluster_label", "")
    date_pub = row.get("published_date", "")
    
    # Description
    desc = ""
    for c in ["description_clean", "description", "raw_text", "snippet"]:
        if c in row.index and isinstance(row[c], str) and row[c].strip():
            desc = row[c]
            break
    
    if desc:
        desc = textwrap.shorten(desc.replace("\n", " "), width=250, placeholder="...")
    
    # URL
    url = row.get("url") or row.get("job_url") or ""
    
    # Container blanc pour la carte
    with st.container():
        # Carte avec fond blanc
        st.markdown(f"""
        <div style="background: white;
                    border-radius: 20px;
                    padding: 2rem;
                    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.12);
                    border: 2px solid #f3f4f6;
                    margin-bottom: 1.5rem;
                    transition: all 0.3s ease;">
        """, unsafe_allow_html=True)
        
        # Badge nouveau
        if index < 5:
            st.markdown("🔴 **NOUVEAU**")
        
        # Titre
        st.markdown(f"### {title}")
        
        # Entreprise
        st.markdown(f"**🏢 {employer}**")
        
        # Localisation
        location_parts = []
        if city:
            location_parts.append(city)
        if region_val:
            location_parts.append(region_val)
        if location_parts:
            st.markdown(f"📍 {', '.join(location_parts)}")
        
        # Description
        if desc:
            st.markdown(f"""
            <div style="background: #f0f9ff;
                        border-left: 4px solid #3b82f6;
                        padding: 1rem;
                        border-radius: 8px;
                        margin: 1rem 0;
                        color: #1e293b;
                        font-size: 0.95rem;
                        line-height: 1.6;">
                {desc}
            </div>
            """, unsafe_allow_html=True)
        
        # Tags
        if contract or remote_label or salary or cluster:
            tags_cols = st.columns(4)
            col_idx = 0
            
            if contract:
                with tags_cols[col_idx]:
                    st.markdown(f"📋 **{contract}**")
                col_idx += 1
            
            if remote_label and remote_label != "unknown":
                remote_text = "🏠 Télétravail" if remote_label == "yes" else "🏢 Sur site"
                if col_idx < 4:
                    with tags_cols[col_idx]:
                        st.markdown(f"**{remote_text}**")
                    col_idx += 1
            
            if salary:
                if col_idx < 4:
                    with tags_cols[col_idx]:
                        st.markdown(f"💰 **{salary}**")
                    col_idx += 1
            
            if cluster:
                if col_idx < 4:
                    with tags_cols[col_idx]:
                        st.markdown(f"🏷️ **{cluster}**")
        
        # Footer
        footer_col1, footer_col2 = st.columns([2, 1])
        
        with footer_col1:
            if date_pub:
                st.caption(f"🗓️ Publié le {date_pub}")
            else:
                st.caption("🗓️ Date non précisée")
        
        with footer_col2:
            if url:
                st.link_button("📨 Postuler", url, use_container_width=True)
            else:
                st.caption("_Lien indisponible_")
        
        st.markdown("</div>", unsafe_allow_html=True)


# Affichage des offres
MAX_CARDS = 50
for idx, (_, row) in enumerate(df.head(MAX_CARDS).iterrows()):
    render_job_card(row, idx)


# =========================
# 6) TABLEAU DÉTAILLÉ
# =========================
st.markdown("---")
with st.expander("📊 Afficher le tableau complet des données"):
    df_table = df.copy()
    for col in ["uuid", "offer_uuid", "id"]:
        if col in df_table.columns:
            df_table = df_table.drop(columns=[col])
    
    st.dataframe(df_table, use_container_width=True, hide_index=True)
    
    csv = df_table.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Télécharger les données (CSV)",
        data=csv,
        file_name='offres_emploi.csv',
        mime='text/csv',
    )


# =========================
# 7) FOOTER
# =========================
st.markdown("---")
st.markdown("""
<div style="text-align: center; padding: 3rem 0; color: #6b7280;">
    <p style="font-size: 1.1rem; font-weight: 700; margin-bottom: 0.5rem;">
        💼 Plateforme de recherche d'emploi
    </p>
    <p style="font-size: 0.95rem;">
        Base de données mise à jour quotidiennement
    </p>
</div>
""", unsafe_allow_html=True)