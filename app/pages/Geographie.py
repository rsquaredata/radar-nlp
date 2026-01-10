import streamlit as st
import pandas as pd
import sys
from pathlib import Path
import folium
from folium.plugins import HeatMap, MarkerCluster
import plotly.graph_objects as go
from datetime import datetime

# Import
sys.path.insert(0, str(Path(__file__).parent.parent))
from utils.components import inject_premium_css, premium_navbar
from utils.db import load_offers_with_skills

# ============================================================================
# CONFIG
# ============================================================================


inject_premium_css()
premium_navbar(active_page="Géographie")

# ============================================================================
# CSS
# ============================================================================

st.markdown("""
<style>
    .nasa-header {
        background: linear-gradient(135deg, #1e293b 0%, #334155 100%);
        border: 3px solid #00ff41;
        border-radius: 20px;
        padding: 2rem;
        margin-bottom: 2rem;
        box-shadow: 0 0 50px rgba(0, 255, 65, 0.3);
    }
    
    .mega-title {
        font-size: 3rem;
        font-weight: 900;
        text-align: center;
        background: linear-gradient(135deg, #00ff41 0%, #00d4ff 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin: 0;
    }
    
    .metric-card {
        background: linear-gradient(135deg, rgba(0, 255, 65, 0.1), rgba(0, 212, 255, 0.1));
        border: 2px solid rgba(0, 255, 65, 0.5);
        border-radius: 16px;
        padding: 2rem;
        text-align: center;
        transition: all 0.3s;
    }
    
    .metric-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 10px 30px rgba(0, 255, 65, 0.4);
    }
    
    .metric-value {
        font-size: 2.5rem;
        font-weight: 900;
        background: linear-gradient(135deg, #00ff41 0%, #00d4ff 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    .metric-label {
        font-size: 0.9rem;
        color: #cbd5e1;
        text-transform: uppercase;
        margin-top: 0.5rem;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================================
# HEADER
# ============================================================================

st.markdown("""
<div class="nasa-header">
    <h1 class="mega-title">🛰️ MISSION CONTROL - GÉOLOCALISATION</h1>
    <p style="text-align: center; color: #00ff41; font-family: monospace; margin-top: 1rem;">
        > SYSTÈME OPÉRATIONNEL • TRACKING EN TEMPS RÉEL
    </p>
</div>
""", unsafe_allow_html=True)



@st.cache_data(ttl=300)
def load_geo_data():
    df = load_offers_with_skills()
    if not df.empty:
        coords = {
            'Île-de-France': (48.8566, 2.3522),
            'Auvergne-Rhône-Alpes': (45.7640, 4.8357),
            'Provence-Alpes-Côte d\'Azur': (43.2965, 5.3698),
            'Nouvelle-Aquitaine': (44.8378, -0.5792),
            'Occitanie': (43.6047, 1.4442),
            'Hauts-de-France': (50.6292, 3.0573),
            'Bretagne': (48.1173, -1.6778),
            'Grand Est': (48.5734, 7.7521),
            'Normandie': (49.4432, 1.0993),
            'Pays de la Loire': (47.2184, -1.5536),
            'Centre-Val de Loire': (47.9029, 1.9093),
            'Bourgogne-Franche-Comté': (47.2805, 5.9993),
            'Corse': (42.0396, 9.0129),
        }
        
        df['lat'] = df['region_name'].map(lambda x: coords.get(x, (46.2276, 2.2137))[0])
        df['lon'] = df['region_name'].map(lambda x: coords.get(x, (46.2276, 2.2137))[1])
        
        import numpy as np
        np.random.seed(42)
        df['lat'] += np.random.uniform(-0.5, 0.5, len(df))
        df['lon'] += np.random.uniform(-0.5, 0.5, len(df))
        
        if 'skills_count' not in df.columns:
            df['skills_count'] = df['all_skills'].apply(lambda x: len(str(x).split(',')) if pd.notna(x) else 0)
    
    return df

df = load_geo_data()

if df.empty:
    st.error("⚠️ Aucune donnée")
    st.stop()



st.markdown("## 🎛️ PANNEAU DE CONTRÔLE")

filter_col1, filter_col2, filter_col3 = st.columns(3)

with filter_col1:
    st.markdown("### 📡 Type de Carte")
    map_mode = st.radio(
        "Mode",
        ["🎯 Clusters", "🔥 Heatmap", "📍 Markers"],
        horizontal=True,
        label_visibility="collapsed"
    )

with filter_col2:
    st.markdown("### 🗺️ Régions")
    regions = sorted(df['region_name'].dropna().unique().tolist())
    sel_regions = st.multiselect(
        "Régions",
        regions,
        default=regions[:5],
        label_visibility="collapsed"
    )

with filter_col3:
    st.markdown("### 🏠 Télétravail")
    remote = st.radio(
        "Mode",
        ["Tous", "Oui", "Non"],
        horizontal=True,
        label_visibility="collapsed"
    )

# Deuxième ligne de filtres
filter_col4, filter_col5, filter_col6 = st.columns(3)

with filter_col4:
    st.markdown("### 📋 Type de Contrat")
    contracts = sorted(df['contract_type'].dropna().unique().tolist())
    sel_contracts = st.multiselect(
        "Contrats",
        contracts,
        default=contracts,
        label_visibility="collapsed"
    )

with filter_col5:
    st.markdown("### 💼 Compétences")
    all_skills = set()
    for s in df['all_skills'].dropna():
        if isinstance(s, str):
            all_skills.update([x.strip() for x in s.split(',') if x.strip()])
    all_skills = sorted(list(all_skills))[:100]
    
    sel_skills = st.multiselect(
        "Compétences",
        all_skills,
        label_visibility="collapsed"
    )

with filter_col6:
    st.markdown("### 🎯 Nb Compétences")
    min_sk, max_sk = st.slider(
        "Plage",
        0, 30, (0, 30),
        label_visibility="collapsed"
    )

st.markdown("---")

# ============================================================================
# FILTRAGE
# ============================================================================

filtered = df.copy()

if sel_regions:
    filtered = filtered[filtered['region_name'].isin(sel_regions)]

if sel_contracts:
    filtered = filtered[filtered['contract_type'].isin(sel_contracts)]

if remote == "Oui":
    filtered = filtered[filtered['remote'] == 'yes']
elif remote == "Non":
    filtered = filtered[filtered['remote'] == 'no']

if sel_skills:
    def has_skills(x):
        if pd.isna(x):
            return False
        return any(s.lower() in str(x).lower() for s in sel_skills)
    filtered = filtered[filtered['all_skills'].apply(has_skills)]

filtered = filtered[(filtered['skills_count'] >= min_sk) & (filtered['skills_count'] <= max_sk)]



st.markdown("## 📊 STATISTIQUES EN TEMPS RÉEL")

m1, m2, m3, m4, m5 = st.columns(5)

with m1:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-value">{len(filtered):,}</div>
        <div class="metric-label">🎯 OFFRES</div>
    </div>
    """, unsafe_allow_html=True)

with m2:
    regions_count = filtered['region_name'].nunique()
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-value">{regions_count}</div>
        <div class="metric-label">🗺️ RÉGIONS</div>
    </div>
    """, unsafe_allow_html=True)

with m3:
    density = len(filtered) / regions_count if regions_count > 0 else 0
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-value">{density:.1f}</div>
        <div class="metric-label">📈 DENSITÉ</div>
    </div>
    """, unsafe_allow_html=True)

with m4:
    remote_pct = (filtered['remote'] == 'yes').sum() / len(filtered) * 100 if len(filtered) > 0 else 0
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-value">{remote_pct:.0f}%</div>
        <div class="metric-label">🏠 REMOTE</div>
    </div>
    """, unsafe_allow_html=True)

with m5:
    if not filtered.empty:
        top = filtered['region_name'].value_counts().index[0]
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value" style="font-size: 1.5rem;">{top[:10]}</div>
            <div class="metric-label">🔥 TOP</div>
        </div>
        """, unsafe_allow_html=True)

st.markdown("---")



st.markdown("## 🗺️ CARTE INTERACTIVE")

if not filtered.empty:
    # Créer carte
    center_lat = filtered['lat'].mean()
    center_lon = filtered['lon'].mean()
    
    m = folium.Map(
        location=[center_lat, center_lon],
        zoom_start=6,
        tiles='OpenStreetMap'
    )
    
    # CLUSTERS
    if map_mode == "🎯 Clusters":
        mc = MarkerCluster().add_to(m)
        
        for idx, row in filtered.head(500).iterrows():
            colors = {
                'CDI': 'green',
                'CDD': 'blue',
                'Stage': 'purple',
                'Alternance': 'orange',
                'Freelance': 'red'
            }
            color = colors.get(str(row.get('contract_type') or 'CDI'), 'gray')
            
            title = str(row.get('title') or 'N/A')[:50]
            company = str(row.get('company_name') or 'N/A')[:40]
            
            popup = f"<b>{title}</b><br>🏢 {company}"
            
            folium.Marker(
                location=[row['lat'], row['lon']],
                popup=popup,
                tooltip=title[:30],
                icon=folium.Icon(color=color, icon='info-sign')
            ).add_to(mc)
    
    # HEATMAP
    elif map_mode == "🔥 Heatmap":
        heat_data = [[row['lat'], row['lon']] for idx, row in filtered.iterrows()]
        HeatMap(heat_data, radius=15).add_to(m)
    
    # MARKERS
    else:
        for idx, row in filtered.head(200).iterrows():
            folium.CircleMarker(
                location=[row['lat'], row['lon']],
                radius=5,
                color='blue',
                fill=True,
                fillOpacity=0.6,
                popup=str(row.get('title') or 'N/A')[:50]
            ).add_to(m)
    
    # Sauvegarder et afficher
    map_html = m._repr_html_()
    st.components.v1.html(map_html, height=600, scrolling=False)

else:
    st.warning("⚠️ Aucune donnée avec ces filtres")

# ============================================================================
# GRAPHIQUES
# ============================================================================

if not filtered.empty:
    st.markdown("---")
    st.markdown("## 📈 ANALYSES")
    
    chart_col1, chart_col2 = st.columns(2)
    
    with chart_col1:
        st.markdown("### 🗺️ Top Régions")
        region_counts = filtered['region_name'].value_counts().head(10)
        
        fig1 = go.Figure(data=[
            go.Bar(
                x=region_counts.values,
                y=region_counts.index,
                orientation='h',
                marker=dict(color='#00ff41')
            )
        ])
        
        fig1.update_layout(
            height=400,
            template='plotly_dark',
            xaxis_title="Nombre d'offres",
            yaxis_title=""
        )
        
        st.plotly_chart(fig1, use_container_width=True)
    
    with chart_col2:
        st.markdown("### 📋 Types de Contrat")
        contract_counts = filtered['contract_type'].value_counts()
        
        fig2 = go.Figure(data=[
            go.Pie(
                labels=contract_counts.index,
                values=contract_counts.values,
                hole=0.4
            )
        ])
        
        fig2.update_layout(
            height=400,
            template='plotly_dark'
        )
        
        st.plotly_chart(fig2, use_container_width=True)

# ============================================================================
# TABLEAU
# ============================================================================

st.markdown("---")
st.markdown("## 📋 DONNÉES")

with st.expander("🔍 Voir le tableau", expanded=False):
    cols = ['title', 'company_name', 'region_name', 'contract_type', 'remote']
    available = [c for c in cols if c in filtered.columns]
    st.dataframe(filtered[available].head(50), use_container_width=True)

# ============================================================================
# EXPORT
# ============================================================================

st.markdown("---")
st.markdown("## 📥 EXPORT")

exp_col1, exp_col2, exp_col3 = st.columns(3)

with exp_col1:
    csv = filtered.to_csv(index=False).encode('utf-8')
    st.download_button(
        "📄 Télécharger CSV",
        csv,
        f"geo_{datetime.now().strftime('%Y%m%d')}.csv",
        use_container_width=True
    )

with exp_col2:
    if st.button("📊 Analytics", use_container_width=True):
        st.info("Redirection...")

with exp_col3:
    if st.button("🔍 Explorer", use_container_width=True):
        st.info("Redirection...")

# ============================================================================
# FOOTER
# ============================================================================

st.markdown("---")
st.markdown(f"""
<div style="text-align: center; padding: 1.5rem; background: rgba(0,0,0,0.5); border-radius: 10px;">
    <p style="color: #00ff41; font-family: monospace; font-size: 1.1rem; margin: 0;">
        🛰️ MISSION STATUS: OPÉRATIONNEL • 
        📡 {len(filtered):,} CIBLES • 
        🗺️ {regions_count} ZONES • 
        ⏰ {datetime.now().strftime('%H:%M:%S')}
    </p>
</div>
""", unsafe_allow_html=True)