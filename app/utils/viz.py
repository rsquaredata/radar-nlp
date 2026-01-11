
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from typing import List, Dict, Any
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from config import COLOR_PALETTE, PROFILE_COLORS, PROFILE_NAMES




def plot_top_skills_comparison(df: pd.DataFrame, 
                               group_by: str,
                               groups: List[str],
                               n_skills: int = 10) -> go.Figure:
  
    fig = make_subplots(
        rows=1, 
        cols=len(groups),
        subplot_titles=groups,
        horizontal_spacing=0.1
    )
    
    for idx, group in enumerate(groups):
        # Filtrer données du groupe
        group_df = df[df[group_by] == group]
        
        # Top compétences
        top_skills = group_df['skill_name'].value_counts().head(n_skills)
        
        # Ajouter bar chart
        fig.add_trace(
            go.Bar(
                y=top_skills.index[::-1],  # Inverser pour avoir le top en haut
                x=top_skills.values[::-1],
                orientation='h',
                name=group,
                marker_color=COLOR_PALETTE['primary'],
                showlegend=False
            ),
            row=1,
            col=idx + 1
        )
    
    fig.update_layout(
        title_text=f"Top {n_skills} Compétences par {group_by}",
        height=500,
        showlegend=False
    )
    
    fig.update_xaxes(title_text="Nombre d'offres")
    
    return fig


def plot_regional_heatmap(df: pd.DataFrame, metric: str = 'count') -> go.Figure:
   
    # Grouper par région
    if metric == 'count':
        region_data = df['region_name'].value_counts().reset_index()
        region_data.columns = ['region_name', 'value']
    else:
        region_data = df.groupby('region_name')[metric].mean().reset_index()
        region_data.columns = ['region_name', 'value']
    
    # Créer heatmap
    fig = px.bar(
        region_data.sort_values('value', ascending=False),
        x='region_name',
        y='value',
        color='value',
        color_continuous_scale='Viridis',
        title=f"Distribution par région ({metric})"
    )
    
    fig.update_layout(
        xaxis_title="Région",
        yaxis_title="Valeur",
        xaxis_tickangle=-45,
        height=500
    )
    
    return fig


def plot_profile_distribution(df: pd.DataFrame, 
                              profile_column: str = 'dominant_profile') -> go.Figure:

    profile_counts = df[profile_column].value_counts()
    
    # Mapper les IDs aux noms
    labels = [PROFILE_NAMES.get(i, f"Profil {i}") for i in profile_counts.index]
    colors = [PROFILE_COLORS.get(i, '#95a5a6') for i in profile_counts.index]
    
    fig = go.Figure(data=[go.Pie(
        labels=labels,
        values=profile_counts.values,
        marker=dict(colors=colors),
        hole=0.3,
        textinfo='label+percent',
        textposition='auto'
    )])
    
    fig.update_layout(
        title_text="Distribution des Profils NLP",
        height=500,
        showlegend=True
    )
    
    return fig


def plot_cluster_scatter(coords_2d: np.ndarray, 
                         labels: np.ndarray,
                         hover_data: pd.DataFrame = None) -> go.Figure:
   
    df_plot = pd.DataFrame({
        'x': coords_2d[:, 0],
        'y': coords_2d[:, 1],
        'cluster': labels
    })
    
    # Ajouter hover data si fourni
    if hover_data is not None:
        for col in hover_data.columns:
            df_plot[col] = hover_data[col].values
    
    # Mapper clusters aux couleurs
    df_plot['cluster_name'] = df_plot['cluster'].map(
        lambda x: PROFILE_NAMES.get(x, f"Cluster {x}")
    )
    
    fig = px.scatter(
        df_plot,
        x='x',
        y='y',
        color='cluster_name',
        hover_data=hover_data.columns.tolist() if hover_data is not None else None,
        title="Clustering K-Means - Visualisation 2D",
        color_discrete_map={
            PROFILE_NAMES.get(i, f"Cluster {i}"): PROFILE_COLORS.get(i, '#95a5a6')
            for i in range(6)
        }
    )
    
    fig.update_layout(
        xaxis_title="Composante principale 1",
        yaxis_title="Composante principale 2",
        height=600,
        hovermode='closest'
    )
    
    fig.update_traces(marker=dict(size=8, opacity=0.7))
    
    return fig


def plot_skill_frequency(skill_counts: pd.Series, 
                        top_n: int = 20,
                        title: str = "Top Compétences") -> go.Figure:
    
    top_skills = skill_counts.head(top_n)
    
    fig = go.Figure(go.Bar(
        y=top_skills.index[::-1],
        x=top_skills.values[::-1],
        orientation='h',
        marker_color=COLOR_PALETTE['primary'],
        text=top_skills.values[::-1],
        textposition='auto'
    ))
    
    fig.update_layout(
        title=title,
        xaxis_title="Nombre d'offres",
        yaxis_title="Compétence",
        height=600,
        showlegend=False
    )
    
    return fig


def plot_regional_comparison_radar(df: pd.DataFrame, 
                                   regions: List[str],
                                   skills: List[str]) -> go.Figure:
    
    fig = go.Figure()
    
    for region in regions:
        # Filtrer région
        region_df = df[df['region_name'] == region]
        
        # Compter compétences
        values = []
        for skill in skills:
            count = (region_df['skill_name'] == skill).sum()
            values.append(count)
        
        fig.add_trace(go.Scatterpolar(
            r=values,
            theta=skills,
            fill='toself',
            name=region
        ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, max([max(v) for v in [values]])]
            )
        ),
        showlegend=True,
        title="Comparaison de Compétences par Région",
        height=600
    )
    
    return fig


def plot_contract_distribution(df: pd.DataFrame) -> go.Figure:
   
    contract_counts = df['contract_type'].value_counts()
    
    fig = go.Figure(data=[go.Pie(
        labels=contract_counts.index,
        values=contract_counts.values,
        hole=0.3
    )])
    
    fig.update_layout(
        title_text="Distribution des Types de Contrat",
        height=400
    )
    
    return fig


def plot_time_series(df: pd.DataFrame, 
                     date_column: str = 'published_date',
                     freq: str = 'M') -> go.Figure:
    
    df_copy = df.copy()
    df_copy[date_column] = pd.to_datetime(df_copy[date_column])
    
    # Grouper par période
    time_counts = df_copy.set_index(date_column).resample(freq).size()
    
    fig = go.Figure(go.Scatter(
        x=time_counts.index,
        y=time_counts.values,
        mode='lines+markers',
        line=dict(color=COLOR_PALETTE['primary'], width=2),
        marker=dict(size=6)
    ))
    
    fig.update_layout(
        title="Évolution du Nombre d'Offres",
        xaxis_title="Date",
        yaxis_title="Nombre d'offres",
        height=400,
        hovermode='x unified'
    )
    
    return fig


def plot_salary_distribution(df: pd.DataFrame, 
                             salary_column: str = 'salary') -> go.Figure:
    
    
    
    fig = go.Figure(data=[go.Histogram(
        x=df[salary_column].dropna(),
        nbinsx=30,
        marker_color=COLOR_PALETTE['primary']
    )])
    
    fig.update_layout(
        title="Distribution des Salaires",
        xaxis_title="Salaire",
        yaxis_title="Fréquence",
        height=400
    )
    
    return fig



def display_metrics_row(stats: Dict[str, Any]):
    """
    Affiche une ligne de métriques Streamlit.
    
    Args:
        stats: Dictionnaire avec clés 'total_offers', 'total_skills', etc.
    """
    import streamlit as st
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "📊 Total Offres",
            f"{stats.get('total_offers', 0):,}"
        )
    
    with col2:
        st.metric(
            "🎯Compétences",
            f"{stats.get('total_skills', 0):,}"
        )
    
    with col3:
        st.metric(
            "🗺️ Régions",
            f"{stats.get('total_regions', 0):,}"
        )
    
    with col4:
        avg_skills = stats.get('avg_skills_per_offer', 0)
        st.metric(
            "📈 Moy. Compétences/Offre",
            f"{avg_skills:.1f}"
        )