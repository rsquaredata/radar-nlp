"""
Configuration centralisée des métiers et mots-clés pour le scraping
Data Science, IA, ML, Big Data

Usage:
    from config_metiers import DATA_AI_KEYWORDS, DATA_AI_QUERIES_FT, DATA_AI_REGEX
"""

from typing import List
import re

# ============================================================================
# MOTS-CLÉS GÉNÉRIQUES (pour HelloWork et autres scrapers HTML)
# ============================================================================

DATA_AI_KEYWORDS: List[str] = [
    # ===== MÉTIERS DATA =====
    "data scientist",
    "data analyst",
    "data engineer",
    "data architect",
    "ingénieur données",
    "ingénieur data",
    "chef de projet data",
    "data manager",
    
    # ===== BUSINESS INTELLIGENCE =====
    "business intelligence",
    "bi developer",
    "bi analyst",
    "analyste décisionnel",
    "décisionnel",
    
    # ===== MACHINE LEARNING / IA =====
    "machine learning",
    "machine learning engineer",
    "ml engineer",
    "deep learning",
    "intelligence artificielle",
    "ingénieur ia",
    "ingénieur machine learning",
    "ai engineer",
    "nlp engineer",
    "computer vision",
    
    # ===== BIG DATA =====
    "big data",
    "big data engineer",
    "spark",
    "hadoop",
    "data platform",
    
    # ===== SPÉCIALITÉS =====
    "statisticien",
    "data mining",
    "predictive analytics",
    "mlops",
    "data ops",
]


# ============================================================================
# REQUÊTES OPTIMISÉES POUR FRANCE TRAVAIL API
# ============================================================================

DATA_AI_QUERIES_FT: List[str] = [
    # ===== Métiers data =====
    "data scientist",
    "data analyst",
    "data engineer",
    "data architect",
    "business intelligence",
    "bi developer",
    "analyste décisionnel",
    "statisticien",
    "statistician",
    "quant",
    
    # ===== IA / ML =====
    "machine learning",
    "machine learning engineer",
    "ml engineer",
    "deep learning",
    "computer vision",
    "nlp",
    "ingénieur ia",
    "ingenieur ia",
    "ai engineer",
    
    # ===== LLM / GenAI (nouveaux) =====
    "llm",
    "rag",
    "transformers",
    "chatbot",
    "gpt",
    "generative ai",
    
    # ===== Skills techniques (rattrapage) =====
    "python data",
    "python sql",
    "spark",
    "pyspark",
    "airflow",
    "dbt",
    "tensorflow",
    "pytorch",
    "databricks",
    "snowflake",
    
    # ===== Big Data =====
    "big data",
    "hadoop",
    "kafka",
    "data platform",
    
    # ===== MLOps =====
    "mlops",
    "ml engineer",
    "data ops",
]


# ============================================================================
# REGEX DE FILTRAGE LOCAL (pour éliminer le bruit)
# ============================================================================

DATA_AI_KEYWORDS_REGEX = re.compile(
    r"\b("
    # Métiers Data
    r"data\s*(scientist|analyst|engineer|architect|science|platform|warehouse|mining)|"
    
    # ML/DL/IA
    r"machine\s*learning|deep\s*learning|\bml\b|\bai\b|"
    r"nlp|computer\s*vision|vision\b|"
    r"intelligence\s*artificielle|ingénieur\s*ia|ingenieur\s*ia|"
    
    # LLM/GenAI
    r"llm|rag|transformers?|gpt|chatbot|generative|"
    
    # BI
    r"business\s*intelligence|\bbi\b|décisionnel|decisionnel|"
    
    # Big Data
    r"big\s*data|hadoop|spark|kafka|"
    
    # Skills techniques
    r"python|sql|spark|pyspark|airflow|dbt|tensorflow|pytorch|"
    r"databricks|snowflake|pandas|numpy|scikit|"
    
    # MLOps
    r"mlops|data\s*ops|kubeflow|mlflow"
    r")\b",
    flags=re.IGNORECASE,
)


# ============================================================================
# CATÉGORISATION DES MÉTIERS (pour analyse ultérieure)
# ============================================================================

CATEGORIES_METIERS = {
    "data_science": [
        "data scientist",
        "machine learning",
        "deep learning",
        "ai engineer",
        "nlp",
        "computer vision",
    ],
    
    "data_engineering": [
        "data engineer",
        "data architect",
        "big data",
        "spark",
        "hadoop",
        "kafka",
        "airflow",
        "data platform",
    ],
    
    "data_analysis": [
        "data analyst",
        "business intelligence",
        "bi developer",
        "analyste décisionnel",
        "statisticien",
    ],
    
    "mlops": [
        "mlops",
        "ml engineer",
        "data ops",
        "mlflow",
        "kubeflow",
    ],
    
    "gen_ai": [
        "llm",
        "rag",
        "chatbot",
        "gpt",
        "transformers",
        "generative ai",
    ],
}


# ============================================================================
# CONFIGURATION PAR SOURCE
# ============================================================================

CONFIG_SOURCES = {
    "hellowork": {
        "keywords": DATA_AI_KEYWORDS,
        "max_pages": 30,
        "max_urls": 1500,
        "sleep_seconds": 0.5,
        "use_local_filter": True,
    },
    
    "france_travail": {
        "queries": DATA_AI_QUERIES_FT,
        "max_per_query": 600,
        "chunk_size": 150,
        "use_local_filter": True,
        "fetch_details": True,
    },
}


# ============================================================================
# FONCTIONS UTILITAIRES
# ============================================================================

def get_keywords_for_source(source: str) -> List[str]:
    """
    Retourne les mots-clés appropriés pour une source donnée.
    
    Args:
        source: 'hellowork' ou 'france_travail'
    
    Returns:
        Liste de mots-clés
    """
    if source.lower() == "hellowork":
        return DATA_AI_KEYWORDS
    elif source.lower() in ["france_travail", "francetravail", "france-travail"]:
        return DATA_AI_QUERIES_FT
    else:
        return DATA_AI_KEYWORDS


def is_data_ai_job(text: str) -> bool:
    """
    Vérifie si un texte correspond à un job Data/IA.
    
    Args:
        text: Titre ou description de l'offre
    
    Returns:
        True si le job est Data/IA
    """
    if not text:
        return False
    return bool(DATA_AI_KEYWORDS_REGEX.search(text))


def categorize_job(title: str, description: str = "") -> str:
    """
    Catégorise un job selon son titre et sa description.
    
    Args:
        title: Titre du poste
        description: Description du poste (optionnel)
    
    Returns:
        Catégorie du métier ('data_science', 'data_engineering', etc.) ou 'other'
    """
    text = f"{title} {description}".lower()
    
    # Parcourir les catégories par ordre de priorité
    for category, keywords in CATEGORIES_METIERS.items():
        for keyword in keywords:
            if keyword.lower() in text:
                return category
    
    return "other"


# ============================================================================
# STATISTIQUES
# ============================================================================

def get_stats() -> dict:
    """Retourne les statistiques de configuration."""
    return {
        "total_keywords": len(DATA_AI_KEYWORDS),
        "total_queries_ft": len(DATA_AI_QUERIES_FT),
        "categories": len(CATEGORIES_METIERS),
        "sources": list(CONFIG_SOURCES.keys()),
    }


# ============================================================================
# EXEMPLE D'UTILISATION
# ============================================================================

if __name__ == "__main__":
    print("=" * 80)
    print("CONFIGURATION MÉTIERS DATA & IA")
    print("=" * 80)
    print()
    
    stats = get_stats()
    print(f"📊 Statistiques :")
    print(f"   • Mots-clés HelloWork : {len(DATA_AI_KEYWORDS)}")
    print(f"   • Requêtes France Travail : {len(DATA_AI_QUERIES_FT)}")
    print(f"   • Catégories de métiers : {len(CATEGORIES_METIERS)}")
    print(f"   • Sources configurées : {', '.join(CONFIG_SOURCES.keys())}")
    print()
    
    print("🔍 Exemples de mots-clés :")
    print(f"   • HelloWork : {', '.join(DATA_AI_KEYWORDS[:5])}...")
    print(f"   • France Travail : {', '.join(DATA_AI_QUERIES_FT[:5])}...")
    print()
    
    print("📁 Catégories :")
    for cat, keywords in CATEGORIES_METIERS.items():
        print(f"   • {cat:20} : {len(keywords)} mots-clés")
    print()
    
    # Test de filtrage
    test_titles = [
        "Data Scientist Senior",
        "Développeur Java",
        "Machine Learning Engineer",
        "Comptable",
    ]
    
    print("🧪 Tests de filtrage :")
    for title in test_titles:
        is_match = is_data_ai_job(title)
        category = categorize_job(title)
        print(f"   • '{title}' : {'✅' if is_match else '❌'} → {category}")