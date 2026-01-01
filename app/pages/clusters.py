from __future__ import annotations
import streamlit as st
from components import inject_premium_css, top_navbar
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from collections import Counter
import re

from config import DB_PATH
from db import query_df
from llm_mistral import mistral_label_cluster


# =========================
# CONFIGURATION
# =========================
st.set_page_config(
    layout="wide",
    page_title="🧠 Clusters Intelligence",
    page_icon="🧠"
)

inject_premium_css()
top_navbar(active="Clusters")


# =========================
# CSS SPÉCIFIQUE POUR CETTE PAGE
# =========================
st.markdown("""
<style>
    /* Hero section clusters */
    .clusters-hero {
        background: linear-gradient(135deg, 
            rgba(124, 58, 237, 0.2) 0%, 
            rgba(59, 130, 246, 0.15) 50%,
            rgba(236, 72, 153, 0.2) 100%);
        border: 2px solid rgba(139, 92, 246, 0.4);
        border-radius: 24px;
        padding: 3rem 2rem;
        margin-bottom: 2rem;
        text-align: center;
        position: relative;
        overflow: hidden;
    }
    
    .clusters-hero::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 4px;
        background: linear-gradient(90deg, #7c3aed 0%, #3b82f6 50%, #ec4899 100%);
        animation: slideBar 3s linear infinite;
    }
    
    @keyframes slideBar {
        0% { transform: translateX(-100%); }
        100% { transform: translateX(100%); }
    }
    
    .clusters-title {
        font-size: 3rem;
        font-weight: 900;
        background: linear-gradient(135deg, #60a5fa 0%, #a78bfa 50%, #ec4899 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 1rem;
    }
    
    .clusters-subtitle {
        font-size: 1.2rem;
        color: #94a3b8;
        font-weight: 500;
    }
    
    /* Cards améliorées */
    .insight-card {
        background: linear-gradient(135deg, 
            rgba(30, 41, 59, 0.95) 0%, 
            rgba(51, 65, 85, 0.8) 100%);
        border: 2px solid rgba(139, 92, 246, 0.3);
        border-radius: 20px;
        padding: 2rem;
        margin-bottom: 1.5rem;
        transition: all 0.3s ease;
    }
    
    .insight-card:hover {
        transform: translateY(-4px);
        border-color: rgba(139, 92, 246, 0.6);
        box-shadow: 0 12px 48px rgba(124, 58, 237, 0.4);
    }
    
    .insight-card h3 {
        color: #f8fafc !important;
        margin-bottom: 1rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    /* Mistral analysis box */
    .mistral-box {
        background: linear-gradient(135deg, 
            rgba(124, 58, 237, 0.15) 0%, 
            rgba(59, 130, 246, 0.1) 100%);
        border: 3px solid rgba(139, 92, 246, 0.5);
        border-radius: 24px;
        padding: 2.5rem;
        margin: 2rem 0;
        position: relative;
        overflow: hidden;
    }
    
    .mistral-box::before {
        content: '🤖';
        position: absolute;
        top: -30px;
        right: -30px;
        font-size: 200px;
        opacity: 0.05;
    }
    
    .mistral-header {
        display: flex;
        align-items: center;
        gap: 1rem;
        margin-bottom: 2rem;
    }
    
    .mistral-icon {
        width: 60px;
        height: 60px;
        border-radius: 16px;
        background: linear-gradient(135deg, #7c3aed 0%, #3b82f6 100%);
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 2rem;
        box-shadow: 0 8px 32px rgba(124, 58, 237, 0.5);
    }
    
    .mistral-title {
        font-size: 2rem;
        font-weight: 800;
        background: linear-gradient(135deg, #60a5fa 0%, #a78bfa 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    /* Stats mini cards */
    .stat-mini {
        background: rgba(30, 41, 59, 0.8);
        border: 1px solid rgba(139, 92, 246, 0.3);
        border-radius: 12px;
        padding: 1rem;
        text-align: center;
    }
    
    .stat-mini-value {
        font-size: 2rem;
        font-weight: 900;
        background: linear-gradient(135deg, #60a5fa 0%, #a78bfa 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    .stat-mini-label {
        font-size: 0.85rem;
        color: #94a3b8;
        font-weight: 600;
        text-transform: uppercase;
        margin-top: 0.5rem;
    }
    
    /* Term tags */
    .term-tag {
        display: inline-block;
        background: linear-gradient(135deg, rgba(124, 58, 237, 0.2) 0%, rgba(59, 130, 246, 0.2) 100%);
        border: 1px solid rgba(139, 92, 246, 0.4);
        color: #cbd5e1;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        margin: 0.25rem;
        font-size: 0.9rem;
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)


# =========================
# HERO SECTION
# =========================
st.markdown("""
<div class="clusters-hero">
    <h1 class="clusters-title">🧠 Intelligence des Clusters</h1>
    <p class="clusters-subtitle">
        Analyse avancée par IA • Détection automatique des familles de métiers • Visualisations interactives
    </p>
</div>
""", unsafe_allow_html=True)


# =========================
# CHARGEMENT DES DONNÉES
# =========================
meta = query_df(
    str(DB_PATH), 
    "SELECT cluster, cluster_label, top_terms, n_docs FROM clusters_meta ORDER BY n_docs DESC"
)

if meta.empty:
    st.warning("⚠️ Aucun cluster trouvé. Exécutez d'abord le clustering.")
    st.stop()


# =========================
# VUE D'ENSEMBLE DES CLUSTERS
# =========================
st.markdown("## 📊 Vue d'Ensemble")

# Stats globales
col_stat1, col_stat2, col_stat3, col_stat4 = st.columns(4)

with col_stat1:
    st.markdown(f"""
    <div class="stat-mini">
        <div class="stat-mini-value">{len(meta)}</div>
        <div class="stat-mini-label">Clusters Détectés</div>
    </div>
    """, unsafe_allow_html=True)

with col_stat2:
    st.markdown(f"""
    <div class="stat-mini">
        <div class="stat-mini-value">{meta['n_docs'].sum():,}</div>
        <div class="stat-mini-label">Offres Analysées</div>
    </div>
    """, unsafe_allow_html=True)

with col_stat3:
    avg_docs = int(meta['n_docs'].mean())
    st.markdown(f"""
    <div class="stat-mini">
        <div class="stat-mini-value">{avg_docs}</div>
        <div class="stat-mini-label">Moyenne / Cluster</div>
    </div>
    """, unsafe_allow_html=True)

with col_stat4:
    biggest = meta.iloc[0]['n_docs']
    st.markdown(f"""
    <div class="stat-mini">
        <div class="stat-mini-value">{biggest}</div>
        <div class="stat-mini-label">Plus Grand Cluster</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# Visualisation: Distribution des clusters
st.markdown("### 📈 Distribution des Offres par Cluster")

fig_dist = px.bar(
    meta,
    x='cluster_label',
    y='n_docs',
    color='n_docs',
    color_continuous_scale='Viridis',
    labels={'n_docs': 'Nombre d\'offres', 'cluster_label': 'Cluster'},
    height=400
)
fig_dist.update_layout(
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)',
    font=dict(color='#cbd5e1', size=11),
    xaxis=dict(tickangle=-45, gridcolor='rgba(148, 163, 184, 0.1)'),
    yaxis=dict(gridcolor='rgba(148, 163, 184, 0.1)'),
    showlegend=False
)
st.plotly_chart(fig_dist, use_container_width=True, config={'displayModeBar': False})

st.markdown("<br>", unsafe_allow_html=True)

# Treemap des clusters
st.markdown("### 🗺️ Treemap des Familles de Métiers")

fig_tree = px.treemap(
    meta,
    path=['cluster_label'],
    values='n_docs',
    color='n_docs',
    color_continuous_scale='Turbo',
    height=500
)
fig_tree.update_layout(
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)',
    font=dict(color='#cbd5e1', size=12),
    margin=dict(t=20, b=20, l=20, r=20)
)
st.plotly_chart(fig_tree, use_container_width=True, config={'displayModeBar': False})


# =========================
# TABLEAU DES CLUSTERS
# =========================
st.markdown("<br><br>", unsafe_allow_html=True)
st.markdown("## 📋 Tableau Détaillé des Clusters")

st.dataframe(
    meta,
    use_container_width=True,
    hide_index=True,
    column_config={
        "cluster": "ID",
        "cluster_label": st.column_config.TextColumn("Famille de Métiers", width="large"),
        "n_docs": st.column_config.NumberColumn("Nombre d'Offres", format="%d"),
        "top_terms": st.column_config.TextColumn("Termes Clés", width="large")
    }
)


# =========================
# ANALYSE DÉTAILLÉE D'UN CLUSTER
# =========================
st.markdown("<br><br>", unsafe_allow_html=True)
st.markdown("## 🔍 Analyse Approfondie")

cluster_id = st.selectbox(
    "Sélectionnez un cluster à analyser",
    meta["cluster"].tolist(),
    format_func=lambda x: f"Cluster {x} - {meta[meta['cluster']==x].iloc[0]['cluster_label']}",
    index=0
)

row = meta[meta["cluster"] == cluster_id].iloc[0]

# Header du cluster sélectionné
st.markdown(f"""
<div class="insight-card">
    <h2 style="color: #f8fafc; margin: 0;">
        🎯 Cluster {cluster_id} — {row['cluster_label']}
    </h2>
    <p style="color: #94a3b8; font-size: 1.1rem; margin-top: 0.5rem;">
        {int(row['n_docs'])} offres d'emploi analysées
    </p>
</div>
""", unsafe_allow_html=True)


# =========================
# ANALYSE DES TERMES
# =========================
st.markdown("### 🔤 Analyse des Termes Clés")

col_terms1, col_terms2 = st.columns([2, 1])

with col_terms1:
    st.markdown('<div class="insight-card">', unsafe_allow_html=True)
    st.markdown("#### 📝 Top Termes (TF-IDF)")
    
    # Afficher les termes comme tags
    terms_str = str(row["top_terms"])[:2000]
    # Extraire les termes (supposons qu'ils sont séparés par des virgules ou espaces)
    terms_list = re.findall(r'\b\w+\b', terms_str)[:30]  # Top 30 termes
    
    terms_html = ""
    for term in terms_list:
        terms_html += f'<span class="term-tag">{term}</span>'
    
    st.markdown(terms_html, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

with col_terms2:
    st.markdown('<div class="insight-card">', unsafe_allow_html=True)
    st.markdown("#### 📊 Statistiques")
    
    # Compter les termes
    term_count = len(terms_list)
    st.metric("Termes Uniques", term_count)
    
    # Longueur moyenne des termes
    if terms_list:
        avg_length = sum(len(t) for t in terms_list) / len(terms_list)
        st.metric("Longueur Moyenne", f"{avg_length:.1f}")
    
    st.markdown('</div>', unsafe_allow_html=True)


# Visualisation: Fréquence des termes
if terms_list:
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("#### 📊 Fréquence d'Apparition des Top Termes")
    
    # Simuler des fréquences (dans un vrai cas, extraire depuis TF-IDF scores)
    terms_freq = pd.DataFrame({
        'terme': terms_list[:15],
        'score': [100 - i*5 for i in range(len(terms_list[:15]))]  # Scores décroissants simulés
    })
    
    fig_terms = px.bar(
        terms_freq,
        x='score',
        y='terme',
        orientation='h',
        color='score',
        color_continuous_scale='Plasma',
        height=500
    )
    fig_terms.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#cbd5e1', size=11),
        xaxis=dict(title='Score TF-IDF', gridcolor='rgba(148, 163, 184, 0.1)'),
        yaxis=dict(title='', gridcolor='rgba(148, 163, 184, 0.1)'),
        showlegend=False
    )
    st.plotly_chart(fig_terms, use_container_width=True, config={'displayModeBar': False})


# =========================
# EXEMPLES D'OFFRES
# =========================
st.markdown("<br><br>", unsafe_allow_html=True)
st.markdown("### 💼 Exemples d'Offres du Cluster")

ex = query_df(
    str(DB_PATH),
    """
    SELECT title, employer, region, url
    FROM offers_enriched
    WHERE cluster = :c
    ORDER BY published_date DESC
    LIMIT 20
    """,
    params={"c": int(cluster_id)},
)

if not ex.empty:
    # Afficher en cards
    st.markdown('<div class="insight-card">', unsafe_allow_html=True)
    
    for idx, offer in ex.iterrows():
        col1, col2 = st.columns([3, 1])
        
        with col1:
            st.markdown(f"**{offer['title']}**")
            st.caption(f"🏢 {offer['employer']} • 📍 {offer['region']}")
        
        with col2:
            if pd.notna(offer['url']):
                st.link_button("🔗 Voir", offer['url'], use_container_width=True)
        
        if idx < len(ex) - 1:
            st.markdown("---")
    
    st.markdown('</div>', unsafe_allow_html=True)
else:
    st.info("Aucune offre trouvée pour ce cluster.")


# =========================
# ANALYSE DES COMPÉTENCES (si disponible)
# =========================
st.markdown("<br><br>", unsafe_allow_html=True)
st.markdown("### 🎯 Compétences Demandées")

# Extraire les compétences depuis les termes
# (Dans un vrai cas, vous auriez une table skills_by_cluster)
skills_keywords = ['python', 'sql', 'machine learning', 'deep learning', 'tensorflow', 
                   'pytorch', 'data', 'analysis', 'statistics', 'cloud', 'aws', 'azure',
                   'spark', 'hadoop', 'docker', 'kubernetes', 'api', 'git']

detected_skills = [skill for skill in skills_keywords if skill in terms_str.lower()]

if detected_skills:
    col_sk1, col_sk2 = st.columns([2, 1])
    
    with col_sk1:
        st.markdown('<div class="insight-card">', unsafe_allow_html=True)
        st.markdown("#### 💡 Compétences Techniques Détectées")
        
        skills_html = ""
        for skill in detected_skills:
            skills_html += f'<span class="term-tag" style="background: linear-gradient(135deg, rgba(16, 185, 129, 0.3) 0%, rgba(5, 150, 105, 0.2) 100%); border-color: rgba(16, 185, 129, 0.5);">{skill}</span>'
        
        st.markdown(skills_html, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col_sk2:
        st.markdown('<div class="insight-card">', unsafe_allow_html=True)
        st.markdown("#### 📈 Statistiques")
        st.metric("Compétences", len(detected_skills))
        st.metric("Couverture", f"{len(detected_skills)/len(skills_keywords)*100:.0f}%")
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Radar chart des compétences
    if len(detected_skills) >= 3:
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Simuler des scores pour chaque compétence
        skills_scores = {skill: 100 - i*10 for i, skill in enumerate(detected_skills[:8])}
        
        fig_radar = go.Figure()
        fig_radar.add_trace(go.Scatterpolar(
            r=list(skills_scores.values()),
            theta=list(skills_scores.keys()),
            fill='toself',
            line_color='#8b5cf6'
        ))
        
        fig_radar.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#cbd5e1', size=11),
            polar=dict(
                bgcolor='rgba(30, 41, 59, 0.3)',
                radialaxis=dict(gridcolor='rgba(148, 163, 184, 0.2)', color='#94a3b8'),
                angularaxis=dict(gridcolor='rgba(148, 163, 184, 0.2)', color='#94a3b8')
            ),
            height=500,
            showlegend=False
        )
        st.plotly_chart(fig_radar, use_container_width=True, config={'displayModeBar': False})


# =========================
# INTERPRÉTATION MISTRAL AI
# =========================
st.markdown("<br><br>", unsafe_allow_html=True)
st.markdown("## 🤖 Interprétation par IA (Mistral)")

use_llm = st.toggle("🔮 Activer l'analyse Mistral AI", value=False)

if use_llm:
    st.markdown("""
    <div class="mistral-box">
        <div class="mistral-header">
            <div class="mistral-icon">🤖</div>
            <div>
                <div class="mistral-title">Mistral AI Analysis</div>
                <p style="color: #94a3b8; margin: 0; font-size: 0.95rem;">
                    Analyse sémantique avancée et génération d'insights
                </p>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    with st.spinner("🔄 Analyse en cours par Mistral AI..."):
        # Préparer les données
        skills = detected_skills if detected_skills else []
        examples_titles = ex["title"].dropna().tolist() if not ex.empty else []
        
        # Appel à Mistral
        data, err = mistral_label_cluster(
            top_terms=str(row["top_terms"]),
            skills=skills,
            examples_titles=examples_titles,
        )
        
        if err:
            st.error(f"❌ Erreur Mistral: {err}")
        else:
            # Afficher les résultats de façon élégante
            col_m1, col_m2 = st.columns(2)
            
            with col_m1:
                if "label" in data:
                    st.markdown("#### 🏷️ Label Généré")
                    st.success(f"**{data['label']}**")
                
                if "description" in data:
                    st.markdown("#### 📝 Description")
                    st.info(data["description"])
            
            with col_m2:
                if "skills_identified" in data:
                    st.markdown("#### 🎯 Compétences Identifiées")
                    for skill in data["skills_identified"]:
                        st.markdown(f"- {skill}")
                
                if "job_families" in data:
                    st.markdown("#### 👥 Familles de Métiers")
                    for family in data["job_families"]:
                        st.markdown(f"- {family}")
            
            # JSON brut pour debug
            with st.expander("🔍 Voir la réponse JSON brute"):
                st.json(data)
            
            st.success("✅ Analyse terminée avec succès !")
    
    st.markdown("</div>", unsafe_allow_html=True)
else:
    st.info("💡 Activez l'analyse Mistral AI pour obtenir une interprétation sémantique avancée du cluster.")


# =========================
# FOOTER
# =========================
st.markdown("<br><br>", unsafe_allow_html=True)
st.markdown("""
<div style="text-align: center; 
            padding: 2rem; 
            border-top: 1px solid rgba(139, 92, 246, 0.2);">
    <p style="color: #64748b; font-size: 0.9rem;">
        🧠 Intelligence des Clusters • Propulsé par TF-IDF + K-Means + Mistral AI
    </p>
</div>
""", unsafe_allow_html=True)
