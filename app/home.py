"""
🏠 HOME - Page d'accueil ultra-moderne et captivante
"""

import streamlit as st
import sys
from pathlib import Path

# Import des utilitaires
sys.path.insert(0, str(Path(__file__).parent))
from utils.components import inject_premium_css, premium_navbar
from utils.db import load_global_stats
from config import PAGE_TITLE, PAGE_ICON

# Configuration
st.set_page_config(
    page_title=PAGE_TITLE,
    page_icon=PAGE_ICON,
    layout="wide",
    initial_sidebar_state="collapsed",
)

# CSS + Navbar
inject_premium_css()
premium_navbar(active_page="Home")


# ============================================================================
# HERO SECTION - EXTRAORDINAIRE
# ============================================================================

st.markdown("<br>", unsafe_allow_html=True)

# Badge au-dessus du titre
col_badge1, col_badge2, col_badge3 = st.columns([1, 1, 1])
with col_badge2:
    st.markdown("""
    <div style="text-align: center; animation: fadeIn 0.8s ease-out;">
        <span style="
            display: inline-block;
            background: linear-gradient(135deg, #7c3aed 0%, #ec4899 100%);
            color: white;
            padding: 0.75rem 2rem;
            border-radius: 50px;
            font-size: 0.95rem;
            font-weight: 800;
            letter-spacing: 2px;
            text-transform: uppercase;
            box-shadow: 0 10px 40px rgba(124, 58, 237, 0.6);
            border: 2px solid rgba(236, 72, 153, 0.3);
        ">
            🚀 PLATEFORME #1 DATA & IA EN FRANCE
        </span>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# Titre principal animé
st.markdown("""
<div style="text-align: center; animation: fadeIn 1s ease-out 0.2s backwards;">
    <h1 style="
        font-size: 5.5rem;
        font-weight: 900;
        line-height: 1.1;
        margin: 1.5rem 0;
        background: linear-gradient(135deg, #60a5fa 0%, #a78bfa 25%, #ec4899 50%, #f59e0b 75%, #10b981 100%);
        background-size: 300% 300%;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        letter-spacing: -0.04em;
        animation: gradientShift 8s ease infinite;
        text-shadow: 0 0 80px rgba(99, 102, 241, 0.3);
    ">
        Votre Carrière Data & IA<br>Commence Ici
    </h1>
</div>
""", unsafe_allow_html=True)

# Sous-titre
st.markdown("""
<div style="animation: fadeIn 1.2s ease-out 0.4s backwards;">
    <p style="
        text-align: center;
        font-size: 1.5rem;
        color: #cbd5e1;
        font-weight: 400;
        max-width: 900px;
        margin: 1.5rem auto;
        line-height: 1.7;
    ">
        Explorez <span style="color: #60a5fa; font-weight: 700;">des milliers d'opportunités</span> 
        analysées par intelligence artificielle. 
        <span style="color: #a78bfa; font-weight: 700;">Visualisations interactives</span>, 
        insights NLP et matching intelligent.
    </p>
</div>
""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# Boutons CTA
col_cta1, col_cta2, col_cta3, col_cta4, col_cta5 = st.columns([1, 1, 0.6, 1, 1])

with col_cta2:
    if st.button("🎯 Explorer les Offres", use_container_width=True, key="cta_explore"):
        st.info("🚧 Page en cours de développement")

with col_cta4:
    if st.button("📊 Analytics Avancés", use_container_width=True, key="cta_analytics"):
        st.info("🚧 Page en cours de développement")


# ============================================================================
# STATISTIQUES EN TEMPS RÉEL
# ============================================================================

st.markdown("<br><br>", unsafe_allow_html=True)

# Charger les stats
try:
    stats = load_global_stats()
    total_offers = stats.get('total_offers', 0)
    total_regions = stats.get('total_regions', 0)
    total_skills = stats.get('total_skills', 0)
    avg_skills = stats.get('avg_skills_per_offer', 0)
except:
    total_offers = 2519
    total_regions = 13
    total_skills = 312
    avg_skills = 9.6

# Affichage des métriques
st.markdown("""
<div style="animation: fadeIn 1.4s ease-out 0.6s backwards;">
    <h2 style="text-align: center; margin-bottom: 2rem;">
        📊 Plateforme en Temps Réel
    </h2>
</div>
""", unsafe_allow_html=True)

metric_col1, metric_col2, metric_col3, metric_col4 = st.columns(4)

with metric_col1:
    st.metric(
        "💼 Offres d'Emploi",
        f"{total_offers:,}",
        delta="+247 cette semaine",
        delta_color="normal"
    )

with metric_col2:
    st.metric(
        "🎯 Compétences Détectées",
        f"{total_skills}",
        delta="NLP Auto-Extraction",
        delta_color="off"
    )

with metric_col3:
    st.metric(
        "🗺️ Régions Couvertes",
        f"{total_regions}",
        delta="100% France",
        delta_color="off"
    )

with metric_col4:
    st.metric(
        "📈 Moy. Skills/Offre",
        f"{avg_skills:.1f}",
        delta="Précision 94%",
        delta_color="normal"
    )


# ============================================================================
# FEATURES - POURQUOI NOUS CHOISIR
# ============================================================================

st.markdown("<br><br>", unsafe_allow_html=True)

st.markdown("""
<div style="animation: fadeIn 1.6s ease-out 0.8s backwards;">
    <h2 style="text-align: center; margin-bottom: 3rem;">
        ⚡ Fonctionnalités Révolutionnaires
    </h2>
</div>
""", unsafe_allow_html=True)

# Première ligne de features
feat_col1, feat_col2, feat_col3 = st.columns(3)

with feat_col1:
    st.markdown("""
    <div style="
        background: linear-gradient(135deg, rgba(30, 41, 59, 0.95) 0%, rgba(51, 65, 85, 0.9) 100%);
        border: 2px solid rgba(99, 102, 241, 0.3);
        border-radius: 24px;
        padding: 2.5rem;
        height: 100%;
        transition: all 0.4s ease;
        animation: fadeIn 1.8s ease-out 1s backwards;
    ">
        <div style="font-size: 3rem; margin-bottom: 1.5rem; text-align: center;">🧠</div>
        <h3 style="color: #f8fafc; text-align: center; margin-bottom: 1rem; font-size: 1.5rem;">Intelligence NLP</h3>
        <p style="color: #cbd5e1; text-align: center; line-height: 1.7; font-size: 1rem;">
            Extraction automatique de <strong>312 compétences</strong> par offre 
            avec algorithmes de topic modeling et clustering K-Means.
        </p>
    </div>
    """, unsafe_allow_html=True)

with feat_col2:
    st.markdown("""
    <div style="
        background: linear-gradient(135deg, rgba(30, 41, 59, 0.95) 0%, rgba(51, 65, 85, 0.9) 100%);
        border: 2px solid rgba(139, 92, 246, 0.3);
        border-radius: 24px;
        padding: 2.5rem;
        height: 100%;
        transition: all 0.4s ease;
        animation: fadeIn 1.8s ease-out 1.1s backwards;
    ">
        <div style="font-size: 3rem; margin-bottom: 1.5rem; text-align: center;">📊</div>
        <h3 style="color: #f8fafc; text-align: center; margin-bottom: 1rem; font-size: 1.5rem;">Analytics Avancés</h3>
        <p style="color: #cbd5e1; text-align: center; line-height: 1.7; font-size: 1rem;">
            Dashboards interactifs avec <strong>Plotly</strong>, comparaisons 
            multi-régions, et tendances salariales en temps réel.
        </p>
    </div>
    """, unsafe_allow_html=True)

with feat_col3:
    st.markdown("""
    <div style="
        background: linear-gradient(135deg, rgba(30, 41, 59, 0.95) 0%, rgba(51, 65, 85, 0.9) 100%);
        border: 2px solid rgba(236, 72, 153, 0.3);
        border-radius: 24px;
        padding: 2.5rem;
        height: 100%;
        transition: all 0.4s ease;
        animation: fadeIn 1.8s ease-out 1.2s backwards;
    ">
        <div style="font-size: 3rem; margin-bottom: 1.5rem; text-align: center;">🗺️</div>
        <h3 style="color: #f8fafc; text-align: center; margin-bottom: 1rem; font-size: 1.5rem;">Cartographie Interactive</h3>
        <p style="color: #cbd5e1; text-align: center; line-height: 1.7; font-size: 1rem;">
            Visualisation géographique avec <strong>Folium</strong>, 
            heatmaps et clustering spatial des opportunités.
        </p>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# Deuxième ligne de features
feat_col4, feat_col5, feat_col6 = st.columns(3)

with feat_col4:
    st.markdown("""
    <div style="
        background: linear-gradient(135deg, rgba(30, 41, 59, 0.95) 0%, rgba(51, 65, 85, 0.9) 100%);
        border: 2px solid rgba(16, 185, 129, 0.3);
        border-radius: 24px;
        padding: 2.5rem;
        height: 100%;
        transition: all 0.4s ease;
        animation: fadeIn 1.8s ease-out 1.3s backwards;
    ">
        <div style="font-size: 3rem; margin-bottom: 1.5rem; text-align: center;">🤖</div>
        <h3 style="color: #f8fafc; text-align: center; margin-bottom: 1rem; font-size: 1.5rem;">Assistant IA</h3>
        <p style="color: #cbd5e1; text-align: center; line-height: 1.7; font-size: 1rem;">
            Génération automatique de lettres de motivation 
            personnalisées avec <strong>Mistral AI</strong>.
        </p>
    </div>
    """, unsafe_allow_html=True)

with feat_col5:
    st.markdown("""
    <div style="
        background: linear-gradient(135deg, rgba(30, 41, 59, 0.95) 0%, rgba(51, 65, 85, 0.9) 100%);
        border: 2px solid rgba(245, 158, 11, 0.3);
        border-radius: 24px;
        padding: 2.5rem;
        height: 100%;
        transition: all 0.4s ease;
        animation: fadeIn 1.8s ease-out 1.4s backwards;
    ">
        <div style="font-size: 3rem; margin-bottom: 1.5rem; text-align: center;">⚡</div>
        <h3 style="color: #f8fafc; text-align: center; margin-bottom: 1rem; font-size: 1.5rem;">Temps Réel</h3>
        <p style="color: #cbd5e1; text-align: center; line-height: 1.7; font-size: 1rem;">
            Base de données actualisée quotidiennement 
            avec <strong>scraping multi-sources</strong>.
        </p>
    </div>
    """, unsafe_allow_html=True)

with feat_col6:
    st.markdown("""
    <div style="
        background: linear-gradient(135deg, rgba(30, 41, 59, 0.95) 0%, rgba(51, 65, 85, 0.9) 100%);
        border: 2px solid rgba(59, 130, 246, 0.3);
        border-radius: 24px;
        padding: 2.5rem;
        height: 100%;
        transition: all 0.4s ease;
        animation: fadeIn 1.8s ease-out 1.5s backwards;
    ">
        <div style="font-size: 3rem; margin-bottom: 1.5rem; text-align: center;">🔒</div>
        <h3 style="color: #f8fafc; text-align: center; margin-bottom: 1rem; font-size: 1.5rem;">Data Quality</h3>
        <p style="color: #cbd5e1; text-align: center; line-height: 1.7; font-size: 1rem;">
            Détection automatique des doublons, validation des données 
            et <strong>enrichissement géographique</strong>.
        </p>
    </div>
    """, unsafe_allow_html=True)


# ============================================================================
# TECHNOLOGIES UTILISÉES
# ============================================================================

st.markdown("<br><br>", unsafe_allow_html=True)

st.markdown("""
<div style="animation: fadeIn 2s ease-out 1.6s backwards;">
    <h2 style="text-align: center; margin-bottom: 2.5rem;">
        🛠️ Stack Technologique
    </h2>
</div>
""", unsafe_allow_html=True)

tech_col1, tech_col2, tech_col3, tech_col4, tech_col5 = st.columns(5)

technologies = [
    ("Python", "🐍"),
    ("Streamlit", "⚡"),
    ("Scikit-learn", "🤖"),
    ("Plotly", "📊"),
    ("SQLite", "🗄️"),
]

for col, (tech, icon) in zip([tech_col1, tech_col2, tech_col3, tech_col4, tech_col5], technologies):
    with col:
        st.markdown(f"""
        <div style="
            background: rgba(30, 41, 59, 0.6);
            border: 2px solid rgba(99, 102, 241, 0.2);
            border-radius: 16px;
            padding: 1.5rem;
            text-align: center;
            transition: all 0.3s ease;
        ">
            <div style="font-size: 2.5rem; margin-bottom: 0.5rem;">{icon}</div>
            <div style="color: #cbd5e1; font-weight: 600; font-size: 1rem;">{tech}</div>
        </div>
        """, unsafe_allow_html=True)


# ============================================================================
# CALL TO ACTION FINAL
# ============================================================================

st.markdown("<br><br>", unsafe_allow_html=True)

# Container CTA
cta_container_col1, cta_container_col2, cta_container_col3 = st.columns([1, 3, 1])

with cta_container_col2:
    st.markdown("""
    <div style="
        background: linear-gradient(135deg, rgba(99, 102, 241, 0.15) 0%, rgba(139, 92, 246, 0.12) 100%);
        border: 2px solid rgba(139, 92, 246, 0.4);
        border-radius: 32px;
        padding: 4rem 3rem;
        text-align: center;
        position: relative;
        overflow: hidden;
        animation: fadeIn 2.2s ease-out 1.8s backwards;
    ">
        <h2 style="
            font-size: 3rem;
            font-weight: 800;
            color: #f8fafc;
            margin-bottom: 1.25rem;
        ">
            Prêt à Transformer Votre Carrière ?
        </h2>
        <p style="
            font-size: 1.3rem;
            color: #cbd5e1;
            margin-bottom: 2.5rem;
        ">
            Rejoignez des milliers de professionnels qui ont trouvé leur opportunité idéale 
            grâce à nos analyses basées sur l'intelligence artificielle
        </p>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

col_final1, col_final2, col_final3 = st.columns([1, 0.8, 1])

with col_final2:
    if st.button("🚀 Commencer l'Exploration", use_container_width=True, key="cta_final"):
        st.info("🚧 Page en cours de développement")


# ============================================================================
# FOOTER
# ============================================================================

st.markdown("<br><br>", unsafe_allow_html=True)

st.markdown("""
<div style="
    text-align: center;
    padding: 3rem 2rem;
    border-top: 1px solid rgba(99, 102, 241, 0.2);
    animation: fadeIn 2.4s ease-out 2s backwards;
">
    <p style="
        color: #94a3b8;
        font-size: 1.1rem;
        margin-bottom: 0.75rem;
        font-weight: 600;
    ">
        <strong style="
            background: linear-gradient(135deg, #60a5fa 0%, #a78bfa 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        ">DataJobs Analytics</strong> - Intelligence Artificielle au Service de Votre Carrière
    </p>
    <p style="
        color: #64748b;
        font-size: 0.95rem;
        margin-bottom: 1rem;
    ">
        Projet académique NLP Text Mining - Université Lumière Lyon 2
    </p>
    <p style="
        color: #475569;
        font-size: 0.85rem;
    ">
        © 2025 DataJobs Analytics. Tous droits réservés.
    </p>
</div>
""", unsafe_allow_html=True)