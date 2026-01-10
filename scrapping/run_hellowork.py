import sys
from pathlib import Path

# Ajout du dossier scrapers au path
sys.path.insert(0, str(Path(__file__).parent / "scrapers"))

from hellowork_html_improved import scrape_hellowork


# Mots-clés Data & IA (optimisés pour HelloWork)
DATA_IA_KEYWORDS = [
    # Métiers Data
    "data scientist",
    "data analyst", 
    "data engineer",
    "data architect",
    
    # Business Intelligence
    "business intelligence",
    "bi developer",
    
    # Machine Learning / IA
    "machine learning",
    "deep learning",
    "intelligence artificielle",
    
    # Big Data
    "big data",
    "spark",
]


def main():
    print("=" * 80)
    print("SCRAPING HELLOWORK ")
    print("=" * 80)
    print()
    print("Configuration :")
    print(f"• Mots-clés : {len(DATA_IA_KEYWORDS)}")
    print(f"• Zone : France entière")
    print(f"• Type : Emploi (CDI/CDD)")
    print(f"• Objectif : ~500-1000 offres")
    print()
    print("Lancement du scraping... )")
    print()
    
    result = scrape_hellowork(
        keywords=DATA_IA_KEYWORDS,
        city=None,  # France entière
        postal=None,
        mode="emploi",
        max_pages=30,  
        max_urls=1500,  
        sleep_s=0.5,  
        out_dir="./data",
    )
    
    print()
    print("=" * 80)
    print("SCRAPING TERMINÉ")
    print("=" * 80)
    print()
    print(f"Résultats :")
    print(f"• Offres collectées : {result['count']}")
    print(f"• Fichier JSONL : {result['jsonl']}")
    print(f"• Fichier CSV : {result['csv']}")
    print()
    print("Les descriptions sont maintenant PROPRES (sans HTML/navigation)")
    print()
    
    # Affichons un aperçu
    if result['count'] > 0:
        print("Aperçu de la première offre :")
        print("-" * 80)
        
        import pandas as pd
        df = pd.read_csv(result['csv'])
        
        first_offer = df.iloc[0]
        print(f"Titre : {first_offer['title']}")
        print(f"Entreprise : {first_offer['employer']}")
        print(f"Localisation : {first_offer['location']}")
        print(f"Contrat : {first_offer['contract_type']}")
        print(f"Salaire : {first_offer['salary']}")
        print()
        print(f"Description (500 premiers caractères) :")
        desc = str(first_offer['description'])[:500]
        print(desc)
        if len(str(first_offer['description'])) > 500:
            print("...")
        print("-" * 80)


if __name__ == "__main__":
    main()