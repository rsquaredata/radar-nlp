import streamlit as st
import pandas as pd
import sys
from pathlib import Path
import json
from datetime import datetime
import hashlib
import requests
import time
from io import StringIO
import os
import re
from typing import List, Dict, Any, Optional

# Import
sys.path.insert(0, str(Path(__file__).parent.parent))
from utils.components import inject_premium_css, premium_navbar
from utils.db import load_offers_with_skills

# Import des fonctions d'insertion
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "app" / "utils"))

try:
    from db_insert import insert_offers, generate_uid, check_duplicate_by_uid
except ImportError:
    # Fallback si db_insert n'est pas trouvé
    def insert_offers(offers):
        return 0, 0, " Module db_insert non trouvé"
    def generate_uid(offer):
        return hashlib.md5(f"{offer.get('title','')}".encode()).hexdigest()
    def check_duplicate_by_uid(uid):
        return False

# ============================================================================
# CONFIG
# ============================================================================

st.set_page_config(
    page_title="Contribuer | DataJobs",
    page_icon="➕",
    layout="wide",
    initial_sidebar_state="expanded",
)

inject_premium_css()
premium_navbar(active_page="Contribuer")

# ============================================================================
# INITIALISATION SESSION STATE
# ============================================================================

if 'contribution_count' not in st.session_state:
    st.session_state.contribution_count = 0
if 'contribution_history' not in st.session_state:
    st.session_state.contribution_history = []
if 'level' not in st.session_state:
    st.session_state.level = 1
if 'xp' not in st.session_state:
    st.session_state.xp = 0

# ============================================================================
# CSS ULTRA-MODERNE GAMIFIÉ
# ============================================================================

st.markdown("""
<style>
    .main {
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 50%, #0f172a 100%);
    }
    
    /* Header Contribution */
    .contrib-header {
        background: linear-gradient(135deg, #1e293b 0%, #334155 100%);
        border: 4px solid #10b981;
        border-radius: 24px;
        padding: 3rem;
        margin-bottom: 2rem;
        box-shadow: 0 0 80px rgba(16, 185, 129, 0.5);
        position: relative;
        overflow: hidden;
        animation: headerPulse 3s ease-in-out infinite;
    }
    
    @keyframes headerPulse {
        0%, 100% { box-shadow: 0 0 80px rgba(16, 185, 129, 0.5); }
        50% { box-shadow: 0 0 100px rgba(16, 185, 129, 0.8); }
    }
    
    .contrib-header::before {
        content: '';
        position: absolute;
        top: 0; left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(16, 185, 129, 0.3), transparent);
        animation: contribScan 4s linear infinite;
    }
    
    @keyframes contribScan {
        0% { left: -100%; }
        100% { left: 100%; }
    }
    
    .contrib-title {
        font-size: 4.5rem;
        font-weight: 900;
        text-align: center;
        background: linear-gradient(135deg, #10b981 0%, #34d399 50%, #6ee7b7 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin: 0;
        font-family: 'Courier New', monospace;
        letter-spacing: 6px;
        animation: titleGlow 2s ease-in-out infinite;
    }
    
    @keyframes titleGlow {
        0%, 100% { filter: drop-shadow(0 0 20px rgba(16, 185, 129, 0.6)); }
        50% { filter: drop-shadow(0 0 40px rgba(16, 185, 129, 1)); }
    }
    
    /* Gamification Panel */
    .gamif-panel {
        background: linear-gradient(135deg, rgba(16, 185, 129, 0.1) 0%, rgba(52, 211, 153, 0.1) 100%);
        border: 3px solid rgba(16, 185, 129, 0.5);
        border-radius: 20px;
        padding: 2rem;
        margin-bottom: 2rem;
        position: relative;
    }
    
    .level-badge {
        display: inline-block;
        background: linear-gradient(135deg, #10b981 0%, #059669 100%);
        color: white;
        padding: 1rem 2rem;
        border-radius: 50px;
        font-size: 1.5rem;
        font-weight: 900;
        box-shadow: 0 10px 30px rgba(16, 185, 129, 0.5);
        animation: badgeBounce 2s ease-in-out infinite;
    }
    
    @keyframes badgeBounce {
        0%, 100% { transform: translateY(0); }
        50% { transform: translateY(-10px); }
    }
    
    .xp-bar {
        background: rgba(0, 0, 0, 0.3);
        border-radius: 50px;
        height: 30px;
        overflow: hidden;
        border: 2px solid #10b981;
    }
    
    .xp-fill {
        background: linear-gradient(90deg, #10b981 0%, #34d399 100%);
        height: 100%;
        border-radius: 50px;
        transition: width 1s ease;
        box-shadow: 0 0 20px rgba(16, 185, 129, 0.8);
        animation: xpPulse 1.5s ease-in-out infinite;
    }
    
    @keyframes xpPulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.7; }
    }
    
    /* Cards Méthodes */
    .method-card {
        background: linear-gradient(135deg, rgba(16, 185, 129, 0.05) 0%, rgba(52, 211, 153, 0.05) 100%);
        border: 3px solid rgba(16, 185, 129, 0.4);
        border-radius: 20px;
        padding: 2rem;
        margin-bottom: 1.5rem;
        transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
        cursor: pointer;
        position: relative;
        overflow: hidden;
    }
    
    .method-card:hover {
        transform: translateY(-15px) scale(1.02);
        border-color: #10b981;
        box-shadow: 0 20px 60px rgba(16, 185, 129, 0.6);
    }
    
    .method-card::after {
        content: '';
        position: absolute;
        top: 0; left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(16, 185, 129, 0.2), transparent);
        transition: left 0.5s;
    }
    
    .method-card:hover::after {
        left: 100%;
    }
    
    .method-icon {
        font-size: 3.5rem;
        margin-bottom: 1rem;
        text-align: center;
        animation: iconFloat 3s ease-in-out infinite;
    }
    
    @keyframes iconFloat {
        0%, 100% { transform: translateY(0); }
        50% { transform: translateY(-10px); }
    }
    
    .method-title {
        color: #10b981;
        font-size: 1.8rem;
        font-weight: 900;
        text-align: center;
        margin-bottom: 1rem;
        text-transform: uppercase;
    }
    
    /* Stats Card */
    .stat-card {
        background: rgba(16, 185, 129, 0.1);
        border: 2px solid rgba(16, 185, 129, 0.5);
        border-radius: 16px;
        padding: 1.5rem;
        text-align: center;
        transition: all 0.3s;
    }
    
    .stat-card:hover {
        transform: scale(1.05);
        border-color: #10b981;
        box-shadow: 0 10px 40px rgba(16, 185, 129, 0.4);
    }
    
    .stat-value {
        font-size: 3rem;
        font-weight: 900;
        background: linear-gradient(135deg, #10b981 0%, #34d399 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    .stat-label {
        color: #6ee7b7;
        font-size: 0.9rem;
        margin-top: 0.5rem;
        text-transform: uppercase;
    }
    
    /* Success Animation */
    .success-animation {
        animation: successPop 0.6s cubic-bezier(0.68, -0.55, 0.265, 1.55);
    }
    
    @keyframes successPop {
        0% { transform: scale(0); opacity: 0; }
        50% { transform: scale(1.2); }
        100% { transform: scale(1); opacity: 1; }
    }
    
    /* Confetti Effect */
    .confetti {
        position: fixed;
        width: 10px;
        height: 10px;
        background: #10b981;
        animation: confettiFall 3s linear infinite;
    }
    
    @keyframes confettiFall {
        to { transform: translateY(100vh) rotate(360deg); opacity: 0; }
    }
</style>
""", unsafe_allow_html=True)

# ============================================================================
# FONCTIONS UTILITAIRES
# ============================================================================

def calculate_level_xp(xp):
    """Calcule le niveau et l'XP pour le prochain niveau"""
    level = int(xp // 100) + 1
    xp_in_level = xp % 100
    xp_for_next = 100
    return level, xp_in_level, xp_for_next

def generate_offer_hash(offer_dict):
    """Génère un hash unique pour détecter les doublons"""
    key_fields = f"{offer_dict.get('title', '')}|{offer_dict.get('company_name', '')}|{offer_dict.get('location', '')}"
    return hashlib.md5(key_fields.lower().encode()).hexdigest()

def check_duplicate(new_offers, existing_df):
    """Vérifie les doublons et retourne uniquement les nouvelles offres"""
    unique_offers = []
    duplicates = []
    
    for offer in new_offers:
        uid = generate_uid(offer)
        
        # Vérifier dans la BDD
        if check_duplicate_by_uid(uid):
            duplicates.append(offer)
        else:
            unique_offers.append(offer)
    
    return unique_offers, duplicates

def add_contribution_xp(points):
    """Ajoute de l'XP et met à jour le niveau"""
    st.session_state.xp += points
    st.session_state.contribution_count += 1
    level, _, _ = calculate_level_xp(st.session_state.xp)
    
    # Level up!
    if level > st.session_state.level:
        st.session_state.level = level
        st.balloons()
        st.success(f"🎉 **LEVEL UP!** Vous êtes maintenant niveau {level}!")

# ============================================================================
# SCRAPING FRANCE TRAVAIL
# ============================================================================

def scrape_france_travail(query: str, max_results: int = 100):
    """Scrape France Travail via API"""
    try:
        # Charger les variables d'environnement
        from dotenv import load_dotenv
        env_file = PROJECT_ROOT / ".env"
        load_dotenv(env_file)
        
        client_id = os.getenv("FRANCE_TRAVAIL_CLIENT_ID")
        client_secret = os.getenv("FRANCE_TRAVAIL_CLIENT_SECRET")
        
        if not client_id or not client_secret:
            return None, "❌ Clés API manquantes. Vérifiez le fichier .env"
        
        # 1. Obtenir le token
        TOKEN_URL = "https://entreprise.pole-emploi.fr/connexion/oauth2/access_token?realm=/partenaire"
        
        token_data = {
            "grant_type": "client_credentials",
            "client_id": client_id,
            "client_secret": client_secret,
            "scope": "api_offresdemploiv2 o2dsoffre"
        }
        
        token_response = requests.post(
            TOKEN_URL,
            data=token_data,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            timeout=10
        )
        
        if token_response.status_code != 200:
            return None, f"❌ Erreur token: {token_response.status_code}"
        
        access_token = token_response.json().get("access_token")
        
        # 2. Rechercher les offres
        SEARCH_URL = "https://api.francetravail.io/partenaire/offresdemploi/v2/offres/search"
        
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Accept": "application/json"
        }
        
        params = {
            "motsCles": query,
            "range": f"0-{max_results-1}"
        }
        
        search_response = requests.get(
            SEARCH_URL,
            headers=headers,
            params=params,
            timeout=30
        )
        
        if search_response.status_code not in [200, 206]:
            return None, f"❌ Erreur recherche: {search_response.status_code}"
        
        data = search_response.json()
        offers_raw = data.get("resultats", [])
        
        # 3. Normaliser les offres
        normalized_offers = []
        for offer in offers_raw:
            normalized = {
                'source': 'france-travail-api',
                'title': offer.get('intitule', ''),
                'company_name': (offer.get('entreprise') or {}).get('nom', ''),
                'location': (offer.get('lieuTravail') or {}).get('libelle', ''),
                'region_name': (offer.get('lieuTravail') or {}).get('libelle', '').split(',')[-1].strip() if (offer.get('lieuTravail') or {}).get('libelle') else '',
                'contract_type': offer.get('typeContratLibelle', ''),
                'remote': 'unknown',
                'salary': (offer.get('salaire') or {}).get('libelle', '') if isinstance(offer.get('salaire'), dict) else '',
                'url': (offer.get('origineOffre') or {}).get('urlOrigine', ''),
                'description': offer.get('description', ''),
                'all_skills': '',
                'added_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            normalized_offers.append(normalized)
        
        return normalized_offers, f"✅ {len(normalized_offers)} offres récupérées"
        
    except Exception as e:
        return None, f"❌ Erreur: {str(e)}"

# ============================================================================
# SCRAPING HELLOWORK
# ============================================================================

def scrape_hellowork(metier: str, mode: str = "emploi", city: str = None, max_pages: int = 3):
    """Scrape HelloWork"""
    try:
        from bs4 import BeautifulSoup
        import unicodedata
        
        def slugify(s: str) -> str:
            s = (s or "").strip().lower()
            s = unicodedata.normalize("NFKD", s)
            s = "".join(ch for ch in s if not unicodedata.combining(ch))
            s = re.sub(r"[^a-z0-9\s-]", " ", s)
            s = re.sub(r"\s+", "-", s).strip("-")
            s = re.sub(r"-+", "-", s)
            return s
        
        # Construire l'URL
        metier_slug = slugify(metier)
        BASE = "https://www.hellowork.com"
        
        if city:
            city_slug = slugify(city)
            path = f"/fr-fr/{mode}/metier_{metier_slug}-ville_{city_slug}.html"
        else:
            path = f"/fr-fr/{mode}/metier_{metier_slug}.html"
        
        listing_url = BASE + path
        
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        
        all_offers = []
        
        for page in range(1, max_pages + 1):
            url = listing_url if page == 1 else f"{listing_url}?p={page}"
            
            response = requests.get(url, headers=headers, timeout=15)
            
            if response.status_code != 200:
                continue
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extraire les liens d'offres
            offer_links = []
            for link in soup.find_all('a', href=True):
                href = link['href']
                if '/fr-fr/emplois/' in href and href.endswith('.html'):
                    full_url = BASE + href if href.startswith('/') else href
                    offer_links.append(full_url)
            
            # Dédupliquer
            offer_links = list(set(offer_links))
            
            # Scraper chaque offre (limiter à 20 par page)
            for offer_url in offer_links[:20]:
                try:
                    offer_response = requests.get(offer_url, headers=headers, timeout=10)
                    if offer_response.status_code != 200:
                        continue
                    
                    offer_soup = BeautifulSoup(offer_response.text, 'html.parser')
                    
                    # Extraire les infos
                    title = offer_soup.find('h1')
                    title = title.get_text(strip=True) if title else "N/A"
                    
                    company = offer_soup.find('span', class_='tw-text-xl')
                    company = company.get_text(strip=True) if company else "N/A"
                    
                    location = offer_soup.find('span', class_='tw-inline-block')
                    location = location.get_text(strip=True) if location else "N/A"
                    
                    description = offer_soup.find('div', class_='content')
                    description = description.get_text(strip=True) if description else ""
                    
                    offer_data = {
                        'source': 'hellowork-scraping',
                        'title': title,
                        'company_name': company,
                        'location': location,
                        'region_name': location.split(',')[-1].strip() if ',' in location else location,
                        'contract_type': mode.upper(),
                        'remote': 'unknown',
                        'salary': '',
                        'url': offer_url,
                        'description': description[:500],
                        'all_skills': '',
                        'added_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    }
                    
                    all_offers.append(offer_data)
                    
                    time.sleep(0.5)  # Pause entre requêtes
                    
                except:
                    continue
            
            time.sleep(1)  # Pause entre pages
        
        return all_offers, f"✅ {len(all_offers)} offres récupérées"
        
    except Exception as e:
        return None, f"❌ Erreur: {str(e)}"

# ============================================================================
# HEADER GAMIFIÉ
# ============================================================================

st.markdown("""
<div class="contrib-header">
    <h1 class="contrib-title">➕ CENTRE DE CONTRIBUTION</h1>
    <p style="text-align: center; color: #10b981; font-family: monospace; font-size: 1.3rem; margin-top: 1.5rem;">
        > PARTAGEZ VOS DÉCOUVERTES • ENRICHISSEZ LA BASE • GAGNEZ DE L'XP
    </p>
</div>
""", unsafe_allow_html=True)

# ============================================================================
# PANNEAU GAMIFICATION
# ============================================================================

level, xp_in_level, xp_for_next = calculate_level_xp(st.session_state.xp)
xp_percentage = (xp_in_level / xp_for_next) * 100

st.markdown('<div class="gamif-panel">', unsafe_allow_html=True)

gamif_col1, gamif_col2, gamif_col3 = st.columns(3)

with gamif_col1:
    st.markdown(f"""
    <div style="text-align: center;">
        <div class="level-badge">
            ⭐ NIVEAU {level}
        </div>
        <p style="color: #6ee7b7; margin-top: 1rem; font-size: 1.1rem;">
            {st.session_state.contribution_count} contributions
        </p>
    </div>
    """, unsafe_allow_html=True)

with gamif_col2:
    st.markdown(f"""
    <div style="padding: 1rem;">
        <p style="color: #10b981; font-size: 1.2rem; margin-bottom: 0.5rem; font-weight: 700;">
            Progression: {xp_in_level}/{xp_for_next} XP
        </p>
        <div class="xp-bar">
            <div class="xp-fill" style="width: {xp_percentage}%;"></div>
        </div>
    </div>
    """, unsafe_allow_html=True)

with gamif_col3:
    st.markdown(f"""
    <div style="text-align: center; padding: 1rem;">
        <p style="color: #6ee7b7; font-size: 1rem; margin-bottom: 0.5rem;">Prochain niveau dans:</p>
        <p style="color: #10b981; font-size: 2rem; font-weight: 900;">{xp_for_next - xp_in_level} XP</p>
    </div>
    """, unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# ============================================================================
# STATISTIQUES
# ============================================================================

st.markdown("### 📊 Statistiques de Contribution")

# Charger données existantes
existing_data = load_offers_with_skills()

stats_col1, stats_col2, stats_col3, stats_col4 = st.columns(4)

with stats_col1:
    st.markdown(f"""
    <div class="stat-card">
        <div class="stat-value">{len(existing_data):,}</div>
        <div class="stat-label">📊 Total Offres</div>
    </div>
    """, unsafe_allow_html=True)

with stats_col2:
    companies = existing_data['company_name'].nunique() if not existing_data.empty else 0
    st.markdown(f"""
    <div class="stat-card">
        <div class="stat-value">{companies:,}</div>
        <div class="stat-label">🏢 Entreprises</div>
    </div>
    """, unsafe_allow_html=True)

with stats_col3:
    regions = existing_data['region_name'].nunique() if not existing_data.empty else 0
    st.markdown(f"""
    <div class="stat-card">
        <div class="stat-value">{regions}</div>
        <div class="stat-label">🗺️ Régions</div>
    </div>
    """, unsafe_allow_html=True)

with stats_col4:
    st.markdown(f"""
    <div class="stat-card">
        <div class="stat-value">{st.session_state.contribution_count}</div>
        <div class="stat-label">➕ Vos Contributions</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# ============================================================================
# MÉTHODES DE CONTRIBUTION
# ============================================================================

st.markdown("### 🎯 Choisissez votre Méthode de Contribution")

tab1, tab2, tab3, tab4 = st.tabs([
    "📝 Ajout Manuel",
    "📤 Upload Fichier",
    "🔍 Scraping France Travail",
    "🌐 Scraping HelloWork"
])

# ============================================================================
# TAB 1: AJOUT MANUEL
# ============================================================================

with tab1:
    st.markdown('<div class="method-card">', unsafe_allow_html=True)
    st.markdown('<div class="method-icon">📝</div>', unsafe_allow_html=True)
    st.markdown('<div class="method-title">Ajout Manuel d\'une Offre</div>', unsafe_allow_html=True)
    
    st.markdown("**Remplissez le formulaire ci-dessous pour ajouter une offre** (Récompense: +10 XP)")
    
    with st.form("manual_form"):
        form_col1, form_col2 = st.columns(2)
        
        with form_col1:
            title = st.text_input("🎯 Titre de l'offre*", placeholder="Ex: Data Scientist Senior")
            company = st.text_input("🏢 Entreprise*", placeholder="Ex: Google France")
            location = st.text_input("📍 Localisation*", placeholder="Ex: Paris, Île-de-France")
            contract = st.selectbox("📋 Type de contrat*", ["CDI", "CDD", "Stage", "Alternance", "Freelance"])
        
        with form_col2:
            remote = st.selectbox("🏠 Télétravail", ["Non", "Oui", "Hybride"])
            salary = st.text_input("💰 Salaire", placeholder="Ex: 50-60K€")
            url = st.text_input("🔗 URL de l'offre", placeholder="https://...")
            skills = st.text_input("🎯 Compétences (séparées par virgules)", placeholder="Python, SQL, Machine Learning")
        
        description = st.text_area("📄 Description", placeholder="Description détaillée de l'offre...", height=150)
        
        submitted = st.form_submit_button("➕ AJOUTER L'OFFRE", use_container_width=True, type="primary")
        
        if submitted:
            if not title or not company or not location:
                st.error("⚠️ Veuillez remplir tous les champs obligatoires (*)")
            else:
                new_offer = {
                    'source': 'manual',
                    'title': title,
                    'company_name': company,
                    'location': location,
                    'region_name': location.split(',')[-1].strip() if ',' in location else location,
                    'contract_type': contract,
                    'remote': 'yes' if remote == 'Oui' else ('hybrid' if remote == 'Hybride' else 'no'),
                    'salary': salary,
                    'url': url,
                    'all_skills': skills,
                    'description': description,
                    'added_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                }
                
                # Vérifier doublon
                unique, dups = check_duplicate([new_offer], existing_data)
                
                if dups:
                    st.warning("⚠️ Cette offre semble déjà exister dans la base de données!")
                    st.json(new_offer)
                else:
                    # INSERTION DANS LA BASE DE DONNÉES
                    inserted, duplicates, message = insert_offers([new_offer])
                    
                    if inserted > 0:
                        st.success("✅ Offre ajoutée avec succès dans la base de données!")
                        add_contribution_xp(10)
                        st.balloons()
                        
                        # Ajouter à l'historique
                        st.session_state.contribution_history.append({
                            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                            'method': 'Manual',
                            'count': 1,
                            'xp': 10
                        })
                        
                        # Afficher récapitulatif
                        st.markdown("#### 📋 Récapitulatif")
                        st.json(new_offer)
                        st.info(message)
                        
                        # Vider le cache pour recharger les données
                        st.cache_data.clear()
                    else:
                        st.error(message)
    
    st.markdown('</div>', unsafe_allow_html=True)

# ============================================================================
# TAB 2: UPLOAD FICHIER
# ============================================================================

with tab2:
    st.markdown('<div class="method-card">', unsafe_allow_html=True)
    st.markdown('<div class="method-icon">📤</div>', unsafe_allow_html=True)
    st.markdown('<div class="method-title">Upload de Fichier (CSV/JSON)</div>', unsafe_allow_html=True)
    
    st.markdown("**Importez vos offres en masse** (Récompense: +5 XP par offre unique)")
    
    uploaded_file = st.file_uploader(
        "Choisissez un fichier CSV ou JSON",
        type=['csv', 'json', 'jsonl'],
        help="Format attendu: title, company_name, location, contract_type, etc."
    )
    
    if uploaded_file is not None:
        try:
            # Lire le fichier
            if uploaded_file.name.endswith('.csv'):
                df_upload = pd.read_csv(uploaded_file)
            elif uploaded_file.name.endswith('.json'):
                df_upload = pd.read_json(uploaded_file)
            elif uploaded_file.name.endswith('.jsonl'):
                df_upload = pd.read_json(uploaded_file, lines=True)
            
            st.success(f"✅ Fichier chargé: {len(df_upload)} lignes détectées")
            
            # Preview
            st.markdown("#### 👁️ Aperçu des données")
            st.dataframe(df_upload.head(10), use_container_width=True)
            
            # Colonnes requises
            required_cols = ['title', 'company_name', 'location']
            missing_cols = [col for col in required_cols if col not in df_upload.columns]
            
            if missing_cols:
                st.error(f"❌ Colonnes manquantes: {', '.join(missing_cols)}")
            else:
                # Ajouter colonnes manquantes avec valeurs par défaut
                if 'source' not in df_upload.columns:
                    df_upload['source'] = 'upload'
                if 'added_at' not in df_upload.columns:
                    df_upload['added_at'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                if 'region_name' not in df_upload.columns and 'location' in df_upload.columns:
                    df_upload['region_name'] = df_upload['location'].apply(
                        lambda x: str(x).split(',')[-1].strip() if pd.notna(x) and ',' in str(x) else str(x)
                    )
                
                # Vérifier doublons
                offers_list = df_upload.to_dict('records')
                unique_offers, duplicates = check_duplicate(offers_list, existing_data)
                
                st.markdown("#### 📊 Analyse des Doublons")
                
                dup_col1, dup_col2 = st.columns(2)
                with dup_col1:
                    st.metric("✅ Offres Uniques", len(unique_offers), delta=f"+{len(unique_offers)}")
                with dup_col2:
                    st.metric("⚠️ Doublons Détectés", len(duplicates), delta=f"-{len(duplicates)}", delta_color="inverse")
                
                if st.button(f"➕ IMPORTER {len(unique_offers)} OFFRES UNIQUES", use_container_width=True, type="primary", key="btn_import"):
                    if unique_offers:
                        # INSERTION DANS LA BASE DE DONNÉES
                        inserted, duplicates_db, message = insert_offers(unique_offers)
                        
                        if inserted > 0:
                            st.success(f"✅ {inserted} offres importées avec succès dans la base de données!")
                            add_contribution_xp(inserted * 5)
                            st.balloons()
                            
                            # Ajouter à l'historique
                            st.session_state.contribution_history.append({
                                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                                'method': 'Upload',
                                'count': inserted,
                                'xp': inserted * 5
                            })
                            
                            st.info(message)
                            
                            # Vider le cache
                            st.cache_data.clear()
                        else:
                            st.error(message)
                    else:
                        st.warning("⚠️ Aucune offre unique à importer")
        
        except Exception as e:
            st.error(f"❌ Erreur lors de la lecture du fichier: {str(e)}")
    
    st.markdown('</div>', unsafe_allow_html=True)

# ============================================================================
# TAB 3: SCRAPING FRANCE TRAVAIL
# ============================================================================

with tab3:
    st.markdown('<div class="method-card">', unsafe_allow_html=True)
    st.markdown('<div class="method-icon">🔍</div>', unsafe_allow_html=True)
    st.markdown('<div class="method-title">Scraping France Travail (API)</div>', unsafe_allow_html=True)
    
    st.markdown("**Récupérez des offres via l'API France Travail** (Récompense: +2 XP par offre)")
    
    st.info("💡 **Configuration requise:** Fichier `.env` à la racine avec `FRANCE_TRAVAIL_CLIENT_ID` et `FRANCE_TRAVAIL_CLIENT_SECRET`")
    
    scrape_col1, scrape_col2 = st.columns(2)
    
    with scrape_col1:
        query_ft = st.text_input(
            "🔍 Mot-clé de recherche",
            value="data scientist",
            placeholder="Ex: machine learning engineer",
            key="query_ft"
        )
        max_results_ft = st.slider("📊 Nombre maximum d'offres", 10, 500, 100, key="max_ft")
    
    with scrape_col2:
        env_path = PROJECT_ROOT / ".env"
        if env_path.exists():
            st.success("✅ Fichier .env détecté")
        else:
            st.warning("⚠️ Fichier .env non trouvé")
        
        st.markdown("**Emplacement attendu:**")
        st.code(str(env_path))
    
    if st.button("🚀 LANCER LE SCRAPING FRANCE TRAVAIL", use_container_width=True, type="primary", key="btn_ft"):
        with st.spinner("🔄 Récupération des offres en cours..."):
            
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            status_text.text("⚙️ Connexion à l'API France Travail...")
            progress_bar.progress(20)
            
            # SCRAPING RÉEL
            offers, message = scrape_france_travail(query_ft, max_results_ft)
            
            if offers is None:
                st.error(message)
                progress_bar.empty()
                status_text.empty()
            else:
                progress_bar.progress(50)
                status_text.text(f"✅ {len(offers)} offres récupérées - Vérification des doublons...")
                
                # Vérifier doublons
                unique_offers, duplicates = check_duplicate(offers, existing_data)
                
                progress_bar.progress(75)
                status_text.text(f"📊 {len(unique_offers)} nouvelles offres détectées")
                
                if unique_offers:
                    # INSERTION DANS LA BASE DE DONNÉES
                    inserted, duplicates_db, save_message = insert_offers(unique_offers)
                    
                    progress_bar.progress(100)
                    
                    if inserted > 0:
                        st.success(f"✅ {inserted} offres importées avec succès dans la base de données!")
                        add_contribution_xp(inserted * 2)
                        st.balloons()
                        
                        # Ajouter à l'historique
                        st.session_state.contribution_history.append({
                            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                            'method': 'France Travail API',
                            'count': inserted,
                            'xp': inserted * 2
                        })
                        
                        # Stats
                        st.markdown("#### 📊 Résultats")
                        res_col1, res_col2 = st.columns(2)
                        with res_col1:
                            st.metric("✅ Nouvelles offres", inserted)
                        with res_col2:
                            st.metric("⚠️ Doublons ignorés", len(duplicates) + duplicates_db)
                        
                        st.info(save_message)
                        
                        # Preview
                        with st.expander("👁️ Voir les premières offres"):
                            st.dataframe(pd.DataFrame(unique_offers[:5]), use_container_width=True)
                        
                        # Vider le cache
                        st.cache_data.clear()
                    else:
                        st.error(save_message)
                else:
                    st.warning(f"⚠️ Aucune nouvelle offre (toutes sont des doublons)")
                    st.info(f"Total récupéré: {len(offers)} • Doublons: {len(duplicates)}")
                
                progress_bar.empty()
                status_text.empty()
    
    st.markdown('</div>', unsafe_allow_html=True)

# ============================================================================
# TAB 4: SCRAPING HELLOWORK
# ============================================================================

with tab4:
    st.markdown('<div class="method-card">', unsafe_allow_html=True)
    st.markdown('<div class="method-icon">🌐</div>', unsafe_allow_html=True)
    st.markdown('<div class="method-title">Scraping HelloWork</div>', unsafe_allow_html=True)
    
    st.markdown("**Scrapez HelloWork par métier et ville** (Récompense: +2 XP par offre)")
    
    st.warning("⚠️ **Important:** Le scraping peut prendre quelques minutes selon le nombre de pages")
    
    scrape_hw_col1, scrape_hw_col2 = st.columns(2)
    
    with scrape_hw_col1:
        metier_hw = st.text_input("💼 Métier", value="data scientist", placeholder="Ex: data analyst", key="metier_hw")
        mode_hw = st.selectbox("📋 Mode", ["emploi", "stage", "alternance"], key="mode_hw")
    
    with scrape_hw_col2:
        city_hw = st.text_input("🏙️ Ville (optionnel)", placeholder="Ex: Paris", key="city_hw")
        max_pages_hw = st.slider("📄 Nombre de pages", 1, 10, 3, key="pages_hw")
    
    if st.button("🚀 LANCER LE SCRAPING HELLOWORK", use_container_width=True, type="primary", key="btn_hw"):
        with st.spinner("🔄 Scraping en cours..."):
            
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            status_text.text(f"🌐 Scraping HelloWork: {metier_hw} ({mode_hw})")
            progress_bar.progress(20)
            
            # SCRAPING RÉEL
            city_param = city_hw if city_hw.strip() else None
            offers, message = scrape_hellowork(metier_hw, mode_hw, city_param, max_pages_hw)
            
            if offers is None:
                st.error(message)
                progress_bar.empty()
                status_text.empty()
            else:
                progress_bar.progress(50)
                status_text.text(f"✅ {len(offers)} offres récupérées - Vérification des doublons...")
                
                # Vérifier doublons
                unique_offers, duplicates = check_duplicate(offers, existing_data)
                
                progress_bar.progress(75)
                status_text.text(f"📊 {len(unique_offers)} nouvelles offres détectées")
                
                if unique_offers:
                    # INSERTION DANS LA BASE DE DONNÉES
                    inserted, duplicates_db, save_message = insert_offers(unique_offers)
                    
                    progress_bar.progress(100)
                    
                    if inserted > 0:
                        st.success(f"✅ {inserted} offres importées avec succès dans la base de données!")
                        add_contribution_xp(inserted * 2)
                        st.balloons()
                        
                        # Ajouter à l'historique
                        st.session_state.contribution_history.append({
                            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                            'method': 'HelloWork Scraping',
                            'count': inserted,
                            'xp': inserted * 2
                        })
                        
                        # Stats
                        st.markdown("#### 📊 Résultats")
                        res_col1, res_col2 = st.columns(2)
                        with res_col1:
                            st.metric("✅ Nouvelles offres", inserted)
                        with res_col2:
                            st.metric("⚠️ Doublons ignorés", len(duplicates) + duplicates_db)
                        
                        st.info(save_message)
                        
                        # Preview
                        with st.expander("👁️ Voir les premières offres"):
                            st.dataframe(pd.DataFrame(unique_offers[:5]), use_container_width=True)
                        
                        # Vider le cache
                        st.cache_data.clear()
                    else:
                        st.error(save_message)
                else:
                    st.warning(f"⚠️ Aucune nouvelle offre (toutes sont des doublons)")
                    st.info(f"Total récupéré: {len(offers)} • Doublons: {len(duplicates)}")
                
                progress_bar.empty()
                status_text.empty()
    
    st.markdown('</div>', unsafe_allow_html=True)

# ============================================================================
# HISTORIQUE DES CONTRIBUTIONS
# ============================================================================

if st.session_state.contribution_history:
    st.markdown("---")
    st.markdown("### 📜 Historique de vos Contributions")
    
    history_df = pd.DataFrame(st.session_state.contribution_history)
    st.dataframe(history_df, use_container_width=True, height=300)

# ============================================================================
# FOOTER
# ============================================================================

st.markdown("---")
st.markdown(f"""
<div class="contrib-header" style="padding: 1.5rem;">
    <p style="text-align: center; color: #10b981; font-family: monospace; font-size: 1.2rem; margin: 0;">
        🎯 NIVEAU {level} • {st.session_state.xp} XP TOTAL • 
        {st.session_state.contribution_count} CONTRIBUTIONS • 
        ⏰ {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}
    </p>
</div>
""", unsafe_allow_html=True)

# ============================================================================
# BADGES ET ACHIEVEMENTS
# ============================================================================

st.markdown("### 🏆 Vos Badges")

badges_col1, badges_col2, badges_col3, badges_col4 = st.columns(4)

with badges_col1:
    if st.session_state.contribution_count >= 1:
        st.markdown("🥉 **Contributeur Débutant**")
    else:
        st.markdown("🔒 Contributeur Débutant (1 contribution)")

with badges_col2:
    if st.session_state.contribution_count >= 10:
        st.markdown("🥈 **Contributeur Actif**")
    else:
        st.markdown("🔒 Contributeur Actif (10 contributions)")

with badges_col3:
    if st.session_state.contribution_count >= 50:
        st.markdown("🥇 **Contributeur Expert**")
    else:
        st.markdown("🔒 Contributeur Expert (50 contributions)")

with badges_col4:
    if st.session_state.contribution_count >= 100:
        st.markdown("💎 **Contributeur Légendaire**")
    else:
        st.markdown("🔒 Contributeur Légendaire (100 contributions)")