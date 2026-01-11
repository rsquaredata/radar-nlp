# Guide Développeur - RADAR

<div align="center">

**Version 1.0 | Documentation Technique**

*Architecture, APIs, et Contribution au Code*

[Accueil](../README.md) • [ Guide User](USER_GUIDE.md) • [ Docker](DOCKER_GUIDE.md) • [ Données](DATA_GUIDE.md)

---

</div>

## Table des matières

1. [Architecture](#architecture)
2. [Installation Dev](#installation-développeur)
3. [Structure du Code](#structure-du-code)
4. [Base de Données](#base-de-données)
5. [Pipeline ETL](#pipeline-etl)
6. [APIs & Intégrations](#apis--intégrations)
7. [NLP & Machine Learning](#nlp--machine-learning)
8. [Frontend Streamlit](#frontend-streamlit)
9. [Contribution](#contribution)
10. [Bonnes Pratiques](#bonnes-pratiques)

---

## Architecture

### Vue d'ensemble

```
┌─────────────────────────────────────────────────────────────┐
│                      ARCHITECTURE GLOBALE                   │
└─────────────────────────────────────────────────────────────┘

┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   Scraping  │───▶│     ETL     │───▶│  Database   │
│  (Collecte) │    │ (Transform) │    │   (SQLite)  │
└─────────────┘    └─────────────┘    └──────┬──────┘
                                              │
                                              ▼
                                       ┌──────────────┐
                                       │   Backend    │
                                       │ (Python/SQL) │
                                       └──────┬───────┘
                                              │
                                              ▼
                                       ┌──────────────┐
                                       │   Frontend   │
                                       │  (Streamlit) │
                                       └──────┬───────┘
                                              │
                                  ┌───────────┴───────────┐
                                  ▼                       ▼
                           ┌──────────┐          ┌──────────┐
                           │ NLP/ML   │          │    IA    │
                           │(scikit)  │          │(Mistral) │
                           └──────────┘          └──────────┘
```

### Stack Technique

| Layer | Technologies |
|-------|--------------|
| **Collecte** | BeautifulSoup, Requests, France Travail API |
| **ETL** | Pandas, SQLite, Custom Pipeline |
| **Backend** | Python 3.11+, SQLite3, Pandas |
| **Frontend** | Streamlit 1.32+, HTML/CSS/JS |
| **NLP** | scikit-learn, NLTK, spaCy |
| **ML** | K-Means, TF-IDF, Cosine Similarity |
| **IA** | Mistral AI API |
| **Viz** | Plotly, Folium, Matplotlib |
| **DevOps** | Docker, Docker Compose |

---

## Installation Développeur

### Prérequis

```bash
# Versions requises
Python >= 3.11
pip >= 23.0
git >= 2.40
```

### Setup Complet

```bash
# 1. Cloner le repo
git clone https://github.com/rsquaredata/radar-nlp.git
cd radar-nlp

# 2. Créer l'environnement virtuel
python -m venv venv

# Activer (Linux/Mac)
source venv/bin/activate

# Activer (Windows)
venv\Scripts\activate

# 3. Installer les dépendances
pip install -r requirements.txt

# 4. Configurer les variables d'environnement
cp .env.example .env
nano .env

# 5. Initialiser la base de données
python database/etl_pipeline.py --input data/raw/jobs.csv --recreate

# 6. Lancer en mode dev
streamlit run app/home.py --server.runOnSave true
```

### Configuration .env

```bash
# API Keys
FRANCE_TRAVAIL_CLIENT_ID=your_client_id
FRANCE_TRAVAIL_CLIENT_SECRET=your_client_secret
FRANCE_TRAVAIL_SCOPE=api_offresdemploiv2 o2dsoffre

MISTRAL_API_KEY=your_mistral_key

# Database
DATABASE_PATH=database/jobs.db

# App Config
STREAMLIT_THEME=dark
DEBUG_MODE=true
```

---

## Structure du Code

### Arborescence Détaillée

```
radar-nlp/
│
├── app/                          #  Frontend Streamlit
│   ├── home.py                   # Page d'accueil (entry point)
│   ├── pages/                    # Pages de l'application
│   │   ├── Explorer.py           #  Exploration des offres
│   │   ├── Geographie.py         #  Cartographie interactive
│   │   ├── Analytics.py          #  Statistiques avancées
│   │   ├── Intelligence.py       #  NLP & Clustering
│   │   ├── Assistant.py          #  Assistant IA Mistral
│   │   └── Contribuer.py         #  Ajout dynamique d'offres
│   │
│   └── utils/                    # 🛠️ Utilitaires
│       ├── components.py         # Composants UI réutilisables
│       ├── db.py                 # Gestion BDD (CRUD)
│       ├── nlp_utils.py          # Fonctions NLP
│       ├── clustering.py         # K-Means & clustering
│       ├── tfidf_analysis.py     # Analyse TF-IDF
│       ├── viz.py                # Graphiques Plotly
│       ├── filters.py            # Filtres de données
│       └── config.py             # Configuration globale
│
├── database/                     #  Base de données
│   ├── schema.sql                # DDL (CREATE TABLE)
│   ├── etl_pipeline.py           # Pipeline ETL complet
│   ├── db_insert.py              # Fonctions d'insertion
│   └── jobs.db                   # Base SQLite (2500+ offres)
│
├── scraping/                     #  Collecte de données
│   ├── config_metiers.py         # Configuration centralisée métiers
│   ├── france_travail_api.py     # Client API France Travail
│   ├── run_france_travail.py     # Script d'exécution FT
│   ├── hellowork_html_improved.py# Scraper HelloWork
│   ├── run_hellowork.py          # Script d'exécution HW
│   └── http_utils.py             # Utilitaires HTTP robustes
│   └── configs_metiers.py        # liste des metiers à scrapper 
├── geographic_enrichment/        #  Géolocalisation
│   ├── enrich_geography.py       # Enrichissement géographique
│   └── regions_france.json       # Référentiel régions FR
│
├── skills_extraction/            #  Extraction compétences
│   ├── skills_extractor.py       # Extracteur de compétences
│   ├── apply_skills_extraction.py# Application sur datasets
│   └── skills_dict.json          # Dictionnaire compétences
│
├── data/                         #  Données
│   ├── raw/                      # Données brutes (CSV)
│   ├── processed/                # Données traitées
│   └── exports/                  # Exports utilisateurs
│
├── docs/                         # Documentation
│   ├── USER_GUIDE.md             # Guide utilisateur
│   ├── DEVELOPER_GUIDE.md        # Guide développeur
│   ├── DOCKER_GUIDE.md           # Guide Docker
│   └── DATA_GUIDE.md             # Guide données
│
├── Dockerfile                    # Image Docker
├── docker-compose.yml            # Orchestration
├── requirements.txt              # Dépendances Python
├── .env.example                  # Template variables d'env
├── .gitignore
└── README.md
```

### Conventions de nommage

```python
# Fichiers
snake_case.py          # Modules Python
PascalCase.py          # Pages Streamlit

# Classes
class DatabaseManager:  # PascalCase

# Fonctions
def load_offers():      # snake_case

# Variables
offer_count = 42        # snake_case
API_KEY = "xxx"         # UPPER_CASE pour constantes

# Constantes
DATABASE_PATH = Path("database/jobs.db")
MAX_RESULTS = 1000
```

---

## Base de Données

### Schéma Relationnel (Star Schema)

```sql
-- ============================================================================
-- STAR SCHEMA OPTIMISÉ POUR L'ANALYSE
-- ============================================================================

-- Dimension : Sources
CREATE TABLE dim_source (
    source_key INTEGER PRIMARY KEY AUTOINCREMENT,
    source_name TEXT NOT NULL UNIQUE,
    source_type TEXT  -- 'api', 'scraping', 'manual'
);

-- Dimension : Régions
CREATE TABLE dim_region (
    region_key INTEGER PRIMARY KEY AUTOINCREMENT,
    region_name TEXT NOT NULL UNIQUE,
    latitude REAL,
    longitude REAL
);

-- Dimension : Entreprises
CREATE TABLE dim_company (
    company_key INTEGER PRIMARY KEY AUTOINCREMENT,
    company_name TEXT NOT NULL
);

-- Dimension : Contrats
CREATE TABLE dim_contract (
    contract_key INTEGER PRIMARY KEY AUTOINCREMENT,
    contract_type TEXT NOT NULL UNIQUE
);

-- Dimension : Compétences
CREATE TABLE dim_skill (
    skill_key INTEGER PRIMARY KEY AUTOINCREMENT,
    skill_name TEXT NOT NULL UNIQUE,
    skill_type TEXT CHECK(skill_type IN ('competences', 'savoir_etre')),
    skill_category TEXT
);

-- Fait : Offres (TABLE CENTRALE)
CREATE TABLE fact_offers (
    offer_key INTEGER PRIMARY KEY AUTOINCREMENT,
    uid TEXT NOT NULL UNIQUE,  -- Hash MD5 pour déduplication
    offer_id TEXT NOT NULL,
    
    -- Foreign keys
    source_key INTEGER,
    region_key INTEGER,
    company_key INTEGER,
    contract_key INTEGER,
    
    -- Attributs offre
    title TEXT NOT NULL,
    source_url TEXT,           -- URL pour postuler
    location TEXT,
    salary TEXT,
    remote TEXT,
    published_date TEXT,
    description TEXT,
    
    -- Compétences (JSON)
    competences TEXT,          -- JSON array
    savoir_etre TEXT,          -- JSON array
    
    -- Métriques
    skills_count INTEGER DEFAULT 0,
    competences_count INTEGER DEFAULT 0,
    savoir_etre_count INTEGER DEFAULT 0,
    
    -- Géolocalisation
    region_lat REAL,
    region_lon REAL,
    
    -- Traçabilité
    added_by TEXT DEFAULT 'import',
    added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (source_key) REFERENCES dim_source(source_key),
    FOREIGN KEY (region_key) REFERENCES dim_region(region_key),
    FOREIGN KEY (company_key) REFERENCES dim_company(company_key),
    FOREIGN KEY (contract_key) REFERENCES dim_contract(contract_key)
);

-- Table associative Many-to-Many
CREATE TABLE fact_offer_skill (
    offer_key INTEGER NOT NULL,
    skill_key INTEGER NOT NULL,
    PRIMARY KEY (offer_key, skill_key),
    FOREIGN KEY (offer_key) REFERENCES fact_offers(offer_key) ON DELETE CASCADE,
    FOREIGN KEY (skill_key) REFERENCES dim_skill(skill_key) ON DELETE CASCADE
);
```

### Index de Performance

```sql
-- Index unique sur UID (évite doublons)
CREATE UNIQUE INDEX idx_fact_offers_uid_unique 
ON fact_offers(uid);

-- Index sur clés étrangères
CREATE INDEX idx_fact_offers_source ON fact_offers(source_key);
CREATE INDEX idx_fact_offers_region ON fact_offers(region_key);
CREATE INDEX idx_fact_offers_company ON fact_offers(company_key);
CREATE INDEX idx_fact_offers_contract ON fact_offers(contract_key);

-- Index sur colonnes de recherche
CREATE INDEX idx_fact_offers_title ON fact_offers(title);
CREATE INDEX idx_fact_offers_location ON fact_offers(location);
CREATE INDEX idx_fact_offers_published ON fact_offers(published_date);

-- Index sur table associative
CREATE INDEX idx_fact_offer_skill_offer ON fact_offer_skill(offer_key);
CREATE INDEX idx_fact_offer_skill_skill ON fact_offer_skill(skill_key);
```

### Vues Matérialisées

```sql
-- Vue : Offres complètes avec dimensions
CREATE VIEW v_offers_complete AS
SELECT 
    fo.offer_key,
    fo.uid,
    fo.title,
    fo.source_url,
    fo.description,
    fo.location,
    fo.salary,
    fo.remote,
    fo.published_date,
    fo.competences,
    fo.savoir_etre,
    fo.skills_count,
    dr.region_name,
    dr.latitude as region_lat,
    dr.longitude as region_lon,
    dc.company_name,
    dct.contract_type,
    ds.source_name,
    fo.added_at
FROM fact_offers fo
LEFT JOIN dim_region dr ON fo.region_key = dr.region_key
LEFT JOIN dim_company dc ON fo.company_key = dc.company_key
LEFT JOIN dim_contract dct ON fo.contract_key = dct.contract_key
LEFT JOIN dim_source ds ON fo.source_key = ds.source_key;

-- Vue : Top compétences avec statistiques
CREATE VIEW v_top_skills AS
SELECT 
    ds.skill_name,
    ds.skill_type,
    COUNT(DISTINCT fos.offer_key) AS offer_count,
    ROUND(COUNT(DISTINCT fos.offer_key) * 100.0 / 
          (SELECT COUNT(*) FROM fact_offers), 2) AS percentage
FROM dim_skill ds
JOIN fact_offer_skill fos ON ds.skill_key = fos.skill_key
GROUP BY ds.skill_key
ORDER BY offer_count DESC
LIMIT 50;

-- Vue : Statistiques par région
CREATE VIEW v_stats_by_region AS
SELECT 
    dr.region_name,
    COUNT(fo.offer_key) AS total_offers,
    AVG(fo.skills_count) AS avg_skills_per_offer,
    COUNT(DISTINCT fo.company_key) AS unique_companies
FROM fact_offers fo
JOIN dim_region dr ON fo.region_key = dr.region_key
GROUP BY dr.region_key
ORDER BY total_offers DESC;
```


### API Python (utils/db.py)

```python
import sqlite3
import pandas as pd
import json
from pathlib import Path
from typing import List, Dict, Optional

class DatabaseManager:
    """Gestionnaire de connexion et requêtes BDD"""
    
    def __init__(self, db_path: str = "database/jobs.db"):
        self.db_path = Path(db_path)
        self.conn = None
    
    def get_connection(self) -> sqlite3.Connection:
        """Connexion SQLite avec row factory"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Accès par nom de colonne
        return conn
    
    def get_offers_with_skills(self) -> pd.DataFrame:
        """Récupère toutes les offres avec compétences"""
        query = """
            SELECT 
                fo.offer_key,
                fo.uid,
                fo.title,
                fo.source_url,
                fo.description,
                fo.location,
                fo.salary,
                fo.remote,
                fo.published_date,
                fo.competences,
                fo.savoir_etre,
                fo.skills_count,
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
            ORDER BY fo.added_at DESC
        """
        
        conn = self.get_connection()
        df = pd.read_sql_query(query, conn)
        conn.close()
        
        # Parser les JSON strings
        if 'competences' in df.columns:
            df['competences'] = df['competences'].apply(
                lambda x: json.loads(x) if x else []
            )
        if 'savoir_etre' in df.columns:
            df['savoir_etre'] = df['savoir_etre'].apply(
                lambda x: json.loads(x) if x else []
            )
        
        return df
    
    def search_offers(self, 
                     search_text: Optional[str] = None,
                     regions: Optional[List[str]] = None,
                     contracts: Optional[List[str]] = None,
                     skills: Optional[List[str]] = None) -> pd.DataFrame:
        """Recherche avec filtres multiples"""
        
        query = "SELECT * FROM v_offers_complete WHERE 1=1"
        params = []
        
        # Filtre texte
        if search_text:
            query += " AND (title LIKE ? OR description LIKE ?)"
            pattern = f"%{search_text}%"
            params.extend([pattern, pattern])
        
        # Filtre régions
        if regions and len(regions) > 0:
            placeholders = ','.join(['?' for _ in regions])
            query += f" AND region_name IN ({placeholders})"
            params.extend(regions)
        
        # Filtre contrats
        if contracts and len(contracts) > 0:
            placeholders = ','.join(['?' for _ in contracts])
            query += f" AND contract_type IN ({placeholders})"
            params.extend(contracts)
        
        # Filtre compétences (sur JSON)
        if skills and len(skills) > 0:
            for skill in skills:
                query += f" AND (competences LIKE ? OR savoir_etre LIKE ?)"
                params.extend([f'%{skill}%', f'%{skill}%'])
        
        conn = self.get_connection()
        df = pd.read_sql_query(query, conn, params=params)
        conn.close()
        
        return df
    
    def insert_offer(self, offer: Dict) -> tuple:
        """Insert une offre (depuis Contribuer.py)"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            # Vérifier doublon
            cursor.execute(
                "SELECT COUNT(*) FROM fact_offers WHERE uid = ?",
                (offer['uid'],)
            )
            if cursor.fetchone()[0] > 0:
                return False, "Offre déjà existante"
            
            # Insert dimensions si nécessaires
            source_key = self._get_or_create_dimension(
                conn, 'dim_source', 'source_name', offer['source']
            )
            region_key = self._get_or_create_dimension(
                conn, 'dim_region', 'region_name', offer.get('region')
            )
            company_key = self._get_or_create_dimension(
                conn, 'dim_company', 'company_name', offer['company']
            )
            contract_key = self._get_or_create_dimension(
                conn, 'dim_contract', 'contract_type', offer['contract_type']
            )
            
            # Insert offre
            cursor.execute("""
                INSERT INTO fact_offers (
                    uid, offer_id, source_key, region_key, company_key, contract_key,
                    title, source_url, location, salary, remote, published_date, description,
                    competences, savoir_etre, skills_count, added_by
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                offer['uid'], offer['offer_id'], source_key, region_key,
                company_key, contract_key, offer['title'], offer.get('source_url'),
                offer['location'], offer.get('salary'), offer.get('remote'),
                offer.get('published_date'), offer['description'],
                json.dumps(offer.get('competences', [])),
                json.dumps(offer.get('savoir_etre', [])),
                offer.get('skills_count', 0), offer.get('added_by', 'manual')
            ))
            
            conn.commit()
            return True, "Offre insérée avec succès"
        
        except Exception as e:
            conn.rollback()
            return False, f"Erreur : {str(e)}"
        finally:
            conn.close()
    
    def _get_or_create_dimension(self, conn, table: str, column: str, value: str) -> int:
        """Récupère ou crée une dimension"""
        if not value:
            return None
        
        cursor = conn.cursor()
        cursor.execute(f"SELECT {table.replace('dim_', '')}_key FROM {table} WHERE {column} = ?", (value,))
        row = cursor.fetchone()
        
        if row:
            return row[0]
        else:
            cursor.execute(f"INSERT INTO {table} ({column}) VALUES (?)", (value,))
            return cursor.lastrowid


# ============================================================================
# FONCTIONS UTILITAIRES
# ============================================================================

@st.cache_data(ttl=300)  # Cache 5 minutes
def load_offers_with_skills() -> pd.DataFrame:
    """Fonction cachée pour Streamlit"""
    db = DatabaseManager()
    return db.get_offers_with_skills()

def get_unique_values(df: pd.DataFrame, column: str) -> List[str]:
    """Récupère les valeurs uniques triées"""
    return sorted(df[column].dropna().unique().tolist())
```

---

## Pipeline ETL

### Architecture ETL

```python
# database/etl_pipeline.py

import argparse
import pandas as pd
import hashlib
import json
from pathlib import Path
from typing import Dict, List
import sqlite3

class ETLPipeline:
    """
    Pipeline Extract-Transform-Load
    
    Gère l'import de données depuis CSV vers la base SQLite
    avec enrichissement géographique et extraction de compétences.
    """
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.conn = None
        self.stats = {
            'offers_extracted': 0,
            'offers_transformed': 0,
            'offers_inserted': 0,
            'offers_duplicates': 0,
            'skills_inserted': 0
        }
    
    def run(self, csv_path: str, recreate_db: bool = False):
        """Exécute le pipeline complet"""
        
        print("=" * 80)
        print("PIPELINE ETL - DÉMARRAGE")
        print("=" * 80)
        print()
        
        # 1. EXTRACT
        print("PHASE 1 : EXTRACTION")
        df = self.extract(csv_path)
        
        # 2. TRANSFORM
        print("\n PHASE 2 : TRANSFORMATION")
        df = self.transform(df)
        
        # 3. LOAD
        print("\n PHASE 3 : CHARGEMENT")
        if recreate_db:
            self.create_database()
        self.load(df)
        
        # 4. STATISTIQUES
        print("\n" + "=" * 80)
        print("STATISTIQUES FINALES")
        print("=" * 80)
        for key, value in self.stats.items():
            print(f"  • {key:30} : {value:,}")
        print()
    
    def extract(self, csv_path: str) -> pd.DataFrame:
        """1. EXTRACT : Charger les données brutes"""
        
        df = pd.read_csv(csv_path)
        self.stats['offers_extracted'] = len(df)
        
        print(f" {len(df):,} lignes extraites de {csv_path}")
        
        return df
    
    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        """2. TRANSFORM : Nettoyer et enrichir"""
        
        # Nettoyage de base
        df = df.dropna(subset=['title'])
        df['title'] = df['title'].str.strip()
        df['company'] = df['company'].fillna('Entreprise non spécifiée')
        
        # Génération UID unique (pour déduplication)
        df['uid'] = df.apply(
            lambda row: hashlib.md5(
                f"{row.get('offer_id', '')}{row.get('source', '')}{row.get('title', '')}".encode()
            ).hexdigest(),
            axis=1
        )
        
        # Enrichissement géographique (si colonnes présentes)
        if 'region' not in df.columns and 'location' in df.columns:
            from geographic_enrichment.enrich_geography import GeographicEnricher
            enricher = GeographicEnricher()
            
            for idx, row in df.iterrows():
                region, lat, lon = enricher.extract_region(row['location'])
                df.at[idx, 'region'] = region
                df.at[idx, 'region_lat'] = lat
                df.at[idx, 'region_lon'] = lon
        
        # Extraction compétences (si description présente)
        if 'description' in df.columns:
            if 'competences' not in df.columns:
                from skills_extraction.skills_extractor import SkillsExtractor
                extractor = SkillsExtractor()
                
                for idx, row in df.iterrows():
                    if pd.notna(row['description']):
                        skills_by_type = extractor.extract_by_type(row['description'])
                        df.at[idx, 'competences'] = json.dumps(skills_by_type['competences'])
                        df.at[idx, 'savoir_etre'] = json.dumps(skills_by_type['savoir_etre'])
                        df.at[idx, 'skills_count'] = len(skills_by_type['competences']) + len(skills_by_type['savoir_etre'])
        
        self.stats['offers_transformed'] = len(df)
        print(f" {len(df):,} offres transformées")
        
        return df
    
    def create_database(self):
        """Crée la base de données"""
        
        schema_path = Path(__file__).parent / "schema.sql"
        
        if schema_path.exists():
            with open(schema_path, 'r', encoding='utf-8') as f:
                schema_sql = f.read()
            
            conn = sqlite3.connect(self.db_path)
            conn.executescript(schema_sql)
            conn.close()
            
            print(" Base de données créée")
        else:
            print(" Fichier schema.sql introuvable")
    
    def load(self, df: pd.DataFrame):
        """3. LOAD : Insertion dans la BDD"""
        
        conn = sqlite3.connect(self.db_path)
        
        try:
            # Charger dimensions
            self.load_dimensions(conn, df)
            
            # Charger faits
            self.load_offers(conn, df)
            
            conn.commit()
            
        except Exception as e:
            conn.rollback()
            print(f" Erreur : {e}")
        finally:
            conn.close()
        
        print(f" {self.stats['offers_inserted']:,} offres insérées")
        print(f" {self.stats['offers_duplicates']:,} doublons ignorés")


# ============================================================================
# CLI
# ============================================================================

def main():
    parser = argparse.ArgumentParser(description="Pipeline ETL RADAR")
    parser.add_argument('-i', '--input', required=True, help="Fichier CSV d'entrée")
    parser.add_argument('--db', default='database/jobs.db', help="Chemin base de données")
    parser.add_argument('--recreate', action='store_true', help="Recréer la BDD")
    
    args = parser.parse_args()
    
    etl = ETLPipeline(db_path=args.db)
    etl.run(csv_path=args.input, recreate_db=args.recreate)


if __name__ == "__main__":
    main()
```

---

## APIs & Intégrations

### France Travail API

```python
# scraping/france_travail_api.py

import os
import requests
from typing import List, Dict, Optional
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

class FranceTravailAPI:
    """
    Client API France Travail (ex-Pôle Emploi)
    
    Documentation : https://francetravail.io/data/api/offres-emploi
    """
    
    TOKEN_URL = "https://entreprise.francetravail.fr/connexion/oauth2/access_token?realm=/partenaire"
    API_BASE = "https://api.francetravail.io/partenaire/offresdemploi/v2"
    
    def __init__(self):
        self.client_id = os.getenv("FRANCE_TRAVAIL_CLIENT_ID")
        self.client_secret = os.getenv("FRANCE_TRAVAIL_CLIENT_SECRET")
        self.scope = os.getenv("FRANCE_TRAVAIL_SCOPE", "api_offresdemploiv2 o2dsoffre")
        self.access_token = None
        
        if not self.client_id or not self.client_secret:
            raise ValueError("FRANCE_TRAVAIL_CLIENT_ID et CLIENT_SECRET requis dans .env")
    
    def authenticate(self):
        """Authentification OAuth2 Client Credentials"""
        
        data = {
            'grant_type': 'client_credentials',
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'scope': self.scope
        }
        
        response = requests.post(
            self.TOKEN_URL,
            data=data,
            headers={'Content-Type': 'application/x-www-form-urlencoded'}
        )
        response.raise_for_status()
        
        self.access_token = response.json()['access_token']
        print(" Authentification réussie")
    
    def search_offers(self, 
                     keywords: Optional[str] = None,
                     location: Optional[str] = None,
                     contract_type: Optional[str] = None,
                     max_results: int = 150) -> List[Dict]:
        """Recherche d'offres d'emploi"""
        
        if not self.access_token:
            self.authenticate()
        
        headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json'
        }
        
        params = {
            'range': f'0-{max_results-1}'
        }
        
        if keywords:
            params['motsCles'] = keywords
        if location:
            params['commune'] = location
        if contract_type:
            params['typeContrat'] = contract_type
        
        response = requests.get(
            f"{self.API_BASE}/offres/search",
            headers=headers,
            params=params
        )
        
        if response.status_code == 401:
            self.authenticate()
            headers['Authorization'] = f'Bearer {self.access_token}'
            response = requests.get(
                f"{self.API_BASE}/offres/search",
                headers=headers,
                params=params
            )
        
        response.raise_for_status()
        
        if response.status_code == 204:
            return []
        
        return response.json().get('resultats', [])


# Utilisation
if __name__ == "__main__":
    api = FranceTravailAPI()
    
    offers = api.search_offers(
        keywords="Data Scientist",
        location="Paris",
        max_results=50
    )
    
    print(f"{len(offers)} offres trouvées")
```


### HelloWork Scraper

```python
# scraping/hellowork_html_improved.py

from bs4 import BeautifulSoup
import requests
import time
from typing import List, Dict
from urllib.parse import urljoin

class HelloWorkScraper:
    """Scraper HelloWork"""
    
    BASE_URL = "https://www.hellowork.com"
    
    HEADERS = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    def scrape_search_page(self, 
                          keywords: str,
                          location: str = None,
                          page: int = 1,
                          sleep_seconds: float = 0.5) -> List[Dict]:
        """Scrape une page de résultats de recherche"""
        
        url = f"{self.BASE_URL}/fr-fr/emplois/recherche.html"
        params = {
            'k': keywords,
            'p': page
        }
        if location:
            params['l'] = location
        
        response = requests.get(url, params=params, headers=self.HEADERS)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        offers = []
        for card in soup.find_all('article', class_='job-card'):
            try:
                offer = {
                    'source': 'hellowork.com',
                    'title': card.find('h2').text.strip(),
                    'company': card.find('p', class_='company-name').text.strip() if card.find('p', class_='company-name') else 'Non spécifiée',
                    'location': card.find('span', class_='location').text.strip() if card.find('span', class_='location') else '',
                    'contract_type': self.extract_contract_type(card),
                    'source_url': urljoin(self.BASE_URL, card.find('a')['href']),
                    'offer_id': self.extract_offer_id(card.find('a')['href'])
                }
                offers.append(offer)
            except Exception as e:
                print(f"Erreur parsing carte : {e}")
                continue
        
        time.sleep(sleep_seconds)
        
        return offers


# Utilisation
if __name__ == "__main__":
    scraper = HelloWorkScraper()
    
    offers = scraper.scrape_search_page(
        keywords="Data Scientist",
        location="Paris",
        page=1
    )
    
    print(f"{len(offers)} offres trouvées")
```

### Mistral AI Integration

```python
# app/utils/mistral_client.py

import os
from mistralai.client import MistralClient
from mistralai.models.chat_completion import ChatMessage
from typing import List, Dict, Optional

class MistralAssistant:
    """Assistant IA avec Mistral AI"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("MISTRAL_API_KEY")
        if not self.api_key:
            raise ValueError("MISTRAL_API_KEY requis")
        
        self.client = MistralClient(api_key=self.api_key)
        self.model = "mistral-large-latest"
    
    def chat(self, 
             user_message: str,
             system_prompt: Optional[str] = None,
             context: Optional[Dict] = None,
             conversation_history: Optional[List[ChatMessage]] = None) -> str:
        """Génère une réponse de l'assistant"""
        
        messages = []
        
        # System prompt
        if system_prompt:
            messages.append(
                ChatMessage(role="system", content=system_prompt)
            )
        else:
            messages.append(
                ChatMessage(
                    role="system",
                    content=self.get_default_system_prompt()
                )
            )
        
        # Context
        if context:
            context_str = self.format_context(context)
            messages.append(
                ChatMessage(role="system", content=context_str)
            )
        
        # User message
        messages.append(
            ChatMessage(role="user", content=user_message)
        )
        
        # API call
        response = self.client.chat(
            model=self.model,
            messages=messages,
            temperature=0.7,
            max_tokens=1000
        )
        
        return response.choices[0].message.content
    
    def get_default_system_prompt(self) -> str:
        """Prompt système par défaut"""
        return """
Tu es un assistant expert en analyse du marché de l'emploi français,
spécialisé dans les métiers de la Data et de l'IA.

Tu as accès à une base de données de 2500+ offres d'emploi actualisées.

Ta mission est d'aider les utilisateurs à :
- Comprendre les tendances du marché
- Identifier les compétences les plus demandées
- Trouver les meilleures opportunités selon leur profil
- Se préparer aux entretiens

Réponds de manière concise, factuelle, et bienveillante.
"""


# Utilisation
if __name__ == "__main__":
    assistant = MistralAssistant()
    
    context = {
        'total_offers': 2520,
        'top_skills': ['Python', 'SQL', 'Docker', 'Kubernetes', 'AWS']
    }
    
    response = assistant.chat(
        user_message="Quelles sont les tendances actuelles du marché Data ?",
        context=context
    )
    
    print(response)
```

---

## NLP & Machine Learning

### Extraction de Compétences

```python
# skills_extraction/skills_extractor.py

import json
import re
from typing import Dict, List
from pathlib import Path

class SkillsExtractor:
    """Extracteur de compétences techniques et savoir-être"""
    
    def __init__(self, skills_dict_path: str = "skills_extraction/skills_dict.json"):
        with open(skills_dict_path, 'r', encoding='utf-8') as f:
            self.skills_data = json.load(f)
        
        self.tech_skills = self.extract_all_skills('competences')
        self.soft_skills = self.extract_all_skills('savoir_etre')
    
    def extract_all_skills(self, skill_type: str) -> List[str]:
        """Extrait toutes les compétences d'un type"""
        skills = []
        if skill_type in self.skills_data:
            for category, data in self.skills_data[skill_type].items():
                if isinstance(data, dict) and 'skills' in data:
                    skills.extend(data['skills'])
                elif isinstance(data, list):
                    skills.extend(data)
        return skills
    
    def extract_from_text(self, text: str) -> Dict[str, List[str]]:
        """
        Extrait les compétences d'un texte
        
        Args:
            text: Description de l'offre
        
        Returns:
            Dict {'competences': [...], 'savoir_etre': [...]}
        """
        text_lower = text.lower()
        
        found_tech = []
        for skill in self.tech_skills:
            # Recherche avec word boundaries
            pattern = r'\b' + re.escape(skill.lower()) + r'\b'
            if re.search(pattern, text_lower):
                found_tech.append(skill)
        
        found_soft = []
        for skill in self.soft_skills:
            pattern = r'\b' + re.escape(skill.lower()) + r'\b'
            if re.search(pattern, text_lower):
                found_soft.append(skill)
        
        return {
            'competences': found_tech,
            'savoir_etre': found_soft
        }
    
    def extract_by_type(self, text: str) -> Dict[str, List[str]]:
        """Alias pour extract_from_text"""
        return self.extract_from_text(text)


# Utilisation
if __name__ == "__main__":
    extractor = SkillsExtractor()
    
    description = """
    Nous recherchons un Data Scientist avec 3 ans d'expérience.
    Compétences requises : Python, SQL, Machine Learning, TensorFlow.
    Qualités : autonomie, esprit d'équipe, rigueur.
    """
    
    skills = extractor.extract_from_text(description)
    
    print("Compétences techniques :", skills['competences'])
    print("Savoir-être :", skills['savoir_etre'])
```

### Analyse NLP Avancée

```python
# app/utils/nlp_utils.py

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
from sklearn.manifold import TSNE
from sklearn.metrics.pairwise import cosine_similarity
import pandas as pd
import numpy as np
from typing import List, Tuple

class NLPAnalyzer:
    """Analyseur NLP pour les offres d'emploi"""
    
    def __init__(self, stopwords: List[str] = None):
        self.stopwords = stopwords or self.get_french_stopwords()
        self.tfidf_vectorizer = None
        self.tfidf_matrix = None
    
    @staticmethod
    def get_french_stopwords() -> List[str]:
        """Stopwords français + géographiques"""
        return [
            'le', 'la', 'les', 'un', 'une', 'des', 'et', 'ou',
            'pour', 'dans', 'avec', 'sur', 'par', 'plus',
            'france', 'paris', 'lyon', 'région'
        ]
    
    def fit_tfidf(self, documents: List[str], max_features: int = 100):
        """Calcule la matrice TF-IDF"""
        
        self.tfidf_vectorizer = TfidfVectorizer(
            max_features=max_features,
            stop_words=self.stopwords,
            ngram_range=(1, 2),
            min_df=2,
            max_df=0.8
        )
        
        self.tfidf_matrix = self.tfidf_vectorizer.fit_transform(documents)
        
        return self.tfidf_matrix
    
    def get_top_terms(self, n_terms: int = 20) -> List[Tuple[str, float]]:
        """Récupère les N termes les plus importants"""
        
        feature_names = self.tfidf_vectorizer.get_feature_names_out()
        tfidf_scores = self.tfidf_matrix.toarray().mean(axis=0)
        
        top_indices = tfidf_scores.argsort()[-n_terms:][::-1]
        top_terms = [(feature_names[i], tfidf_scores[i]) for i in top_indices]
        
        return top_terms
    
    def clustering_kmeans(self, n_clusters: int = 6) -> Tuple[KMeans, np.ndarray]:
        """Clustering K-Means sur la matrice TF-IDF"""
        
        if self.tfidf_matrix is None:
            raise ValueError("TF-IDF not fitted. Call fit_tfidf() first.")
        
        kmeans = KMeans(
            n_clusters=n_clusters,
            random_state=42,
            n_init=10
        )
        
        clusters = kmeans.fit_predict(self.tfidf_matrix)
        
        return kmeans, clusters
    
    def visualize_tsne(self, perplexity: int = 30) -> np.ndarray:
        """Réduit la dimensionnalité avec t-SNE pour visualisation 2D"""
        
        if self.tfidf_matrix is None:
            raise ValueError("TF-IDF not fitted")
        
        tsne = TSNE(
            n_components=2,
            random_state=42,
            perplexity=min(perplexity, self.tfidf_matrix.shape[0] - 1)
        )
        
        coords_2d = tsne.fit_transform(self.tfidf_matrix.toarray())
        
        return coords_2d


# Utilisation dans Intelligence.py
if __name__ == "__main__":
    from app.utils.db import load_offers_with_skills
    df = load_offers_with_skills()
    
    # Préparer les textes
    documents = (df['title'] + ' ' + df['description']).tolist()
    
    # Analyser
    nlp = NLPAnalyzer()
    nlp.fit_tfidf(documents)
    
    # Top termes
    top_terms = nlp.get_top_terms(n_terms=20)
    print("Top 20 termes:")
    for term, score in top_terms:
        print(f"  {term:20} : {score:.4f}")
    
    # Clustering
    kmeans, clusters = nlp.clustering_kmeans(n_clusters=6)
    print(f"\n{len(set(clusters))} clusters identifiés")
```

---

## Frontend Streamlit

### Architecture des Pages

```python
# app/home.py

import streamlit as st
from pathlib import Path
import sys

# Configuration
st.set_page_config(
    page_title="RADAR - Analyse Marché Emploi",
    page_icon="",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Import utilitaires
sys.path.insert(0, str(Path(__file__).parent))
from utils.components import inject_premium_css, premium_navbar

# CSS Premium
inject_premium_css()

# Navbar
premium_navbar(active_page="Accueil")

# Contenu de la page
st.title(" RADAR - Analyse du Marché de l'Emploi")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Offres Analysées", "2,520", "+150")

with col2:
    st.metric("Compétences", "350+", "+25")

with col3:
    st.metric("Régions", "13", "")
```

### Composants Réutilisables

```python
# app/utils/components.py

import streamlit as st
from typing import Optional

def inject_premium_css():
    """Injecte le CSS premium dans l'application"""
    
    st.markdown("""
    <style>
        :root {
            --primary-color: #58a6ff;
            --background-dark: #0d1117;
        }
        
        .main {
            background: linear-gradient(135deg, var(--background-dark) 0%, #161b22 100%);
        }
        
        .metric-card {
            background: linear-gradient(135deg, rgba(88, 166, 255, 0.1) 0%, rgba(31, 111, 235, 0.1) 100%);
            border: 2px solid var(--primary-color);
            border-radius: 16px;
            padding: 1.5rem;
            transition: all 0.3s;
        }
        
        .metric-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 10px 40px rgba(88, 166, 255, 0.3);
        }
    </style>
    """, unsafe_allow_html=True)


def premium_navbar(active_page: str):
    """Barre de navigation premium"""
    
    pages = {
        " Accueil": "home.py",
        " Explorer": "pages/Explorer.py",
        " Géographie": "pages/Geographie.py",
        " Analytics": "pages/Analytics.py",
        " Intelligence": "pages/Intelligence.py",
        " Assistant": "pages/Assistant.py",
        " Contribuer": "pages/Contribuer.py"
    }
    
    st.sidebar.markdown("##  Navigation")
    
    for page_name, page_path in pages.items():
        if active_page in page_name:
            st.sidebar.success(f"**{page_name}**")
        else:
            if st.sidebar.button(page_name, key=page_name):
                st.switch_page(page_path)


def create_filter_sidebar(df: pd.DataFrame) -> dict:
    """Crée une sidebar de filtres standard"""
    
    st.sidebar.markdown("## 🔧 Filtres")
    
    filters = {}
    
    # Recherche textuelle
    filters['search'] = st.sidebar.text_input(
        " Recherche",
        placeholder="Mots-clés..."
    )
    
    # Régions
    regions = ['Toutes les régions'] + sorted(df['region_name'].dropna().unique().tolist())
    filters['regions'] = st.sidebar.multiselect(
        "🗺️ Régions",
        regions,
        default=['Toutes les régions']
    )
    
    # Contrats
    contracts = ['Tous les contrats'] + sorted(df['contract_type'].dropna().unique().tolist())
    filters['contracts'] = st.sidebar.multiselect(
        " Types de contrat",
        contracts,
        default=['Tous les contrats']
    )
    
    return filters
```

---

## Contribution

### Workflow de Contribution

```bash
# 1. Fork le projet sur GitHub

# 2. Cloner votre fork
git clone https://github.com/rsquaredata/radar-nlp.git
cd radar-nlp

# 3. Créer une branche pour votre feature
git checkout -b feature/ma-super-feature

# 4. Faire vos modifications
# ... code ...

# 5. Commit avec un message clair
git add .
git commit -m "feat: Ajout de la fonctionnalité X"

# 6. Push vers votre fork
git push origin feature/ma-super-feature

# 7. Créer une Pull Request sur GitHub
```

### Convention de Commits

```bash
# Format
<type>(<scope>): <subject>

# Types
feat:     # Nouvelle fonctionnalité
fix:      # Correction de bug
docs:     # Documentation
style:    # Formatting
refactor: # Refactoring
chore:    # Maintenance

# Exemples
feat(scraping): Ajout scraper LinkedIn
fix(db): Correction requête SQL doublons
docs(readme): Mise à jour installation
refactor(nlp): Optimisation TF-IDF
```

### Code Review Checklist

Avant de soumettre une PR, vérifier :

- [ ] Le code suit les conventions PEP8
- [ ] Les docstrings sont présentes
- [ ] Les fonctions ont des type hints
- [ ] Le code est commenté quand nécessaire
- [ ] Pas de code commenté (dead code)
- [ ] Pas de print() de debug
- [ ] Les variables ont des noms explicites
- [ ] Le code est DRY (Don't Repeat Yourself)
- [ ] Les erreurs sont gérées (try/except)
- [ ] La doc est mise à jour si nécessaire

---

## Bonnes Pratiques

### Code Quality

```python
#  BON
def calculate_skill_frequency(offers: List[Dict], skill_name: str) -> float:
    """
    Calcule la fréquence d'apparition d'une compétence.
    
    Args:
        offers: Liste des offres d'emploi
        skill_name: Nom de la compétence recherchée
    
    Returns:
        Fréquence (0-1)
    
    Raises:
        ValueError: Si offers est vide
    """
    if not offers:
        raise ValueError("Liste d'offres vide")
    
    count = sum(1 for offer in offers if skill_name in offer.get('competences', []))
    return count / len(offers)


#  MAUVAIS
def calc(o, s):
    c = 0
    for x in o:
        if s in x['competences']:
            c += 1
    return c / len(o)
```

### Gestion des Erreurs

```python
#  BON : Gestion explicite
def load_data_from_api():
    """Charge les données depuis l'API avec gestion d'erreurs"""
    try:
        response = requests.get(API_URL, timeout=10)
        response.raise_for_status()
        return response.json()
    
    except requests.Timeout:
        logger.error("Timeout lors de l'appel API")
        return None
    
    except requests.HTTPError as e:
        logger.error(f"Erreur HTTP {e.response.status_code}")
        return None
    
    except Exception as e:
        logger.error(f"Erreur inattendue : {e}")
        return None


#  MAUVAIS : Catch all sans logging
def load_data_from_api():
    try:
        response = requests.get(API_URL)
        return response.json()
    except:
        return None
```

### Performance

```python
#  BON : Utiliser les compréhensions de liste
filtered_offers = [
    offer for offer in offers
    if offer['region'] == 'Île-de-France'
]

#  MAUVAIS : Boucle for avec append
filtered_offers = []
for offer in offers:
    if offer['region'] == 'Île-de-France':
        filtered_offers.append(offer)


#  BON : Cache Streamlit
@st.cache_data(ttl=3600)
def load_offers():
    return pd.read_sql_query("SELECT * FROM fact_offers", conn)


#  BON : Vectorisation Pandas
df['skills_count'] = df['competences'].apply(len)

#  MAUVAIS : Boucle for sur DataFrame
for idx, row in df.iterrows():
    df.at[idx, 'skills_count'] = len(row['competences'])
```

### Sécurité

```python
#  BON : Paramètres SQL
cursor.execute(
    "SELECT * FROM fact_offers WHERE title LIKE ?",
    (f"%{search_term}%",)
)

#  MAUVAIS : SQL Injection
cursor.execute(
    f"SELECT * FROM fact_offers WHERE title LIKE '%{search_term}%'"
)


#  BON : Variables d'environnement
API_KEY = os.getenv("MISTRAL_API_KEY")

#  MAUVAIS : Clé en dur
API_KEY = "sk-1234567890abcdef"
```

### Documentation

```python
#  BON : Docstring complète (Google Style)
def extract_skills(description: str, min_confidence: float = 0.7) -> List[str]:
    """
    Extrait les compétences d'une description d'offre.
    
    Args:
        description: Texte de la description de l'offre
        min_confidence: Score de confiance minimum (0-1)
    
    Returns:
        Liste des compétences identifiées
    
    Raises:
        ValueError: Si description est vide
    
    Examples:
        >>> extract_skills("Recherche Data Scientist Python SQL")
        ['Python', 'SQL']
    """
    pass


#  MAUVAIS : Pas de docstring
def extract_skills(description, min_confidence=0.7):
    pass
```

---

## Ressources

### Documentation Externe

- **Streamlit** : https://docs.streamlit.io
- **Pandas** : https://pandas.pydata.org/docs
- **scikit-learn** : https://scikit-learn.org/stable
- **Plotly** : https://plotly.com/python
- **France Travail API** : https://francetravail.io/data/api/offres-emploi
- **Mistral AI** : https://docs.mistral.ai

### Contacts

- **GitHub** : https://github.com/rsquaredata/radar-nlp
- **Issues** : https://github.com/rsquaredata/radar-nlp/issues
- **Discussions** : https://github.com/rsquaredata/radar-nlp/discussions

---

<div align="center">

** RADAR - Analyse du Marché de l'Emploi**



[⬆ Retour en haut](#table-des-matières)

</div>
