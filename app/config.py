"""
Configuration globale de l'application Streamlit.
"""

import os
from pathlib import Path

# ============================================================================
# CHEMINS
# ============================================================================

# Racine du projet
PROJECT_ROOT = Path(__file__).parent.parent

# Base de données
DATABASE_PATH = PROJECT_ROOT / "database" / "jobs.db"

# Modèles NLP
MODELS_DIR = PROJECT_ROOT / "nlp_analysis"
TOPIC_MODEL_PATH = MODELS_DIR / "skill_topic_model.pkl"
CLUSTERING_MODEL_PATH = MODELS_DIR / "clustering_model.pkl"

# Assets
ASSETS_DIR = PROJECT_ROOT / "app" / "assets"
WORDCLOUDS_DIR = PROJECT_ROOT / "nlp_analysis" / "wordclouds"



PAGE_TITLE = "Data Jobs Analytics - France"
PAGE_ICON = "📊"
LAYOUT = "wide"



# Palette de couleurs
COLOR_PALETTE = {
    'primary': '#1f77b4',
    'secondary': '#ff7f0e',
    'success': '#2ca02c',
    'danger': '#d62728',
    'warning': '#ff9800',
    'info': '#17a2b8',
}

# Couleurs par profil NLP
PROFILE_COLORS = {
    0: '#e74c3c',  # Data Scientist/ML - Rouge
    1: '#3498db',  # Data Engineer - Bleu
    2: '#9b59b6',  # Cloud/DevOps - Violet
    3: '#2ecc71',  # Data Analyst/BI - Vert
    4: '#f39c12',  # Data Architect - Orange
    5: '#1abc9c',  # Full Stack - Turquoise
}

PROFILE_NAMES = {
    0: "🤖 Data Scientist/ML",
    1: "⚙️ Data Engineer",
    2: "☁️ Cloud/DevOps",
    3: "📊 Data Analyst/BI",
    4: "🏗️ Data Architect",
    5: "🎨 Full Stack Dev"
}

# Couleurs par région (exemples)
REGION_COLORS = {
    'Île-de-France': '#e74c3c',
    'Auvergne-Rhône-Alpes': '#3498db',
    'Occitanie': '#2ecc71',
    'Nouvelle-Aquitaine': '#f39c12',
    'Provence-Alpes-Côte d\'Azur': '#9b59b6',
}

# ============================================================================
# CONFIGURATION DONNÉES
# ============================================================================

# Types de contrat
CONTRACT_TYPES = ['CDI', 'CDD', 'Stage', 'Alternance', 'Intérim', 'Freelance']

# Options télétravail
REMOTE_OPTIONS = ['Oui', 'Non', 'Hybride', 'Unknown']

# Sources de données
DATA_SOURCES = ['France Travail', 'HelloWork', 'Adzuna']



# Nombre de topics/clusters
N_TOPICS = 6
N_CLUSTERS = 6

# Stop words personnalisés (en plus de ceux par défaut)
CUSTOM_STOPWORDS = [
    'data', 'données', 'ia', 'poste', 'offre', 'emploi',
    'recherche', 'candidat', 'profil', 'mission', 'entreprise'
]



# Centre de la France pour la carte
FRANCE_CENTER = [46.603354, 1.888334]
FRANCE_ZOOM = 6



# Mistral AI (à configurer avec variable d'environnement)
MISTRAL_API_KEY = os.getenv('MISTRAL_API_KEY', '')
MISTRAL_MODEL = 'mistral-medium'



ITEMS_PER_PAGE = 20
MAX_ITEMS_PER_PAGE = 100



CACHE_TTL = 3600  # 1 heure