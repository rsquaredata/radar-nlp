import streamlit as st
import pandas as pd
from typing import Dict, List, Tuple, Any
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from config import CONTRACT_TYPES, REMOTE_OPTIONS


def create_sidebar_filters(df: pd.DataFrame) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """
    Crée les filtres dans la sidebar et retourne le DataFrame filtré.
    
    Args:
        df: DataFrame à filtrer
    
    Returns:
        Tuple (DataFrame filtré, dict des filtres actifs)
    """
    st.sidebar.header("🔍 Filtres")
    
    filters = {}
    
    # ========================================================================
    # RÉGION
    # ========================================================================
    
    if 'region_name' in df.columns:
        regions = ['Toutes'] + sorted(df['region_name'].dropna().unique().tolist())
        
        selected_regions = st.sidebar.multiselect(
            "🗺️ Région",
            options=regions,
            default=['Toutes'],
            help="Sélectionner une ou plusieurs régions"
        )
        
        filters['regions'] = selected_regions
    else:
        selected_regions = ['Toutes']
        filters['regions'] = selected_regions
    
    # ========================================================================
    # TYPE DE CONTRAT
    # ========================================================================
    
    if 'contract_type' in df.columns:
        contracts = ['Tous'] + sorted(df['contract_type'].dropna().unique().tolist())
        
        selected_contract = st.sidebar.selectbox(
            "📋 Type de contrat",
            options=contracts,
            help="Filtrer par type de contrat"
        )
        
        filters['contract'] = selected_contract
    else:
        selected_contract = 'Tous'
        filters['contract'] = selected_contract
    
    # ========================================================================
    # TÉLÉTRAVAIL
    # ========================================================================
    
    if 'remote' in df.columns:
        remote_opts = ['Tous'] + sorted(df['remote'].dropna().unique().tolist())
        
        selected_remote = st.sidebar.selectbox(
            "🏠 Télétravail",
            options=remote_opts,
            help="Filtrer par modalité de télétravail"
        )
        
        filters['remote'] = selected_remote
    else:
        selected_remote = 'Tous'
        filters['remote'] = selected_remote
    
    # ========================================================================
    # SOURCE
    # ========================================================================
    
    if 'source_name' in df.columns:
        sources = ['Toutes'] + sorted(df['source_name'].dropna().unique().tolist())
        
        selected_sources = st.sidebar.multiselect(
            "📊 Source",
            options=sources,
            default=['Toutes'],
            help="Filtrer par source de données"
        )
        
        filters['sources'] = selected_sources
    else:
        selected_sources = ['Toutes']
        filters['sources'] = selected_sources
    
    # ========================================================================
    # COMPÉTENCES (si disponible)
    # ========================================================================
    
    # On ne filtre pas ici car trop complexe, géré dans search_offers de db.py
    
    # ========================================================================
    # RECHERCHE TEXTE
    # ========================================================================
    
    search_text = st.sidebar.text_input(
        "🔎 Recherche libre",
        placeholder="Mots-clés dans titre ou description",
        help="Rechercher dans le titre ou la description"
    )
    
    filters['search_text'] = search_text
    
    # ========================================================================
    # APPLIQUER LES FILTRES
    # ========================================================================
    
    filtered_df = df.copy()
    
    # Filtre régions
    if 'region_name' in filtered_df.columns and 'Toutes' not in selected_regions:
        filtered_df = filtered_df[filtered_df['region_name'].isin(selected_regions)]
    
    # Filtre contrat
    if 'contract_type' in filtered_df.columns and selected_contract != 'Tous':
        filtered_df = filtered_df[filtered_df['contract_type'] == selected_contract]
    
    # Filtre télétravail
    if 'remote' in filtered_df.columns and selected_remote != 'Tous':
        filtered_df = filtered_df[filtered_df['remote'] == selected_remote]
    
    # Filtre sources
    if 'source_name' in filtered_df.columns and 'Toutes' not in selected_sources:
        filtered_df = filtered_df[filtered_df['source_name'].isin(selected_sources)]
    
    # Filtre texte
    if search_text:
        if 'title' in filtered_df.columns and 'description' in filtered_df.columns:
            mask = (
                filtered_df['title'].str.contains(search_text, case=False, na=False) |
                filtered_df['description'].str.contains(search_text, case=False, na=False)
            )
            filtered_df = filtered_df[mask]
    
    # ========================================================================
    # AFFICHER NOMBRE DE RÉSULTATS
    # ========================================================================
    
    st.sidebar.markdown("---")
    st.sidebar.metric(
        "📊 Résultats",
        f"{len(filtered_df):,}",
        delta=f"{len(filtered_df) - len(df):,}" if len(filtered_df) != len(df) else None
    )
    
    return filtered_df, filters


def create_comparison_filters() -> Dict[str, List[str]]:
    """
    Crée des filtres pour comparer des régions/domaines.
    
    Returns:
        Dict avec régions et domaines sélectionnés
    """
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🗺️ Comparer des régions")
        # Charger régions depuis DB
        from utils.db import get_db_manager
        db = get_db_manager()
        regions_df = db.get_offers_by_region()
        
        selected_regions = st.multiselect(
            "Sélectionner 2-4 régions",
            options=regions_df['region_name'].tolist(),
            max_selections=4,
            help="Comparer les caractéristiques de différentes régions"
        )
    
    with col2:
        st.subheader("🎯 Comparer des profils")
        from config import PROFILE_NAMES
        
        selected_profiles = st.multiselect(
            "Sélectionner 2-4 profils",
            options=list(PROFILE_NAMES.values()),
            max_selections=4,
            help="Comparer les profils types d'offres"
        )
    
    return {
        'regions': selected_regions,
        'profiles': selected_profiles
    }


def create_skill_filter(all_skills: List[str], key: str = "skill_filter") -> List[str]:
    """
    Crée un sélecteur de compétences avec recherche.
    
    Args:
        all_skills: Liste de toutes les compétences
        key: Clé unique pour le widget
    
    Returns:
        Liste des compétences sélectionnées
    """
    selected_skills = st.multiselect(
        "🎯 Filtrer par compétences",
        options=sorted(all_skills),
        help="Sélectionner une ou plusieurs compétences",
        key=key
    )
    
    return selected_skills


def save_filters_to_session(filters: Dict[str, Any]):
    """Sauvegarde les filtres dans st.session_state"""
    st.session_state['app_filters'] = filters


def load_filters_from_session() -> Dict[str, Any]:
    """Charge les filtres depuis st.session_state"""
    return st.session_state.get('app_filters', {})