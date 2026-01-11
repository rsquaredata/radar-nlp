import streamlit as st
import pandas as pd
import sys
from pathlib import Path
from datetime import datetime
import json
import os
from typing import Dict, Any, List
import re

# Charger les variables d'environnement EN PREMIER
from dotenv import load_dotenv

# Charger le .env depuis la racine du projet
PROJECT_ROOT = Path(__file__).parent.parent.parent
ENV_FILE = PROJECT_ROOT / ".env"

if ENV_FILE.exists():
    load_dotenv(ENV_FILE)
    print(f"✅ Fichier .env chargé depuis: {ENV_FILE}")
else:
    print(f"⚠️ Fichier .env non trouvé: {ENV_FILE}")

# Import
sys.path.insert(0, str(Path(__file__).parent.parent))
from utils.components import inject_premium_css, premium_navbar
from utils.db import load_offers_with_skills

# Mistral AI - NOUVELLE API
try:
    from mistralai import Mistral

    MISTRAL_AVAILABLE = True
except ImportError:
    MISTRAL_AVAILABLE = False
    st.error("⚠️ Installez mistralai: pip install mistralai")

# PyPDF2 pour lire les CV
try:
    import PyPDF2

    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False

# python-docx pour lire les CV Word
try:
    import docx

    DOCX_AVAILABLE = True
except ImportError:
    DOCX_AVAILABLE = False

# reportlab pour générer des PDF
try:
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import cm
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
    from reportlab.lib.enums import TA_JUSTIFY, TA_LEFT
    from io import BytesIO

    PDF_GENERATION_AVAILABLE = True
except ImportError:
    PDF_GENERATION_AVAILABLE = False

# ============================================================================
# CONFIG
# ============================================================================

st.set_page_config(
    page_title="Assistant IA | DataJobs",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)

inject_premium_css()
premium_navbar(active_page="Assistant")

# ============================================================================
# INITIALISATION SESSION STATE
# ============================================================================

if "cv_text" not in st.session_state:
    st.session_state.cv_text = ""
if "cv_analysis" not in st.session_state:
    st.session_state.cv_analysis = None
if "generated_letters" not in st.session_state:
    st.session_state.generated_letters = []
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# ============================================================================
# CSS ULTRA-MODERNE IA
# ============================================================================

st.markdown(
    """
<style>
    .main {
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
    }
    
    .ai-header {
        background: linear-gradient(135deg, #0f3460 0%, #16213e 100%);
        border: 4px solid #e94560;
        border-radius: 24px;
        padding: 3rem;
        margin-bottom: 2rem;
        box-shadow: 0 0 100px rgba(233, 69, 96, 0.6);
        position: relative;
        overflow: hidden;
        animation: aiPulse 4s ease-in-out infinite;
    }
    
    @keyframes aiPulse {
        0%, 100% { box-shadow: 0 0 100px rgba(233, 69, 96, 0.6); }
        50% { box-shadow: 0 0 150px rgba(233, 69, 96, 0.9); }
    }
    
    .ai-header::before {
        content: '';
        position: absolute;
        top: 0; left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(233, 69, 96, 0.4), transparent);
        animation: aiScan 3s linear infinite;
    }
    
    @keyframes aiScan {
        0% { left: -100%; }
        100% { left: 100%; }
    }
    
    .ai-title {
        font-size: 4.5rem;
        font-weight: 900;
        text-align: center;
        background: linear-gradient(135deg, #e94560 0%, #ff6b6b 50%, #ffa07a 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin: 0;
        font-family: 'Courier New', monospace;
        letter-spacing: 6px;
        animation: titleGlitch 5s ease-in-out infinite;
    }
    
    @keyframes titleGlitch {
        0%, 100% { text-shadow: 0 0 20px rgba(233, 69, 96, 0.8); }
        50% { text-shadow: 0 0 40px rgba(233, 69, 96, 1), 0 0 60px rgba(255, 107, 107, 0.8); }
    }
    
    .ai-card {
        background: linear-gradient(135deg, rgba(233, 69, 96, 0.1) 0%, rgba(255, 107, 107, 0.1) 100%);
        border: 3px solid rgba(233, 69, 96, 0.5);
        border-radius: 20px;
        padding: 2rem;
        margin-bottom: 1.5rem;
        transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
        position: relative;
        overflow: hidden;
    }
    
    .ai-card:hover {
        transform: translateY(-10px) scale(1.02);
        border-color: #e94560;
        box-shadow: 0 20px 80px rgba(233, 69, 96, 0.7);
    }
    
    .ai-card::after {
        content: '';
        position: absolute;
        top: 0; left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(233, 69, 96, 0.3), transparent);
        transition: left 0.5s;
    }
    
    .ai-card:hover::after {
        left: 100%;
    }
    
    .feature-icon {
        font-size: 4rem;
        text-align: center;
        margin-bottom: 1rem;
        animation: iconFloat 3s ease-in-out infinite;
    }
    
    @keyframes iconFloat {
        0%, 100% { transform: translateY(0) rotate(0deg); }
        50% { transform: translateY(-15px) rotate(5deg); }
    }
    
    .feature-title {
        color: #e94560;
        font-size: 2rem;
        font-weight: 900;
        text-align: center;
        margin-bottom: 1rem;
        text-transform: uppercase;
        letter-spacing: 3px;
    }
    
    .chat-message {
        background: rgba(233, 69, 96, 0.1);
        border-left: 4px solid #e94560;
        border-radius: 10px;
        padding: 1rem;
        margin: 0.5rem 0;
        animation: messageSlide 0.3s ease-out;
    }
    
    @keyframes messageSlide {
        from { transform: translateX(-20px); opacity: 0; }
        to { transform: translateX(0); opacity: 1; }
    }
    
    .letter-output {
        background: rgba(15, 52, 96, 0.8);
        border: 2px solid #e94560;
        border-radius: 15px;
        padding: 2rem;
        margin: 1rem 0;
        font-family: 'Georgia', serif;
        line-height: 1.8;
        color: #f0f0f0;
        box-shadow: 0 10px 40px rgba(233, 69, 96, 0.3);
    }
    
    .analysis-box {
        background: linear-gradient(135deg, rgba(233, 69, 96, 0.15) 0%, rgba(255, 107, 107, 0.15) 100%);
        border: 2px solid #e94560;
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1rem 0;
    }
    
    .score-badge {
        display: inline-block;
        background: linear-gradient(135deg, #e94560 0%, #ff6b6b 100%);
        color: white;
        padding: 0.5rem 1.5rem;
        border-radius: 25px;
        font-weight: 900;
        font-size: 1.2rem;
        box-shadow: 0 5px 20px rgba(233, 69, 96, 0.5);
        animation: scorePulse 2s ease-in-out infinite;
    }
    
    @keyframes scorePulse {
        0%, 100% { transform: scale(1); }
        50% { transform: scale(1.05); }
    }
    
    .typing-indicator {
        display: inline-block;
        animation: typing 1.5s ease-in-out infinite;
    }
    
    @keyframes typing {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.3; }
    }
</style>
""",
    unsafe_allow_html=True,
)

# ============================================================================
# FONCTIONS MISTRAL AI
# ============================================================================


def get_mistral_client():
    """Initialise le client Mistral AI (nouvelle API)"""
    api_key = os.getenv("MISTRAL_API_KEY")

    if not api_key:
        st.error(
            "❌ Clé API Mistral manquante. Ajoutez MISTRAL_API_KEY dans votre fichier .env"
        )
        return None

    return Mistral(api_key=api_key)


def generate_cover_letter(
    cv_text: str, job_offer: Dict[str, Any], custom_instructions: str = ""
) -> str:
    """Génère une lettre de motivation avec Mistral AI"""

    client = get_mistral_client()
    if not client:
        return "❌ Client Mistral non disponible"

    # Construire le prompt optimisé
    prompt = f"""Tu es un expert en rédaction de lettres de motivation. Tu dois générer une lettre ULTRA-PERSONNALISÉE en utilisant OBLIGATOIREMENT les vraies informations du CV et de l'offre.

**RÈGLES ABSOLUES :**
1. EXTRAIS le nom, prénom, email, téléphone, adresse du CV
2. EXTRAIS les expériences concrètes, projets, compétences du CV
3. UTILISE le nom exact de l'entreprise : {job_offer.get('company_name', 'N/A')}
4. UTILISE le titre exact du poste : {job_offer.get('title', 'N/A')}
5. MENTIONNE au moins 2-3 EXPÉRIENCES CONCRÈTES du CV (avec détails réels)
6. CITE des compétences SPÉCIFIQUES qui matchent l'offre
7. NE METS JAMAIS de placeholders comme [Votre Nom], [mentionner un projet], etc.
8. Si une info est absente du CV, NE LA MENTIONNE PAS (pas de placeholder)

**INFORMATIONS DU CV :**
{cv_text[:4000]}

**OFFRE D'EMPLOI :**
- **Entreprise :** {job_offer.get('company_name', 'N/A')}
- **Poste :** {job_offer.get('title', 'N/A')}
- **Localisation :** {job_offer.get('location', 'N/A')}
- **Type de contrat :** {job_offer.get('contract_type', 'N/A')}
- **Compétences requises :** {job_offer.get('all_skills', 'N/A')}
- **Description complète :** {job_offer.get('description', 'N/A')[:2000]}

**INSTRUCTIONS SPÉCIFIQUES :**
{custom_instructions if custom_instructions else "Aucune"}

**STRUCTURE DE LA LETTRE :**

[Prénom Nom extrait du CV]
[Adresse extraite du CV]
[Email extrait du CV]
[Téléphone extrait du CV]

{datetime.now().strftime('%d %B %Y')}

À l'attention du Service Recrutement
{job_offer.get('company_name', '[Entreprise]')}
{job_offer.get('location', '')}

Objet : Candidature au poste de {job_offer.get('title', '[Poste]')}

Madame, Monsieur,

[INTRODUCTION : 2-3 phrases]
- Mentionne le poste exact et l'entreprise
- Exprime motivation et adéquation avec le profil recherché
- Cite 1 compétence clé qui matche

[PARAGRAPHE 1 : Expériences et compétences - 5-6 phrases]
- Cite AU MOINS 2 EXPÉRIENCES CONCRÈTES du CV avec détails (entreprise, projet, résultats)
- Mentionne des TECHNOLOGIES/OUTILS SPÉCIFIQUES du CV qui correspondent à l'offre
- Quantifie si possible (durée, résultats, impact)
- Montre comment ces expériences préparent pour le poste

[PARAGRAPHE 2 : Motivation et adéquation - 4-5 phrases]
- Explique pourquoi cette entreprise et ce poste en particulier
- Cite des éléments de la description de l'offre qui résonnent
- Mentionne 1-2 projets ou réalisations du CV en lien
- Montre compréhension des enjeux du poste

[CONCLUSION : 2-3 phrases]
- Disponibilité pour entretien
- Formule de politesse

[Prénom Nom]

**EXEMPLE DE CE QUI EST ATTENDU :**
Au lieu de : "lors de [mentionner un projet]"
Écris : "lors de mon stage chez Google où j'ai développé un modèle de NLP avec BERT"

Au lieu de : "[Votre formation]"
Écris : "mon Master en Data Science à l'Université Paris-Saclay"

**GÉNÈRE MAINTENANT LA LETTRE COMPLÈTE avec TOUTES les vraies informations extraites du CV :**"""

    try:
        # Appel à Mistral AI (nouvelle API)
        response = client.chat.complete(
            model="mistral-large-latest",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=2500,
        )

        return response.choices[0].message.content

    except Exception as e:
        return f"❌ Erreur lors de la génération: {str(e)}"


def analyze_cv(cv_text: str) -> Dict[str, Any]:
    """Analyse le CV avec Mistral AI"""

    client = get_mistral_client()
    if not client:
        return {"error": "Client Mistral non disponible"}

    prompt = f"""Analyse ce CV en profondeur et retourne une analyse JSON structurée.

**CV :**
{cv_text[:4000]}

**FORMAT DE RÉPONSE (JSON uniquement) :**
{{
    "competences_techniques": ["liste des compétences techniques identifiées"],
    "competences_transversales": ["soft skills identifiés"],
    "experience_totale_annees": nombre d'années d'expérience estimé,
    "niveau_etudes": "niveau d'études le plus élevé",
    "domaines_expertise": ["domaines d'expertise principaux"],
    "points_forts": ["3-5 points forts du candidat"],
    "points_amelioration": ["2-3 suggestions d'amélioration"],
    "score_global": note sur 100,
    "resume_profil": "résumé du profil en 2-3 phrases"
}}

Réponds UNIQUEMENT avec le JSON, rien d'autre."""

    try:
        response = client.chat.complete(
            model="mistral-large-latest",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=1500,
        )

        content = response.choices[0].message.content

        # Extraire le JSON de la réponse
        json_match = re.search(r"\{.*\}", content, re.DOTALL)
        if json_match:
            return json.loads(json_match.group())
        else:
            return {"error": "Format JSON invalide"}

    except Exception as e:
        return {"error": f"Erreur: {str(e)}"}


def match_cv_offer(cv_text: str, job_offer: Dict[str, Any]) -> Dict[str, Any]:
    """Calcule le matching entre CV et offre"""

    client = get_mistral_client()
    if not client:
        return {"error": "Client Mistral non disponible"}

    prompt = f"""Évalue la correspondance entre ce CV et cette offre d'emploi. Retourne une analyse JSON.

**CV :**
{cv_text[:2000]}

**OFFRE :**
- Titre : {job_offer.get('title', 'N/A')}
- Compétences : {job_offer.get('all_skills', 'N/A')}
- Description : {job_offer.get('description', 'N/A')[:1000]}

**FORMAT DE RÉPONSE (JSON) :**
{{
    "score_matching": note sur 100,
    "competences_matchees": ["compétences du CV qui correspondent"],
    "competences_manquantes": ["compétences requises absentes du CV"],
    "points_positifs": ["3-4 points positifs du matching"],
    "points_attention": ["2-3 points d'attention"],
    "recommandations": ["3-4 recommandations pour améliorer les chances"],
    "verdict": "EXCELLENT / BON / MOYEN / FAIBLE"
}}

JSON uniquement."""

    try:
        response = client.chat.complete(
            model="mistral-large-latest",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=1500,
        )

        content = response.choices[0].message.content
        json_match = re.search(r"\{.*\}", content, re.DOTALL)

        if json_match:
            return json.loads(json_match.group())
        else:
            return {"error": "Format invalide"}

    except Exception as e:
        return {"error": f"Erreur: {str(e)}"}


def chat_with_ai(message: str, context: str = "") -> str:
    """Chat avec l'assistant IA"""

    client = get_mistral_client()
    if not client:
        return "❌ Client Mistral non disponible"

    system_prompt = f"""Tu es un coach carrière expert en data science et IA. Tu aides les candidats avec :
- Conseils carrière personnalisés
- Préparation aux entretiens
- Stratégies de recherche d'emploi
- Développement de compétences

{f"CONTEXTE: {context}" if context else ""}

Sois précis, encourageant et actionnable."""

    try:
        response = client.chat.complete(
            model="mistral-large-latest",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": message},
            ],
            temperature=0.7,
            max_tokens=1000,
        )

        return response.choices[0].message.content

    except Exception as e:
        return f"❌ Erreur: {str(e)}"


# ============================================================================
# FONCTIONS DE LECTURE CV
# ============================================================================


def read_pdf(file) -> str:
    """Lit un fichier PDF"""
    if not PDF_AVAILABLE:
        return "❌ PyPDF2 non installé. Installez: pip install PyPDF2"

    try:
        pdf_reader = PyPDF2.PdfReader(file)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text() + "\n"
        return text
    except Exception as e:
        return f"❌ Erreur lecture PDF: {str(e)}"


def read_docx(file) -> str:
    """Lit un fichier Word"""
    if not DOCX_AVAILABLE:
        return "❌ python-docx non installé. Installez: pip install python-docx"

    try:
        doc = docx.Document(file)
        text = "\n".join([para.text for para in doc.paragraphs])
        return text
    except Exception as e:
        return f"❌ Erreur lecture DOCX: {str(e)}"


def read_txt(file) -> str:
    """Lit un fichier texte"""
    try:
        return file.read().decode("utf-8")
    except:
        return file.read().decode("latin-1")


def generate_pdf(letter_text: str, company_name: str = "entreprise") -> bytes:
    """Génère un PDF formaté à partir de la lettre"""
    if not PDF_GENERATION_AVAILABLE:
        return None

    try:
        # Créer buffer
        buffer = BytesIO()

        # Créer document
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=2 * cm,
            leftMargin=2 * cm,
            topMargin=2 * cm,
            bottomMargin=2 * cm,
        )

        # Styles
        styles = getSampleStyleSheet()

        # Style personnalisé pour le corps
        style_normal = ParagraphStyle(
            "CustomNormal",
            parent=styles["Normal"],
            fontSize=11,
            leading=16,
            alignment=TA_JUSTIFY,
            spaceAfter=12,
        )

        # Style pour l'en-tête
        style_header = ParagraphStyle(
            "CustomHeader",
            parent=styles["Normal"],
            fontSize=10,
            leading=14,
            alignment=TA_LEFT,
            spaceAfter=6,
        )

        # Construire le contenu
        story = []

        # Séparer le texte en paragraphes
        paragraphs = letter_text.split("\n\n")

        for i, para_text in enumerate(paragraphs):
            if para_text.strip():
                # Les 5 premières lignes sont l'en-tête (coordonnées)
                if i < 5:
                    para = Paragraph(para_text.replace("\n", "<br/>"), style_header)
                else:
                    para = Paragraph(para_text.replace("\n", "<br/>"), style_normal)

                story.append(para)
                story.append(Spacer(1, 0.3 * cm))

        # Construire le PDF
        doc.build(story)

        # Récupérer les bytes
        pdf_bytes = buffer.getvalue()
        buffer.close()

        return pdf_bytes

    except Exception as e:
        print(f"Erreur génération PDF: {e}")
        return None


# ============================================================================
# HEADER
# ============================================================================

st.markdown(
    """
<div class="ai-header">
    <h1 class="ai-title">🤖 ASSISTANT IA CARRIÈRE</h1>
    <p style="text-align: center; color: #e94560; font-family: monospace; font-size: 1.4rem; margin-top: 1.5rem; font-weight: 700;">
        > POWERED BY MISTRAL AI • LETTRES DE MOTIVATION • ANALYSE CV • MATCHING • CONSEILS
    </p>
</div>
""",
    unsafe_allow_html=True,
)

# Vérification Mistral AI
if not MISTRAL_AVAILABLE:
    st.error("⚠️ **Mistral AI non disponible.** Installez avec: `pip install mistralai`")
    st.stop()

# Vérification clé API avec diagnostic
mistral_key = os.getenv("MISTRAL_API_KEY")
env_file_exists = ENV_FILE.exists()

if not mistral_key:
    st.error("⚠️ **Clé API Mistral manquante.**")

    st.markdown("### 🔍 Diagnostic")

    diag_col1, diag_col2 = st.columns(2)

    with diag_col1:
        if env_file_exists:
            st.success(f"✅ Fichier .env trouvé : `{ENV_FILE}`")
        else:
            st.error(f"❌ Fichier .env introuvable : `{ENV_FILE}`")

    with diag_col2:
        if mistral_key:
            st.success("✅ Variable MISTRAL_API_KEY chargée")
        else:
            st.error("❌ Variable MISTRAL_API_KEY absente")

    st.markdown("### 💡 Solution")
    st.info(
        f"""
**Ajoutez votre clé API Mistral dans le fichier `.env` :**

1. Créez/Éditez le fichier : `{ENV_FILE}`
2. Ajoutez la ligne : `MISTRAL_API_KEY=votre_cle_ici`
3. Sauvegardez et **rechargez la page** (F5)

**Obtenir une clé API :** https://console.mistral.ai/
    """
    )

    st.stop()

st.success(
    f"✅ **Mistral AI connecté et prêt !** (Clé : {mistral_key[:8]}...{mistral_key[-4:]})"
)

# ============================================================================
# TABS PRINCIPALES
# ============================================================================

tab1, tab2, tab3, tab4 = st.tabs(
    [
        "📝 Générer Lettre de Motivation",
        "📄 Analyser mon CV",
        "🎯 Matching CV/Offre",
        "💬 Chat avec l'IA",
    ]
)

# ============================================================================
# TAB 1: GÉNÉRATION LETTRE DE MOTIVATION
# ============================================================================

with tab1:
    st.markdown('<div class="ai-card">', unsafe_allow_html=True)
    st.markdown('<div class="feature-icon">✍️</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="feature-title">Générateur de Lettre de Motivation</div>',
        unsafe_allow_html=True,
    )

    st.markdown("### 📤 1. Importez votre CV")

    cv_file = st.file_uploader(
        "Choisissez votre CV",
        type=["pdf", "docx", "txt"],
        help="Formats acceptés: PDF, Word, TXT",
    )

    if cv_file:
        # Lire le CV
        file_extension = cv_file.name.split(".")[-1].lower()

        with st.spinner("📖 Lecture du CV..."):
            if file_extension == "pdf":
                cv_text = read_pdf(cv_file)
            elif file_extension == "docx":
                cv_text = read_docx(cv_file)
            else:
                cv_text = read_txt(cv_file)

        st.session_state.cv_text = cv_text

        if cv_text and not cv_text.startswith("❌"):
            st.success(f"✅ CV chargé ({len(cv_text)} caractères)")

            with st.expander("👁️ Aperçu du CV"):
                st.text_area(
                    "Contenu",
                    cv_text[:1000] + "..." if len(cv_text) > 1000 else cv_text,
                    height=200,
                )

    st.markdown("---")
    st.markdown("### 🎯 2. Sélectionnez une offre d'emploi")

    # Charger les offres
    offers_df = load_offers_with_skills()

    if not offers_df.empty:
        # Filtres rapides
        filter_col1, filter_col2 = st.columns(2)

        with filter_col1:
            search_term = st.text_input(
                "🔍 Recherche", placeholder="data scientist, machine learning..."
            )

        with filter_col2:
            region_filter = st.selectbox(
                "🗺️ Région",
                ["Toutes"]
                + sorted(offers_df["region_name"].dropna().unique().tolist()),
            )

        # Filtrer
        filtered_offers = offers_df.copy()

        if search_term:
            filtered_offers = filtered_offers[
                filtered_offers["title"].str.contains(search_term, case=False, na=False)
                | filtered_offers["description"].str.contains(
                    search_term, case=False, na=False
                )
            ]

        if region_filter != "Toutes":
            filtered_offers = filtered_offers[
                filtered_offers["region_name"] == region_filter
            ]

        st.info(f"📊 {len(filtered_offers)} offres disponibles")

        # Sélection de l'offre
        if not filtered_offers.empty:
            offer_titles = filtered_offers.apply(
                lambda row: f"{row['title']} - {row['company_name']} ({row['region_name']})",
                axis=1,
            ).tolist()

            selected_offer_idx = st.selectbox(
                "Choisissez une offre",
                range(len(offer_titles)),
                format_func=lambda x: offer_titles[x],
            )

            selected_offer = filtered_offers.iloc[selected_offer_idx].to_dict()

            # Afficher l'offre
            with st.expander("📋 Détails de l'offre sélectionnée", expanded=True):
                st.markdown(f"### 🎯 {selected_offer.get('title', 'N/A')}")

                detail_col1, detail_col2 = st.columns(2)

                with detail_col1:
                    st.markdown(
                        f"**🏢 Entreprise:** {selected_offer.get('company_name', 'N/A')}"
                    )
                    st.markdown(
                        f"**📍 Localisation:** {selected_offer.get('location', 'N/A')}"
                    )
                    st.markdown(
                        f"**📋 Contrat:** {selected_offer.get('contract_type', 'N/A')}"
                    )

                with detail_col2:
                    st.markdown(
                        f"**🏠 Télétravail:** {selected_offer.get('remote', 'N/A')}"
                    )
                    st.markdown(
                        f"**💰 Salaire:** {selected_offer.get('salary', 'Non renseigné')}"
                    )
                    st.markdown(
                        f"**🎯 Compétences:** {selected_offer.get('skills_count', 0)}"
                    )

                if selected_offer.get("all_skills"):
                    st.markdown("**💼 Compétences requises:**")
                    st.info(selected_offer["all_skills"])

                if selected_offer.get("description"):
                    st.markdown("**📄 Description de l'offre:**")
                    # Afficher la description complète
                    desc_text = selected_offer["description"]
                    if len(desc_text) > 500:
                        st.text_area("", desc_text, height=300, disabled=True)
                    else:
                        st.text_area("", desc_text, height=150, disabled=True)

                st.success(
                    "✅ Ces informations seront utilisées par Mistral AI pour personnaliser votre lettre"
                )

    st.markdown("---")
    st.markdown("### ⚙️ 3. Personnalisez (optionnel)")

    custom_instructions = st.text_area(
        "Instructions spécifiques",
        placeholder="Ex: Mets l'accent sur mon expérience en machine learning, mentionne ma passion pour l'IA...",
        height=100,
    )

    st.markdown("---")

    # Génération
    if st.button(
        "✨ GÉNÉRER LA LETTRE DE MOTIVATION", use_container_width=True, type="primary"
    ):
        if not st.session_state.cv_text:
            st.error("⚠️ Veuillez d'abord charger votre CV")
        elif not selected_offer:
            st.error("⚠️ Veuillez sélectionner une offre")
        else:
            with st.spinner("🤖 L'IA Mistral rédige votre lettre... ✍️"):
                letter = generate_cover_letter(
                    st.session_state.cv_text, selected_offer, custom_instructions
                )

                if not letter.startswith("❌"):
                    st.success("✅ Lettre de motivation générée avec succès !")

                    st.markdown('<div class="letter-output">', unsafe_allow_html=True)
                    st.markdown(letter)
                    st.markdown("</div>", unsafe_allow_html=True)

                    # Sauvegarder
                    st.session_state.generated_letters.append(
                        {
                            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                            "offer": selected_offer.get("title", "N/A"),
                            "company": selected_offer.get("company_name", "N/A"),
                            "letter": letter,
                        }
                    )

                    # Téléchargement
                    dl_col1, dl_col2 = st.columns(2)

                    with dl_col1:
                        # Téléchargement TXT
                        st.download_button(
                            "📄 Télécharger en TXT",
                            letter,
                            file_name=f"lettre_motivation_{selected_offer.get('company_name', 'entreprise').replace(' ', '_')}_{datetime.now().strftime('%Y%m%d')}.txt",
                            mime="text/plain",
                            use_container_width=True,
                        )

                    with dl_col2:
                        # Téléchargement PDF
                        if PDF_GENERATION_AVAILABLE:
                            pdf_bytes = generate_pdf(
                                letter, selected_offer.get("company_name", "entreprise")
                            )

                            if pdf_bytes:
                                st.download_button(
                                    "📕 Télécharger en PDF",
                                    pdf_bytes,
                                    file_name=f"lettre_motivation_{selected_offer.get('company_name', 'entreprise').replace(' ', '_')}_{datetime.now().strftime('%Y%m%d')}.pdf",
                                    mime="application/pdf",
                                    use_container_width=True,
                                )
                            else:
                                st.error("❌ Erreur génération PDF")
                        else:
                            st.warning(
                                "⚠️ PDF non disponible. Installez: pip install reportlab"
                            )
                else:
                    st.error(letter)

    st.markdown("</div>", unsafe_allow_html=True)

# ============================================================================
# TAB 2: ANALYSE CV
# ============================================================================

with tab2:
    st.markdown('<div class="ai-card">', unsafe_allow_html=True)
    st.markdown('<div class="feature-icon">🔍</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="feature-title">Analyse Approfondie de CV</div>',
        unsafe_allow_html=True,
    )

    st.markdown("### 📤 Importez votre CV")

    cv_file_analysis = st.file_uploader(
        "Choisissez votre CV",
        type=["pdf", "docx", "txt"],
        key="cv_file_for_analysis",  # ← Clé différente
    )

    if cv_file_analysis:
        file_extension = cv_file_analysis.name.split(".")[-1].lower()

        with st.spinner("📖 Lecture du CV..."):
            if file_extension == "pdf":
                cv_text_analysis = read_pdf(cv_file_analysis)
            elif file_extension == "docx":
                cv_text_analysis = read_docx(cv_file_analysis)
            else:
                cv_text_analysis = read_txt(cv_file_analysis)

        if cv_text_analysis and not cv_text_analysis.startswith("❌"):
            st.success("✅ CV chargé")

            if st.button(
                "🔍 ANALYSER MON CV", use_container_width=True, type="primary"
            ):
                with st.spinner("🤖 Analyse en cours par l'IA Mistral..."):
                    analysis = analyze_cv(cv_text_analysis)

                    if "error" not in analysis:
                        st.session_state.cv_analysis = analysis

                        st.success("✅ Analyse terminée !")

                        # Afficher l'analyse
                        st.markdown(
                            '<div class="analysis-box">', unsafe_allow_html=True
                        )

                        # Score global
                        score = analysis.get("score_global", 0)
                        st.markdown(
                            f"<div style='text-align: center; margin: 2rem 0;'>"
                            f"<div class='score-badge'>SCORE GLOBAL: {score}/100</div>"
                            f"</div>",
                            unsafe_allow_html=True,
                        )

                        # Résumé profil
                        st.markdown("### 👤 Résumé du Profil")
                        st.info(analysis.get("resume_profil", "N/A"))

                        # Colonnes
                        col1, col2 = st.columns(2)

                        with col1:
                            st.markdown("### ✅ Points Forts")
                            for point in analysis.get("points_forts", []):
                                st.markdown(f"- {point}")

                            st.markdown("### 💼 Compétences Techniques")
                            skills = analysis.get("competences_techniques", [])
                            st.write(", ".join(skills[:15]))

                        with col2:
                            st.markdown("### 🎯 Points d'Amélioration")
                            for point in analysis.get("points_amelioration", []):
                                st.markdown(f"- {point}")

                            st.markdown("### 🌟 Soft Skills")
                            soft_skills = analysis.get("competences_transversales", [])
                            st.write(", ".join(soft_skills[:10]))

                        # Infos générales
                        info_col1, info_col2, info_col3 = st.columns(3)

                        with info_col1:
                            st.metric(
                                "📚 Niveau d'études",
                                analysis.get("niveau_etudes", "N/A"),
                            )

                        with info_col2:
                            st.metric(
                                "⏳ Expérience",
                                f"{analysis.get('experience_totale_annees', 0)} ans",
                            )

                        with info_col3:
                            domaines = analysis.get("domaines_expertise", [])
                            st.metric("🎯 Domaines", len(domaines))

                        st.markdown("### 🚀 Domaines d'Expertise")
                        st.write(", ".join(analysis.get("domaines_expertise", [])))

                        st.markdown("</div>", unsafe_allow_html=True)
                    else:
                        st.error(f"❌ {analysis.get('error')}")

    st.markdown("</div>", unsafe_allow_html=True)

# ============================================================================
# TAB 3: MATCHING CV/OFFRE
# ============================================================================

with tab3:
    st.markdown('<div class="ai-card">', unsafe_allow_html=True)
    st.markdown('<div class="feature-icon">🎯</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="feature-title">Matching CV / Offre</div>', unsafe_allow_html=True
    )

    st.markdown("### 📤 1. Votre CV")

    cv_file_match = st.file_uploader(
        "Choisissez votre CV",
        type=["pdf", "docx", "txt"],
        key="cv_file_for_match",  # ← Clé unique
    )

    cv_text_match = ""

    if cv_file_match:
        file_extension = cv_file_match.name.split(".")[-1].lower()

        with st.spinner("📖 Lecture..."):
            if file_extension == "pdf":
                cv_text_match = read_pdf(cv_file_match)
            elif file_extension == "docx":
                cv_text_match = read_docx(cv_file_match)
            else:
                cv_text_match = read_txt(cv_file_match)

        if cv_text_match and not cv_text_match.startswith("❌"):
            st.success("✅ CV chargé")

    st.markdown("### 🎯 2. Offre d'emploi")

    offers_df_match = load_offers_with_skills()

    if not offers_df_match.empty:
        offer_titles_match = offers_df_match.apply(
            lambda row: f"{row['title']} - {row['company_name']}", axis=1
        ).tolist()

        selected_offer_match_idx = st.selectbox(
            "Choisissez une offre",
            range(len(offer_titles_match)),
            format_func=lambda x: offer_titles_match[x],
            key="offer_select_for_match",  # ← Clé unique
        )

        selected_offer_match = offers_df_match.iloc[selected_offer_match_idx].to_dict()

        st.markdown("---")

        if st.button(
            "🎯 CALCULER LE MATCHING", use_container_width=True, type="primary"
        ):
            if not cv_text_match:
                st.error("⚠️ Veuillez charger votre CV")
            else:
                with st.spinner("🤖 Calcul du matching en cours..."):
                    matching = match_cv_offer(cv_text_match, selected_offer_match)

                    if "error" not in matching:
                        st.success("✅ Matching calculé !")

                        st.markdown(
                            '<div class="analysis-box">', unsafe_allow_html=True
                        )

                        # Score
                        score = matching.get("score_matching", 0)
                        verdict = matching.get("verdict", "MOYEN")

                        verdict_colors = {
                            "EXCELLENT": "#10b981",
                            "BON": "#3b82f6",
                            "MOYEN": "#f59e0b",
                            "FAIBLE": "#ef4444",
                        }

                        st.markdown(
                            f"<div style='text-align: center; margin: 2rem 0;'>"
                            f"<div style='background: {verdict_colors.get(verdict, '#f59e0b')}; "
                            f"color: white; padding: 1rem 2rem; border-radius: 25px; "
                            f"font-weight: 900; font-size: 1.5rem; display: inline-block;'>"
                            f"{verdict}: {score}/100</div>"
                            f"</div>",
                            unsafe_allow_html=True,
                        )

                        # Détails
                        col1, col2 = st.columns(2)

                        with col1:
                            st.markdown("### ✅ Compétences Matchées")
                            for skill in matching.get("competences_matchees", []):
                                st.markdown(f"- ✔️ {skill}")

                            st.markdown("### 🌟 Points Positifs")
                            for point in matching.get("points_positifs", []):
                                st.markdown(f"- {point}")

                        with col2:
                            st.markdown("### ⚠️ Compétences Manquantes")
                            for skill in matching.get("competences_manquantes", []):
                                st.markdown(f"- ❌ {skill}")

                            st.markdown("### ⚡ Points d'Attention")
                            for point in matching.get("points_attention", []):
                                st.markdown(f"- {point}")

                        st.markdown("### 💡 Recommandations")
                        for rec in matching.get("recommandations", []):
                            st.info(f"💡 {rec}")

                        st.markdown("</div>", unsafe_allow_html=True)
                    else:
                        st.error(f"❌ {matching.get('error')}")

    st.markdown("</div>", unsafe_allow_html=True)

# ============================================================================
# TAB 4: CHAT IA
# ============================================================================

with tab4:
    st.markdown('<div class="ai-card">', unsafe_allow_html=True)
    st.markdown('<div class="feature-icon">💬</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="feature-title">Chat avec votre Coach IA</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        "Posez vos questions sur votre carrière, la préparation d'entretiens, les stratégies de recherche d'emploi..."
    )

    # Afficher l'historique
    if st.session_state.chat_history:
        st.markdown("### 💬 Conversation")
        for msg in st.session_state.chat_history:
            if msg["role"] == "user":
                st.markdown(
                    f"<div class='chat-message' style='border-left-color: #3b82f6;'>"
                    f"<b>👤 Vous:</b> {msg['content']}</div>",
                    unsafe_allow_html=True,
                )
            else:
                st.markdown(
                    f"<div class='chat-message' style='border-left-color: #e94560;'>"
                    f"<b>🤖 Assistant:</b> {msg['content']}</div>",
                    unsafe_allow_html=True,
                )

    # Input
    user_message = st.text_area(
        "Votre message",
        placeholder="Ex: Comment puis-je améliorer mes chances d'obtenir un poste de Data Scientist ?",
        height=100,
    )

    col1, col2 = st.columns([3, 1])

    with col1:
        if st.button("💬 ENVOYER", use_container_width=True, type="primary"):
            if user_message:
                # Ajouter message utilisateur
                st.session_state.chat_history.append(
                    {"role": "user", "content": user_message}
                )

                # Contexte CV si disponible
                context = ""
                if st.session_state.cv_text:
                    context = f"Le candidat a un CV de {len(st.session_state.cv_text)} caractères."

                # Réponse IA
                with st.spinner("🤖 L'assistant réfléchit..."):
                    response = chat_with_ai(user_message, context)

                    # Ajouter réponse
                    st.session_state.chat_history.append(
                        {"role": "assistant", "content": response}
                    )

                    st.rerun()

    with col2:
        if st.button("🗑️ Effacer", use_container_width=True):
            st.session_state.chat_history = []
            st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)

# ============================================================================
# FOOTER
# ============================================================================

st.markdown("---")
st.markdown(
    f"""
<div class="ai-header" style="padding: 1.5rem;">
    <p style="text-align: center; color: #e94560; font-family: monospace; font-size: 1.2rem; margin: 0; font-weight: 700;">
        🤖 POWERED BY MISTRAL AI • {len(st.session_state.generated_letters)} LETTRES GÉNÉRÉES • 
        ⏰ {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}
    </p>
</div>
""",
    unsafe_allow_html=True,
)
