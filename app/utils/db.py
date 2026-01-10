import sqlite3
import pandas as pd
from pathlib import Path
import streamlit as st
from typing import Optional, List, Dict, Any
import sys

# Ajouter le parent au path pour import config
sys.path.insert(0, str(Path(__file__).parent.parent))
from config import DATABASE_PATH


class DatabaseManager:
    """Gestionnaire de connexion à la base de données"""
    
    def __init__(self, db_path: Path = DATABASE_PATH):
        self.db_path = db_path
        
        if not self.db_path.exists():
            raise FileNotFoundError(f"Base de données introuvable: {self.db_path}")
    
    def get_connection(self):
        """Retourne une connexion à la base de données"""
        return sqlite3.connect(self.db_path)
    
    def execute_query(self, query: str, params: tuple = None) -> pd.DataFrame:
        """
        Exécute une requête SELECT et retourne un DataFrame.
        
        Args:
            query: Requête SQL
            params: Paramètres de la requête
        
        Returns:
            DataFrame avec les résultats
        """
        conn = self.get_connection()
        try:
            if params:
                df = pd.read_sql_query(query, conn, params=params)
            else:
                df = pd.read_sql_query(query, conn)
            return df
        finally:
            conn.close()
    
    def execute_write(self, query: str, params: tuple = None) -> int:
        """
        Exécute une requête INSERT/UPDATE/DELETE.
        
        Returns:
            Nombre de lignes affectées
        """
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            conn.commit()
            return cursor.rowcount
        finally:
            conn.close()
    
    # ========================================================================
    # REQUÊTES MÉTIER
    # ========================================================================
    
    def get_all_offers(self, limit: int = None) -> pd.DataFrame:
        """Récupère toutes les offres avec leurs dimensions"""
        query = """
            SELECT 
                fo.offer_key,
                fo.uid,
                fo.title,
                fo.location,
                fo.salary,
                fo.remote,
                fo.description,
                fo.source_url,
                fo.skills_count,
                fo.competences_count,
                fo.savoir_etre_count,
                fo.added_by,
                fo.added_at,
                ds.source_name,
                dr.region_name,
                dr.latitude as region_lat,
                dr.longitude as region_lon,
                dc.company_name,
                dct.contract_type,
                dd.full_date as published_date
            FROM fact_offers fo
            LEFT JOIN dim_source ds ON fo.source_key = ds.source_key
            LEFT JOIN dim_region dr ON fo.region_key = dr.region_key
            LEFT JOIN dim_company dc ON fo.company_key = dc.company_key
            LEFT JOIN dim_contract dct ON fo.contract_key = dct.contract_key
            LEFT JOIN dim_date dd ON fo.date_key = dd.date_key
        """
        
        if limit:
            query += f" LIMIT {limit}"
        
        return self.execute_query(query)
    
    def get_offers_with_skills(self) -> pd.DataFrame:
        """Récupère les offres avec leurs compétences agrégées"""
        query = """
            SELECT 
                fo.offer_key,
                fo.uid,
                fo.title,
                fo.location,
                fo.salary,
                fo.remote,
                fo.description,
                fo.source_url,
                dr.region_name,
                dc.company_name,
                dct.contract_type,
                GROUP_CONCAT(CASE WHEN ds.skill_type = 'competences' 
                             THEN ds.skill_name END) as competences,
                GROUP_CONCAT(CASE WHEN ds.skill_type = 'savoir_etre' 
                             THEN ds.skill_name END) as savoir_etre,
                GROUP_CONCAT(ds.skill_name) as all_skills
            FROM fact_offers fo
            LEFT JOIN fact_offer_skill fos ON fo.offer_key = fos.offer_key
            LEFT JOIN dim_skill ds ON fos.skill_key = ds.skill_key
            LEFT JOIN dim_region dr ON fo.region_key = dr.region_key
            LEFT JOIN dim_company dc ON fo.company_key = dc.company_key
            LEFT JOIN dim_contract dct ON fo.contract_key = dct.contract_key
            GROUP BY fo.offer_key
        """
        return self.execute_query(query)
    
    def get_all_skills(self) -> pd.DataFrame:
        """Récupère toutes les compétences"""
        query = """
            SELECT 
                skill_key,
                skill_name,
                skill_type,
                skill_category
            FROM dim_skill
            ORDER BY skill_name
        """
        return self.execute_query(query)
    
    def get_top_skills(self, n: int = 20, skill_type: str = None) -> pd.DataFrame:
        """
        Récupère les top compétences.
        
        Args:
            n: Nombre de compétences
            skill_type: 'competences' ou 'savoir_etre' (None = tous)
        """
        query = """
            SELECT 
                skill_name,
                skill_type,
                offer_count,
                percentage
            FROM v_top_skills
        """
        
        if skill_type:
            query += f" WHERE skill_type = '{skill_type}'"
        
        query += f" LIMIT {n}"
        
        return self.execute_query(query)
    
    def get_offers_by_region(self) -> pd.DataFrame:
        """Récupère les statistiques par région"""
        return self.execute_query("SELECT * FROM v_offers_by_region")
    
    def get_global_stats(self) -> Dict[str, Any]:
        """Récupère les statistiques globales"""
        query = "SELECT * FROM v_stats_global"
        df = self.execute_query(query)
        
        if len(df) > 0:
            return df.iloc[0].to_dict()
        return {}
    
    def search_offers(self, 
                     regions: List[str] = None,
                     skills: List[str] = None,
                     contract_types: List[str] = None,
                     remote: str = None,
                     search_text: str = None) -> pd.DataFrame:
        """
        Recherche d'offres avec filtres multiples.
        
        Args:
            regions: Liste de régions
            skills: Liste de compétences
            contract_types: Liste de types de contrat
            remote: Télétravail (Oui/Non/Hybride)
            search_text: Texte libre (titre ou description)
        
        Returns:
            DataFrame avec offres filtrées
        """
        query = """
            SELECT DISTINCT
                fo.offer_key,
                fo.uid,
                fo.title,
                fo.location,
                fo.salary,
                fo.remote,
                fo.skills_count,
                dr.region_name,
                dc.company_name,
                dct.contract_type,
                ds_src.source_name
            FROM fact_offers fo
            LEFT JOIN dim_region dr ON fo.region_key = dr.region_key
            LEFT JOIN dim_company dc ON fo.company_key = dc.company_key
            LEFT JOIN dim_contract dct ON fo.contract_key = dct.contract_key
            LEFT JOIN dim_source ds_src ON fo.source_key = ds_src.source_key
            LEFT JOIN fact_offer_skill fos ON fo.offer_key = fos.offer_key
            LEFT JOIN dim_skill ds ON fos.skill_key = ds.skill_key
            WHERE 1=1
        """
        
        params = []
        
        # Filtre régions
        if regions and len(regions) > 0 and 'Toutes' not in regions:
            placeholders = ','.join(['?' for _ in regions])
            query += f" AND dr.region_name IN ({placeholders})"
            params.extend(regions)
        
        # Filtre compétences
        if skills and len(skills) > 0:
            # Au moins une compétence doit matcher
            placeholders = ','.join(['?' for _ in skills])
            query += f" AND ds.skill_name IN ({placeholders})"
            params.extend(skills)
        
        # Filtre contrats
        if contract_types and len(contract_types) > 0 and 'Tous' not in contract_types:
            placeholders = ','.join(['?' for _ in contract_types])
            query += f" AND dct.contract_type IN ({placeholders})"
            params.extend(contract_types)
        
        # Filtre télétravail
        if remote and remote != 'Tous':
            query += " AND fo.remote = ?"
            params.append(remote)
        
        # Recherche texte
        if search_text:
            query += " AND (fo.title LIKE ? OR fo.description LIKE ?)"
            search_pattern = f"%{search_text}%"
            params.extend([search_pattern, search_pattern])
        
        query += " ORDER BY fo.added_at DESC"
        
        return self.execute_query(query, tuple(params) if params else None)
    
    def get_offer_details(self, offer_key: int) -> Dict[str, Any]:
        """Récupère les détails complets d'une offre"""
        # Infos générales
        query_offer = """
            SELECT 
                fo.*,
                dr.region_name,
                dr.latitude as region_lat,
                dr.longitude as region_lon,
                dc.company_name,
                dct.contract_type,
                ds.source_name
            FROM fact_offers fo
            LEFT JOIN dim_region dr ON fo.region_key = dr.region_key
            LEFT JOIN dim_company dc ON fo.company_key = dc.company_key
            LEFT JOIN dim_contract dct ON fo.contract_key = dct.contract_key
            LEFT JOIN dim_source ds ON fo.source_key = ds.source_key
            WHERE fo.offer_key = ?
        """
        
        offer_df = self.execute_query(query_offer, (offer_key,))
        
        if len(offer_df) == 0:
            return {}
        
        offer = offer_df.iloc[0].to_dict()
        
        # Compétences
        query_skills = """
            SELECT 
                ds.skill_name,
                ds.skill_type,
                ds.skill_category
            FROM fact_offer_skill fos
            JOIN dim_skill ds ON fos.skill_key = ds.skill_key
            WHERE fos.offer_key = ?
            ORDER BY ds.skill_type, ds.skill_name
        """
        
        skills_df = self.execute_query(query_skills, (offer_key,))
        
        offer['competences'] = skills_df[skills_df['skill_type'] == 'competences']['skill_name'].tolist()
        offer['savoir_etre'] = skills_df[skills_df['skill_type'] == 'savoir_etre']['skill_name'].tolist()
        
        return offer
    
    def check_duplicate(self, uid: str) -> bool:
        """Vérifie si un uid existe déjà"""
        query = "SELECT COUNT(*) as count FROM fact_offers WHERE uid = ?"
        result = self.execute_query(query, (uid,))
        return result.iloc[0]['count'] > 0


# ============================================================================
# CACHE STREAMLIT
# ============================================================================

@st.cache_resource
def get_db_manager():
    """Retourne une instance cachée du DatabaseManager"""
    return DatabaseManager()


@st.cache_data(ttl=3600)
def load_all_offers():
    """Charge toutes les offres (avec cache 1h)"""
    db = get_db_manager()
    return db.get_all_offers()


@st.cache_data(ttl=3600)
def load_offers_with_skills():
    """Charge offres avec compétences (avec cache 1h)"""
    db = get_db_manager()
    return db.get_offers_with_skills()


@st.cache_data(ttl=3600)
def load_global_stats():
    """Charge stats globales (avec cache 1h)"""
    db = get_db_manager()
    return db.get_global_stats()