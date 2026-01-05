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
from sklearn.decomposition import LatentDirichletAllocation, NMF
from sklearn.cluster import KMeans, AgglomerativeClustering
from sklearn.metrics.pairwise import cosine_similarity
from scipy.cluster.hierarchy import dendrogram, linkage
from sklearn.manifold import TSNE
import seaborn as sns

# Import
sys.path.insert(0, str(Path(__file__).parent.parent))
from utils.components import inject_premium_css, premium_navbar
from utils.db import load_offers_with_skills

# ============================================================================
# CONFIG
# ============================================================================

st.set_page_config(
    page_title="Intelligence NLP | DataJobs",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
)

inject_premium_css()
premium_navbar(active_page="Intelligence")

# ============================================================================
# CSS STYLE LABORATOIRE NLP
# ============================================================================

st.markdown("""
<style>
    .main {
        background: linear-gradient(135deg, #0a0e27 0%, #1a1f3a 50%, #0f1419 100%);
    }
    
    .lab-header {
        background: linear-gradient(135deg, #1e293b 0%, #334155 100%);
        border: 3px solid #a855f7;
        border-radius: 20px;
        padding: 2.5rem;
        margin-bottom: 2rem;
        box-shadow: 0 0 60px rgba(168, 85, 247, 0.4);
        position: relative;
        overflow: hidden;
    }
    
    .lab-header::before {
        content: '';
        position: absolute;
        top: 0; left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(168, 85, 247, 0.3), transparent);
        animation: labScan 4s linear infinite;
    }
    
    @keyframes labScan {
        0% { left: -100%; }
        100% { left: 100%; }
    }
    
    .lab-title {
        font-size: 4rem;
        font-weight: 900;
        text-align: center;
        background: linear-gradient(135deg, #a855f7 0%, #ec4899 50%, #f97316 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin: 0;
        font-family: 'Courier New', monospace;
        letter-spacing: 5px;
        text-shadow: 0 0 30px rgba(168, 85, 247, 0.5);
    }
    
    .nlp-card {
        background: linear-gradient(135deg, rgba(168, 85, 247, 0.05) 0%, rgba(236, 72, 153, 0.05) 100%);
        border: 2px solid rgba(168, 85, 247, 0.3);
        border-radius: 16px;
        padding: 2rem;
        margin-bottom: 1.5rem;
        transition: all 0.3s;
    }
    
    .nlp-card:hover {
        transform: translateY(-5px);
        border-color: #a855f7;
        box-shadow: 0 15px 50px rgba(168, 85, 247, 0.4);
    }
    
    .nlp-section {
        background: linear-gradient(90deg, rgba(168, 85, 247, 0.2) 0%, transparent 100%);
        border-left: 5px solid #a855f7;
        padding: 1.5rem;
        margin: 2rem 0 1.5rem 0;
        border-radius: 0 10px 10px 0;
    }
    
    .nlp-title {
        color: #a855f7;
        font-size: 2rem;
        font-weight: 900;
        margin: 0;
        font-family: 'Courier New', monospace;
        text-transform: uppercase;
    }
    
    .metric-nlp {
        background: rgba(168, 85, 247, 0.1);
        border: 2px solid rgba(168, 85, 247, 0.4);
        border-radius: 12px;
        padding: 1.5rem;
        text-align: center;
    }
    
    .metric-value-nlp {
        font-size: 2.5rem;
        font-weight: 900;
        background: linear-gradient(135deg, #a855f7 0%, #ec4899 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    .pulse-nlp {
        animation: pulseNLP 3s ease-in-out infinite;
    }
    
    @keyframes pulseNLP {
        0%, 100% { transform: scale(1); }
        50% { transform: scale(1.05); }
    }
</style>
""", unsafe_allow_html=True)

# ============================================================================
# HEADER
# ============================================================================

st.markdown("""
<div class="lab-header pulse-nlp">
    <h1 class="lab-title">🧠 NLP INTELLIGENCE LAB</h1>
    <p style="text-align: center; color: #a855f7; font-family: monospace; font-size: 1.2rem; margin-top: 1rem;">
        > NATURAL LANGUAGE PROCESSING • TOPIC MODELING • TEXT MINING • DEEP ANALYSIS
    </p>
</div>
""", unsafe_allow_html=True)

# ============================================================================
# CHARGER DONNÉES
# ============================================================================

@st.cache_data(ttl=600)
def load_nlp_data():
    df = load_offers_with_skills()
    if not df.empty:
        # Créer corpus textuel
        df['text_corpus'] = df.apply(
            lambda row: ' '.join([
                str(row.get('title', '')),
                str(row.get('company_name', '')),
                str(row.get('all_skills', '')),
                str(row.get('region_name', ''))
            ]).lower(),
            axis=1
        )
        
        # Nettoyage basique
        df['text_clean'] = df['text_corpus'].apply(
            lambda x: re.sub(r'[^\w\s]', ' ', str(x))
        )
    
    return df

with st.spinner("🧠 CHARGEMENT DES DONNÉES NLP..."):
    df = load_nlp_data()

if df.empty:
    st.error("⚠️ Aucune donnée")
    st.stop()

# ============================================================================
# FILTRES
# ============================================================================

st.markdown('<div class="nlp-section"><h2 class="nlp-title">🎛️ Filtres d\'Analyse</h2></div>', unsafe_allow_html=True)

filter_col1, filter_col2, filter_col3 = st.columns(3)

with filter_col1:
    st.markdown("### 🗺️ Régions")
    regions = ['Toutes'] + sorted(df['region_name'].dropna().unique().tolist())
    sel_regions = st.multiselect("Régions", regions, default=['Toutes'], label_visibility="collapsed")

with filter_col2:
    st.markdown("### 📋 Contrats")
    contracts = ['Tous'] + sorted(df['contract_type'].dropna().unique().tolist())
    sel_contracts = st.multiselect("Contrats", contracts, default=['Tous'], label_visibility="collapsed")

with filter_col3:
    st.markdown("### 🔄 Actions")
    if st.button("🔄 RESET", use_container_width=True):
        st.rerun()

# Filtrage
filtered = df.copy()
if sel_regions and 'Toutes' not in sel_regions:
    filtered = filtered[filtered['region_name'].isin(sel_regions)]
if sel_contracts and 'Tous' not in sel_contracts:
    filtered = filtered[filtered['contract_type'].isin(sel_contracts)]

st.info(f"🧠 **{len(filtered):,} documents** analysés sur **{len(df):,}**")

if filtered.empty:
    st.error("⚠️ Aucune donnée avec ces filtres")
    st.stop()

st.markdown("---")

# ============================================================================
# MÉTRIQUES NLP
# ============================================================================

st.markdown('<div class="nlp-section"><h2 class="nlp-title">📊 Métriques Linguistiques</h2></div>', unsafe_allow_html=True)

metric_col1, metric_col2, metric_col3, metric_col4, metric_col5 = st.columns(5)

# Calculs
total_words = filtered['text_clean'].str.split().str.len().sum()
unique_words = len(set(' '.join(filtered['text_clean'].tolist()).split()))
avg_words = filtered['text_clean'].str.split().str.len().mean()
vocab_richness = (unique_words / total_words * 100) if total_words > 0 else 0

with metric_col1:
    st.markdown(f"""
    <div class="metric-nlp">
        <div class="metric-value-nlp">{total_words:,}</div>
        <div style="color: #a855f7; font-size: 0.9rem; margin-top: 0.5rem;">MOTS TOTAUX</div>
    </div>
    """, unsafe_allow_html=True)

with metric_col2:
    st.markdown(f"""
    <div class="metric-nlp">
        <div class="metric-value-nlp">{unique_words:,}</div>
        <div style="color: #a855f7; font-size: 0.9rem; margin-top: 0.5rem;">VOCABULAIRE</div>
    </div>
    """, unsafe_allow_html=True)

with metric_col3:
    st.markdown(f"""
    <div class="metric-nlp">
        <div class="metric-value-nlp">{avg_words:.1f}</div>
        <div style="color: #a855f7; font-size: 0.9rem; margin-top: 0.5rem;">MOY. MOTS/DOC</div>
    </div>
    """, unsafe_allow_html=True)

with metric_col4:
    st.markdown(f"""
    <div class="metric-nlp">
        <div class="metric-value-nlp">{vocab_richness:.2f}%</div>
        <div style="color: #a855f7; font-size: 0.9rem; margin-top: 0.5rem;">RICHESSE</div>
    </div>
    """, unsafe_allow_html=True)

with metric_col5:
    st.markdown(f"""
    <div class="metric-nlp">
        <div class="metric-value-nlp">{len(filtered):,}</div>
        <div style="color: #a855f7; font-size: 0.9rem; margin-top: 0.5rem;">DOCUMENTS</div>
    </div>
    """, unsafe_allow_html=True)

# ============================================================================
# WORD CLOUDS
# ============================================================================

st.markdown('<div class="nlp-section"><h2 class="nlp-title">☁️ Word Clouds Interactifs</h2></div>', unsafe_allow_html=True)

wc_tab1, wc_tab2, wc_tab3 = st.tabs(["🌍 Global", "🗺️ Par Région", "📋 Par Contrat"])

with wc_tab1:
    st.markdown('<div class="nlp-card">', unsafe_allow_html=True)
    st.markdown("### ☁️ Word Cloud Global")
    
    text_global = ' '.join(filtered['text_clean'].tolist())
    
    if text_global.strip():
        wordcloud = WordCloud(
            width=1600,
            height=800,
            background_color='#0a0e27',
            colormap='plasma',
            max_words=200,
            relative_scaling=0.5,
            min_font_size=10
        ).generate(text_global)
        
        fig_wc1, ax = plt.subplots(figsize=(20, 10))
        ax.imshow(wordcloud, interpolation='bilinear')
        ax.axis('off')
        plt.tight_layout(pad=0)
        st.pyplot(fig_wc1)
        plt.close()
    else:
        st.warning("Pas assez de texte")
    
    st.markdown('</div>', unsafe_allow_html=True)

with wc_tab2:
    st.markdown('<div class="nlp-card">', unsafe_allow_html=True)
    st.markdown("### 🗺️ Comparaison par Région")
    
    top_regions = filtered['region_name'].value_counts().head(6).index.tolist()
    
    cols = st.columns(3)
    for idx, region in enumerate(top_regions):
        with cols[idx % 3]:
            st.markdown(f"**{region}**")
            region_text = ' '.join(
                filtered[filtered['region_name'] == region]['text_clean'].tolist()
            )
            
            if region_text.strip():
                wc = WordCloud(
                    width=400,
                    height=300,
                    background_color='#0a0e27',
                    colormap='viridis',
                    max_words=50
                ).generate(region_text)
                
                fig, ax = plt.subplots(figsize=(5, 3.75))
                ax.imshow(wc, interpolation='bilinear')
                ax.axis('off')
                plt.tight_layout(pad=0)
                st.pyplot(fig)
                plt.close()
    
    st.markdown('</div>', unsafe_allow_html=True)

with wc_tab3:
    st.markdown('<div class="nlp-card">', unsafe_allow_html=True)
    st.markdown("### 📋 Comparaison par Type de Contrat")
    
    contracts_list = filtered['contract_type'].unique().tolist()
    
    cols = st.columns(len(contracts_list) if len(contracts_list) <= 5 else 5)
    for idx, contract in enumerate(contracts_list[:5]):
        with cols[idx]:
            st.markdown(f"**{contract}**")
            contract_text = ' '.join(
                filtered[filtered['contract_type'] == contract]['text_clean'].tolist()
            )
            
            if contract_text.strip():
                wc = WordCloud(
                    width=300,
                    height=300,
                    background_color='#0a0e27',
                    colormap='cool',
                    max_words=40
                ).generate(contract_text)
                
                fig, ax = plt.subplots(figsize=(4, 4))
                ax.imshow(wc, interpolation='bilinear')
                ax.axis('off')
                plt.tight_layout(pad=0)
                st.pyplot(fig)
                plt.close()
    
    st.markdown('</div>', unsafe_allow_html=True)

# ============================================================================
# TF-IDF ANALYSIS
# ============================================================================

st.markdown('<div class="nlp-section"><h2 class="nlp-title">📊 TF-IDF Analysis</h2></div>', unsafe_allow_html=True)

tfidf_col1, tfidf_col2 = st.columns(2)

with tfidf_col1:
    st.markdown('<div class="nlp-card">', unsafe_allow_html=True)
    st.markdown("### 🔥 Top 30 Termes TF-IDF Globaux")
    
    # TF-IDF vectorization
    tfidf = TfidfVectorizer(
        max_features=100,
        stop_words='english',
        ngram_range=(1, 2),
        min_df=2
    )
    
    tfidf_matrix = tfidf.fit_transform(filtered['text_clean'])
    feature_names = tfidf.get_feature_names_out()
    
    # Moyennes TF-IDF
    tfidf_means = np.asarray(tfidf_matrix.mean(axis=0)).flatten()
    top_indices = tfidf_means.argsort()[-30:][::-1]
    
    top_terms = [feature_names[i] for i in top_indices]
    top_scores = [tfidf_means[i] for i in top_indices]
    
    fig_tfidf = go.Figure()
    fig_tfidf.add_trace(go.Bar(
        y=top_terms,
        x=top_scores,
        orientation='h',
        marker=dict(
            color=top_scores,
            colorscale='Plasma',
            line=dict(color='#a855f7', width=1)
        ),
        text=[f'{s:.4f}' for s in top_scores],
        textposition='auto'
    ))
    
    fig_tfidf.update_layout(
        template='plotly_dark',
        height=700,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#a855f7'),
        xaxis_title="Score TF-IDF",
        yaxis_title="",
        showlegend=False
    )
    
    st.plotly_chart(fig_tfidf, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

with tfidf_col2:
    st.markdown('<div class="nlp-card">', unsafe_allow_html=True)
    st.markdown("### 🗺️ TF-IDF par Région (Top 5)")
    
    top5_regions = filtered['region_name'].value_counts().head(5).index
    
    region_tfidf_data = []
    for region in top5_regions:
        region_docs = filtered[filtered['region_name'] == region]['text_clean'].tolist()
        if region_docs:
            region_tfidf = TfidfVectorizer(max_features=20, stop_words='english')
            try:
                region_matrix = region_tfidf.fit_transform(region_docs)
                terms = region_tfidf.get_feature_names_out()
                scores = np.asarray(region_matrix.mean(axis=0)).flatten()
                top_3 = scores.argsort()[-3:][::-1]
                
                for idx in top_3:
                    region_tfidf_data.append({
                        'region': region,
                        'term': terms[idx],
                        'score': scores[idx]
                    })
            except:
                pass
    
    if region_tfidf_data:
        df_region_tfidf = pd.DataFrame(region_tfidf_data)
        
        fig_region_tfidf = px.bar(
            df_region_tfidf,
            x='score',
            y='term',
            color='region',
            orientation='h',
            barmode='group',
            color_discrete_sequence=px.colors.qualitative.Vivid
        )
        
        fig_region_tfidf.update_layout(
            template='plotly_dark',
            height=700,
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#a855f7'),
            xaxis_title="Score TF-IDF",
            yaxis_title=""
        )
        
        st.plotly_chart(fig_region_tfidf, use_container_width=True)
    else:
        st.warning("Pas assez de données")
    
    st.markdown('</div>', unsafe_allow_html=True)

# ============================================================================
# N-GRAMS ANALYSIS
# ============================================================================

st.markdown('<div class="nlp-section"><h2 class="nlp-title">📈 N-Grams Analysis</h2></div>', unsafe_allow_html=True)

ngram_col1, ngram_col2 = st.columns(2)

with ngram_col1:
    st.markdown('<div class="nlp-card">', unsafe_allow_html=True)
    st.markdown("### 📊 Top 20 Bi-grams")
    
    # Vectorizer pour bi-grams
    bigram_vec = CountVectorizer(ngram_range=(2, 2), max_features=100, min_df=2)
    bigram_matrix = bigram_vec.fit_transform(filtered['text_clean'])
    bigram_freq = bigram_matrix.sum(axis=0).A1
    bigram_names = bigram_vec.get_feature_names_out()
    
    bigram_df = pd.DataFrame({
        'bigram': bigram_names,
        'frequency': bigram_freq
    }).sort_values('frequency', ascending=False).head(20)
    
    fig_bigram = go.Figure()
    fig_bigram.add_trace(go.Bar(
        y=bigram_df['bigram'],
        x=bigram_df['frequency'],
        orientation='h',
        marker=dict(
            color=bigram_df['frequency'],
            colorscale='Viridis',
            line=dict(color='#a855f7', width=1)
        ),
        text=bigram_df['frequency'],
        textposition='auto'
    ))
    
    fig_bigram.update_layout(
        template='plotly_dark',
        height=600,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#a855f7'),
        xaxis_title="Fréquence",
        showlegend=False
    )
    
    st.plotly_chart(fig_bigram, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

with ngram_col2:
    st.markdown('<div class="nlp-card">', unsafe_allow_html=True)
    st.markdown("### 📊 Top 20 Tri-grams")
    
    # Vectorizer pour tri-grams
    trigram_vec = CountVectorizer(ngram_range=(3, 3), max_features=100, min_df=2)
    trigram_matrix = trigram_vec.fit_transform(filtered['text_clean'])
    trigram_freq = trigram_matrix.sum(axis=0).A1
    trigram_names = trigram_vec.get_feature_names_out()
    
    trigram_df = pd.DataFrame({
        'trigram': trigram_names,
        'frequency': trigram_freq
    }).sort_values('frequency', ascending=False).head(20)
    
    fig_trigram = go.Figure()
    fig_trigram.add_trace(go.Bar(
        y=trigram_df['trigram'],
        x=trigram_df['frequency'],
        orientation='h',
        marker=dict(
            color=trigram_df['frequency'],
            colorscale='Cividis',
            line=dict(color='#a855f7', width=1)
        ),
        text=trigram_df['frequency'],
        textposition='auto'
    ))
    
    fig_trigram.update_layout(
        template='plotly_dark',
        height=600,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#a855f7'),
        xaxis_title="Fréquence",
        showlegend=False
    )
    
    st.plotly_chart(fig_trigram, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

# ============================================================================
# TOPIC MODELING (LDA)
# ============================================================================

st.markdown('<div class="nlp-section"><h2 class="nlp-title">🎯 Topic Modeling (LDA)</h2></div>', unsafe_allow_html=True)

st.markdown('<div class="nlp-card">', unsafe_allow_html=True)

lda_col1, lda_col2 = st.columns([1, 2])

with lda_col1:
    st.markdown("### ⚙️ Paramètres")
    n_topics = st.slider("Nombre de topics", 3, 10, 5)
    n_words = st.slider("Mots par topic", 5, 15, 10)

with lda_col2:
    st.markdown("### 🧠 Topics Découverts")
    
    # Vectorization
    cv = CountVectorizer(max_features=500, stop_words='english', min_df=2)
    doc_term_matrix = cv.fit_transform(filtered['text_clean'])
    
    # LDA
    lda_model = LatentDirichletAllocation(
        n_components=n_topics,
        random_state=42,
        max_iter=20
    )
    lda_model.fit(doc_term_matrix)
    
    # Extraire topics
    feature_names = cv.get_feature_names_out()
    
    topics_data = []
    for topic_idx, topic in enumerate(lda_model.components_):
        top_indices = topic.argsort()[-n_words:][::-1]
        top_words = [feature_names[i] for i in top_indices]
        topics_data.append({
            'topic': f'Topic {topic_idx + 1}',
            'words': ', '.join(top_words)
        })
    
    topics_df = pd.DataFrame(topics_data)
    st.dataframe(topics_df, use_container_width=True, hide_index=True)

# Distribution des topics
st.markdown("### 📊 Distribution des Topics dans les Documents")

doc_topics = lda_model.transform(doc_term_matrix)
topic_dist = doc_topics.mean(axis=0)

fig_topic_dist = go.Figure()
fig_topic_dist.add_trace(go.Bar(
    x=[f'Topic {i+1}' for i in range(n_topics)],
    y=topic_dist,
    marker=dict(
        color=topic_dist,
        colorscale='Plasma',
        line=dict(color='#a855f7', width=2)
    ),
    text=[f'{v:.3f}' for v in topic_dist],
    textposition='outside'
))

fig_topic_dist.update_layout(
    template='plotly_dark',
    height=400,
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)',
    font=dict(color='#a855f7'),
    yaxis_title="Proportion moyenne",
    showlegend=False
)

st.plotly_chart(fig_topic_dist, use_container_width=True)

st.markdown('</div>', unsafe_allow_html=True)

# ============================================================================
# CLUSTERING
# ============================================================================

st.markdown('<div class="nlp-section"><h2 class="nlp-title">🌳 Clustering Hiérarchique</h2></div>', unsafe_allow_html=True)

cluster_col1, cluster_col2 = st.columns(2)

with cluster_col1:
    st.markdown('<div class="nlp-card">', unsafe_allow_html=True)
    st.markdown("### 🎯 K-Means Clustering")
    
    n_clusters = st.slider("Nombre de clusters", 3, 8, 5, key='kmeans')
    
    # TF-IDF pour clustering
    sample_size = min(500, len(filtered))
    sample_df = filtered.sample(n=sample_size, random_state=42)
    
    tfidf_cluster = TfidfVectorizer(max_features=100, stop_words='english')
    X_tfidf = tfidf_cluster.fit_transform(sample_df['text_clean'])
    
    # K-Means
    kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
    clusters = kmeans.fit_predict(X_tfidf)
    
    # t-SNE pour visualisation
    tsne = TSNE(n_components=2, random_state=42, perplexity=30)
    X_tsne = tsne.fit_transform(X_tfidf.toarray())
    
    tsne_df = pd.DataFrame({
        'x': X_tsne[:, 0],
        'y': X_tsne[:, 1],
        'cluster': clusters,
        'region': sample_df['region_name'].values
    })
    
    fig_kmeans = px.scatter(
        tsne_df,
        x='x',
        y='y',
        color='cluster',
        hover_data=['region'],
        color_continuous_scale='Plasma'
    )
    
    fig_kmeans.update_layout(
        template='plotly_dark',
        height=500,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#a855f7'),
        title="Visualisation t-SNE des Clusters"
    )
    
    st.plotly_chart(fig_kmeans, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

with cluster_col2:
    st.markdown('<div class="nlp-card">', unsafe_allow_html=True)
    st.markdown("### 🌳 Dendrogramme")
    
    # Clustering hiérarchique sur échantillon
    sample_small = min(50, len(filtered))
    X_small = X_tfidf[:sample_small].toarray()
    
    linkage_matrix = linkage(X_small, method='ward')
    
    fig_dendro, ax = plt.subplots(figsize=(12, 8))
    dendrogram(
        linkage_matrix,
        ax=ax,
        color_threshold=0,
        above_threshold_color='#a855f7'
    )
    ax.set_facecolor('#0a0e27')
    fig_dendro.patch.set_facecolor('#0a0e27')
    ax.tick_params(colors='#a855f7')
    ax.spines['bottom'].set_color('#a855f7')
    ax.spines['left'].set_color('#a855f7')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.set_xlabel('Documents', color='#a855f7')
    ax.set_ylabel('Distance', color='#a855f7')
    
    st.pyplot(fig_dendro)
    plt.close()
    
    st.markdown('</div>', unsafe_allow_html=True)

# ============================================================================
# COMPARAISON INTER-RÉGIONS
# ============================================================================

st.markdown('<div class="nlp-section"><h2 class="nlp-title">🗺️ Comparaison Inter-Régions</h2></div>', unsafe_allow_html=True)

st.markdown('<div class="nlp-card">', unsafe_allow_html=True)

comp_col1, comp_col2 = st.columns(2)

with comp_col1:
    st.markdown("### 📊 Similarité Cosinus entre Régions")
    
    # Top 8 régions
    top_regions_comp = filtered['region_name'].value_counts().head(8).index
    
    region_vectors = []
    region_names_comp = []
    
    for region in top_regions_comp:
        region_text = ' '.join(
            filtered[filtered['region_name'] == region]['text_clean'].tolist()
        )
        region_vectors.append(region_text)
        region_names_comp.append(region)
    
    # TF-IDF
    tfidf_comp = TfidfVectorizer(max_features=200, stop_words='english')
    region_matrix = tfidf_comp.fit_transform(region_vectors)
    
    # Similarité
    similarity_matrix = cosine_similarity(region_matrix)
    
    fig_sim = go.Figure(data=go.Heatmap(
        z=similarity_matrix,
        x=region_names_comp,
        y=region_names_comp,
        colorscale='Plasma',
        text=np.round(similarity_matrix, 2),
        texttemplate='%{text}',
        textfont=dict(color='white')
    ))
    
    fig_sim.update_layout(
        template='plotly_dark',
        height=600,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#a855f7'),
        title="Matrice de Similarité"
    )
    
    st.plotly_chart(fig_sim, use_container_width=True)

with comp_col2:
    st.markdown("### 🎯 Termes Distinctifs par Région")
    
    # Pour chaque région, trouver termes uniques
    distinctif_data = []
    
    for region in top_regions_comp[:5]:
        region_docs = filtered[filtered['region_name'] == region]['text_clean'].tolist()
        other_docs = filtered[filtered['region_name'] != region]['text_clean'].tolist()
        
        if region_docs and other_docs:
            # TF-IDF sur région
            tfidf_region = TfidfVectorizer(max_features=50, stop_words='english')
            try:
                tfidf_region.fit(region_docs + other_docs)
                
                region_vec = tfidf_region.transform(region_docs)
                other_vec = tfidf_region.transform(other_docs)
                
                region_mean = region_vec.mean(axis=0).A1
                other_mean = other_vec.mean(axis=0).A1
                
                diff = region_mean - other_mean
                top_diff_idx = diff.argsort()[-3:][::-1]
                
                terms = tfidf_region.get_feature_names_out()
                for idx in top_diff_idx:
                    distinctif_data.append({
                        'Région': region,
                        'Terme': terms[idx],
                        'Score': diff[idx]
                    })
            except:
                pass
    
    if distinctif_data:
        df_dist = pd.DataFrame(distinctif_data)
        
        fig_dist = px.bar(
            df_dist,
            x='Score',
            y='Terme',
            color='Région',
            orientation='h',
            barmode='group',
            color_discrete_sequence=px.colors.qualitative.Vivid
        )
        
        fig_dist.update_layout(
            template='plotly_dark',
            height=600,
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#a855f7')
        )
        
        st.plotly_chart(fig_dist, use_container_width=True)
    else:
        st.warning("Pas assez de données")

st.markdown('</div>', unsafe_allow_html=True)

# ============================================================================
# FOOTER
# ============================================================================

st.markdown("---")
st.markdown(f"""
<div class="lab-header" style="padding: 1.5rem;">
    <p style="text-align: center; color: #a855f7; font-family: monospace; font-size: 1.1rem; margin: 0;">
        🧠 NLP ANALYSIS COMPLETE • {len(filtered):,} DOCUMENTS ANALYZED • 
        {unique_words:,} UNIQUE TERMS • {n_topics} TOPICS DISCOVERED • 
        ⏰ {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}
    </p>
</div>
""", unsafe_allow_html=True)