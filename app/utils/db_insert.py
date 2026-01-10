import sqlite3
import pandas as pd
from pathlib import Path
from typing import List, Dict, Any, Tuple
from datetime import datetime
import hashlib
import sys

# Import du DatabaseManager existant
sys.path.insert(0, str(Path(__file__).parent.parent))
from config import DATABASE_PATH


class ContributionManager:
    """Gestionnaire d'insertion pour les contributions"""
    
    def __init__(self, db_path: Path = DATABASE_PATH):
        self.db_path = db_path
        
        if not self.db_path.exists():
            raise FileNotFoundError(f"Base de données introuvable: {self.db_path}")
    
    def get_connection(self):
        """Retourne une connexion à la base de données"""
        return sqlite3.connect(self.db_path)
    

    def insert_offers(self, offers: List[Dict[str, Any]]) -> Tuple[int, int, str]:
       
        conn = self.get_connection()
        cursor = conn.cursor()
        
        inserted_count = 0
        duplicate_count = 0
        
        try:
            for offer in offers:
                # Générer UID unique
                uid = self.generate_uid(offer)
                
                # Vérifier si l'offre existe déjà
                cursor.execute("SELECT COUNT(*) FROM fact_offers WHERE uid = ?", (uid,))
                exists = cursor.fetchone()[0] > 0
                
                if exists:
                    duplicate_count += 1
                    continue
                
                # Récupérer ou créer les dimensions
                source_key = self._get_or_create_source(cursor, offer.get('source', 'manual'))
                region_key = self._get_or_create_region(cursor, offer.get('region_name', 'Unknown'))
                company_key = self._get_or_create_company(cursor, offer.get('company_name', 'Unknown'))
                contract_key = self._get_or_create_contract(cursor, offer.get('contract_type', 'Unknown'))
                date_key = self._get_or_create_date(cursor, datetime.now())
                
                # Générer offer_id (identifiant unique de l'offre source)
                offer_id = offer.get('offer_id') or offer.get('uid') or uid
                
                # Insérer l'offre dans fact_offers
                cursor.execute("""
                    INSERT INTO fact_offers (
                        offer_id, uid, title, location, salary, remote, description, source_url,
                        skills_count, competences_count, savoir_etre_count,
                        source_key, region_key, company_key, contract_key, date_key,
                        added_by, added_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    offer_id,
                    uid,
                    offer.get('title', ''),
                    offer.get('location', ''),
                    offer.get('salary', ''),
                    offer.get('remote', 'no'),
                    offer.get('description', ''),
                    offer.get('url', ''),
                    0,  # skills_count (sera mis à jour après)
                    0,  # competences_count
                    0,  # savoir_etre_count
                    source_key,
                    region_key,
                    company_key,
                    contract_key,
                    date_key,
                    'streamlit_app',
                    datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                ))
                
                offer_key = cursor.lastrowid
                
                # Insérer les compétences si présentes
                if offer.get('all_skills'):
                    skills_added = self._insert_skills(cursor, offer_key, offer['all_skills'])
                    
                    # Mettre à jour skills_count
                    cursor.execute("""
                        UPDATE fact_offers 
                        SET skills_count = ?, competences_count = ?
                        WHERE offer_key = ?
                    """, (skills_added, skills_added, offer_key))
                
                inserted_count += 1
            
            conn.commit()
            
            message = f"✅ {inserted_count} offres insérées dans la base de données"
            if duplicate_count > 0:
                message += f" • {duplicate_count} doublons ignorés"
            
            return inserted_count, duplicate_count, message
            
        except Exception as e:
            conn.rollback()
            return 0, 0, f"Erreur lors de l'insertion: {str(e)}"
        
        finally:
            conn.close()
    
 
    
    def check_duplicate_by_uid(self, uid: str) -> bool:
        """Vérifie si un UID existe déjà dans fact_offers"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("SELECT COUNT(*) FROM fact_offers WHERE uid = ?", (uid,))
            exists = cursor.fetchone()[0] > 0
            return exists
        finally:
            conn.close()
    
    def generate_uid(self, offer: Dict[str, Any]) -> str:
        """Génère un UID unique basé sur title + company + location"""
        key = f"{offer.get('title', '')}|{offer.get('company_name', '')}|{offer.get('location', '')}"
        return hashlib.md5(key.lower().encode()).hexdigest()
    
  
    
    def _get_or_create_source(self, cursor, source_name: str) -> int:
        """Récupère ou crée une source dans dim_source"""
        cursor.execute("SELECT source_key FROM dim_source WHERE source_name = ?", (source_name,))
        result = cursor.fetchone()
        
        if result:
            return result[0]
        
        cursor.execute("INSERT INTO dim_source (source_name) VALUES (?)", (source_name,))
        return cursor.lastrowid
    
    def _get_or_create_region(self, cursor, region_name: str) -> int:
        """Récupère ou crée une région dans dim_region"""
        cursor.execute("SELECT region_key FROM dim_region WHERE region_name = ?", (region_name,))
        result = cursor.fetchone()
        
        if result:
            return result[0]
        
        # Créer avec lat/lon par défaut (peut être enrichi après)
        cursor.execute("""
            INSERT INTO dim_region (region_name, latitude, longitude) 
            VALUES (?, ?, ?)
        """, (region_name, 0.0, 0.0))
        return cursor.lastrowid
    
    def _get_or_create_company(self, cursor, company_name: str) -> int:
        """Récupère ou crée une entreprise dans dim_company"""
        cursor.execute("SELECT company_key FROM dim_company WHERE company_name = ?", (company_name,))
        result = cursor.fetchone()
        
        if result:
            return result[0]
        
        cursor.execute("INSERT INTO dim_company (company_name) VALUES (?)", (company_name,))
        return cursor.lastrowid
    
    def _get_or_create_contract(self, cursor, contract_type: str) -> int:
        """Récupère ou crée un type de contrat dans dim_contract"""
        cursor.execute("SELECT contract_key FROM dim_contract WHERE contract_type = ?", (contract_type,))
        result = cursor.fetchone()
        
        if result:
            return result[0]
        
        cursor.execute("INSERT INTO dim_contract (contract_type) VALUES (?)", (contract_type,))
        return cursor.lastrowid
    
    def _get_or_create_date(self, cursor, date: datetime) -> int:
        """Récupère ou crée une dimension date dans dim_date"""
        date_str = date.strftime('%Y-%m-%d')
        
        cursor.execute("SELECT date_key FROM dim_date WHERE full_date = ?", (date_str,))
        result = cursor.fetchone()
        
        if result:
            return result[0]
        
        cursor.execute("""
            INSERT INTO dim_date (full_date, year, month, day, day_of_week) 
            VALUES (?, ?, ?, ?, ?)
        """, (
            date_str,
            date.year,
            date.month,
            date.day,
            date.strftime('%A')
        ))
        return cursor.lastrowid
    
    def _insert_skills(self, cursor, offer_key: int, skills_str: str) -> int:
        """
        Insère les compétences d'une offre dans dim_skill et fact_offer_skill
        
        Returns:
            Nombre de compétences insérées
        """
        if not skills_str:
            return 0
        
        # Parser les compétences (séparées par virgules)
        skills = [s.strip() for s in skills_str.split(',') if s.strip()]
        skills_added = 0
        
        for skill_name in skills:
            # Récupérer ou créer la compétence
            cursor.execute("SELECT skill_key FROM dim_skill WHERE skill_name = ?", (skill_name,))
            result = cursor.fetchone()
            
            if result:
                skill_key = result[0]
            else:
                # Créer la compétence
                cursor.execute("""
                    INSERT INTO dim_skill (skill_name, skill_type, skill_category) 
                    VALUES (?, ?, ?)
                """, (skill_name, 'competences', 'technique'))
                skill_key = cursor.lastrowid
            
            # Lier l'offre à la compétence (éviter doublons)
            cursor.execute("""
                INSERT OR IGNORE INTO fact_offer_skill (offer_key, skill_key) 
                VALUES (?, ?)
            """, (offer_key, skill_key))
            
            skills_added += 1
        
        return skills_added




def get_contribution_manager() -> ContributionManager:
    """Retourne une instance du ContributionManager"""
    return ContributionManager()


def insert_offers(offers: List[Dict[str, Any]]) -> Tuple[int, int, str]:
    """
    Fonction principale pour insérer des offres.
    
    Args:
        offers: Liste de dictionnaires avec les données
    
    Returns:
        (inserted_count, duplicate_count, message)
    """
    manager = get_contribution_manager()
    return manager.insert_offers(offers)


def check_duplicate_by_uid(uid: str) -> bool:
    """Vérifie si un UID existe déjà"""
    manager = get_contribution_manager()
    return manager.check_duplicate_by_uid(uid)


def generate_uid(offer: Dict[str, Any]) -> str:
    """Génère un UID unique pour une offre"""
    manager = get_contribution_manager()
    return manager.generate_uid(offer)