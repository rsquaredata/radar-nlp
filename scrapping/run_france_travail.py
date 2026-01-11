
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List

import pandas as pd

from france_travail_api import FranceTravailClient

# Import de la configuration centralisée
from config_metiers import (
    DATA_AI_QUERIES_FT,
    CONFIG_SOURCES,
    get_stats,
    categorize_job,
)


OUT_DIR = Path("../data")
OUT_DIR.mkdir(parents=True, exist_ok=True)


def save_jsonl(rows: List[Dict[str, Any]], path: Path) -> None:
    """Sauvegarde les données en JSONL."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")


def save_csv(rows: List[Dict[str, Any]], path: Path) -> None:
    """Sauvegarde les données en CSV."""
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        pd.DataFrame([]).to_csv(path, index=False, encoding="utf-8")
        return
    df = pd.DataFrame(rows)
    if "description" in df.columns:
        df["description"] = df["description"].astype(str).str.slice(0, 4000)
    df.to_csv(path, index=False, encoding="utf-8")


def normalize_ft(rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Normalise les offres France Travail."""
    out = []
    for r in rows:
        out.append(
            {
                "source": r.get("source", "france-travail-api"),
                "offer_id": r.get("offer_id"),
                "url": r.get("url"),
                "title": r.get("title"),
                "company": r.get("company"),
                "location": r.get("location"),
                "published_date": r.get("published_date"),
                "contract_type": r.get("contract_type"),
                "salary": r.get("salary"),
                "query": r.get("query"),
                "description": r.get("description"),
            }
        )
    return out


def add_categories(rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Ajoute la catégorisation des métiers."""
    for r in rows:
        title = r.get("title", "")
        description = r.get("description", "")
        r["category"] = categorize_job(title, description)
    return rows


def print_stats(rows: List[Dict[str, Any]]) -> None:
    """Affiche les statistiques de collecte."""
    if not rows:
        print("❌ Aucune offre collectée")
        return
    
    print()
    print("=" * 80)
    print("STATISTIQUES")
    print("=" * 80)
    print()
    
    # Total
    print(f"📊 Total : {len(rows)} offres")
    print()
    
    # Par catégorie
    df = pd.DataFrame(rows)
    
    if "category" in df.columns:
        print("📁 Répartition par catégorie :")
        cat_counts = df["category"].value_counts()
        for cat, count in cat_counts.items():
            pct = (count / len(rows)) * 100
            print(f"   • {cat:20} : {count:4} offres ({pct:5.1f}%)")
        print()
    
    # Par type de contrat
    if "contract_type" in df.columns:
        print("📋 Répartition par contrat :")
        contract_counts = df["contract_type"].value_counts().head(5)
        for contract, count in contract_counts.items():
            pct = (count / len(rows)) * 100
            print(f"   • {contract:20} : {count:4} offres ({pct:5.1f}%)")
        print()
    
    # Top 5 villes
    if "location" in df.columns:
        print("🏙️ Top 5 localisations :")
        loc_counts = df["location"].value_counts().head(5)
        for loc, count in loc_counts.items():
            pct = (count / len(rows)) * 100
            loc_str = str(loc)[:30]
            print(f"   • {loc_str:30} : {count:4} offres ({pct:5.1f}%)")
        print()


def main() -> None:
    """
    Collecte principale des offres France Travail.
    Utilise la configuration centralisée.
    """
    print("=" * 80)
    print("COLLECTE FRANCE TRAVAIL API - DATA & IA")
    print("=" * 80)
    print()
    
    # Configuration depuis config_metiers.py
    config = CONFIG_SOURCES["france_travail"]
    stats = get_stats()
    
    print("📊 Configuration :")
    print(f"   • Requêtes : {stats['total_queries_ft']}")
    print(f"   • Max par requête : {config['max_per_query']}")
    print(f"   • Chunk size : {config['chunk_size']}")
    print(f"   • Filtre local : {'✅' if config['use_local_filter'] else '❌'}")
    print(f"   • Détails : {'✅' if config['fetch_details'] else '❌'}")
    print()
    
    print("🔍 Exemples de requêtes :")
    for q in DATA_AI_QUERIES_FT[:10]:
        print(f"   • {q}")
    if len(DATA_AI_QUERIES_FT) > 10:
        print(f"   ... et {len(DATA_AI_QUERIES_FT) - 10} autres")
    print()
    
    print("🚀 Lancement de la collecte...")
    print()
    
    # Initialiser le client
    try:
        ft = FranceTravailClient()
    except Exception as e:
        print(f"❌ Erreur initialisation : {e}")
        return
    
    # Collecter les offres
    try:
        rows = ft.collect_data_ai_offers(
            queries=DATA_AI_QUERIES_FT,  # Config centralisée
            max_per_query=config["max_per_query"],
            chunk=config["chunk_size"],
            fetch_detail=config["fetch_details"],
            local_filter=config["use_local_filter"],
        )
    except Exception as e:
        print(f"❌ Erreur collecte : {e}")
        return
    
    print()
    print(f"✅ {len(rows)} offres collectées")
    
    # Normaliser
    rows = normalize_ft(rows)
    
    # Ajouter catégorisation
    rows = add_categories(rows)
    
    # Sauvegarder
    save_jsonl(rows, OUT_DIR / "france_travail.jsonl")
    save_csv(rows, OUT_DIR / "france_travail.csv")
    
    print()
    print("💾 Fichiers sauvegardés :")
    print(f"   • JSONL : {(OUT_DIR / 'france_travail.jsonl').resolve()}")
    print(f"   • CSV   : {(OUT_DIR / 'france_travail.csv').resolve()}")
    
    # Statistiques
    print_stats(rows)
    
    # Aperçu
    if rows:
        print()
        print("👁️ Aperçu de la première offre :")
        print("-" * 80)
        first = rows[0]
        print(f"Titre       : {first.get('title')}")
        print(f"Entreprise  : {first.get('company')}")
        print(f"Location    : {first.get('location')}")
        print(f"Contrat     : {first.get('contract_type')}")
        print(f"Salaire     : {first.get('salary')}")
        print(f"Catégorie   : {first.get('category')}")
        print(f"Requête     : {first.get('query')}")
        print()
        desc = str(first.get('description', ''))[:300]
        print(f"Description : {desc}...")
        print("-" * 80)
    
    print()
    print("=" * 80)
    print("COLLECTE TERMINÉE")
    print("=" * 80)


def collect_by_query(query: str, max_results: int = 200) -> List[Dict[str, Any]]:
    """
    Collecte ciblée sur une seule requête.
    
    Args:
        query: Requête de recherche
        max_results: Nombre max de résultats
    
    Returns:
        Liste d'offres
    """
    print(f"🎯 Collecte ciblée : '{query}'")
    print()
    
    ft = FranceTravailClient()
    config = CONFIG_SOURCES["france_travail"]
    
    rows = ft.collect_data_ai_offers(
        queries=[query],  # Une seule requête
        max_per_query=max_results,
        chunk=config["chunk_size"],
        fetch_detail=config["fetch_details"],
        local_filter=config["use_local_filter"],
    )
    
    print(f"✅ {len(rows)} offres collectées pour '{query}'")
    return rows


def collect_by_location(query: str, location: str, max_results: int = 100) -> List[Dict[str, Any]]:
    """
    Collecte ciblée sur une localisation.
    
    Args:
        query: Requête (ex: "data scientist")
        location: Localisation (ex: "Paris")
        max_results: Nombre max de résultats
    
    Returns:
        Liste d'offres
    """
    print(f"📍 Collecte : '{query}' à {location}")
    print()
    
    ft = FranceTravailClient()
    
    # Recherche avec localisation
    params = {
        "motsCles": query,
        "commune": location,
    }
    
    offers = ft.search_all(params=params, max_results=max_results)
    
    rows = []
    for o in offers:
        try:
            if ft.collect_data_ai_offers.__defaults__[2]:  # fetch_detail
                detail = ft.detail(o["id"])
                norm = ft.normalize_offer(detail, query=query)
            else:
                norm = ft.normalize_offer(o, query=query)
            rows.append(norm)
        except Exception:
            continue
    
    print(f"✅ {len(rows)} offres collectées à {location}")
    return rows


# ============================================================================
# CLI
# ============================================================================

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Collecte France Travail - Data & IA")
    parser.add_argument(
        "--query",
        type=str,
        help="Requête spécifique (ex: 'data scientist')"
    )
    parser.add_argument(
        "--location",
        type=str,
        help="Localisation (ex: 'Paris')"
    )
    parser.add_argument(
        "--max",
        type=int,
        default=600,
        help="Nombre max de résultats par requête"
    )
    
    args = parser.parse_args()
    
    if args.query and args.location:
        # Collecte ciblée avec localisation
        rows = collect_by_location(args.query, args.location, args.max)
        if rows:
            save_csv(rows, OUT_DIR / f"ft_{args.query}_{args.location}.csv")
    elif args.query:
        # Collecte sur une seule requête
        rows = collect_by_query(args.query, args.max)
        if rows:
            save_csv(rows, OUT_DIR / f"ft_{args.query}.csv")
    else:
        # Collecte complète (défaut)
        main()