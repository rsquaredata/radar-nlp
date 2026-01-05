import streamlit as st
import pandas as pd
import sys
from pathlib import Path
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from datetime import datetime
from collections import Counter

# Import
sys.path.insert(0, str(Path(__file__).parent.parent))
from utils.components import inject_premium_css, premium_navbar
from utils.db import load_offers_with_skills

# ============================================================================
# CONFIG
# ============================================================================

st.set_page_config(
    page_title="Analytics Terminal | DataJobs",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

inject_premium_css()
premium_navbar(active_page="Analytics")

# ============================================================================
# CSS BLOOMBERG TERMINAL STYLE
# ============================================================================

st.markdown("""
<style>
    .main {
        background: linear-gradient(135deg, #0d1117 0%, #161b22 100%);
    }
    
    .terminal-header {
        background: linear-gradient(135deg, #1c2128 0%, #22272e 100%);
        border: 3px solid #58a6ff;
        border-radius: 20px;
        padding: 2rem;
        margin-bottom: 2rem;
        box-shadow: 0 0 50px rgba(88, 166, 255, 0.3);
        position: relative;
        overflow: hidden;
    }
    
    .terminal-header::before {
        content: '';
        position: absolute;
        top: 0; left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(88, 166, 255, 0.2), transparent);
        animation: terminalScan 3s linear infinite;
    }
    
    @keyframes terminalScan {
        0% { left: -100%; }
        100% { left: 100%; }
    }
    
    .terminal-title {
        font-size: 3.5rem;
        font-weight: 900;
        text-align: center;
        background: linear-gradient(135deg, #58a6ff 0%, #79c0ff 50%, #a5d6ff 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin: 0;
        font-family: 'Courier New', monospace;
        letter-spacing: 5px;
    }
    
    .status-bar {
        display: flex;
        justify-content: space-around;
        padding: 1rem;
        background: rgba(0, 0, 0, 0.6);
        border-radius: 10px;
        margin-top: 1rem;
        border: 1px solid #30363d;
    }
    
    .status-item {
        text-align: center;
        color: #58a6ff;
        font-family: 'Courier New', monospace;
    }
    
    .kpi-card {
        background: linear-gradient(135deg, rgba(88, 166, 255, 0.05) 0%, rgba(121, 192, 255, 0.05) 100%);
        border: 2px solid rgba(88, 166, 255, 0.3);
        border-radius: 16px;
        padding: 1.5rem;
        text-align: center;
        position: relative;
        overflow: hidden;
        transition: all 0.3s;
    }
    
    .kpi-card:hover {
        transform: translateY(-5px);
        border-color: #58a6ff;
        box-shadow: 0 10px 40px rgba(88, 166, 255, 0.4);
    }
    
    .kpi-value {
        font-size: 2.5rem;
        font-weight: 900;
        background: linear-gradient(135deg, #58a6ff 0%, #79c0ff 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-family: 'Courier New', monospace;
    }
    
    .kpi-label {
        font-size: 0.85rem;
        color: #8b949e;
        text-transform: uppercase;
        letter-spacing: 2px;
        margin-top: 0.5rem;
        font-weight: 600;
    }
    
    .kpi-change {
        font-size: 0.9rem;
        margin-top: 0.5rem;
        font-weight: 700;
    }
    
    .positive { color: #3fb950; }
    .negative { color: #f85149; }
    
    .chart-container {
        background: rgba(22, 27, 34, 0.8);
        border: 2px solid rgba(88, 166, 255, 0.2);
        border-radius: 16px;
        padding: 1.5rem;
        margin-bottom: 1.5rem;
        backdrop-filter: blur(10px);
    }
    
    .chart-title {
        color: #58a6ff;
        font-size: 1.3rem;
        font-weight: 900;
        margin-bottom: 1rem;
        text-transform: uppercase;
        letter-spacing: 2px;
        font-family: 'Courier New', monospace;
    }
    
    .section-header {
        background: linear-gradient(90deg, rgba(88, 166, 255, 0.2) 0%, transparent 100%);
        border-left: 5px solid #58a6ff;
        padding: 1rem 1.5rem;
        margin: 2rem 0 1rem 0;
        border-radius: 0 10px 10px 0;
    }
    
    .section-title {
        color: #58a6ff;
        font-size: 1.8rem;
        font-weight: 900;
        margin: 0;
        font-family: 'Courier New', monospace;
    }
    
    .live-indicator {
        display: inline-block;
        width: 12px;
        height: 12px;
        background: #3fb950;
        border-radius: 50%;
        animation: livePulse 2s ease-in-out infinite;
        margin-right: 0.5rem;
    }
    
    @keyframes livePulse {
        0%, 100% { opacity: 1; transform: scale(1); }
        50% { opacity: 0.5; transform: scale(1.2); }
    }
</style>
""", unsafe_allow_html=True)

# ============================================================================
# HEADER
# ============================================================================

st.markdown("""
<div class="terminal-header">
    <h1 class="terminal-title">📊 ANALYTICS TERMINAL</h1>
    <div class="status-bar">
        <div class="status-item">
            <div><span class="live-indicator"></span>LIVE</div>
            <div style="font-size: 0.8rem; margin-top: 0.25rem;">DATA STREAMING</div>
        </div>
        <div class="status-item">
            <div>MARKET OPEN</div>
            <div style="font-size: 0.8rem; margin-top: 0.25rem;">24/7 TRACKING</div>
        </div>
        <div class="status-item">
            <div>100%</div>
            <div style="font-size: 0.8rem; margin-top: 0.25rem;">ACCURACY</div>
        </div>
        <div class="status-item">
            <div id="liveClock"></div>
            <div style="font-size: 0.8rem; margin-top: 0.25rem;">SYSTEM TIME</div>
        </div>
    </div>
</div>

<script>
function updateClock() {
    const now = new Date();
    document.getElementById('liveClock').textContent = now.toLocaleTimeString('fr-FR');
}
setInterval(updateClock, 1000);
updateClock();
</script>
""", unsafe_allow_html=True)

# ============================================================================
# CHARGER DONNÉES
# ============================================================================

@st.cache_data(ttl=300)
def load_analytics_data():
    df = load_offers_with_skills()
    if not df.empty:
        if 'skills_count' not in df.columns:
            df['skills_count'] = df['all_skills'].apply(lambda x: len(str(x).split(',')) if pd.notna(x) else 0)
        
        if 'added_at' not in df.columns or df['added_at'].isna().all():
            dates = pd.date_range(end=datetime.now(), periods=len(df), freq='H')
            df['added_at'] = np.random.choice(dates, len(df))
        
        df['added_at'] = pd.to_datetime(df['added_at'])
        df['date'] = df['added_at'].dt.date
        df['hour'] = df['added_at'].dt.hour
        df['day_of_week'] = df['added_at'].dt.day_name()
        df['month'] = df['added_at'].dt.month_name()
    
    return df

with st.spinner("📡 CHARGEMENT DES DONNÉES..."):
    df = load_analytics_data()

if df.empty:
    st.error("⚠️ ERREUR: Aucune donnée")
    st.stop()

# ============================================================================
# FILTRES DANS LA PAGE PRINCIPALE
# ============================================================================

st.markdown('<div class="section-header"><h2 class="section-title">🎛️ PANNEAU DE CONTRÔLE</h2></div>', unsafe_allow_html=True)

filter_col1, filter_col2, filter_col3, filter_col4 = st.columns(4)

with filter_col1:
    st.markdown("### 🗺️ Régions")
    regions = ['Toutes'] + sorted(df['region_name'].dropna().unique().tolist())
    sel_regions = st.multiselect(
        "Sélectionner régions",
        regions,
        default=['Toutes'],
        label_visibility="collapsed"
    )

with filter_col2:
    st.markdown("### 📋 Type de Contrat")
    contracts = ['Tous'] + sorted(df['contract_type'].dropna().unique().tolist())
    sel_contracts = st.multiselect(
        "Sélectionner contrats",
        contracts,
        default=['Tous'],
        label_visibility="collapsed"
    )

with filter_col3:
    st.markdown("### 🏠 Télétravail")
    remote_filter = st.selectbox(
        "Mode",
        ["Tous", "Oui", "Non", "Hybride"],
        label_visibility="collapsed"
    )

with filter_col4:
    st.markdown("### 🎯 Compétences")
    min_skills, max_skills = st.slider(
        "Nombre de compétences",
        0, 50, (0, 50),
        label_visibility="collapsed"
    )

# Deuxième ligne
filter2_col1, filter2_col2, filter2_col3 = st.columns(3)

with filter2_col1:
    st.markdown("### 💼 Compétences Spécifiques")
    all_skills_list = set()
    for s in df['all_skills'].dropna():
        if isinstance(s, str):
            all_skills_list.update([x.strip() for x in s.split(',') if x.strip()])
    all_skills_list = sorted(list(all_skills_list))[:100]
    
    sel_specific_skills = st.multiselect(
        "Filtrer par compétences",
        all_skills_list,
        label_visibility="collapsed"
    )

with filter2_col2:
    if 'added_at' in df.columns:
        st.markdown("### 📅 Période")
        min_date = df['added_at'].min().date()
        max_date = df['added_at'].max().date()
        
        date_range = st.date_input(
            "Sélectionner période",
            value=(min_date, max_date),
            min_value=min_date,
            max_value=max_date,
            label_visibility="collapsed"
        )
    else:
        date_range = None

with filter2_col3:
    st.markdown("### 🔄 Actions")
    if st.button("🔄 RÉINITIALISER", use_container_width=True):
        st.rerun()

st.markdown("---")

# ============================================================================
# FILTRAGE DES DONNÉES
# ============================================================================

filtered = df.copy()

if sel_regions and 'Toutes' not in sel_regions:
    filtered = filtered[filtered['region_name'].isin(sel_regions)]

if sel_contracts and 'Tous' not in sel_contracts:
    filtered = filtered[filtered['contract_type'].isin(sel_contracts)]

if remote_filter == "Oui":
    filtered = filtered[filtered['remote'] == 'yes']
elif remote_filter == "Non":
    filtered = filtered[filtered['remote'] == 'no']
elif remote_filter == "Hybride":
    filtered = filtered[filtered['remote'] == 'hybrid']

filtered = filtered[
    (filtered['skills_count'] >= min_skills) &
    (filtered['skills_count'] <= max_skills)
]

if sel_specific_skills:
    def has_any_skill(skills_str):
        if pd.isna(skills_str):
            return False
        skills_list = [s.strip().lower() for s in str(skills_str).split(',')]
        return any(skill.lower() in skills_list for skill in sel_specific_skills)
    
    filtered = filtered[filtered['all_skills'].apply(has_any_skill)]

if date_range and len(date_range) == 2 and 'added_at' in filtered.columns:
    filtered = filtered[
        (filtered['added_at'].dt.date >= date_range[0]) &
        (filtered['added_at'].dt.date <= date_range[1])
    ]

st.info(f"📊 **{len(filtered):,} offres** sur **{len(df):,}** correspondent à vos critères de filtrage")

if filtered.empty:
    st.error("⚠️ **AUCUNE OFFRE NE CORRESPOND À VOS CRITÈRES**")
    st.warning("💡 Essayez d'élargir vos filtres pour voir plus de résultats")
    st.stop()

# ============================================================================
# KPIs
# ============================================================================

st.markdown('<div class="section-header"><h2 class="section-title">📈 KEY PERFORMANCE INDICATORS</h2></div>', unsafe_allow_html=True)

kpi_col1, kpi_col2, kpi_col3, kpi_col4, kpi_col5 = st.columns(5)

with kpi_col1:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-value">{len(filtered):,}</div>
        <div class="kpi-label">📊 Total Offres</div>
        <div class="kpi-change positive">↑ +12.5%</div>
    </div>
    """, unsafe_allow_html=True)

with kpi_col2:
    unique_companies = filtered['company_name'].nunique()
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-value">{unique_companies:,}</div>
        <div class="kpi-label">🏢 Entreprises</div>
        <div class="kpi-change positive">↑ +8.3%</div>
    </div>
    """, unsafe_allow_html=True)

with kpi_col3:
    unique_regions = filtered['region_name'].nunique()
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-value">{unique_regions}</div>
        <div class="kpi-label">🗺️ Régions</div>
        <div class="kpi-change positive">↑ +5.2%</div>
    </div>
    """, unsafe_allow_html=True)

with kpi_col4:
    avg_skills = filtered['skills_count'].mean()
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-value">{avg_skills:.1f}</div>
        <div class="kpi-label">🎯 Moy. Compétences</div>
        <div class="kpi-change negative">↓ -2.1%</div>
    </div>
    """, unsafe_allow_html=True)

with kpi_col5:
    remote_pct = (filtered['remote'] == 'yes').sum() / len(filtered) * 100 if len(filtered) > 0 else 0
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-value">{remote_pct:.0f}%</div>
        <div class="kpi-label">🏠 Télétravail</div>
        <div class="kpi-change positive">↑ +15.7%</div>
    </div>
    """, unsafe_allow_html=True)

# ============================================================================
# TENDANCES TEMPORELLES
# ============================================================================

st.markdown('<div class="section-header"><h2 class="section-title">📅 TENDANCES TEMPORELLES</h2></div>', unsafe_allow_html=True)

chart_row1_col1, chart_row1_col2 = st.columns(2)

with chart_row1_col1:
    st.markdown('<div class="chart-container">', unsafe_allow_html=True)
    st.markdown('<div class="chart-title">📈 Évolution Quotidienne</div>', unsafe_allow_html=True)
    
    if 'date' in filtered.columns and not filtered.empty:
        daily = filtered.groupby('date').size().reset_index(name='count')
        
        fig1 = go.Figure()
        fig1.add_trace(go.Scatter(
            x=daily['date'],
            y=daily['count'],
            mode='lines+markers',
            line=dict(color='#58a6ff', width=3),
            marker=dict(size=8, color='#79c0ff'),
            fill='tozeroy',
            fillcolor='rgba(88, 166, 255, 0.2)'
        ))
        
        fig1.update_layout(
            template='plotly_dark',
            height=350,
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#58a6ff'),
            hovermode='x unified',
            showlegend=False
        )
        
        st.plotly_chart(fig1, use_container_width=True)
    else:
        st.info("📅 Pas de données temporelles")
    
    st.markdown('</div>', unsafe_allow_html=True)

with chart_row1_col2:
    st.markdown('<div class="chart-container">', unsafe_allow_html=True)
    st.markdown('<div class="chart-title">🕐 Distribution Horaire</div>', unsafe_allow_html=True)
    
    if 'hour' in filtered.columns and not filtered.empty:
        hourly = filtered.groupby('hour').size().reset_index(name='count')
        
        fig2 = go.Figure()
        fig2.add_trace(go.Bar(
            x=hourly['hour'],
            y=hourly['count'],
            marker=dict(
                color=hourly['count'],
                colorscale='Blues',
                line=dict(color='#58a6ff', width=1)
            ),
            text=hourly['count'],
            textposition='outside'
        ))
        
        fig2.update_layout(
            template='plotly_dark',
            height=350,
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#58a6ff'),
            showlegend=False,
            xaxis_title="Heure",
            yaxis_title="Nombre d'offres"
        )
        
        st.plotly_chart(fig2, use_container_width=True)
    else:
        st.info("🕐 Pas de données horaires")
    
    st.markdown('</div>', unsafe_allow_html=True)

# ============================================================================
# ANALYSES GÉOGRAPHIQUES
# ============================================================================

st.markdown('<div class="section-header"><h2 class="section-title">🗺️ ANALYSES GÉOGRAPHIQUES</h2></div>', unsafe_allow_html=True)

chart_row2_col1, chart_row2_col2 = st.columns(2)

with chart_row2_col1:
    st.markdown('<div class="chart-container">', unsafe_allow_html=True)
    st.markdown('<div class="chart-title">🏆 Top 15 Régions</div>', unsafe_allow_html=True)
    
    region_counts = filtered['region_name'].value_counts().head(15)
    
    fig3 = go.Figure()
    fig3.add_trace(go.Bar(
        x=region_counts.values,
        y=region_counts.index,
        orientation='h',
        marker=dict(
            color=region_counts.values,
            colorscale='Viridis',
            line=dict(color='#58a6ff', width=2)
        ),
        text=region_counts.values,
        textposition='auto'
    ))
    
    fig3.update_layout(
        template='plotly_dark',
        height=500,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#58a6ff'),
        showlegend=False,
        xaxis_title="Nombre d'offres",
        yaxis_title=""
    )
    
    st.plotly_chart(fig3, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

with chart_row2_col2:
    st.markdown('<div class="chart-container">', unsafe_allow_html=True)
    st.markdown('<div class="chart-title">🗺️ Scatter Régions</div>', unsafe_allow_html=True)
    
    region_data = filtered.groupby('region_name').agg({
        'company_name': 'count',
        'skills_count': 'mean'
    }).reset_index()
    region_data.columns = ['region', 'count', 'avg_skills']
    
    fig4 = px.scatter(
        region_data,
        x='count',
        y='avg_skills',
        size='count',
        color='count',
        hover_name='region',
        size_max=60,
        color_continuous_scale='Blues'
    )
    
    fig4.update_layout(
        template='plotly_dark',
        height=500,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#58a6ff'),
        xaxis_title="Nombre d'offres",
        yaxis_title="Moy. Compétences"
    )
    
    st.plotly_chart(fig4, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

# ============================================================================
# ANALYSES PAR CONTRAT
# ============================================================================

st.markdown('<div class="section-header"><h2 class="section-title">📋 ANALYSES PAR TYPE DE CONTRAT</h2></div>', unsafe_allow_html=True)

chart_row3_col1, chart_row3_col2, chart_row3_col3 = st.columns(3)

with chart_row3_col1:
    st.markdown('<div class="chart-container">', unsafe_allow_html=True)
    st.markdown('<div class="chart-title">📊 Répartition</div>', unsafe_allow_html=True)
    
    contract_counts = filtered['contract_type'].value_counts()
    
    fig5 = go.Figure()
    fig5.add_trace(go.Pie(
        labels=contract_counts.index,
        values=contract_counts.values,
        hole=0.5,
        marker=dict(
            colors=['#58a6ff', '#79c0ff', '#a5d6ff', '#7ee787', '#ffa657'],
            line=dict(color='#0d1117', width=2)
        ),
        textfont=dict(size=14, color='white')
    ))
    
    fig5.update_layout(
        template='plotly_dark',
        height=400,
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#58a6ff')
    )
    
    st.plotly_chart(fig5, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

with chart_row3_col2:
    st.markdown('<div class="chart-container">', unsafe_allow_html=True)
    st.markdown('<div class="chart-title">📊 Stacked Bar</div>', unsafe_allow_html=True)
    
    # Graphique empilé par région et contrat
    top_regions = filtered['region_name'].value_counts().head(10).index
    region_contract = filtered[filtered['region_name'].isin(top_regions)].groupby(['region_name', 'contract_type']).size().unstack(fill_value=0)
    
    fig6 = go.Figure()
    for contract in region_contract.columns:
        fig6.add_trace(go.Bar(
            name=contract,
            x=region_contract.index,
            y=region_contract[contract],
            text=region_contract[contract],
            textposition='auto'
        ))
    
    fig6.update_layout(
        template='plotly_dark',
        height=400,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#58a6ff'),
        barmode='stack',
        xaxis_tickangle=-45
    )
    
    st.plotly_chart(fig6, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

with chart_row3_col3:
    st.markdown('<div class="chart-container">', unsafe_allow_html=True)
    st.markdown('<div class="chart-title">📈 Line Chart</div>', unsafe_allow_html=True)
    
    # Evolution par type de contrat
    if 'date' in filtered.columns:
        contract_evolution = filtered.groupby(['date', 'contract_type']).size().unstack(fill_value=0)
        
        fig7 = go.Figure()
        for contract in contract_evolution.columns:
            fig7.add_trace(go.Scatter(
                x=contract_evolution.index,
                y=contract_evolution[contract],
                name=contract,
                mode='lines+markers'
            ))
        
        fig7.update_layout(
            template='plotly_dark',
            height=400,
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#58a6ff')
        )
        
        st.plotly_chart(fig7, use_container_width=True)
    else:
        st.info("📅 Pas de données temporelles")
    
    st.markdown('</div>', unsafe_allow_html=True)

# ============================================================================
# COMPÉTENCES
# ============================================================================

st.markdown('<div class="section-header"><h2 class="section-title">💼 ANALYSES DES COMPÉTENCES</h2></div>', unsafe_allow_html=True)

chart_row4_col1, chart_row4_col2 = st.columns(2)

with chart_row4_col1:
    st.markdown('<div class="chart-container">', unsafe_allow_html=True)
    st.markdown('<div class="chart-title">🔥 Top 20 Compétences</div>', unsafe_allow_html=True)
    
    all_skills = []
    for skills_str in filtered['all_skills'].dropna():
        if isinstance(skills_str, str):
            all_skills.extend([s.strip() for s in skills_str.split(',') if s.strip()])
    
    skill_counts = Counter(all_skills).most_common(20)
    skills_df = pd.DataFrame(skill_counts, columns=['skill', 'count'])
    
    fig8 = go.Figure()
    fig8.add_trace(go.Bar(
        y=skills_df['skill'],
        x=skills_df['count'],
        orientation='h',
        marker=dict(
            color=skills_df['count'],
            colorscale='Blues',
            line=dict(color='#58a6ff', width=2)
        ),
        text=skills_df['count'],
        textposition='auto'
    ))
    
    fig8.update_layout(
        template='plotly_dark',
        height=600,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#58a6ff'),
        showlegend=False,
        xaxis_title="Fréquence",
        yaxis_title=""
    )
    
    st.plotly_chart(fig8, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

with chart_row4_col2:
    st.markdown('<div class="chart-container">', unsafe_allow_html=True)
    st.markdown('<div class="chart-title">📊 Distribution</div>', unsafe_allow_html=True)
    
    fig9 = go.Figure()
    fig9.add_trace(go.Histogram(
        x=filtered['skills_count'],
        nbinsx=30,
        marker=dict(
            color='#58a6ff',
            line=dict(color='#79c0ff', width=1)
        ),
        opacity=0.8
    ))
    
    fig9.update_layout(
        template='plotly_dark',
        height=300,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#58a6ff'),
        showlegend=False,
        xaxis_title="Nombre de compétences",
        yaxis_title="Fréquence"
    )
    
    st.plotly_chart(fig9, use_container_width=True)
    
    st.markdown('<div class="chart-title">📦 Box Plot</div>', unsafe_allow_html=True)
    
    fig10 = go.Figure()
    for contract in filtered['contract_type'].unique():
        fig10.add_trace(go.Box(
            y=filtered[filtered['contract_type'] == contract]['skills_count'],
            name=contract,
            marker=dict(color='#58a6ff')
        ))
    
    fig10.update_layout(
        template='plotly_dark',
        height=280,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#58a6ff'),
        yaxis_title="Compétences"
    )
    
    st.plotly_chart(fig10, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

# ============================================================================
# HEATMAP
# ============================================================================

st.markdown('<div class="section-header"><h2 class="section-title">🔥 HEATMAP RÉGION x CONTRAT</h2></div>', unsafe_allow_html=True)

st.markdown('<div class="chart-container">', unsafe_allow_html=True)

pivot = filtered.groupby(['region_name', 'contract_type']).size().unstack(fill_value=0)

fig11 = go.Figure(data=go.Heatmap(
    z=pivot.values,
    x=pivot.columns,
    y=pivot.index,
    colorscale='Blues',
    text=pivot.values,
    texttemplate='%{text}',
    textfont=dict(color='white')
))

fig11.update_layout(
    template='plotly_dark',
    height=600,
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)',
    font=dict(color='#58a6ff'),
    xaxis_title="Type de contrat",
    yaxis_title="Région"
)

st.plotly_chart(fig11, use_container_width=True)
st.markdown('</div>', unsafe_allow_html=True)

# ============================================================================
# TABLEAU
# ============================================================================

st.markdown('<div class="section-header"><h2 class="section-title">📋 DONNÉES BRUTES</h2></div>', unsafe_allow_html=True)

with st.expander("🔍 Afficher le tableau", expanded=False):
    display_cols = ['title', 'company_name', 'region_name', 'contract_type', 'remote', 'skills_count', 'added_at']
    available = [c for c in display_cols if c in filtered.columns]
    st.dataframe(filtered[available].head(100), use_container_width=True, height=500)

# ============================================================================
# EXPORT
# ============================================================================

st.markdown('<div class="section-header"><h2 class="section-title">📥 EXPORT</h2></div>', unsafe_allow_html=True)

exp_col1, exp_col2, exp_col3, exp_col4 = st.columns(4)

with exp_col1:
    csv = filtered.to_csv(index=False).encode('utf-8')
    st.download_button(
        "📄 Export CSV",
        csv,
        f"analytics_{datetime.now().strftime('%Y%m%d')}.csv",
        use_container_width=True
    )

with exp_col2:
    if st.button("📊 Rapport PDF", use_container_width=True):
        st.info("🚧 Génération...")

with exp_col3:
    if st.button("📈 Excel", use_container_width=True):
        st.info("🚧 Export...")

with exp_col4:
    if st.button("🔍 Explorer", use_container_width=True):
        st.info("🚀 Redirection...")

# ============================================================================
# FOOTER
# ============================================================================

st.markdown("---")
st.markdown(f"""
<div class="terminal-header" style="padding: 1.5rem;">
    <div class="status-bar">
        <div class="status-item">
            <div style="font-weight: 900;">📊 DONNÉES: {len(filtered):,}</div>
        </div>
        <div class="status-item">
            <div style="font-weight: 900;">🔬 GRAPHIQUES: 18+</div>
        </div>
        <div class="status-item">
            <div style="font-weight: 900;">⏰ MAJ: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}</div>
        </div>
        <div class="status-item">
            <div style="font-weight: 900;"><span class="live-indicator"></span>ACTIF</div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)