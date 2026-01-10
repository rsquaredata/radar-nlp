"""
Script de scraping HelloWork - Version refactorisée
Utilise la configuration centralisée depuis config_metiers.py
"""

import sys
from pathlib import Path

# Ajout du dossier scrapers au path
sys.path.insert(0, str(Path(__file__).parent))

from hellowork_html_improved import scrape_hellowork

# Import de la configuration centralisée
from config_metiers import (
    DATA_AI_KEYWORDS,
    CONFIG_SOURCES,
    get_stats,
)


def main():
    """
    Lance le scraping HelloWork avec la configuration centralisée.
    """
    print("=" * 80)
    print("SCRAPING HELLOWORK - DATA & IA")
    print("=" * 80)
    print()
    
    # Récupérer la configuration depuis config_metiers.py
    config = CONFIG_SOURCES["hellowork"]
    stats = get_stats()
    
    print("📊 Configuration :")
    print(f"   • Mots-clés : {stats['total_keywords']}")
    print(f"   • Zone : France entière")
    print(f"   • Type : Emploi (CDI/CDD)")
    print(f"   • Pages max par mot-clé : {config['max_pages']}")
    print(f"   • URLs max : {config['max_urls']}")
    print(f"   • Délai entre requêtes : {config['sleep_seconds']}s")
    print()
    
    print("🔍 Exemples de mots-clés :")
    for kw in DATA_AI_KEYWORDS[:10]:
        print(f"   • {kw}")
    if len(DATA_AI_KEYWORDS) > 10:
        print(f"   ... et {len(DATA_AI_KEYWORDS) - 10} autres")
    print()
    
    print("🚀 Lancement du scraping...")
    print()
    
    # Lancer le scraping avec la config centralisée
    result = scrape_hellowork(
        keywords=DATA_AI_KEYWORDS,
        city=None,  # France entière
        postal=None,
        mode="emploi",
        max_pages=config["max_pages"],
        max_urls=config["max_urls"],
        sleep_s=config["sleep_seconds"],
        out_dir="./data",
    )
    
    print()
    print("=" * 80)
    print("SCRAPING TERMINÉ")
    print("=" * 80)
    print()
    
    print(f"📊 Résultats :")
    print(f"   • Offres collectées : {result['count']}")
    print(f"   • Fichier JSONL : {result['jsonl']}")
    print(f"   • Fichier CSV : {result['csv']}")
    print()
    
    # Aperçu de la première offre
    if result['count'] > 0:
        print("👁️ Aperçu de la première offre :")
        print("-" * 80)
        
        import pandas as pd
        try:
            df = pd.read_csv(result['csv'])
            
            first_offer = df.iloc[0]
            print(f"Titre       : {first_offer['title']}")
            print(f"Entreprise  : {first_offer['employer']}")
            print(f"Location    : {first_offer['location']}")
            print(f"Contrat     : {first_offer['contract_type']}")
            print(f"Salaire     : {first_offer['salary']}")
            print(f"Remote      : {first_offer['remote']}")
            print()
            print(f"Description (300 premiers caractères) :")
            desc = str(first_offer['description'])[:300]
            print(desc)
            if len(str(first_offer['description'])) > 300:
                print("...")
        except Exception as e:
            print(f"⚠️ Erreur lecture CSV : {e}")
        
        print("-" * 80)
    
    print()
    print("✅ Les descriptions sont nettoyées (sans HTML/navigation)")
    print()


def scrape_by_city(city: str, postal: str = None, max_pages: int = 10):
    """
    Scraping ciblé sur une ville spécifique.
    
    Args:
        city: Nom de la ville
        postal: Code postal (optionnel)
        max_pages: Nombre de pages max
    """
    config = CONFIG_SOURCES["hellowork"]
    
    print(f"🎯 Scraping ciblé : {city}" + (f" ({postal})" if postal else ""))
    print()
    
    result = scrape_hellowork(
        keywords=DATA_AI_KEYWORDS,
        city=city,
        postal=postal,
        mode="emploi",
        max_pages=max_pages,
        max_urls=500,  # Moins d'URLs pour une ville
        sleep_s=config["sleep_seconds"],
        out_dir="./data",
    )
    
    print(f"✅ {result['count']} offres collectées pour {city}")
    return result


def scrape_stage():
    """Scraping des stages Data & IA."""
    config = CONFIG_SOURCES["hellowork"]
    
    print("🎓 Scraping des STAGES Data & IA")
    print()
    
    result = scrape_hellowork(
        keywords=DATA_AI_KEYWORDS,
        city=None,
        postal=None,
        mode="stage",  # Mode stage
        max_pages=20,
        max_urls=800,
        sleep_s=config["sleep_seconds"],
        out_dir="./data",
    )
    
    print(f"✅ {result['count']} stages collectés")
    return result


def scrape_alternance():
    """Scraping des alternances Data & IA."""
    config = CONFIG_SOURCES["hellowork"]
    
    print("🎒 Scraping des ALTERNANCES Data & IA")
    print()
    
    result = scrape_hellowork(
        keywords=DATA_AI_KEYWORDS,
        city=None,
        postal=None,
        mode="alternance",  # Mode alternance
        max_pages=20,
        max_urls=800,
        sleep_s=config["sleep_seconds"],
        out_dir="./data",
    )
    
    print(f"✅ {result['count']} alternances collectées")
    return result


# ============================================================================
# CLI
# ============================================================================

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Scraping HelloWork - Data & IA")
    parser.add_argument(
        "--mode",
        choices=["emploi", "stage", "alternance", "all"],
        default="emploi",
        help="Type d'offres à scraper"
    )
    parser.add_argument(
        "--city",
        type=str,
        help="Scraper une ville spécifique (ex: Paris)"
    )
    parser.add_argument(
        "--postal",
        type=str,
        help="Code postal (ex: 75)"
    )
    
    args = parser.parse_args()
    
    # Exécution selon le mode
    if args.city:
        # Scraping ciblé ville
        scrape_by_city(args.city, args.postal)
    elif args.mode == "all":
        # Scraping complet (emploi + stage + alternance)
        print("🚀 Scraping COMPLET (emploi + stage + alternance)")
        print()
        main()
        scrape_stage()
        scrape_alternance()
    elif args.mode == "stage":
        scrape_stage()
    elif args.mode == "alternance":
        scrape_alternance()
    else:
        # Scraping emploi (défaut)
        main()