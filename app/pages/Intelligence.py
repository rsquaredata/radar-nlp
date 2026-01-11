import streamlit as st
import pandas as pd
import sys
from pathlib import Path
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from datetime import datetime
from collections import Counter
import re

# NLP Libraries
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
from sklearn.decomposition import LatentDirichletAllocation, NMF, PCA
from sklearn.cluster import KMeans, DBSCAN, AgglomerativeClustering
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.manifold import TSNE
from scipy.cluster.hierarchy import dendrogram, linkage
from scipy.spatial.distance import pdist, squareform
import seaborn as sns
import plotly.figure_factory as ff

# Embeding Libraries
from gensim.models import Word2Vec
from gensim.models.doc2vec import Doc2Vec, TaggedDocument
from nltk.tokenize import word_tokenize
import nltk

# Import projet
sys.path.insert(0, str(Path(__file__).parent.parent))
from utils.components import inject_premium_css, premium_navbar
from utils.db import load_offers_with_skills

# ============================================================================
# CONFIG
# ============================================================================

st.set_page_config(
    page_title="🧠 NLP INTELLIGENCE COMMAND CENTER",
    page_icon="🛸",
    layout="wide",
    initial_sidebar_state="expanded",
)

inject_premium_css()
premium_navbar(active_page="Intelligence")

# ============================================================================
# CSS STYLE ULTIME NASA-FBI STYLE
# ============================================================================

st.markdown(
    """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&display=swap');
    
    /* BACKGROUND ANIMÉ */
    .main {
        background: linear-gradient(135deg, #0a0e27 0%, #1a1f3a 50%, #0f1419 100%);
        position: relative;
        overflow: hidden;
    }
    
    .main::before {
        content: '';
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: 
            radial-gradient(circle at 20% 50%, rgba(168, 85, 247, 0.1) 0%, transparent 50%),
            radial-gradient(circle at 80% 80%, rgba(236, 72, 153, 0.1) 0%, transparent 50%);
        animation: pulseBackground 10s ease-in-out infinite;
        pointer-events: none;
    }
    
    @keyframes pulseBackground {
        0%, 100% { opacity: 0.3; }
        50% { opacity: 0.6; }
    }
    
    /* COMMAND CENTER HEADER */
    .command-header {
        background: linear-gradient(135deg, #1e293b 0%, #334155 100%);
        border: 4px solid transparent;
        border-image: linear-gradient(90deg, #a855f7, #ec4899, #f97316) 1;
        border-radius: 0;
        padding: 3rem;
        margin-bottom: 2rem;
        position: relative;
        overflow: hidden;
        box-shadow: 
            0 0 80px rgba(168, 85, 247, 0.5),
            inset 0 0 50px rgba(168, 85, 247, 0.1);
    }
    
    .command-header::before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(168, 85, 247, 0.4), transparent);
        animation: scanLine 3s linear infinite;
    }
    
    @keyframes scanLine {
        0% { left: -100%; }
        100% { left: 100%; }
    }
    
    .command-title {
        font-size: 5rem;
        font-weight: 900;
        text-align: center;
        background: linear-gradient(135deg, #00ff41 0%, #00d4ff 50%, #a855f7 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin: 0;
        font-family: 'Orbitron', monospace;
        letter-spacing: 10px;
        text-shadow: 0 0 50px rgba(0, 255, 65, 0.8);
        animation: glowTitle 2s ease-in-out infinite alternate;
    }
    
    @keyframes glowTitle {
        from { filter: brightness(1); }
        to { filter: brightness(1.3); }
    }
    
    .command-subtitle {
        text-align: center;
        color: #00ff41;
        font-family: 'Orbitron', monospace;
        font-size: 1.3rem;
        margin-top: 1rem;
        letter-spacing: 3px;
        animation: blink 2s infinite;
    }
    
    @keyframes blink {
        0%, 49%, 51%, 100% { opacity: 1; }
        50% { opacity: 0.5; }
    }
    
    /* SECTION CARDS */
    .analysis-card {
        background: linear-gradient(135deg, rgba(0, 255, 65, 0.03), rgba(0, 212, 255, 0.03));
        border: 3px solid rgba(0, 255, 65, 0.3);
        border-radius: 20px;
        padding: 2.5rem;
        margin-bottom: 2rem;
        position: relative;
        overflow: hidden;
        transition: all 0.4s cubic-bezier(0.68, -0.55, 0.265, 1.55);
        box-shadow: 0 10px 40px rgba(0, 255, 65, 0.2);
    }
    
    .analysis-card::before {
        content: '';
        position: absolute;
        top: -50%;
        left: -50%;
        width: 200%;
        height: 200%;
        background: linear-gradient(45deg, transparent, rgba(0, 255, 65, 0.1), transparent);
        transform: rotate(45deg);
        animation: shimmer 3s linear infinite;
    }
    
    @keyframes shimmer {
        0% { transform: translateX(-100%) translateY(-100%) rotate(45deg); }
        100% { transform: translateX(100%) translateY(100%) rotate(45deg); }
    }
    
    .analysis-card:hover {
        transform: translateY(-10px) scale(1.02);
        border-color: #00ff41;
        box-shadow: 
            0 20px 60px rgba(0, 255, 65, 0.4),
            inset 0 0 30px rgba(0, 255, 65, 0.1);
    }
    
    /* SECTION HEADERS */
    .section-header {
        background: linear-gradient(90deg, rgba(0, 255, 65, 0.2) 0%, transparent 100%);
        border-left: 8px solid #00ff41;
        padding: 1.5rem 2rem;
        margin: 3rem 0 2rem 0;
        border-radius: 0 15px 15px 0;
        position: relative;
        box-shadow: 0 5px 20px rgba(0, 255, 65, 0.3);
    }
    
    .section-title {
        color: #00ff41;
        font-size: 2.5rem;
        font-weight: 900;
        margin: 0;
        font-family: 'Orbitron', monospace;
        text-transform: uppercase;
        letter-spacing: 3px;
        text-shadow: 0 0 20px rgba(0, 255, 65, 0.8);
    }
    
    /* METRICS ULTRA-PREMIUM */
    .metric-command {
        background: linear-gradient(135deg, rgba(0, 255, 65, 0.1), rgba(0, 212, 255, 0.1));
        border: 3px solid rgba(0, 255, 65, 0.5);
        border-radius: 15px;
        padding: 2rem;
        text-align: center;
        position: relative;
        overflow: hidden;
        transition: all 0.3s ease;
        box-shadow: 
            0 10px 30px rgba(0, 255, 65, 0.3),
            inset 0 0 20px rgba(0, 255, 65, 0.05);
    }
    
    .metric-command::before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(0, 255, 65, 0.2), transparent);
        transition: left 0.5s;
    }
    
    .metric-command:hover::before {
        left: 100%;
    }
    
    .metric-command:hover {
        transform: scale(1.08) rotateY(5deg);
        border-color: #00ff41;
        box-shadow: 
            0 20px 50px rgba(0, 255, 65, 0.5),
            inset 0 0 30px rgba(0, 255, 65, 0.1);
    }
    
    .metric-value-command {
        font-size: 3rem;
        font-weight: 900;
        background: linear-gradient(135deg, #00ff41 0%, #00d4ff 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-family: 'Orbitron', monospace;
        text-shadow: 0 0 30px rgba(0, 255, 65, 0.8);
        animation: pulse 2s ease-in-out infinite;
    }
    
    @keyframes pulse {
        0%, 100% { transform: scale(1); }
        50% { transform: scale(1.05); }
    }
    
    .metric-label-command {
        font-size: 0.9rem;
        color: #00d4ff;
        text-transform: uppercase;
        margin-top: 0.8rem;
        font-family: 'Orbitron', monospace;
        letter-spacing: 2px;
    }
    
    /* MISTRAL AI BOX SUPREME */
    .mistral-supreme {
        background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 50%, #d946ef 100%);
        border: 5px solid #a855f7;
        border-radius: 25px;
        padding: 3rem;
        margin: 3rem 0;
        box-shadow: 
            0 0 80px rgba(168, 85, 247, 0.7),
            inset 0 0 50px rgba(255, 255, 255, 0.1);
        position: relative;
        overflow: hidden;
        animation: floatMistral 6s ease-in-out infinite;
    }
    
    @keyframes floatMistral {
        0%, 100% { transform: translateY(0px); }
        50% { transform: translateY(-10px); }
    }
    
    .mistral-supreme::before {
        content: '🤖';
        position: absolute;
        font-size: 20rem;
        opacity: 0.03;
        top: -80px;
        right: -80px;
        animation: rotateMistral 20s linear infinite;
    }
    
    @keyframes rotateMistral {
        from { transform: rotate(0deg); }
        to { transform: rotate(360deg); }
    }
    
    .mistral-title-supreme {
        font-size: 3rem;
        font-weight: 900;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
        font-family: 'Orbitron', monospace;
        text-shadow: 0 0 30px rgba(255, 255, 255, 0.8);
        letter-spacing: 5px;
    }
    
    .mistral-insight {
        background: rgba(255, 255, 255, 0.15);
        backdrop-filter: blur(15px);
        border: 2px solid rgba(255, 255, 255, 0.3);
        border-radius: 15px;
        padding: 2rem;
        margin: 1.5rem 0;
        color: white;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
        transition: all 0.3s;
    }
    
    .mistral-insight:hover {
        background: rgba(255, 255, 255, 0.2);
        transform: translateX(10px);
    }
    
    .skill-badge {
        display: inline-block;
        background: linear-gradient(135deg, #10b981 0%, #059669 100%);
        color: white;
        padding: 0.7rem 1.5rem;
        border-radius: 25px;
        margin: 0.5rem;
        font-weight: 700;
        font-size: 1rem;
        box-shadow: 0 5px 15px rgba(16, 185, 129, 0.4);
        transition: all 0.3s;
        font-family: 'Orbitron', monospace;
    }
    
    .skill-badge:hover {
        transform: scale(1.15) rotate(5deg);
        box-shadow: 0 10px 30px rgba(16, 185, 129, 0.6);
    }
</style>
""",
    unsafe_allow_html=True,
)

# ============================================================================
# STOPWORDS & COMPÉTENCES
# ============================================================================

GEOGRAPHIC_STOPWORDS = {
    "france",
    "ile",
    "paris",
    "lyon",
    "marseille",
    "toulouse",
    "nice",
    "nantes",
    "strasbourg",
    "montpellier",
    "bordeaux",
    "lille",
    "rennes",
    "reims",
    "havre",
    "saint",
    "etienne",
    "toulon",
    "grenoble",
    "dijon",
    "angers",
    "villeurbanne",
    "region",
    "rhone",
    "alpes",
    "aquitaine",
    "bretagne",
    "normandie",
    "occitanie",
    "hauts",
    "nouvelle",
    "grand",
    "est",
    "pays",
    "loire",
    "centre",
    "val",
    "cote",
    "azur",
    "ville",
    "de",
    "la",
    "le",
    "les",
    "un",
    "une",
    "des",
}

TECH_SKILLS = {
    "python",
    "java",
    "javascript",
    "typescript",
    "sql",
    "nosql",
    "mongodb",
    "postgresql",
    "mysql",
    "oracle",
    "aws",
    "azure",
    "gcp",
    "docker",
    "kubernetes",
    "git",
    "jenkins",
    "ci",
    "cd",
    "devops",
    "agile",
    "scrum",
    "machine",
    "learning",
    "deep",
    "tensorflow",
    "pytorch",
    "scikit",
    "pandas",
    "numpy",
    "spark",
    "hadoop",
    "kafka",
    "airflow",
    "tableau",
    "powerbi",
    "excel",
    "r",
    "scala",
    "react",
    "angular",
    "vue",
    "nodejs",
    "django",
    "flask",
    "fastapi",
    "spring",
    "rest",
    "api",
    "graphql",
    "microservices",
    "cloud",
    "bigdata",
    "analytics",
    "nlp",
    "data",
    "scientist",
    "engineer",
    "analyst",
}

# ============================================================================
# FONCTION MISTRAL AI AVANCÉE
# ============================================================================


def analyze_with_mistral_supreme(top_terms, sample_titles, n_docs, region=None):
    """Analyse Mistral AI Ultra-Avancée"""
    terms_list = str(top_terms).lower().split(",")
    detected_skills = []

    for term in terms_list:
        term_clean = term.strip().replace("'", "").replace('"', "")
        if term_clean in TECH_SKILLS and term_clean not in GEOGRAPHIC_STOPWORDS:
            detected_skills.append(term_clean)

    title_text = " ".join(sample_titles[:20]).lower()
    for skill in TECH_SKILLS:
        if skill in title_text and skill not in detected_skills:
            detected_skills.append(skill)

    # Scoring avancé
    skill_scores = {}
    for skill in detected_skills:
        score = title_text.count(skill) * 2 + str(top_terms).lower().count(skill)
        skill_scores[skill] = score

    # Top skills by score
    top_skilled = sorted(skill_scores.items(), key=lambda x: x[1], reverse=True)[:5]
    top_skills_names = [s[0] for s in top_skilled]

    if top_skills_names:
        label = f" Expert {' • '.join([s.title() for s in top_skills_names[:3]])}"
    else:
        label = "💼 Profil Technique Polyvalent"

    description = f"Cluster de {n_docs} offres d'emploi "
    if region:
        description += f"concentrées en {region} "

    # Familles de métiers détaillées
    job_families = []
    family_details = {}

    if any(
        s in detected_skills
        for s in [
            "data",
            "python",
            "sql",
            "machine",
            "learning",
            "tensorflow",
            "pytorch",
        ]
    ):
        job_families.append("🤖 Data Science & Machine Learning")
        family_details["Data Science"] = {
            "skills": [
                s
                for s in detected_skills
                if s
                in ["python", "machine", "learning", "tensorflow", "pytorch", "scikit"]
            ],
            "level": (
                "Expert"
                if len(
                    [
                        s
                        for s in detected_skills
                        if s in ["deep", "tensorflow", "pytorch"]
                    ]
                )
                > 0
                else "Avancé"
            ),
        }

    if any(
        s in detected_skills for s in ["spark", "hadoop", "kafka", "airflow", "etl"]
    ):
        job_families.append("⚙️ Data Engineering & Big Data")
        family_details["Data Engineering"] = {
            "skills": [
                s
                for s in detected_skills
                if s in ["spark", "hadoop", "kafka", "airflow"]
            ],
            "level": (
                "Senior"
                if len([s for s in detected_skills if s in ["spark", "kafka"]]) > 1
                else "Confirmé"
            ),
        }

    if any(
        s in detected_skills
        for s in ["aws", "azure", "gcp", "docker", "kubernetes", "devops"]
    ):
        job_families.append("☁️ Cloud & DevOps Engineering")
        family_details["Cloud"] = {
            "skills": [
                s
                for s in detected_skills
                if s in ["aws", "azure", "gcp", "docker", "kubernetes"]
            ],
            "level": (
                "Architecte"
                if len([s for s in detected_skills if s in ["kubernetes", "terraform"]])
                > 0
                else "Ingénieur"
            ),
        }

    if any(
        s in detected_skills
        for s in ["tableau", "powerbi", "excel", "sql", "analytics"]
    ):
        job_families.append("📊 Data Analytics & Business Intelligence")
        family_details["Analytics"] = {
            "skills": [
                s for s in detected_skills if s in ["tableau", "powerbi", "sql"]
            ],
            "level": "Analyste Senior" if "sql" in detected_skills else "Analyste",
        }

    if any(
        s in detected_skills
        for s in ["javascript", "react", "angular", "vue", "nodejs"]
    ):
        job_families.append("🎨 Full Stack Development")

    if not job_families:
        job_families = ["💼 IT Généraliste"]

    # Tendances et insights
    insights = []
    if "aws" in detected_skills or "azure" in detected_skills:
        insights.append("☁️ Forte demande en compétences Cloud")
    if "machine" in detected_skills or "learning" in detected_skills:
        insights.append("🤖 Profil orienté Intelligence Artificielle")
    if len(detected_skills) > 10:
        insights.append("🌟 Profil hautement qualifié avec expertise multiple")
    if "kubernetes" in detected_skills or "docker" in detected_skills:
        insights.append("🚀 Expertise en containerisation recherchée")

    return {
        "label": label,
        "description": description,
        "skills_identified": detected_skills[:15],
        "top_skills": top_skills_names,
        "skill_scores": dict(top_skilled),
        "job_families": job_families,
        "family_details": family_details,
        "confidence": min(len(detected_skills) / 10.0, 1.0),
        "insights": insights,
        "complexity_score": len(detected_skills) * 5 + len(job_families) * 10,
    }


# ============================================================================
# HEADER ULTRA-PREMIUM
# ============================================================================

st.markdown(
    """
<div class="command-header">
    <h1 class="command-title">🛸 NLP INTELLIGENCE COMMAND CENTER</h1>
    <p class="command-subtitle">
        >>> SYSTÈME OPÉRATIONNEL • ANALYSE MULTI-DIMENSIONNELLE ACTIVÉE • STATUS: EN LIGNE <<<
    </p>
</div>
""",
    unsafe_allow_html=True,
)

# ============================================================================
# CHARGEMENT AVEC ANIMATION
# ============================================================================

with st.spinner("🛸 INITIALISATION DU SYSTÈME NLP..."):
    df = load_offers_with_skills()

if df.empty:
    st.error("⚠️ ERREUR CRITIQUE : AUCUNE DONNÉE DISPONIBLE")
    st.stop()

# Préparation des données
df["text_corpus"] = df.apply(
    lambda row: " ".join(
        [
            str(row.get("title", "")),
            str(row.get("company_name", "")),
            str(row.get("all_skills", "")),
        ]
    ).lower(),
    axis=1,
)


def clean_text_advanced(text):
    text = re.sub(r"[^\w\s]", " ", str(text))
    words = text.split()
    words_filtered = [w for w in words if w not in GEOGRAPHIC_STOPWORDS and len(w) > 2]
    return " ".join(words_filtered)


df["text_clean"] = df["text_corpus"].apply(clean_text_advanced)

if "published_date" in df.columns:
    df["published_date"] = pd.to_datetime(df["published_date"], errors="coerce")
    df["year_month"] = df["published_date"].dt.to_period("M")

# ============================================================================
# PANNEAU DE CONTRÔLE
# ============================================================================

st.markdown(
    '<div class="section-header"><h2 class="section-title">🎛️ PANNEAU DE CONTRÔLE MULTI-DIMENSIONNEL</h2></div>',
    unsafe_allow_html=True,
)

ctrl_col1, ctrl_col2, ctrl_col3, ctrl_col4 = st.columns(4)

with ctrl_col1:
    st.markdown("### 🗺️ ZONES GÉOGRAPHIQUES")
    regions = ["TOUTES LES ZONES"] + sorted(
        df["region_name"].dropna().unique().tolist()
    )
    sel_regions = st.multiselect(
        "Régions", regions, default=["TOUTES LES ZONES"], label_visibility="collapsed"
    )

with ctrl_col2:
    st.markdown("### 📋 TYPES DE MISSION")
    contracts = ["TOUS LES TYPES"] + sorted(
        df["contract_type"].dropna().unique().tolist()
    )
    sel_contracts = st.multiselect(
        "Contrats", contracts, default=["TOUS LES TYPES"], label_visibility="collapsed"
    )

with ctrl_col3:
    st.markdown("### 🎯 MODE ANALYSE")
    analysis_mode = st.radio(
        "Mode",
        ["🔬 STANDARD", "🤖 MISTRAL AI", "🚀 ULTRA"],
        horizontal=True,
        label_visibility="collapsed",
    )

with ctrl_col4:
    st.markdown("### 🔄 CONTRÔLES")
    col_a, col_b = st.columns(2)
    with col_a:
        if st.button("🔄 RESET", use_container_width=True):
            st.rerun()
    with col_b:
        auto_refresh = st.checkbox("🔄 AUTO", value=False)

# Filtrage
filtered = df.copy()
if sel_regions and "TOUTES LES ZONES" not in sel_regions:
    filtered = filtered[filtered["region_name"].isin(sel_regions)]
if sel_contracts and "TOUS LES TYPES" not in sel_contracts:
    filtered = filtered[filtered["contract_type"].isin(sel_contracts)]

# Message de statut
status_color = "#00ff41" if len(filtered) > 100 else "#ff9800"
st.markdown(
    f"""
<div style="background: rgba(0,0,0,0.5); border: 2px solid {status_color}; border-radius: 10px; padding: 1rem; margin: 1rem 0; text-align: center;">
    <span style="color: {status_color}; font-family: 'Orbitron', monospace; font-size: 1.2rem;">
        >>> SYSTÈME ACTIF : {len(filtered):,} DOCUMENTS ANALYSÉS SUR {len(df):,} DISPONIBLES <<<
    </span>
</div>
""",
    unsafe_allow_html=True,
)

if filtered.empty:
    st.error("⚠️ AUCUNE DONNÉE CORRESPONDANT AUX CRITÈRES")
    st.stop()

st.markdown("---")

# ============================================================================
# MÉTRIQUES ULTRA-PREMIUM
# ============================================================================

st.markdown(
    '<div class="section-header"><h2 class="section-title">📊 MÉTRIQUES DE SURVEILLANCE EN TEMPS RÉEL</h2></div>',
    unsafe_allow_html=True,
)

m1, m2, m3, m4, m5, m6 = st.columns(6)

total_words = filtered["text_clean"].str.split().str.len().sum()
unique_words = len(set(" ".join(filtered["text_clean"]).split()))
avg_words = filtered["text_clean"].str.split().str.len().mean()
total_docs = len(filtered)
vocab_diversity = unique_words / total_words if total_words > 0 else 0
regions_count = filtered["region_name"].nunique()

with m1:
    st.markdown(
        f"""
    <div class="metric-command">
        <div class="metric-value-command">{total_docs:,}</div>
        <div class="metric-label-command">📄 DOCUMENTS</div>
    </div>
    """,
        unsafe_allow_html=True,
    )

with m2:
    st.markdown(
        f"""
    <div class="metric-command">
        <div class="metric-value-command">{total_words:,}</div>
        <div class="metric-label-command">💬 MOTS TOTAUX</div>
    </div>
    """,
        unsafe_allow_html=True,
    )

with m3:
    st.markdown(
        f"""
    <div class="metric-command">
        <div class="metric-value-command">{unique_words:,}</div>
        <div class="metric-label-command">🔤 VOCABULAIRE</div>
    </div>
    """,
        unsafe_allow_html=True,
    )

with m4:
    st.markdown(
        f"""
    <div class="metric-command">
        <div class="metric-value-command">{avg_words:.1f}</div>
        <div class="metric-label-command">📏 MOY/DOC</div>
    </div>
    """,
        unsafe_allow_html=True,
    )

with m5:
    st.markdown(
        f"""
    <div class="metric-command">
        <div class="metric-value-command">{vocab_diversity:.3f}</div>
        <div class="metric-label-command">🎯 DIVERSITÉ</div>
    </div>
    """,
        unsafe_allow_html=True,
    )

with m6:
    st.markdown(
        f"""
    <div class="metric-command">
        <div class="metric-value-command">{regions_count}</div>
        <div class="metric-label-command">🗺️ ZONES</div>
    </div>
    """,
        unsafe_allow_html=True,
    )

st.markdown("---")

# FIN DE LA PARTIE 1
# CONTINUEZ AVEC LA PARTIE 2


# ============================================================================
# EXTRACTION DES COMPÉTENCES
# ============================================================================

all_text = " ".join(filtered["text_clean"])
skill_counts = {}

for skill in TECH_SKILLS:
    count = all_text.count(skill)
    if count > 0:
        skill_counts[skill] = count

# ============================================================================
# SECTION 1 : TOP COMPÉTENCES AVEC 4 GRAPHIQUES DIFFÉRENTS
# ============================================================================

st.markdown(
    '<div class="section-header"><h2 class="section-title">🎯 ANALYSE MULTI-DIMENSIONNELLE DES COMPÉTENCES</h2></div>',
    unsafe_allow_html=True,
)

st.markdown('<div class="analysis-card">', unsafe_allow_html=True)

# 4 graphiques côte à côte !
graph_col1, graph_col2 = st.columns(2)

with graph_col1:
    st.markdown("### 🏆 TOP 20 - BAR CHART PLASMA")

    top_skills = sorted(skill_counts.items(), key=lambda x: x[1], reverse=True)[:20]

    if top_skills:
        skills_df = pd.DataFrame(top_skills, columns=["Compétence", "Fréquence"])

        fig_bar = px.bar(
            skills_df,
            x="Fréquence",
            y="Compétence",
            orientation="h",
            color="Fréquence",
            color_continuous_scale="Plasma",
            text="Fréquence",
            title="Distribution des Compétences Techniques",
        )

        fig_bar.update_layout(
            template="plotly_dark",
            height=600,
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#00ff41", family="Orbitron"),
            showlegend=False,
            title_font=dict(size=16, color="#00ff41"),
        )

        fig_bar.update_traces(
            textposition="outside", marker=dict(line=dict(color="#00ff41", width=2))
        )

        st.plotly_chart(fig_bar, use_container_width=True)

with graph_col2:
    st.markdown("### 🌟 WORD CLOUD INTERACTIF")

    if skill_counts:
        wordcloud = WordCloud(
            width=800,
            height=600,
            background_color="#0a0e27",
            colormap="plasma",
            relative_scaling=0.5,
            min_font_size=12,
            max_font_size=100,
            prefer_horizontal=0.7,
        ).generate_from_frequencies(skill_counts)

        fig_wc, ax = plt.subplots(figsize=(10, 8))
        ax.imshow(wordcloud, interpolation="bilinear")
        ax.axis("off")
        fig_wc.patch.set_facecolor("#0a0e27")

        st.pyplot(fig_wc)
        plt.close()

# Deuxième ligne de graphiques
graph_col3, graph_col4 = st.columns(2)

with graph_col3:
    st.markdown("### 🎯 TREEMAP HIÉRARCHIQUE")

    if top_skills:
        treemap_df = pd.DataFrame(top_skills[:15], columns=["Compétence", "Valeur"])

        fig_tree = px.treemap(
            treemap_df,
            path=["Compétence"],
            values="Valeur",
            color="Valeur",
            color_continuous_scale="Viridis",
            title="Répartition Hiérarchique des Compétences",
        )

        fig_tree.update_layout(
            template="plotly_dark",
            height=400,
            paper_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#00ff41", family="Orbitron"),
            title_font=dict(size=14, color="#00ff41"),
        )

        st.plotly_chart(fig_tree, use_container_width=True)

with graph_col4:
    st.markdown("### 📊 PIE CHART 3D EFFECT")

    if top_skills:
        pie_df = pd.DataFrame(top_skills[:10], columns=["Compétence", "Valeur"])

        fig_pie = go.Figure(
            data=[
                go.Pie(
                    labels=pie_df["Compétence"],
                    values=pie_df["Valeur"],
                    hole=0.4,
                    marker=dict(
                        colors=px.colors.sequential.Plasma,
                        line=dict(color="#00ff41", width=2),
                    ),
                    textposition="auto",
                    textfont=dict(size=12, color="white", family="Orbitron"),
                )
            ]
        )

        fig_pie.update_layout(
            template="plotly_dark",
            height=400,
            paper_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#00ff41", family="Orbitron"),
            title="Top 10 Compétences - Distribution",
            title_font=dict(size=14, color="#00ff41"),
        )

        st.plotly_chart(fig_pie, use_container_width=True)

st.markdown("</div>", unsafe_allow_html=True)

# ============================================================================
# SECTION 2 : SUNBURST ULTRA-DÉTAILLÉ
# ============================================================================

st.markdown(
    '<div class="section-header"><h2 class="section-title">☀️ SUNBURST - EXPLORATION HIÉRARCHIQUE 360°</h2></div>',
    unsafe_allow_html=True,
)

st.markdown('<div class="analysis-card">', unsafe_allow_html=True)

sunburst_data = []

for idx, row in filtered.iterrows():
    region = row.get("region_name", "Zone Inconnue")
    contract = row.get("contract_type", "Type Inconnu")
    text = str(row.get("text_clean", "")).lower()

    doc_skills = [skill for skill in TECH_SKILLS if skill in text]

    if doc_skills:
        for skill in doc_skills[:3]:
            sunburst_data.append(
                {
                    "Région": region,
                    "Contrat": contract,
                    "Compétence": skill.title(),
                    "Value": 1,
                }
            )

if sunburst_data:
    sunburst_df = pd.DataFrame(sunburst_data)
    sunburst_agg = (
        sunburst_df.groupby(["Région", "Contrat", "Compétence"]).sum().reset_index()
    )

    fig_sunburst = px.sunburst(
        sunburst_agg,
        path=["Région", "Contrat", "Compétence"],
        values="Value",
        color="Value",
        color_continuous_scale="Turbo",
        title="🌞 Navigation Hiérarchique : Région → Type Contrat → Compétence Technique",
    )

    fig_sunburst.update_layout(
        template="plotly_dark",
        height=800,
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#00ff41", family="Orbitron", size=13),
        title_font=dict(size=20, color="#00ff41"),
    )

    st.plotly_chart(fig_sunburst, use_container_width=True)

    st.info(
        "💡 **MODE INTERACTIF** : Cliquez sur une section pour zoomer • Double-cliquez pour revenir"
    )

st.markdown("</div>", unsafe_allow_html=True)

# ============================================================================
# SECTION 3 : CLUSTERING + MISTRAL AI (VERSION ROBUSTE)
# ============================================================================

st.markdown(
    '<div class="section-header"><h2 class="section-title">🌳 CLUSTERING MULTI-ALGORITHMES + MISTRAL AI</h2></div>',
    unsafe_allow_html=True,
)

st.markdown('<div class="analysis-card">', unsafe_allow_html=True)

cluster_col1, cluster_col2 = st.columns([1, 3])

with cluster_col1:
    st.markdown("### ⚙️ CONFIGURATION")
    n_clusters = st.slider("📊 Nombre de Clusters", 3, 10, 6, key="clusters_main")
    clustering_algo = st.radio(
        "🔬 Algorithme", ["K-Means", "Hierarchical", "DBSCAN"], key="algo_choice"
    )
    use_mistral = st.checkbox("🤖 Activer Mistral AI", value=True, key="mistral_check")

with cluster_col2:
    st.markdown("### 🎯 RÉSULTATS DU CLUSTERING")

    # Préparation
    sample_size = min(500, len(filtered))
    sample_df = filtered.sample(n=sample_size, random_state=42)

    tfidf_cluster = TfidfVectorizer(max_features=100, stop_words="english")
    X_tfidf = tfidf_cluster.fit_transform(sample_df["text_clean"])

    # Clustering selon algorithme choisi
    if clustering_algo == "K-Means":
        model = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
        clusters = model.fit_predict(X_tfidf)
    elif clustering_algo == "Hierarchical":
        model = AgglomerativeClustering(n_clusters=n_clusters)
        clusters = model.fit_predict(X_tfidf.toarray())
    else:  # DBSCAN
        model = DBSCAN(eps=0.5, min_samples=5)
        clusters = model.fit_predict(X_tfidf.toarray())
        n_clusters = len(set(clusters)) - (1 if -1 in clusters else 0)

    # t-SNE
    tsne = TSNE(n_components=2, random_state=42, perplexity=min(30, sample_size - 1))
    X_tsne = tsne.fit_transform(X_tfidf.toarray())

    tsne_df = pd.DataFrame(
        {
            "x": X_tsne[:, 0],
            "y": X_tsne[:, 1],
            "cluster": clusters,
            "region": sample_df["region_name"].values,
            "contract": sample_df["contract_type"].values,
        }
    )

    # Message de succès
    st.success(
        f"✅ {clustering_algo} exécuté avec succès ! {n_clusters} clusters identifiés"
    )

# Scatter 2D
st.markdown("### 🎯 Visualisation t-SNE 2D")

fig_scatter = px.scatter(
    tsne_df,
    x="x",
    y="y",
    color="cluster",
    hover_data=["region", "contract"],
    color_continuous_scale="Turbo",
    title=f"{clustering_algo} - Projection t-SNE 2D",
)

fig_scatter.update_layout(
    template="plotly_dark",
    height=600,
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(color="#00ff41", family="Orbitron"),
    title_font=dict(size=18, color="#00ff41"),
)

fig_scatter.update_traces(
    marker=dict(size=10, opacity=0.7, line=dict(color="#00ff41", width=1))
)

st.plotly_chart(fig_scatter, use_container_width=True)

st.markdown("</div>", unsafe_allow_html=True)

# FIN DE LA PARTIE 2
# LA PARTIE 3 SUIT


# ============================================================================
# SECTION MISTRAL AI (VERSION ROBUSTE ET CORRIGÉE)
# ============================================================================

if use_mistral:
    st.markdown(
        '<div class="section-header"><h2 class="section-title">🤖 MISTRAL AI - ANALYSE SÉMANTIQUE ULTRA-AVANCÉE</h2></div>',
        unsafe_allow_html=True,
    )

    st.markdown('<div class="mistral-supreme">', unsafe_allow_html=True)
    st.markdown(
        '<h2 class="mistral-title-supreme">🤖 MISTRAL AI INTELLIGENCE ENGINE</h2>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<p style="text-align: center; color: white; font-family: Orbitron; font-size: 1.1rem; letter-spacing: 2px;">>>> ANALYSE MULTI-DIMENSIONNELLE EN COURS <<<</p>',
        unsafe_allow_html=True,
    )

    # Analyser chaque cluster
    for cluster_id in range(min(n_clusters, 6)):
        try:
            # Obtenir les indices des documents du cluster
            cluster_mask = clusters == cluster_id
            cluster_indices = sample_df.index[cluster_mask].tolist()
            n_docs = len(cluster_indices)

            if n_docs == 0:
                continue

            # Récupérer les documents du cluster depuis filtered
            cluster_docs = filtered.loc[cluster_indices].copy()

            # Top termes TF-IDF
            cluster_texts = cluster_docs["text_clean"].dropna().tolist()

            if not cluster_texts or len([t for t in cluster_texts if t.strip()]) == 0:
                st.warning(f"⚠️ Cluster {cluster_id} : Pas de texte disponible")
                continue

            cluster_text = " ".join(cluster_texts)

            vectorizer_cluster = TfidfVectorizer(max_features=20, stop_words="english")
            X_cluster = vectorizer_cluster.fit_transform([cluster_text])
            feature_names_cluster = vectorizer_cluster.get_feature_names_out()
            tfidf_scores = X_cluster.toarray()[0]

            top_terms_indices = tfidf_scores.argsort()[-15:][::-1]
            top_terms = [feature_names_cluster[i] for i in top_terms_indices]

            # Titres d'exemple
            sample_titles = cluster_docs["title"].dropna().tolist()[:25]

            # Région dominante
            top_region = None
            if "region_name" in cluster_docs.columns and len(cluster_docs) > 0:
                region_counts = cluster_docs["region_name"].value_counts()
                if len(region_counts) > 0:
                    top_region = region_counts.index[0]

            # Analyse Mistral SUPREME
            with st.spinner(f"🔄 ANALYSE MISTRAL AI DU CLUSTER {cluster_id}..."):
                analysis = analyze_with_mistral_supreme(
                    top_terms, sample_titles, n_docs, top_region
                )

            # Affichage SPECTACULAIRE
            with st.expander(
                f"🔍 **CLUSTER {cluster_id}** — {analysis['label']} ({n_docs} documents) • Score: {analysis['complexity_score']}/100",
                expanded=(cluster_id == 0),
            ):
                st.markdown('<div class="mistral-insight">', unsafe_allow_html=True)
                st.markdown("#### 📝 DESCRIPTION SÉMANTIQUE")
                st.write(analysis["description"])
                if analysis.get("insights"):
                    st.markdown("**💡 Insights Détectés :**")
                    for insight in analysis["insights"]:
                        st.markdown(f"- {insight}")
                st.markdown("</div>", unsafe_allow_html=True)

                # Compétences identifiées
                st.markdown('<div class="mistral-insight">', unsafe_allow_html=True)
                st.markdown("#### 🎯 COMPÉTENCES TECHNIQUES IDENTIFIÉES")

                if analysis.get("skills_identified"):
                    skills_html = "".join(
                        [
                            f'<span class="skill-badge">{skill.upper()}</span>'
                            for skill in analysis["skills_identified"][:12]
                        ]
                    )
                    st.markdown(skills_html, unsafe_allow_html=True)
                st.markdown("</div>", unsafe_allow_html=True)

                # Familles de métiers
                fam_col1, fam_col2 = st.columns(2)

                with fam_col1:
                    st.markdown('<div class="mistral-insight">', unsafe_allow_html=True)
                    st.markdown("#### 👥 FAMILLES DE MÉTIERS")
                    if analysis.get("job_families"):
                        for family in analysis["job_families"]:
                            st.markdown(f"### {family}")
                    st.markdown("</div>", unsafe_allow_html=True)

                with fam_col2:
                    st.markdown('<div class="mistral-insight">', unsafe_allow_html=True)
                    st.markdown("#### 📊 MÉTRIQUES")
                    st.metric("Documents", n_docs)
                    st.metric("Confiance", f"{analysis['confidence']:.1%}")
                    st.metric("Complexité", f"{analysis['complexity_score']}/100")
                    st.markdown("</div>", unsafe_allow_html=True)

        except Exception as e:
            st.error(f"⚠️ Erreur cluster {cluster_id}")
            with st.expander("🔍 Détails", expanded=False):
                st.code(f"{type(e).__name__}: {str(e)}")

    st.markdown("</div>", unsafe_allow_html=True)

# ============================================================================
# FOOTER SPECTACULAIRE
# ============================================================================

st.markdown("---")

timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
n_skills_detected = len([s for s in skill_counts if s])

st.markdown(
    f"""
<div class="command-header" style="padding: 2rem;">
    <p style="text-align: center; color: #00ff41; font-family: 'Orbitron', monospace; font-size: 1.3rem; margin: 0;">
        🛸 MISSION ACCOMPLIE • ANALYSE COMPLÈTE TERMINÉE 🛸
    </p>
    <p style="text-align: center; color: #00d4ff; font-family: 'Orbitron', monospace; font-size: 1rem; margin-top: 1rem;">
        📊 {len(filtered):,} DOCUMENTS • {unique_words:,} TERMES • 
        {n_clusters} CLUSTERS • {n_skills_detected} COMPÉTENCES •
        ⏰ {timestamp}
    </p>
    <p style="text-align: center; color: #a855f7; font-family: 'Orbitron', monospace; font-size: 0.9rem; margin-top: 1rem;">
        >>> NLP INTELLIGENCE COMMAND CENTER v3.0 • POWERED BY MISTRAL AI <<<
    </p>
</div>
""",
    unsafe_allow_html=True,
)

# ============================================================================
# WORD EMBEDDINGS - WORD2VEC & DOC2VEC
# ============================================================================

st.markdown(
    '<div class="section-header"><h2 class="section-title">🎯 WORD EMBEDDINGS - INTELLIGENCE VECTORIELLE</h2></div>',
    unsafe_allow_html=True,
)

# Télécharger les ressources NLTK si nécessaire
try:
    nltk.data.find("tokenizers/punkt")
except LookupError:
    nltk.download("punkt", quiet=True)

# ============================================================================
# PRÉPARATION DES DONNÉES
# ============================================================================


@st.cache_resource
def prepare_embeddings_data(df_input):
    """Prépare les données pour Word2Vec et Doc2Vec"""
    corpus_tokens = []
    for text in df_input["text_clean"]:
        tokens = word_tokenize(text.lower())
        tokens = [t for t in tokens if len(t) >= 3 and t.isalpha()]
        if tokens:
            corpus_tokens.append(tokens)

    documents = [
        TaggedDocument(words=tokens, tags=[i]) for i, tokens in enumerate(corpus_tokens)
    ]

    return corpus_tokens, documents


with st.spinner("🔄 PRÉPARATION DES DONNÉES POUR EMBEDDINGS..."):
    corpus_tokens, doc_tagged = prepare_embeddings_data(filtered)

st.markdown(
    f"""
<div style="background: rgba(0,255,65,0.1); border: 2px solid rgba(0,255,65,0.3); border-radius: 10px; padding: 1rem; margin: 1rem 0; text-align: center;">
    <span style="color: #00ff41; font-family: 'Orbitron', monospace; font-size: 1.1rem;">
        >>> {len(corpus_tokens):,} DOCUMENTS TOKENISÉS • PRÊT POUR L'ENTRAÎNEMENT <<<
    </span>
</div>
""",
    unsafe_allow_html=True,
)

# ============================================================================
# CONFIGURATION DES MODÈLES
# ============================================================================

st.markdown('<div class="analysis-card">', unsafe_allow_html=True)

embed_col1, embed_col2 = st.columns(2)

with embed_col1:
    st.markdown("### ⚙️ PARAMÈTRES WORD2VEC")
    w2v_size = st.slider("🔢 Dimension Vecteurs", 50, 300, 100, step=50, key="w2v_size")
    w2v_window = st.slider("🪟 Fenêtre Contexte", 2, 10, 5, key="w2v_window")
    w2v_min_count = st.slider("📊 Fréquence Minimale", 1, 5, 2, key="w2v_min")

with embed_col2:
    st.markdown("### ⚙️ PARAMÈTRES DOC2VEC")
    d2v_size = st.slider("🔢 Dimension Vecteurs", 50, 300, 100, step=50, key="d2v_size")
    d2v_window = st.slider("🪟 Fenêtre Contexte", 2, 10, 5, key="d2v_window")
    d2v_min_count = st.slider("📊 Fréquence Minimale", 1, 5, 2, key="d2v_min")


@st.cache_resource
def train_word2vec(corpus, vector_size, window, min_count):
    model = Word2Vec(
        sentences=corpus,
        vector_size=vector_size,
        window=window,
        min_count=min_count,
        epochs=20,
        seed=42,
        workers=4,
    )
    return model


@st.cache_resource
def train_doc2vec(documents, vector_size, window, min_count):
    model = Doc2Vec(
        documents=documents,
        vector_size=vector_size,
        window=window,
        min_count=min_count,
        epochs=40,
        seed=42,
        workers=4,
    )
    return model


# Entraînement
with st.spinner("🧠 ENTRAÎNEMENT WORD2VEC EN COURS..."):
    model_w2v = train_word2vec(corpus_tokens, w2v_size, w2v_window, w2v_min_count)

with st.spinner("🧠 ENTRAÎNEMENT DOC2VEC EN COURS..."):
    model_d2v = train_doc2vec(doc_tagged, d2v_size, d2v_window, d2v_min_count)

vocab_size_w2v = len(model_w2v.wv)
vocab_size_d2v = len(model_d2v.dv)

# Préparer vocabulaire
word_freq = Counter()
for doc in corpus_tokens:
    word_freq.update(doc)
vocab_list_full = [word for word, _ in word_freq.most_common()]

# Métriques d'entraînement
em1, em2, em3, em4 = st.columns(4)

with em1:
    st.markdown(
        f"""
    <div class="metric-command">
        <div class="metric-value-command">{vocab_size_w2v:,}</div>
        <div class="metric-label-command">🔤 MOTS W2V</div>
    </div>
    """,
        unsafe_allow_html=True,
    )

with em2:
    st.markdown(
        f"""
    <div class="metric-command">
        <div class="metric-value-command">{vocab_size_d2v:,}</div>
        <div class="metric-label-command">📄 DOCS D2V</div>
    </div>
    """,
        unsafe_allow_html=True,
    )

with em3:
    st.markdown(
        f"""
    <div class="metric-command">
        <div class="metric-value-command">{w2v_size}D</div>
        <div class="metric-label-command">📐 DIM W2V</div>
    </div>
    """,
        unsafe_allow_html=True,
    )

with em4:
    st.markdown(
        f"""
    <div class="metric-command">
        <div class="metric-value-command">{d2v_size}D</div>
        <div class="metric-label-command">📐 DIM D2V</div>
    </div>
    """,
        unsafe_allow_html=True,
    )

st.markdown("</div>", unsafe_allow_html=True)

# ============================================================================
# WORD2VEC EXPLORATION
# ============================================================================

st.markdown(
    '<div class="section-header"><h2 class="section-title">🔤 EXPLORATION WORD2VEC</h2></div>',
    unsafe_allow_html=True,
)

w2v_tabs = st.tabs(["🎯 Similarité", "⚡ Analogies", "📊 Visualisation", "🎨 Clusters"])

# ============================================================================
# TAB 1: SIMILARITÉ / DISSIMILARITÉ
# ============================================================================

with w2v_tabs[0]:
    st.markdown('<div class="analysis-card">', unsafe_allow_html=True)

    sim_col1, sim_col2 = st.columns(2)

    with sim_col1:
        st.markdown("### 🔍 MOTS SIMILAIRES")

        limit_vocab_sim = st.checkbox(
            "📊 Limiter aux 500 mots fréquents", value=True, key="limit_sim"
        )
        vocab_to_use = vocab_list_full[:500] if limit_vocab_sim else vocab_list_full

        st.info(f"📚 **{len(vocab_to_use):,} mots disponibles**")

        selected_word = st.selectbox(
            "Mot cible",
            options=vocab_to_use,
            index=0 if vocab_to_use else None,
            key="w2v_similar_word",
        )

        top_n_similar = st.slider("Nombre de résultats", 3, 20, 10, key="top_n_sim")

        # Vérifier que le mot est valide
        if selected_word:
            if selected_word in model_w2v.wv:
                try:
                    similar_words = model_w2v.wv.most_similar(
                        selected_word, topn=top_n_similar
                    )

                    st.markdown(f"#### 🎯 Mots similaires à **'{selected_word}'**")

                    similar_df = pd.DataFrame(similar_words, columns=["Mot", "Score"])
                    similar_df = similar_df.sort_values("Score", ascending=False)
                    similar_df = similar_df.iloc[::-1]

                    fig_similar = go.Figure()
                    fig_similar.add_trace(
                        go.Bar(
                            y=similar_df["Mot"],
                            x=similar_df["Score"],
                            orientation="h",
                            marker=dict(
                                color=similar_df["Score"],
                                colorscale="Viridis",
                                line=dict(color="#00ff41", width=2),
                            ),
                            text=[f"{s:.4f}" for s in similar_df["Score"]],
                            textposition="auto",
                            textfont=dict(color="white", family="Orbitron"),
                        )
                    )

                    fig_similar.update_layout(
                        template="plotly_dark",
                        height=450,
                        paper_bgcolor="rgba(0,0,0,0)",
                        plot_bgcolor="rgba(0,0,0,0)",
                        font=dict(color="#00ff41", family="Orbitron"),
                        xaxis_title="Score Similarité",
                        yaxis_title="",
                        showlegend=False,
                    )

                    st.plotly_chart(fig_similar, use_container_width=True)

                except Exception as e:
                    st.error(f"⚠️ ERREUR: {e}")
                    st.code(str(e))  # Debug info
            else:
                st.warning(
                    f"⚠️ Le mot '{selected_word}' n'est pas dans le vocabulaire Word2Vec"
                )
                st.info(
                    f"💡 Essayez un autre mot parmi les {len(vocab_to_use):,} disponibles"
                )
        else:
            st.info("👆 Sélectionnez un mot pour voir les mots similaires")

    with sim_col2:
        st.markdown("### ⚡ MOTS DISSIMILAIRES")

        limit_vocab_dis = st.checkbox(
            "📊 Limiter aux 500 mots fréquents", value=True, key="limit_dis"
        )
        vocab_to_use_dis = vocab_list_full[:500] if limit_vocab_dis else vocab_list_full

        st.info(f"📚 **{len(vocab_to_use_dis):,} mots disponibles**")

        selected_word_dis = st.selectbox(
            "Mot cible",
            options=vocab_to_use_dis,
            index=1 if len(vocab_to_use_dis) > 1 else 0,
            key="w2v_dissimilar_word",
        )

        top_n_dissimilar = st.slider("Nombre de résultats", 3, 20, 10, key="top_n_dis")

        if selected_word_dis and selected_word_dis in model_w2v.wv:
            try:
                # Calculer tous les mots et leurs similarités
                all_words = vocab_list_full[:1000]  # Limiter pour performance

                similarities = []
                for word in all_words:
                    if word != selected_word_dis and word in model_w2v.wv:
                        sim = model_w2v.wv.similarity(selected_word_dis, word)
                        similarities.append((word, sim))

                # Trier par similarité croissante (les moins similaires)
                dissimilar_words = sorted(similarities, key=lambda x: x[1])[
                    :top_n_dissimilar
                ]

                st.markdown(f"#### ⚡ Mots dissimilaires à **'{selected_word_dis}'**")

                dissimilar_df = pd.DataFrame(dissimilar_words, columns=["Mot", "Score"])
                dissimilar_df = dissimilar_df.sort_values("Score", ascending=True)
                dissimilar_df = dissimilar_df.iloc[::-1]
                fig_dissimilar = go.Figure()
                fig_dissimilar.add_trace(
                    go.Bar(
                        y=dissimilar_df["Mot"],
                        x=dissimilar_df["Score"],
                        orientation="h",
                        marker=dict(
                            color=dissimilar_df["Score"],
                            colorscale="Reds_r",
                            line=dict(color="#f97316", width=2),
                        ),
                        text=[f"{s:.4f}" for s in dissimilar_df["Score"]],
                        textposition="auto",
                        textfont=dict(color="white", family="Orbitron"),
                    )
                )

                fig_dissimilar.update_layout(
                    template="plotly_dark",
                    height=450,
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",
                    font=dict(color="#f97316", family="Orbitron"),
                    xaxis_title="Score de similarité",
                    yaxis_title="",
                    showlegend=False,
                )

                st.plotly_chart(fig_dissimilar, use_container_width=True)

            except Exception as e:
                st.error(f"⚠️ ERREUR: {e}")
        else:
            st.warning("⚠️ Mot non trouvé")

    st.markdown("</div>", unsafe_allow_html=True)

# ============================================================================
# TAB 2: ANALOGIES
# ============================================================================

with w2v_tabs[1]:
    st.markdown('<div class="analysis-card">', unsafe_allow_html=True)
    st.markdown("### 🧮 ANALOGIES VECTORIELLES")
    st.markdown("**Explorez les relations : A est à B ce que C est à ?**")

    limit_vocab_analogy = st.checkbox(
        "📊 Limiter aux 500 mots fréquents", value=True, key="limit_analogy"
    )
    vocab_analogy = vocab_list_full[:500] if limit_vocab_analogy else vocab_list_full

    st.info(f"📚 **{len(vocab_analogy):,} mots disponibles**")

    anal_col1, anal_col2, anal_col3 = st.columns(3)

    with anal_col1:
        word_a = st.selectbox(
            "🅰️ Mot A (positif)", vocab_analogy, index=0, key="analogy_a"
        )
    with anal_col2:
        word_b = st.selectbox(
            "🅱️ Mot B (négatif)",
            vocab_analogy,
            index=1 if len(vocab_analogy) > 1 else 0,
            key="analogy_b",
        )
    with anal_col3:
        word_c = st.selectbox(
            "©️ Mot C (positif)",
            vocab_analogy,
            index=2 if len(vocab_analogy) > 2 else 0,
            key="analogy_c",
        )

    if st.button("🔍 CALCULER L'ANALOGIE", use_container_width=True):
        try:
            if all(w in model_w2v.wv for w in [word_a, word_b, word_c]):
                results = model_w2v.wv.most_similar(
                    positive=[word_a, word_c], negative=[word_b], topn=10
                )

                st.markdown(
                    f"### 🎯 **{word_a}** : **{word_b}** = **{word_c}** : **?**"
                )

                analogy_df = pd.DataFrame(results, columns=["Mot", "Score"])

                # Graphique
                fig_analogy = go.Figure()
                fig_analogy.add_trace(
                    go.Scatter(
                        x=list(range(len(analogy_df))),
                        y=analogy_df["Score"],
                        mode="markers+lines+text",
                        marker=dict(
                            size=20,
                            color=analogy_df["Score"],
                            colorscale="Plasma",
                            line=dict(color="#00ff41", width=3),
                        ),
                        line=dict(color="#00d4ff", width=3),
                        text=analogy_df["Mot"],
                        textposition="top center",
                        textfont=dict(color="#00ff41", family="Orbitron", size=11),
                    )
                )

                fig_analogy.update_layout(
                    template="plotly_dark",
                    height=500,
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",
                    font=dict(color="#00ff41", family="Orbitron"),
                    xaxis_title="Rang",
                    yaxis_title="Score Similarité",
                    showlegend=False,
                )

                st.plotly_chart(fig_analogy, use_container_width=True)

                # Table
                st.dataframe(
                    analogy_df.style.format({"Score": "{:.4f}"}),
                    use_container_width=True,
                    hide_index=True,
                )
            else:
                st.error("⚠️ Un ou plusieurs mots introuvables")
        except Exception as e:
            st.error(f"⚠️ ERREUR: {e}")

    st.markdown("</div>", unsafe_allow_html=True)

# ============================================================================
# TAB 3: VISUALISATION t-SNE
# ============================================================================

with w2v_tabs[2]:
    st.markdown('<div class="analysis-card">', unsafe_allow_html=True)
    st.markdown("### 📊 VISUALISATION t-SNE DES EMBEDDINGS")

    viz_method = st.radio(
        "Méthode de sélection",
        ["🎯 Sélection Manuelle", "📊 Top N Fréquents", "🎲 Aléatoire"],
        horizontal=True,
    )

    if viz_method == "🎯 Sélection Manuelle":
        limit_vocab_viz = st.checkbox(
            "📊 Limiter aux 500 mots fréquents", value=True, key="limit_viz"
        )
        vocab_viz = vocab_list_full[:500] if limit_vocab_viz else vocab_list_full

        st.info(f"📚 **{len(vocab_viz):,} mots disponibles**")

        viz_words = st.multiselect(
            "Sélectionner des mots",
            options=vocab_viz,
            default=vocab_viz[:30] if len(vocab_viz) >= 30 else vocab_viz,
            key="viz_words",
        )
    elif viz_method == "📊 Top N Fréquents":
        n_top_words = st.slider(
            "Nombre de mots", 10, min(200, vocab_size_w2v), 50, key="n_top_viz"
        )
        viz_words = vocab_list_full[:n_top_words]
    else:
        n_random_words = st.slider(
            "Nombre de mots", 10, min(200, vocab_size_w2v), 50, key="n_random_viz"
        )
        import random

        viz_words = random.sample(
            vocab_list_full[:500], min(n_random_words, len(vocab_list_full[:500]))
        )

    if viz_words and len(viz_words) >= 2:
        try:
            word_vectors = np.array(
                [model_w2v.wv[word] for word in viz_words if word in model_w2v.wv]
            )
            viz_words_valid = [word for word in viz_words if word in model_w2v.wv]

            if len(word_vectors) < 2:
                st.warning("⚠️ Pas assez de mots valides")
            else:
                perplexity_val = min(30, len(word_vectors) - 1)
                tsne = TSNE(n_components=2, random_state=42, perplexity=perplexity_val)
                coords_2d = tsne.fit_transform(word_vectors)

                viz_df = pd.DataFrame(
                    {
                        "x": coords_2d[:, 0],
                        "y": coords_2d[:, 1],
                        "word": viz_words_valid,
                        "freq": [word_freq.get(w, 0) for w in viz_words_valid],
                    }
                )

                fig_tsne = go.Figure()
                fig_tsne.add_trace(
                    go.Scatter(
                        x=viz_df["x"],
                        y=viz_df["y"],
                        mode="markers+text",
                        marker=dict(
                            size=[np.log1p(f) * 4 for f in viz_df["freq"]],
                            color=viz_df["freq"],
                            colorscale="Turbo",
                            line=dict(color="#00ff41", width=2),
                            showscale=True,
                            colorbar=dict(
                                title="Fréquence",
                                titlefont=dict(color="#00ff41", family="Orbitron"),
                                tickfont=dict(color="#00ff41", family="Orbitron"),
                            ),
                        ),
                        text=viz_df["word"],
                        textposition="top center",
                        textfont=dict(color="#00ff41", size=10, family="Orbitron"),
                        hovertemplate="<b>%{text}</b><br>Fréquence: %{customdata}<extra></extra>",
                        customdata=viz_df["freq"],
                    )
                )

                fig_tsne.update_layout(
                    template="plotly_dark",
                    height=700,
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",
                    font=dict(color="#00ff41", family="Orbitron"),
                    xaxis_title="t-SNE Dimension 1",
                    yaxis_title="t-SNE Dimension 2",
                    showlegend=False,
                    hovermode="closest",
                )

                st.plotly_chart(fig_tsne, use_container_width=True)
                st.caption("💡 Taille des points = fréquence des mots dans le corpus")

        except Exception as e:
            st.error(f"⚠️ ERREUR: {e}")
    else:
        st.info("📌 Sélectionnez au moins 2 mots")

    st.markdown("</div>", unsafe_allow_html=True)

# ============================================================================
# TAB 4: CLUSTERING DE MOTS
# ============================================================================

with w2v_tabs[3]:
    st.markdown('<div class="analysis-card">', unsafe_allow_html=True)
    st.markdown("### 🎨 CLUSTERING SÉMANTIQUE DES MOTS")
    st.markdown("**Découvrez des groupes de mots cohérents**")

    cluster_col1, cluster_col2 = st.columns([1, 2])

    with cluster_col1:
        st.markdown("#### ⚙️ CONFIGURATION")
        n_words_cluster = st.slider(
            "Nombre de mots",
            50,
            min(500, vocab_size_w2v),
            min(150, vocab_size_w2v),
            step=50,
            key="n_words_cluster",
        )
        n_word_clusters = st.slider(
            "Nombre de clusters", 3, 15, 8, key="n_word_clusters"
        )

        if st.button("🎯 GÉNÉRER LES CLUSTERS", use_container_width=True):
            try:
                top_words = vocab_list_full[:n_words_cluster]
                word_vecs = np.array(
                    [model_w2v.wv[w] for w in top_words if w in model_w2v.wv]
                )
                valid_words = [w for w in top_words if w in model_w2v.wv]

                kmeans_words = KMeans(
                    n_clusters=n_word_clusters, random_state=42, n_init=10
                )
                word_clusters = kmeans_words.fit_predict(word_vecs)

                st.session_state["word_cluster_results"] = {
                    "words": valid_words,
                    "clusters": word_clusters,
                    "vectors": word_vecs,
                    "n_clusters": n_word_clusters,
                }

                st.success(f"✅ {len(valid_words)} mots • {n_word_clusters} clusters !")

            except Exception as e:
                st.error(f"⚠️ ERREUR: {e}")

    with cluster_col2:
        if "word_cluster_results" in st.session_state:
            results = st.session_state["word_cluster_results"]

            st.markdown("#### 📊 VISUALISATION t-SNE")

            perplexity_cluster = min(30, len(results["vectors"]) - 1)
            tsne_cluster = TSNE(
                n_components=2, random_state=42, perplexity=perplexity_cluster
            )
            coords_cluster = tsne_cluster.fit_transform(results["vectors"])

            cluster_viz_df = pd.DataFrame(
                {
                    "x": coords_cluster[:, 0],
                    "y": coords_cluster[:, 1],
                    "word": results["words"],
                    "cluster": results["clusters"],
                }
            )

            fig_word_clusters = px.scatter(
                cluster_viz_df,
                x="x",
                y="y",
                color="cluster",
                text="word",
                color_continuous_scale="Turbo",
                title=f"{len(results['words'])} mots • {results['n_clusters']} clusters",
            )

            fig_word_clusters.update_traces(
                textposition="top center",
                textfont=dict(size=8, color="#00ff41", family="Orbitron"),
                marker=dict(size=12, line=dict(width=2, color="#00ff41")),
            )

            fig_word_clusters.update_layout(
                template="plotly_dark",
                height=600,
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font=dict(color="#00ff41", family="Orbitron"),
                title_font=dict(size=16, color="#00ff41"),
            )

            st.plotly_chart(fig_word_clusters, use_container_width=True)
        else:
            st.info("👆 Cliquez sur 'GÉNÉRER LES CLUSTERS'")

    # Analyse détaillée
    if "word_cluster_results" in st.session_state:
        st.markdown("---")
        st.markdown("#### 🔍 ANALYSE DÉTAILLÉE DES CLUSTERS")

        results = st.session_state["word_cluster_results"]
        cluster_analysis_df = pd.DataFrame(
            {"word": results["words"], "cluster": results["clusters"]}
        )

        cols_clusters = st.columns(min(3, results["n_clusters"]))

        for i in range(results["n_clusters"]):
            with cols_clusters[i % 3]:
                cluster_words = cluster_analysis_df[
                    cluster_analysis_df["cluster"] == i
                ]["word"].tolist()

                st.markdown(
                    f"""
                <div style="background: linear-gradient(135deg, rgba(0, 255, 65, 0.1), rgba(0, 212, 255, 0.1)); 
                            border: 3px solid rgba(0, 255, 65, 0.5); 
                            border-radius: 15px; 
                            padding: 1.5rem; 
                            margin-bottom: 1.5rem;">
                    <h4 style="color: #00ff41; font-family: 'Orbitron', monospace; margin: 0 0 0.5rem 0;">
                        CLUSTER {i+1}
                    </h4>
                    <p style="color: #00d4ff; font-family: 'Orbitron', monospace; font-size: 0.9rem;">
                        {len(cluster_words)} MOTS
                    </p>
                    <div style="color: #e0e0e0; font-size: 0.85rem; line-height: 1.8; font-family: 'Courier New';">
                        {', '.join(cluster_words[:20])}{'...' if len(cluster_words) > 20 else ''}
                    </div>
                </div>
                """,
                    unsafe_allow_html=True,
                )

        # Distribution
        st.markdown("#### 📊 DISTRIBUTION DES MOTS")

        cluster_counts = cluster_analysis_df["cluster"].value_counts().sort_index()

        fig_cluster_dist = go.Figure()
        fig_cluster_dist.add_trace(
            go.Bar(
                x=[f"Cluster {i}" for i in cluster_counts.index],
                y=cluster_counts.values,
                marker=dict(
                    color=cluster_counts.values,
                    colorscale="Turbo",
                    line=dict(color="#00ff41", width=3),
                ),
                text=cluster_counts.values,
                textposition="outside",
                textfont=dict(color="#00ff41", family="Orbitron", size=14),
            )
        )

        fig_cluster_dist.update_layout(
            template="plotly_dark",
            height=350,
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#00ff41", family="Orbitron"),
            yaxis_title="Nombre de mots",
        )

        st.plotly_chart(fig_cluster_dist, use_container_width=True)

    st.markdown("</div>", unsafe_allow_html=True)

# ============================================================================
# DOC2VEC EXPLORATION (SANS CLUSTERING - UNIQUEMENT SIMILARITÉ)
# ============================================================================

st.markdown(
    '<div class="section-header"><h2 class="section-title">📄 EXPLORATION DOC2VEC</h2></div>',
    unsafe_allow_html=True,
)

st.markdown('<div class="analysis-card">', unsafe_allow_html=True)

doc_col1, doc_col2 = st.columns(2)

with doc_col1:
    st.markdown("### 🔍 DOCUMENTS SIMILAIRES")

    doc_indices = list(range(min(300, vocab_size_d2v)))
    selected_doc_idx = st.selectbox(
        "Document cible",
        options=doc_indices,
        format_func=lambda x: f"Doc {x}: {filtered.iloc[x]['title'][:45]}...",
        key="d2v_doc",
    )

    top_n_docs = st.slider("Nombre de résultats", 3, 20, 10, key="top_n_docs")

    if st.button("🔍 RECHERCHER DOCUMENTS SIMILAIRES", use_container_width=True):
        try:
            similar_docs = model_d2v.dv.most_similar(selected_doc_idx, topn=top_n_docs)

            st.markdown(f"#### 📄 Document source (#{selected_doc_idx})")
            st.markdown(f"**Titre:** {filtered.iloc[selected_doc_idx]['title']}")
            st.markdown(f"**Région:** {filtered.iloc[selected_doc_idx]['region_name']}")
            st.markdown(
                f"**Contrat:** {filtered.iloc[selected_doc_idx]['contract_type']}"
            )
            st.markdown("---")

            similar_docs_data = []
            for doc_id, score in similar_docs:
                if doc_id < len(filtered):
                    similar_docs_data.append(
                        {
                            "Index": doc_id,
                            "Score": score,
                            "Titre": filtered.iloc[doc_id]["title"][:60],
                            "Région": filtered.iloc[doc_id]["region_name"],
                            "Contrat": filtered.iloc[doc_id]["contract_type"],
                        }
                    )

            similar_docs_df = pd.DataFrame(similar_docs_data)

            # Graphique
            fig_doc_sim = go.Figure()
            fig_doc_sim.add_trace(
                go.Bar(
                    y=[f"Doc {row['Index']}" for _, row in similar_docs_df.iterrows()],
                    x=similar_docs_df["Score"],
                    orientation="h",
                    marker=dict(
                        color=similar_docs_df["Score"],
                        colorscale="Turbo",
                        line=dict(color="#00ff41", width=2),
                    ),
                    text=[f"{s:.4f}" for s in similar_docs_df["Score"]],
                    textposition="auto",
                    textfont=dict(color="white", family="Orbitron"),
                    hovertext=[
                        f"{row['Titre']}<br>{row['Région']}<br>{row['Contrat']}"
                        for _, row in similar_docs_df.iterrows()
                    ],
                    hoverinfo="text+x",
                )
            )

            fig_doc_sim.update_layout(
                template="plotly_dark",
                height=450,
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font=dict(color="#00ff41", family="Orbitron"),
                xaxis_title="Score Similarité",
                showlegend=False,
            )

            st.plotly_chart(fig_doc_sim, use_container_width=True)

            # Table
            st.dataframe(
                similar_docs_df.style.format({"Score": "{:.4f}"}),
                use_container_width=True,
                hide_index=True,
            )

        except Exception as e:
            st.error(f"⚠️ ERREUR: {e}")

with doc_col2:
    st.markdown("### 🆕 ANALYSE TEXTE LIBRE")
    st.markdown("**Trouvez des offres similaires à partir d'un texte**")

    new_text = st.text_area(
        "Entrez une description de poste",
        height=180,
        placeholder="Ex: Data Scientist Python avec Machine Learning, Spark et AWS...",
        key="new_doc_text",
    )

    if st.button("🔍 ANALYSER LE TEXTE", use_container_width=True):
        if new_text.strip():
            try:
                new_tokens = word_tokenize(new_text.lower())
                new_tokens = [t for t in new_tokens if len(t) >= 3 and t.isalpha()]

                new_vector = model_d2v.infer_vector(new_tokens)
                similar_to_new = model_d2v.dv.most_similar([new_vector], topn=10)

                st.success("✅ ANALYSE TERMINÉE !")

                new_similar_data = []
                for doc_id, score in similar_to_new:
                    if doc_id < len(filtered):
                        new_similar_data.append(
                            {
                                "Index": doc_id,
                                "Score": f"{score:.4f}",
                                "Titre": filtered.iloc[doc_id]["title"][:55],
                                "Région": filtered.iloc[doc_id]["region_name"],
                                "Contrat": filtered.iloc[doc_id]["contract_type"],
                            }
                        )

                new_similar_df = pd.DataFrame(new_similar_data)
                st.dataframe(new_similar_df, use_container_width=True, hide_index=True)

            except Exception as e:
                st.error(f"⚠️ ERREUR: {e}")
        else:
            st.warning("⚠️ Veuillez entrer du texte")

st.markdown("</div>", unsafe_allow_html=True)

# ============================================================================
# FOOTER EMBEDDINGS
# ============================================================================

st.markdown("---")

st.markdown(
    f"""
<div class="command-header" style="padding: 2rem;">
    <p style="text-align: center; color: #00ff41; font-family: 'Orbitron', monospace; font-size: 1.4rem; margin: 0;">
        🎯 EMBEDDINGS ANALYSIS COMPLETE
    </p>
    <p style="text-align: center; color: #00d4ff; font-family: 'Orbitron', monospace; font-size: 1.1rem; margin-top: 1rem;">
        Word2Vec: {vocab_size_w2v:,} MOTS • {w2v_size}D | 
        Doc2Vec: {vocab_size_d2v:,} DOCS • {d2v_size}D
    </p>
    <p style="text-align: center; color: #a855f7; font-family: 'Orbitron', monospace; font-size: 0.9rem; margin-top: 0.8rem;">
        >>> INTELLIGENCE VECTORIELLE OPÉRATIONNELLE <<<
    </p>
</div>
""",
    unsafe_allow_html=True,
)
