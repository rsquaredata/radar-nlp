from __future__ import annotations
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np

from components import inject_premium_css, top_navbar
from config import DB_PATH, DEFAULT_TABLE
from db import query_df
from charts import kpis, fig_offers_by_region, fig_offers_by_cluster, fig_timeline


# =========================
# CONFIGURATION
# =========================
st.set_page_config(
    layout="wide", 
    page_title="🚀 Data & IA Jobs Analytics", 
    page_icon="🚀",
    initial_sidebar_state="collapsed"
)

inject_premium_css()
top_navbar(active="Dashboard")


# =========================
# CSS ULTRA-CRÉATIF ET FUTURISTE
# =========================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800;900&display=swap');
    
    * {
        font-family: 'Inter', sans-serif;
    }
    
    /* Configuration globale */
    .main .block-container {
        max-width: 100% !important;
        padding: 1rem 2rem !important;
    }
    
    /* Background animé futuriste avec particules */
    .main {
        background: #0a0e27;
        position: relative;
        overflow: hidden;
    }
    
    .main::before {
        content: '';
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: 
            radial-gradient(circle at 20% 80%, rgba(124, 58, 237, 0.2) 0%, transparent 50%),
            radial-gradient(circle at 80% 20%, rgba(59, 130, 246, 0.2) 0%, transparent 50%),
            radial-gradient(circle at 40% 40%, rgba(236, 72, 153, 0.15) 0%, transparent 50%),
            radial-gradient(circle at 60% 80%, rgba(16, 185, 129, 0.1) 0%, transparent 50%);
        animation: backgroundShift 20s ease infinite;
        pointer-events: none;
    }
    
    @keyframes backgroundShift {
        0%, 100% { opacity: 1; transform: scale(1) rotate(0deg); }
        50% { opacity: 0.8; transform: scale(1.1) rotate(5deg); }
    }
    
    /* Particules flottantes */
    .main::after {
        content: '';
        position: fixed;
        width: 100%;
        height: 100%;
        background-image: 
            radial-gradient(2px 2px at 20% 30%, rgba(255, 255, 255, 0.3), transparent),
            radial-gradient(2px 2px at 60% 70%, rgba(255, 255, 255, 0.2), transparent),
            radial-gradient(1px 1px at 50% 50%, rgba(255, 255, 255, 0.3), transparent),
            radial-gradient(1px 1px at 80% 10%, rgba(255, 255, 255, 0.2), transparent);
        background-size: 200% 200%;
        animation: particlesFloat 30s ease infinite;
        pointer-events: none;
    }
    
    @keyframes particlesFloat {
        0%, 100% { background-position: 0% 0%; }
        50% { background-position: 100% 100%; }
    }
    
    /* Hero ultra-moderne */
    .hero-futuristic {
        position: relative;
        background: linear-gradient(135deg, 
            rgba(124, 58, 237, 0.25) 0%, 
            rgba(59, 130, 246, 0.2) 50%,
            rgba(236, 72, 153, 0.25) 100%);
        border: 2px solid rgba(139, 92, 246, 0.4);
        border-radius: 30px;
        padding: 3rem;
        margin-bottom: 2rem;
        overflow: hidden;
        box-shadow: 
            0 20px 60px rgba(124, 58, 237, 0.5),
            inset 0 1px 0 rgba(255, 255, 255, 0.1),
            0 0 100px rgba(59, 130, 246, 0.2);
    }
    
    .hero-futuristic::before {
        content: '';
        position: absolute;
        top: -50%;
        left: -50%;
        width: 200%;
        height: 200%;
        background: linear-gradient(
            45deg,
            transparent 30%,
            rgba(255, 255, 255, 0.08) 50%,
            transparent 70%
        );
        animation: shine 4s ease-in-out infinite;
    }
    
    @keyframes shine {
        0% { transform: translateX(-100%) translateY(-100%) rotate(45deg); }
        100% { transform: translateX(100%) translateY(100%) rotate(45deg); }
    }
    
    .hero-badge {
        display: inline-block;
        background: linear-gradient(135deg, #7c3aed 0%, #ec4899 100%);
        padding: 0.5rem 1.5rem;
        border-radius: 50px;
        font-size: 0.85rem;
        font-weight: 800;
        letter-spacing: 2px;
        text-transform: uppercase;
        box-shadow: 0 4px 20px rgba(124, 58, 237, 0.6),
                    0 0 40px rgba(236, 72, 153, 0.4);
        animation: pulse 2s ease-in-out infinite;
    }
    
    @keyframes pulse {
        0%, 100% { transform: scale(1); box-shadow: 0 4px 20px rgba(124, 58, 237, 0.6); }
        50% { transform: scale(1.05); box-shadow: 0 8px 40px rgba(124, 58, 237, 0.8); }
    }
    
    .hero-title {
        font-size: 3.5rem;
        font-weight: 900;
        margin: 1rem 0;
        background: linear-gradient(135deg, #60a5fa 0%, #a78bfa 50%, #ec4899 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        line-height: 1.2;
        letter-spacing: -2px;
        text-shadow: 0 0 80px rgba(96, 165, 250, 0.5);
    }
    
    /* Filtres avec néomorphisme */
    .filter-section {
        background: rgba(15, 23, 42, 0.7);
        border: 1px solid rgba(148, 163, 184, 0.3);
        border-radius: 24px;
        padding: 2rem;
        margin-bottom: 2rem;
        backdrop-filter: blur(20px);
        box-shadow: 
            0 8px 32px rgba(0, 0, 0, 0.5),
            inset 0 1px 0 rgba(255, 255, 255, 0.05);
    }
    
    .stMultiSelect > div > div,
    .stTextInput > div > div > input,
    .stSelectbox > div > div > select {
        background: rgba(30, 41, 59, 0.9) !important;
        border: 2px solid rgba(100, 116, 139, 0.4) !important;
        border-radius: 16px !important;
        color: #f8fafc !important;
        padding: 0.75rem 1rem !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
    }
    
    .stMultiSelect > div > div:focus-within,
    .stTextInput > div > div > input:focus,
    .stSelectbox > div > div > select:focus {
        border-color: #8b5cf6 !important;
        box-shadow: 0 0 0 4px rgba(139, 92, 246, 0.3) !important;
        transform: translateY(-2px);
        background: rgba(30, 41, 59, 1) !important;
    }
    
    .stMultiSelect > label, .stTextInput > label, .stSelectbox > label {
        color: #cbd5e1 !important;
        font-weight: 700 !important;
        font-size: 0.9rem !important;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    /* KPI Cards avec effet 3D spectaculaire */
    [data-testid="metric-container"] {
        background: linear-gradient(135deg, 
            rgba(30, 41, 59, 0.95) 0%, 
            rgba(51, 65, 85, 0.8) 100%);
        border: 2px solid rgba(139, 92, 246, 0.4);
        border-radius: 24px;
        padding: 2rem 1.5rem;
        position: relative;
        overflow: hidden;
        transition: all 0.5s cubic-bezier(0.4, 0, 0.2, 1);
    }
    
    [data-testid="metric-container"]::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: linear-gradient(135deg, 
            rgba(124, 58, 237, 0.2) 0%, 
            rgba(236, 72, 153, 0.1) 100%);
        opacity: 0;
        transition: opacity 0.5s;
    }
    
    [data-testid="metric-container"]::after {
        content: '';
        position: absolute;
        top: -50%;
        left: -50%;
        width: 200%;
        height: 200%;
        background: linear-gradient(
            45deg,
            transparent 40%,
            rgba(255, 255, 255, 0.05) 50%,
            transparent 60%
        );
        transform: translateX(-100%) translateY(-100%);
        transition: transform 0.6s;
    }
    
    [data-testid="metric-container"]:hover {
        transform: translateY(-10px) scale(1.03);
        border-color: #a78bfa;
        box-shadow: 
            0 25px 80px rgba(124, 58, 237, 0.5),
            0 0 100px rgba(124, 58, 237, 0.3),
            inset 0 1px 0 rgba(255, 255, 255, 0.1);
    }
    
    [data-testid="metric-container"]:hover::before {
        opacity: 1;
    }
    
    [data-testid="metric-container"]:hover::after {
        transform: translateX(100%) translateY(100%);
    }
    
    [data-testid="metric-container"] [data-testid="stMetricLabel"] {
        color: #94a3b8 !important;
        font-size: 0.85rem !important;
        font-weight: 700 !important;
        text-transform: uppercase;
        letter-spacing: 1.5px;
    }
    
    [data-testid="metric-container"] [data-testid="stMetricValue"] {
        font-size: 3rem !important;
        font-weight: 900 !important;
        background: linear-gradient(135deg, #60a5fa 0%, #a78bfa 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        letter-spacing: -1px;
    }
    
    /* Chart containers avec effet 3D et glow */
    .chart-card {
        background: linear-gradient(135deg, 
            rgba(15, 23, 42, 0.98) 0%, 
            rgba(30, 41, 59, 0.95) 100%);
        border: 2px solid rgba(139, 92, 246, 0.3);
        border-radius: 24px;
        padding: 2rem;
        margin-bottom: 2rem;
        position: relative;
        overflow: hidden;
        box-shadow: 
            0 10px 40px rgba(0, 0, 0, 0.6),
            inset 0 1px 0 rgba(255, 255, 255, 0.05);
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
    }
    
    .chart-card::after {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 4px;
        background: linear-gradient(90deg, 
            #7c3aed 0%, 
            #3b82f6 25%, 
            #10b981 50%, 
            #f59e0b 75%, 
            #ec4899 100%);
        animation: rainbowSlide 3s linear infinite;
    }
    
    @keyframes rainbowSlide {
        0% { transform: translateX(-100%); }
        100% { transform: translateX(100%); }
    }
    
    .chart-card:hover {
        transform: translateY(-6px);
        box-shadow: 
            0 20px 70px rgba(124, 58, 237, 0.4),
            0 0 100px rgba(59, 130, 246, 0.3),
            inset 0 1px 0 rgba(255, 255, 255, 0.1);
        border-color: rgba(139, 92, 246, 0.6);
    }
    
    .chart-title {
        font-size: 1.3rem;
        font-weight: 800;
        color: #f8fafc;
        margin-bottom: 1.5rem;
        display: flex;
        align-items: center;
        gap: 0.75rem;
    }
    
    .chart-title::before {
        content: '';
        width: 4px;
        height: 28px;
        background: linear-gradient(180deg, #7c3aed 0%, #ec4899 100%);
        border-radius: 4px;
        box-shadow: 0 0 20px rgba(124, 58, 237, 0.6);
    }
    
    /* Stats badge avec glow */
    .stats-badge {
        display: inline-block;
        background: linear-gradient(135deg, 
            rgba(59, 130, 246, 0.25) 0%, 
            rgba(139, 92, 246, 0.25) 100%);
        border: 2px solid rgba(139, 92, 246, 0.5);
        padding: 1.2rem 2.5rem;
        border-radius: 20px;
        margin: 1rem 0;
        backdrop-filter: blur(10px);
        box-shadow: 
            0 8px 32px rgba(124, 58, 237, 0.3),
            inset 0 1px 0 rgba(255, 255, 255, 0.1);
        transition: all 0.3s ease;
    }
    
    .stats-badge:hover {
        transform: scale(1.05);
        box-shadow: 
            0 12px 48px rgba(124, 58, 237, 0.5),
            inset 0 1px 0 rgba(255, 255, 255, 0.2);
    }
    
    .stats-badge-number {
        font-size: 2.2rem;
        font-weight: 900;
        background: linear-gradient(135deg, #60a5fa 0%, #a78bfa 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    /* Section headers avec ligne décorative */
    .section-header {
        display: flex;
        align-items: center;
        gap: 1rem;
        margin: 3rem 0 1.5rem 0;
    }
    
    .section-header h2 {
        font-size: 2rem;
        font-weight: 800;
        background: linear-gradient(135deg, #60a5fa 0%, #a78bfa 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin: 0;
    }
    
    .section-header::after {
        content: '';
        flex: 1;
        height: 2px;
        background: linear-gradient(90deg, 
            rgba(139, 92, 246, 0.5) 0%, 
            transparent 100%);
    }
    
    /* Scrollbar futuriste */
    ::-webkit-scrollbar {
        width: 12px;
        height: 12px;
    }
    
    ::-webkit-scrollbar-track {
        background: rgba(15, 23, 42, 0.8);
        border-radius: 10px;
    }
    
    ::-webkit-scrollbar-thumb {
        background: linear-gradient(135deg, #7c3aed 0%, #3b82f6 100%);
        border-radius: 10px;
        border: 2px solid rgba(15, 23, 42, 0.8);
        box-shadow: 0 0 10px rgba(124, 58, 237, 0.5);
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: linear-gradient(135deg, #8b5cf6 0%, #60a5fa 100%);
        box-shadow: 0 0 20px rgba(139, 92, 246, 0.8);
    }
    
    /* Animations d'entrée échelonnées */
    @keyframes slideInUp {
        from {
            opacity: 0;
            transform: translateY(40px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    @keyframes fadeIn {
        from {
            opacity: 0;
        }
        to {
            opacity: 1;
        }
    }
    
    .animate-slide {
        animation: slideInUp 0.8s ease-out backwards;
    }
    
    .animate-fade {
        animation: fadeIn 1s ease-out backwards;
    }
    
    .animate-delay-1 { animation-delay: 0.1s; }
    .animate-delay-2 { animation-delay: 0.2s; }
    .animate-delay-3 { animation-delay: 0.3s; }
    .animate-delay-4 { animation-delay: 0.4s; }
    .animate-delay-5 { animation-delay: 0.5s; }
    
    /* Textes */
    h1, h2, h3, h4, h5, h6 {
        color: #f8fafc !important;
    }
    
    p, span, div, label {
        color: #cbd5e1 !important;
    }
    
    /* Mini cards pour insights */
    .insight-card {
        background: rgba(30, 41, 59, 0.6);
        border: 1px solid rgba(139, 92, 246, 0.3);
        border-radius: 16px;
        padding: 1rem;
        margin: 0.5rem 0;
        backdrop-filter: blur(10px);
    }
    
    .insight-card:hover {
        border-color: rgba(139, 92, 246, 0.6);
        background: rgba(30, 41, 59, 0.8);
    }
</style>
""", unsafe_allow_html=True)


# =========================
# CHARGEMENT DES DONNÉES
# =========================
df = query_df(str(DB_PATH), f"SELECT * FROM {DEFAULT_TABLE}")

if df.empty:
    st.error("⚠️ Aucune donnée disponible.")
    st.stop()


# =========================
# HERO SECTION FUTURISTE
# =========================
st.markdown("""
<div class="hero-futuristic animate-slide">
    <div class="hero-badge">🚀 LIVE ANALYTICS</div>
    <div class="hero-title">
        Dashboard Intelligence<br>Marché Data & IA
    </div>
    <p style="font-size: 1.2rem; color: #cbd5e1; max-width: 900px; line-height: 1.8; margin-top: 1rem;">
        Explorez <strong style="color: #60a5fa;">en temps réel</strong> les tendances du marché de l'emploi. 
        Visualisations avancées, clustering IA, analyse géospatiale et insights prédictifs.
    </p>
</div>
""", unsafe_allow_html=True)


# =========================
# SECTION FILTRES
# =========================
st.markdown('<div class="filter-section animate-slide animate-delay-1">', unsafe_allow_html=True)
st.markdown("### 🎯 Filtres Intelligents")

col1, col2, col3, col4 = st.columns(4)

with col1:
    regions = sorted([r for r in df["region"].dropna().unique()])
    region_sel = st.multiselect(
        "🌍 Région",
        options=regions,
        default=regions,
    )

with col2:
    sources = sorted([s for s in df["source"].dropna().unique()])
    source_sel = st.multiselect(
        "📡 Source",
        options=sources,
        default=sources,
    )

with col3:
    clusters_labels = sorted([c for c in df["cluster_label"].dropna().unique()])
    cluster_sel = st.multiselect(
        "🏷️ Cluster",
        options=clusters_labels,
        default=clusters_labels[:10] if len(clusters_labels) > 10 else clusters_labels,
    )

with col4:
    if "remote" in df.columns:
        remote_options = ["Tous"] + sorted([r for r in df["remote"].dropna().unique()])
        remote_sel = st.selectbox("🏠 Télétravail", remote_options)

search = st.text_input(
    "🔎 Recherche avancée",
    placeholder="Machine learning, senior, alternance...",
)

st.markdown('</div>', unsafe_allow_html=True)


# =========================
# APPLICATION DES FILTRES
# =========================
df_filtered = df.copy()

if region_sel:
    df_filtered = df_filtered[df_filtered["region"].isin(region_sel)]

if source_sel:
    df_filtered = df_filtered[df_filtered["source"].isin(source_sel)]

if cluster_sel:
    df_filtered = df_filtered[df_filtered["cluster_label"].isin(cluster_sel)]

if "remote" in df.columns and 'remote_sel' in locals() and remote_sel != "Tous":
    df_filtered = df_filtered[df_filtered["remote"] == remote_sel]

if search:
    mask_title = df_filtered["title"].fillna("").str.contains(search, case=False, na=False)
    mask_emp = df_filtered["employer"].fillna("").str.contains(search, case=False, na=False)
    df_filtered = df_filtered[mask_title | mask_emp]

# Stats
total_offers = df['uid'].nunique() if 'uid' in df else len(df)
filtered_offers = df_filtered['uid'].nunique() if 'uid' in df_filtered else len(df_filtered)
percentage = (filtered_offers / total_offers * 100) if total_offers > 0 else 0

st.markdown(f"""
<div class="stats-badge animate-slide animate-delay-2">
    <span class="stats-badge-number">{filtered_offers:,}</span>
    <span style="color: #64748b; font-size: 1.1rem; font-weight: 600;"> / {total_offers:,} offres</span>
    <span style="color: #94a3b8; margin-left: 1rem; font-size: 1rem;">({percentage:.1f}%)</span>
</div>
""", unsafe_allow_html=True)

if df_filtered.empty:
    st.warning("⚠️ Aucune offre ne correspond aux filtres.")
    st.stop()


# =========================
# KPIs FUTURISTES
# =========================
st.markdown("<br>", unsafe_allow_html=True)

stats = kpis(df_filtered)

col_k1, col_k2, col_k3, col_k4 = st.columns(4)

with col_k1:
    st.markdown('<div class="animate-slide animate-delay-1">', unsafe_allow_html=True)
    st.metric("🎯 Offres", f"{stats['Offres']:,}")
    st.markdown('</div>', unsafe_allow_html=True)

with col_k2:
    st.markdown('<div class="animate-slide animate-delay-2">', unsafe_allow_html=True)
    st.metric("🌍 Régions", stats["Régions"])
    st.markdown('</div>', unsafe_allow_html=True)

with col_k3:
    st.markdown('<div class="animate-slide animate-delay-3">', unsafe_allow_html=True)
    st.metric("🧠 Clusters", stats["Clusters"])
    st.markdown('</div>', unsafe_allow_html=True)

with col_k4:
    st.markdown('<div class="animate-slide animate-delay-4">', unsafe_allow_html=True)
    st.metric("📊 Sources", stats["Sources"])
    st.markdown('</div>', unsafe_allow_html=True)


# =========================
# SECTION 1: VISUALISATIONS AVANCÉES
# =========================
st.markdown('<div class="section-header"><h2>📊 Analyses Hiérarchiques</h2></div>', unsafe_allow_html=True)

col1, col2 = st.columns([1.2, 1])

with col1:
    st.markdown('<div class="chart-card animate-slide">', unsafe_allow_html=True)
    st.markdown('<div class="chart-title">🌟 Sunburst - Région → Cluster → Source</div>', unsafe_allow_html=True)
    
    df_sunburst = df_filtered.groupby(['region', 'cluster_label', 'source']).size().reset_index(name='count')
    fig_sunburst = px.sunburst(
        df_sunburst,
        path=['region', 'cluster_label', 'source'],
        values='count',
        color='count',
        color_continuous_scale='Turbo',
        height=550
    )
    fig_sunburst.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#cbd5e1', size=11),
        margin=dict(t=10, b=10, l=10, r=10)
    )
    st.plotly_chart(fig_sunburst, use_container_width=True, config={'displayModeBar': False})
    st.markdown('</div>', unsafe_allow_html=True)

with col2:
    st.markdown('<div class="chart-card animate-slide animate-delay-1">', unsafe_allow_html=True)
    st.markdown('<div class="chart-title">🔮 Polar Chart - Clusters par Région</div>', unsafe_allow_html=True)
    
    # Top 8 clusters
    top_clusters = df_filtered['cluster_label'].value_counts().head(8).index
    df_polar = df_filtered[df_filtered['cluster_label'].isin(top_clusters)]
    df_polar_grouped = df_polar.groupby(['cluster_label', 'region']).size().reset_index(name='count')
    
    fig_polar = px.line_polar(
        df_polar_grouped,
        r='count',
        theta='cluster_label',
        color='region',
        line_close=True,
        height=550,
        color_discrete_sequence=px.colors.qualitative.Vivid
    )
    fig_polar.update_traces(fill='toself')
    fig_polar.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#cbd5e1', size=10),
        polar=dict(
            bgcolor='rgba(30, 41, 59, 0.3)',
            radialaxis=dict(gridcolor='rgba(148, 163, 184, 0.2)', color='#94a3b8'),
            angularaxis=dict(gridcolor='rgba(148, 163, 184, 0.2)', color='#94a3b8')
        ),
        margin=dict(t=40, b=40, l=40, r=40),
        legend=dict(font=dict(size=9))
    )
    st.plotly_chart(fig_polar, use_container_width=True, config={'displayModeBar': False})
    st.markdown('</div>', unsafe_allow_html=True)


# =========================
# SECTION 2: DISTRIBUTIONS ET TREEMAP
# =========================
st.markdown('<div class="section-header"><h2>📦 Distributions et Hiérarchies</h2></div>', unsafe_allow_html=True)

col3, col4 = st.columns(2)

with col3:
    st.markdown('<div class="chart-card animate-slide">', unsafe_allow_html=True)
    st.markdown('<div class="chart-title">📦 Treemap - Sources × Régions</div>', unsafe_allow_html=True)
    
    df_treemap = df_filtered.groupby(['source', 'region']).size().reset_index(name='count')
    fig_treemap = px.treemap(
        df_treemap,
        path=['source', 'region'],
        values='count',
        color='count',
        color_continuous_scale='Rainbow',
        height=500
    )
    fig_treemap.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#cbd5e1', size=12),
        margin=dict(t=20, b=20, l=20, r=20)
    )
    st.plotly_chart(fig_treemap, use_container_width=True, config={'displayModeBar': False})
    st.markdown('</div>', unsafe_allow_html=True)

with col4:
    st.markdown('<div class="chart-card animate-slide animate-delay-1">', unsafe_allow_html=True)
    st.markdown('<div class="chart-title">🎭 Sankey - Flux Source → Région → Cluster</div>', unsafe_allow_html=True)
    
    # Préparer données pour Sankey (limiter pour lisibilité)
    top_5_sources = df_filtered['source'].value_counts().head(5).index
    top_5_regions = df_filtered['region'].value_counts().head(5).index
    top_5_clusters = df_filtered['cluster_label'].value_counts().head(5).index
    
    df_sankey = df_filtered[
        (df_filtered['source'].isin(top_5_sources)) &
        (df_filtered['region'].isin(top_5_regions)) &
        (df_filtered['cluster_label'].isin(top_5_clusters))
    ]
    
    # Créer labels et indices
    all_labels = list(top_5_sources) + list(top_5_regions) + list(top_5_clusters)
    label_to_idx = {label: idx for idx, label in enumerate(all_labels)}
    
    # Source -> Region
    source_region = df_sankey.groupby(['source', 'region']).size().reset_index(name='value')
    source_idx = [label_to_idx[s] for s in source_region['source']]
    region_idx = [label_to_idx[r] for r in source_region['region']]
    values_sr = source_region['value'].tolist()
    
    # Region -> Cluster
    region_cluster = df_sankey.groupby(['region', 'cluster_label']).size().reset_index(name='value')
    region_idx2 = [label_to_idx[r] for r in region_cluster['region']]
    cluster_idx = [label_to_idx[c] for c in region_cluster['cluster_label']]
    values_rc = region_cluster['value'].tolist()
    
    fig_sankey = go.Figure(data=[go.Sankey(
        node=dict(
            pad=15,
            thickness=20,
            line=dict(color='rgba(255, 255, 255, 0.2)', width=0.5),
            label=all_labels,
            color=['#3b82f6', '#8b5cf6', '#ec4899', '#f59e0b', '#10b981'] * 3
        ),
        link=dict(
            source=source_idx + region_idx2,
            target=region_idx + cluster_idx,
            value=values_sr + values_rc,
            color='rgba(139, 92, 246, 0.3)'
        )
    )])
    
    fig_sankey.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#cbd5e1', size=11),
        height=500,
        margin=dict(t=20, b=20, l=20, r=20)
    )
    st.plotly_chart(fig_sankey, use_container_width=True, config={'displayModeBar': False})
    st.markdown('</div>', unsafe_allow_html=True)


# =========================
# SECTION 3: DISTRIBUTIONS GÉOGRAPHIQUES
# =========================
st.markdown('<div class="section-header"><h2>🌍 Analyses Géographiques</h2></div>', unsafe_allow_html=True)

col5, col6 = st.columns(2)

with col5:
    st.markdown('<div class="chart-card animate-slide">', unsafe_allow_html=True)
    st.markdown('<div class="chart-title">🗺️ Distribution Géographique</div>', unsafe_allow_html=True)
    fig_reg = fig_offers_by_region(df_filtered)
    st.plotly_chart(fig_reg, use_container_width=True, config={'displayModeBar': False})
    st.markdown('</div>', unsafe_allow_html=True)

with col6:
    st.markdown('<div class="chart-card animate-slide animate-delay-1">', unsafe_allow_html=True)
    st.markdown('<div class="chart-title">💎 Bubble Chart - Clusters × Régions</div>', unsafe_allow_html=True)
    
    # Top 10 régions et clusters pour lisibilité
    top_regions = df_filtered['region'].value_counts().head(10).index
    top_clusters_bubble = df_filtered['cluster_label'].value_counts().head(10).index
    
    df_bubble = df_filtered[
        (df_filtered['region'].isin(top_regions)) &
        (df_filtered['cluster_label'].isin(top_clusters_bubble))
    ]
    df_bubble_grouped = df_bubble.groupby(['region', 'cluster_label']).size().reset_index(name='count')
    
    fig_bubble = px.scatter(
        df_bubble_grouped,
        x='region',
        y='cluster_label',
        size='count',
        color='count',
        color_continuous_scale='Spectral',
        size_max=60,
        height=500
    )
    fig_bubble.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#cbd5e1', size=10),
        xaxis=dict(tickangle=-45, gridcolor='rgba(148, 163, 184, 0.1)'),
        yaxis=dict(gridcolor='rgba(148, 163, 184, 0.1)'),
        margin=dict(t=20, b=100, l=150, r=20)
    )
    st.plotly_chart(fig_bubble, use_container_width=True, config={'displayModeBar': False})
    st.markdown('</div>', unsafe_allow_html=True)


# =========================
# SECTION 4: CLUSTERS ET HEATMAP
# =========================
st.markdown('<div class="section-header"><h2>🧠 Analyses des Clusters</h2></div>', unsafe_allow_html=True)

col7, col8 = st.columns(2)

with col7:
    st.markdown('<div class="chart-card animate-slide">', unsafe_allow_html=True)
    st.markdown('<div class="chart-title">🎯 Top Clusters Métiers</div>', unsafe_allow_html=True)
    fig_clu = fig_offers_by_cluster(df_filtered)
    st.plotly_chart(fig_clu, use_container_width=True, config={'displayModeBar': False})
    st.markdown('</div>', unsafe_allow_html=True)

with col8:
    st.markdown('<div class="chart-card animate-slide animate-delay-1">', unsafe_allow_html=True)
    st.markdown('<div class="chart-title">📊 Radar - Top 6 Clusters par Source</div>', unsafe_allow_html=True)
    
    # Top 6 clusters
    top_6_clusters = df_filtered['cluster_label'].value_counts().head(6).index
    df_radar = df_filtered[df_filtered['cluster_label'].isin(top_6_clusters)]
    df_radar_grouped = df_radar.groupby(['cluster_label', 'source']).size().reset_index(name='count')
    
    fig_radar = go.Figure()
    
    for source in df_radar_grouped['source'].unique():
        df_source = df_radar_grouped[df_radar_grouped['source'] == source]
        fig_radar.add_trace(go.Scatterpolar(
            r=df_source['count'],
            theta=df_source['cluster_label'],
            fill='toself',
            name=source
        ))
    
    fig_radar.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#cbd5e1', size=10),
        polar=dict(
            bgcolor='rgba(30, 41, 59, 0.3)',
            radialaxis=dict(gridcolor='rgba(148, 163, 184, 0.2)', color='#94a3b8'),
            angularaxis=dict(gridcolor='rgba(148, 163, 184, 0.2)', color='#94a3b8')
        ),
        height=500,
        margin=dict(t=40, b=40, l=40, r=40),
        legend=dict(font=dict(size=10))
    )
    st.plotly_chart(fig_radar, use_container_width=True, config={'displayModeBar': False})
    st.markdown('</div>', unsafe_allow_html=True)


# =========================
# SECTION 5: HEATMAP ET FUNNEL
# =========================
st.markdown('<div class="section-header"><h2>🔥 Matrices de Corrélation</h2></div>', unsafe_allow_html=True)

col9, col10 = st.columns([1.5, 1])

with col9:
    st.markdown('<div class="chart-card animate-slide">', unsafe_allow_html=True)
    st.markdown('<div class="chart-title">🔥 Heatmap - Région × Source</div>', unsafe_allow_html=True)
    
    df_heatmap = df_filtered.groupby(['region', 'source']).size().reset_index(name='count')
    df_pivot = df_heatmap.pivot(index='region', columns='source', values='count').fillna(0)
    
    fig_heatmap = go.Figure(data=go.Heatmap(
        z=df_pivot.values,
        x=df_pivot.columns,
        y=df_pivot.index,
        colorscale='Turbo',
        text=df_pivot.values.astype(int),
        texttemplate='%{text}',
        textfont={"size": 11},
        hoverongaps=False,
        colorbar=dict(tickfont=dict(color='#cbd5e1'))
    ))
    
    fig_heatmap.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#cbd5e1', size=11),
        xaxis=dict(tickangle=-45, gridcolor='rgba(148, 163, 184, 0.1)'),
        yaxis=dict(gridcolor='rgba(148, 163, 184, 0.1)'),
        height=450,
        margin=dict(t=20, b=100, l=150, r=20)
    )
    st.plotly_chart(fig_heatmap, use_container_width=True, config={'displayModeBar': False})
    st.markdown('</div>', unsafe_allow_html=True)

with col10:
    st.markdown('<div class="chart-card animate-slide animate-delay-1">', unsafe_allow_html=True)
    st.markdown('<div class="chart-title">📈 Insights Clés</div>', unsafe_allow_html=True)
    
    # Top employeurs
    if 'employer' in df_filtered.columns:
        top_employers = df_filtered['employer'].value_counts().head(5)
        st.markdown("**🏢 Top 5 Employeurs**")
        for idx, (emp, count) in enumerate(top_employers.items(), 1):
            st.markdown(f'<div class="insight-card">{idx}. <strong>{emp}</strong> · {count} offres</div>', unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Télétravail
    if 'remote' in df_filtered.columns:
        remote_dist = df_filtered['remote'].value_counts()
        st.markdown("**🏠 Télétravail**")
        for status, count in remote_dist.items():
            pct = (count / len(df_filtered) * 100)
            st.markdown(f'<div class="insight-card"><strong>{status}</strong> · {count} ({pct:.1f}%)</div>', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)


# =========================
# SECTION 6: TIMELINE
# =========================
st.markdown('<div class="section-header"><h2>⏱️ Évolution Temporelle</h2></div>', unsafe_allow_html=True)

st.markdown('<div class="chart-card animate-slide">', unsafe_allow_html=True)
st.markdown('<div class="chart-title">📅 Timeline des Publications</div>', unsafe_allow_html=True)

fig_time = fig_timeline(df_filtered)
if fig_time:
    st.plotly_chart(fig_time, use_container_width=True, config={'displayModeBar': False})
else:
    st.info("ℹ️ Timeline non disponible - colonne 'published_date' manquante ou mal formatée")

st.markdown('</div>', unsafe_allow_html=True)


# =========================
# FOOTER FUTURISTE
# =========================
st.markdown("<br><br>", unsafe_allow_html=True)
st.markdown("""
<div style="text-align: center; 
            padding: 3rem 0; 
            border-top: 2px solid rgba(139, 92, 246, 0.3);
            position: relative;">
    <div style="font-size: 1.3rem; 
                font-weight: 900; 
                background: linear-gradient(135deg, #60a5fa 0%, #a78bfa 50%, #ec4899 100%);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                margin-bottom: 0.75rem;
                letter-spacing: 1px;">
        🚀 Dashboard Intelligence Data & IA
    </div>
    <p style="color: #64748b; font-size: 0.95rem; margin-bottom: 0.5rem;">
        Données actualisées en continu • Clustering par IA • 12+ types de visualisations
    </p>
    <p style="color: #475569; font-size: 0.85rem;">
        Propulsé par Streamlit • Plotly • Python
    </p>
</div>
""", unsafe_allow_html=True)