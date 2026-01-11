# Guide Développeur - Job Radar

<div align="center">

**Version 1.0 | Documentation Technique**

*Architecture, APIs, et Contribution au Code*

[Accueil](../README.md) • [ Guide User](USER_GUIDE.md) • [ Docker](DOCKER_GUIDE.md) • [ Données](DATA_GUIDE.md)

---

</div>

##  Table des matières

1. [Architecture](#architecture)
2. [Installation Dev](#installation-développeur)
3. [Structure du Code](#structure-du-code)
4. [Base de Données](#base-de-données)
5. [Pipeline ETL](#pipeline-etl)
6. [APIs & Intégrations](#apis--intégrations)
7. [NLP & Machine Learning](#nlp--machine-learning)
8. [Frontend Streamlit](#frontend-streamlit)
9. [Tests](#tests)
10. [CI/CD](#cicd)
11. [Contribution](#contribution)
12. [Bonnes Pratiques](#bonnes-pratiques)

---

## 🏛️ Architecture

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
| **DevOps** | Docker, Docker Compose, GitHub Actions |

---

##  Installation Développeur

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
cd job-radar

# 2. Créer l'environnement virtuel
python -m venv venv

# Activer (Linux/Mac)
source venv/bin/activate

# Activer (Windows)
venv\Scripts\activate

# 3. Installer les dépendances
pip install -r requirements.txt
pip install -r requirements-dev.txt  # Outils de dev

# 4. Configurer les variables d'environnement
cp .env.example .env
nano .env

# 5. Initialiser la base de données
python database/etl_pipeline.py --input data/raw/jobs.csv --recreate

# 6. Lancer en mode dev
streamlit run app/home.py --server.runOnSave true
```

### Requirements Dev

```txt
# requirements-dev.txt
pytest>=7.4.0
pytest-cov>=4.1.0
black>=23.3.0
flake8>=6.0.0
mypy>=1.4.0
pre-commit>=3.3.0
ipython>=8.14.0
jupyter>=1.0.0
```

---

## 📁 Structure du Code

### Arborescence Détaillée

```python
projet_nlp/
│
├── app/                          # Frontend Streamlit
│   ├── home.py                   # Page d'accueil (entry point)
│   ├── pages/                    # Pages de l'app
│   │   ├── Explorer.py           # Exploration offres
│   │   ├── Geographie.py         # Cartographie
│   │   ├── Analytics.py          # Statistiques
│   │   ├── Intelligence.py       # NLP/ML
│   │   ├── Assistant.py          # IA Mistral
│   │   └── Contribuer.py         # Ajout offres
│   │
│   └── utils/                    # Utilitaires
│       ├── components.py         # Composants UI réutilisables
│       ├── db.py                 # Gestion BDD (CRUD)
│       ├── nlp_utils.py          # Fonctions NLP
│       ├── clustering.py         # K-Means & clustering
│       ├── tfidf_analysis.py     # Analyse TF-IDF
│       ├── viz.py                # Graphiques Plotly
│       ├── filters.py            # Filtres de données
│       └── config.py             # Configuration globale
│
├── database/                     # Base de données
│   ├── schema.sql                # DDL (CREATE TABLE, etc.)
│   ├── etl_pipeline.py           # Pipeline ETL complet
│   ├── db_insert.py              # Fonctions d'insertion
│   └── jobs.db                   # Base SQLite
│
├── scraping/                     # Collecte données
│   ├── france_travail_api.py     # Client API France Travail
│   ├── hellowork_scraper.py      # Scraper HelloWork
│   └── enrichment.py             # Enrichissement post-scraping
│
├── geographic_enrichment/        # Géolocalisation
│   ├── enrich_geo.py             # Enrichissement géo
│   └── regions_france.json       # Référentiel régions
│
├── data/                         # Données
│   ├── raw/                      # Données brutes (CSV)
│   ├── processed/                # Données traitées
│   └── exports/                  # Exports utilisateurs
│
│
├── docs/                         # Documentation
│   ├── USER_GUIDE.md
│   ├── DEVELOPER_GUIDE.md
│   ├── DOCKER_GUIDE.md
│   └── DATA_GUIDE.md
│

├── Dockerfile                    # Image Docker
├── docker-compose.yml            # Orchestration
├── requirements.txt              # Dépendances prod        # Dépendances dev                 # Variables d'env
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

## 🗄️ Base de Données

### Schéma Relationnel

```sql
-- Star Schema optimisé pour l'analyse

-- Dimension : Sources
CREATE TABLE dim_source (
    source_key INTEGER PRIMARY KEY AUTOINCREMENT,
    source_name TEXT NOT NULL UNIQUE,
    source_type TEXT  -- 'api', 'scraping'
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

-- Fait : Offres (CENTRALE)
CREATE TABLE fact_offers (
    offer_key INTEGER PRIMARY KEY AUTOINCREMENT,
    uid TEXT NOT NULL UNIQUE,  -- Hash MD5 pour déduplication
    offer_id TEXT NOT NULL,
    
    -- Foreign keys
    source_key INTEGER,
    region_key INTEGER,
    company_key INTEGER,
    contract_key INTEGER,
    
    -- Attributs
    title TEXT NOT NULL,
    source_url TEXT,           -- URL de l'offre
    location TEXT,
    salary TEXT,
    remote TEXT,
    published_date TEXT,
    description TEXT,
    
    -- Métriques
    skills_count INTEGER DEFAULT 0,
    competences_count INTEGER DEFAULT 0,
    savoir_etre_count INTEGER DEFAULT 0,
    
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
    fo.source_url,  -- Important pour le bouton Postuler
    fo.description,
    dr.region_name,
    dc.company_name,
    dct.contract_type,
    ds.source_name
FROM fact_offers fo
LEFT JOIN dim_region dr ON fo.region_key = dr.region_key
LEFT JOIN dim_company dc ON fo.company_key = dc.company_key
LEFT JOIN dim_contract dct ON fo.contract_key = dct.contract_key
LEFT JOIN dim_source ds ON fo.source_key = ds.source_key;

-- Vue : Top compétences avec stats
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
ORDER BY offer_count DESC;
```

### API Python (utils/db.py)

```python
import sqlite3
import pandas as pd
from pathlib import Path

class DatabaseManager:
    """Gestionnaire de connexion BDD"""
    
    def __init__(self, db_path: Path):
        self.db_path = db_path
        self.conn = None
    
    def get_connection(self):
        """Connexion SQLite"""
        return sqlite3.connect(self.db_path)
    
    def get_offers_with_skills(self) -> pd.DataFrame:
        """Récupère les offres avec compétences agrégées"""
        query = """
            SELECT 
                fo.offer_key,
                fo.uid,
                fo.title,
                fo.source_url,  -- IMPORTANT !
                fo.description,
                dr.region_name,
                dc.company_name,
                dct.contract_type,
                GROUP_CONCAT(ds.skill_name) as all_skills
            FROM fact_offers fo
            LEFT JOIN fact_offer_skill fos ON fo.offer_key = fos.offer_key
            LEFT JOIN dim_skill ds ON fos.skill_key = ds.skill_key
            LEFT JOIN dim_region dr ON fo.region_key = dr.region_key
            LEFT JOIN dim_company dc ON fo.company_key = dc.company_key
            LEFT JOIN dim_contract dct ON fo.contract_key = dct.contract_key
            GROUP BY fo.offer_key
        """
        return pd.read_sql_query(query, self.get_connection())
    
    def search_offers(self, 
                     search_text: str = None,
                     regions: list = None,
                     contracts: list = None) -> pd.DataFrame:
        """Recherche avec filtres"""
        query = "SELECT * FROM v_offers_complete WHERE 1=1"
        params = []
        
        if search_text:
            query += " AND (title LIKE ? OR description LIKE ?)"
            pattern = f"%{search_text}%"
            params.extend([pattern, pattern])
        
        if regions:
            placeholders = ','.join(['?' for _ in regions])
            query += f" AND region_name IN ({placeholders})"
            params.extend(regions)
        
        if contracts:
            placeholders = ','.join(['?' for _ in contracts])
            query += f" AND contract_type IN ({placeholders})"
            params.extend(contracts)
        
        conn = self.get_connection()
        return pd.read_sql_query(query, conn, params=params)
```

---

## 🔄 Pipeline ETL

### Architecture ETL

```python
# database/etl_pipeline.py

class ETLPipeline:
    """Pipeline Extract-Transform-Load"""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.conn = None
        self.stats = {
            'offers_inserted': 0,
            'offers_duplicates': 0,
            'skills_inserted': 0
        }
    
    def extract(self, csv_path: str) -> pd.DataFrame:
        """1. EXTRACT : Charger les données brutes"""
        df = pd.read_csv(csv_path)
        print(f"✅ {len(df)} lignes extraites")
        return df
    
    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        """2. TRANSFORM : Nettoyer et enrichir"""
        # Nettoyage
        df = df.dropna(subset=['title', 'company'])
        df['title'] = df['title'].str.strip()
        
        # Génération UID unique (déduplication)
        df['uid'] = df.apply(
            lambda row: hashlib.md5(
                f"{row['offer_id']}{row['source']}".encode()
            ).hexdigest(),
            axis=1
        )
        
        # Extraction compétences
        df['competences'] = df['description'].apply(self.extract_skills)
        
        print(f"✅ {len(df)} lignes transformées")
        return df
    
    def load(self, df: pd.DataFrame):
        """3. LOAD : Insertion dans la BDD"""
        # Charger dimensions
        self.load_dimensions(df)
        
        # Charger faits
        self.load_offers(df)
        
        # Charger associations
        self.load_offer_skills(df)
        
        print(f"✅ {self.stats['offers_inserted']} offres insérées")
    
    def extract_skills(self, description: str) -> list:
        """Extraction de compétences par regex + NLP"""
        skills = []
        
        # Patterns de compétences techniques
        patterns = [
            r'\bPython\b', r'\bSQL\b', r'\bDocker\b',
            r'\bKubernetes\b', r'\bMachine Learning\b',
            r'\bTensorFlow\b', r'\bPyTorch\b'
        ]
        
        for pattern in patterns:
            if re.search(pattern, description, re.IGNORECASE):
                skills.append(pattern.replace(r'\b', ''))
        
        return skills

# Utilisation
if __name__ == "__main__":
    etl = ETLPipeline(db_path="database/jobs.db")
    
    # Extract
    df = etl.extract("data/raw/jobs.csv")
    
    # Transform
    df = etl.transform(df)
    
    # Load
    etl.load(df)
```

### Déduplication

```python
def check_duplicate(self, uid: str) -> bool:
    """Vérifie si une offre existe déjà"""
    query = "SELECT COUNT(*) FROM fact_offers WHERE uid = ?"
    cursor = self.conn.execute(query, (uid,))
    count = cursor.fetchone()[0]
    return count > 0

def insert_offer(self, row: dict):
    """Insert avec gestion des doublons"""
    if self.check_duplicate(row['uid']):
        self.stats['offers_duplicates'] += 1
        return
    
    # Insertion
    query = """
        INSERT INTO fact_offers (uid, offer_id, title, ...)
        VALUES (?, ?, ?, ...)
    """
    self.conn.execute(query, (row['uid'], row['offer_id'], ...))
    self.stats['offers_inserted'] += 1
```

---

## 🔌 APIs & Intégrations

### France Travail API

```python
# scraping/france_travail_api.py

import requests
from typing import List, Dict

class FranceTravailAPI:
    """Client API France Travail"""
    
    BASE_URL = "https://api.francetravail.io/partenaire/offresdemploi/v2"
    
    def __init__(self, client_id: str, client_secret: str):
        self.client_id = client_id
        self.client_secret = client_secret
        self.access_token = None
    
    def authenticate(self):
        """Authentification OAuth2"""
        url = "https://entreprise.francetravail.fr/connexion/oauth2/access_token"
        
        data = {
            'grant_type': 'client_credentials',
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'scope': 'api_offresdemploiv2 o2dsoffre'
        }
        
        response = requests.post(url, data=data)
        response.raise_for_status()
        
        self.access_token = response.json()['access_token']
    
    def search_offers(self, 
                     keywords: str = None,
                     location: str = None,
                     contract_type: str = None,
                     max_results: int = 150) -> List[Dict]:
        """Recherche d'offres"""
        
        if not self.access_token:
            self.authenticate()
        
        headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json'
        }
        
        params = {
            'motsCles': keywords,
            'commune': location,
            'typeContrat': contract_type,
            'range': f'0-{max_results}'
        }
        
        response = requests.get(
            f"{self.BASE_URL}/search",
            headers=headers,
            params=params
        )
        response.raise_for_status()
        
        return response.json()['resultats']

# Utilisation
api = FranceTravailAPI(
    client_id=os.getenv('FRANCE_TRAVAIL_CLIENT_ID'),
    client_secret=os.getenv('FRANCE_TRAVAIL_CLIENT_SECRET')
)

offers = api.search_offers(
    keywords="Data Scientist",
    location="Paris",
    contract_type="CDI"
)
```

### HelloWork Scraper

```python
# scraping/hellowork_scraper.py

from bs4 import BeautifulSoup
import requests
from typing import List, Dict

class HelloWorkScraper:
    """Scraper HelloWork"""
    
    BASE_URL = "https://www.hellowork.com"
    
    def scrape_search_page(self, 
                          keywords: str,
                          location: str = None,
                          page: int = 1) -> List[Dict]:
        """Scrape une page de résultats"""
        
        url = f"{self.BASE_URL}/fr-fr/emplois/recherche.html"
        params = {
            'k': keywords,
            'l': location,
            'p': page
        }
        
        response = requests.get(url, params=params)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        offers = []
        for card in soup.find_all('article', class_='job-card'):
            offer = {
                'title': card.find('h2').text.strip(),
                'company': card.find('p', class_='company').text.strip(),
                'location': card.find('span', class_='location').text.strip(),
                'url': self.BASE_URL + card.find('a')['href'],
                'contract_type': self.extract_contract_type(card)
            }
            offers.append(offer)
        
        return offers
    
    def scrape_offer_details(self, offer_url: str) -> Dict:
        """Scrape les détails d'une offre"""
        
        response = requests.get(offer_url)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        return {
            'description': soup.find('div', class_='description').text.strip(),
            'salary': self.extract_salary(soup),
            'skills': self.extract_skills(soup)
        }

# Utilisation
scraper = HelloWorkScraper()
offers = scraper.scrape_search_page("Data Scientist", "Paris")
```

### Mistral AI Integration

```python
# app/utils/mistral_client.py

from mistralai.client import MistralClient
from mistralai.models.chat_completion import ChatMessage

class MistralAssistant:
    """Client Mistral AI pour l'assistant"""
    
    def __init__(self, api_key: str):
        self.client = MistralClient(api_key=api_key)
        self.model = "mistral-large-latest"
    
    def chat(self, 
             user_message: str,
             system_prompt: str = None,
             context: dict = None) -> str:
        """Discussion avec l'assistant"""
        
        messages = []
        
        # System prompt
        if system_prompt:
            messages.append(
                ChatMessage(role="system", content=system_prompt)
            )
        
        # Context (données du marché)
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
            messages=messages
        )
        
        return response.choices[0].message.content
    
    def format_context(self, context: dict) -> str:
        """Formatte le contexte du marché"""
        return f"""
        Contexte du marché de l'emploi :
        - Total offres : {context['total_offers']}
        - Top 3 compétences : {', '.join(context['top_skills'])}
        - Régions principales : {', '.join(context['top_regions'])}
        """

# Utilisation
assistant = MistralAssistant(api_key=os.getenv('MISTRAL_API_KEY'))

response = assistant.chat(
    user_message="Quelles sont les tendances du marché ?",
    context={
        'total_offers': 2520,
        'top_skills': ['Python', 'SQL', 'Docker'],
        'top_regions': ['Île-de-France', 'Auvergne', 'Occitanie']
    }
)
