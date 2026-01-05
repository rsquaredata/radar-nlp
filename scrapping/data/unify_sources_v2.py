#!/usr/bin/env python3
"""
FUSION DES SOURCES - Script complet
Fusionne France Travail, HelloWork et Adzuna (si disponible)
en un fichier unifié avec schéma commun.

Usage:
    python unify_sources.py
    
    Ou spécifier les fichiers :
    python unify_sources.py --ft france_travail.csv --hw hellowork.csv --az adzuna.csv
"""

import pandas as pd
from pathlib import Path
import argparse
import sys


# ============================================================================
# SCHÉMA UNIFIÉ (colonnes communes à toutes les sources)
# ============================================================================

UNIFIED_SCHEMA = {
    'uid': str,              # Identifiant unique : SOURCE_ID (ex: FT_12345)
    'source': str,           # Nom de la source
    'source_url': str,       # URL de l'offre
    'offer_id': str,         # ID original de l'offre
    'title': str,            # Titre du poste
    'company': str,          # Entreprise
    'location': str,         # Localisation
    'contract_type': str,    # Type de contrat (normalisé)
    'salary': str,           # Salaire
    'remote': str,           # Télétravail (yes/no/unknown)
    'published_date': str,   # Date de publication
    'description': str,      # Description complète
    'query': str,            # Mot-clé de recherche (si applicable)
}


# ============================================================================
# FONCTIONS DE NORMALISATION
# ============================================================================

def normalize_contract(contract_str):
    """
    Normalise les types de contrats en catégories standards.
    
    Entrées possibles : "CDI", "cdi", "Contrat à durée indéterminée", etc.
    Sorties : "CDI", "CDD", "Stage", "Alternance", "Intérim", "Freelance"
    """
    if pd.isna(contract_str):
        return None
    
    contract = str(contract_str).upper().strip()
    
    # Mapping
    if 'CDI' in contract or 'INDÉTERMINÉE' in contract or 'INDETERMINEE' in contract:
        return 'CDI'
    elif 'CDD' in contract or 'DÉTERMINÉE' in contract or 'DETERMINEE' in contract:
        return 'CDD'
    elif 'STAGE' in contract:
        return 'Stage'
    elif 'ALTERNANCE' in contract or 'APPRENTISSAGE' in contract or 'PROFESSIONNALISATION' in contract:
        return 'Alternance'
    elif 'INTERIM' in contract or 'INTÉRIM' in contract or 'TEMPORAIRE' in contract:
        return 'Intérim'
    elif 'FREELANCE' in contract or 'INDÉPENDANT' in contract or 'INDEPENDANT' in contract:
        return 'Freelance'
    else:
        return contract  # Garder l'original si pas reconnu


def normalize_remote(remote_str):
    """
    Normalise l'information télétravail.
    
    Entrées : "yes", "no", "unknown", "complet", "partiel", etc.
    Sorties : "yes", "no", "unknown"
    """
    if pd.isna(remote_str):
        return 'unknown'
    
    remote = str(remote_str).lower().strip()
    
    if remote in ['yes', 'oui', 'complet', 'total', 'full', 'remote']:
        return 'yes'
    elif remote in ['no', 'non', 'aucun', 'sur site', 'onsite']:
        return 'no'
    elif remote in ['partiel', 'hybride', 'occasionnel', 'hybrid']:
        return 'hybrid'
    else:
        return 'unknown'


def normalize_salary(salary_str):
    """Normalise le format des salaires"""
    if pd.isna(salary_str):
        return None
    return str(salary_str).strip()


# ============================================================================
# CHARGEMENT PAR SOURCE
# ============================================================================

def load_france_travail(file_path):
    """
    Charge et normalise France Travail au schéma unifié.
    
    Colonnes attendues :
    - source, offer_id, url, title, company, location, 
      published_date, contract_type, salary, query, description
    """
    print("📂 Chargement France Travail...")
    df = pd.read_csv(file_path)
    
    print(f"   Colonnes trouvées : {list(df.columns)}")
    
    # Mapping vers schéma unifié
    df_unified = pd.DataFrame({
        'uid': 'FT_' + df['offer_id'].astype(str),
        'source': 'France Travail',
        'source_url': df['url'],
        'offer_id': df['offer_id'].astype(str),
        'title': df['title'],
        'company': df['company'],
        'location': df['location'],
        'contract_type': df['contract_type'].apply(normalize_contract),
        'salary': df['salary'].apply(normalize_salary),
        'remote': 'unknown',  # France Travail n'a pas cette info
        'published_date': df['published_date'],
        'description': df['description'],
        'query': df.get('query', None)
    })
    
    print(f"   ✅ {len(df_unified):,} offres France Travail")
    return df_unified


def load_hellowork(file_path):
    """
    Charge et normalise HelloWork au schéma unifié.
    
    Colonnes attendues :
    - source, url, offer_id, title, employer, location, 
      contract_type, salary, remote, published_relative, description
    """
    print("📂 Chargement HelloWork...")
    df = pd.read_csv(file_path)
    
    print(f"   Colonnes trouvées : {list(df.columns)}")
    
    # Mapping vers schéma unifié
    df_unified = pd.DataFrame({
        'uid': 'HW_' + df['offer_id'].astype(str),
        'source': 'HelloWork',
        'source_url': df['url'],
        'offer_id': df['offer_id'].astype(str),
        'title': df['title'],
        'company': df.get('employer', df.get('company')),  # employer ou company
        'location': df['location'],
        'contract_type': df['contract_type'].apply(normalize_contract),
        'salary': df['salary'].apply(normalize_salary),
        'remote': df.get('remote', 'unknown').apply(normalize_remote),
        'published_date': df.get('published_relative', None),
        'description': df['description'],
        'query': None  # HelloWork n'a pas de query
    })
    
    print(f"   ✅ {len(df_unified):,} offres HelloWork")
    return df_unified


def load_adzuna(file_path):
    """
    Charge et normalise Adzuna au schéma unifié.
    
    Colonnes attendues :
    - source, offer_id, url, title, company, location, 
      contract_type, salary, published_date, query, raw_text/description
    """
    print("📂 Chargement Adzuna...")
    
    if not Path(file_path).exists():
        print("   ⚠️  Fichier Adzuna non trouvé")
        return pd.DataFrame()
    
    df = pd.read_csv(file_path)
    
    print(f"   Colonnes trouvées : {list(df.columns)}")
    
    # Déterminer la colonne description
    desc_col = 'raw_text' if 'raw_text' in df.columns else 'description'
    
    # Mapping vers schéma unifié
    df_unified = pd.DataFrame({
        'uid': 'AZ_' + df['offer_id'].astype(str),
        'source': 'Adzuna',
        'source_url': df['url'],
        'offer_id': df['offer_id'].astype(str),
        'title': df['title'],
        'company': df['company'],
        'location': df['location'],
        'contract_type': df.get('contract_type', None).apply(normalize_contract) if 'contract_type' in df else None,
        'salary': df.get('salary', None).apply(normalize_salary) if 'salary' in df else None,
        'remote': 'unknown',
        'published_date': df.get('published_date', df.get('created', None)),
        'description': df[desc_col],
        'query': df.get('query', None)
    })
    
    print(f"   ✅ {len(df_unified):,} offres Adzuna")
    return df_unified


# ============================================================================
# FONCTION PRINCIPALE
# ============================================================================

def main():
    parser = argparse.ArgumentParser(description="Fusion des sources d'offres d'emploi")
    parser.add_argument('--ft', default='france_travail.csv', help="Fichier France Travail")
    parser.add_argument('--hw', default='hellowork_emploi_france_clean.csv', help="Fichier HelloWork")
    parser.add_argument('--az', default='adzuna_fr_data_ia.csv', help="Fichier Adzuna")
    parser.add_argument('-o', '--output', default='unified_offers.csv', help="Fichier de sortie")
    
    args = parser.parse_args()
    
    print("=" * 80)
    print("🔄 FUSION DES SOURCES D'OFFRES D'EMPLOI")
    print("=" * 80)
    print()
    
    # Liste des DataFrames à fusionner
    dfs = []
    
    # Charger France Travail
    if Path(args.ft).exists():
        try:
            dfs.append(load_france_travail(args.ft))
        except Exception as e:
            print(f"   ❌ Erreur : {e}")
    else:
        print(f"⚠️  {args.ft} introuvable")
    
    print()
    
    # Charger HelloWork
    if Path(args.hw).exists():
        try:
            dfs.append(load_hellowork(args.hw))
        except Exception as e:
            print(f"   ❌ Erreur : {e}")
    else:
        print(f"⚠️  {args.hw} introuvable")
    
    print()
    
    # Charger Adzuna (optionnel)
    if Path(args.az).exists():
        try:
            df_az = load_adzuna(args.az)
            if len(df_az) > 0:
                dfs.append(df_az)
        except Exception as e:
            print(f"   ❌ Erreur : {e}")
    else:
        print(f"ℹ️  {args.az} introuvable (normal si scraping en cours)")
    
    print()
    
    # Vérifier qu'on a au moins une source
    if not dfs:
        print("❌ ERREUR : Aucun fichier source trouvé !")
        print()
        print("💡 Vérifie que les fichiers sont dans le dossier courant :")
        print(f"   - {args.ft}")
        print(f"   - {args.hw}")
        print(f"   - {args.az} (optionnel)")
        sys.exit(1)
    
    # Fusion
    print("🔄 Fusion des sources...")
    df_unified = pd.concat(dfs, ignore_index=True)
    
    # Supprimer les doublons éventuels (même offer_id)
    before_dedup = len(df_unified)
    df_unified = df_unified.drop_duplicates(subset=['uid'], keep='first')
    after_dedup = len(df_unified)
    
    if before_dedup > after_dedup:
        print(f"   ℹ️  {before_dedup - after_dedup} doublons supprimés")
    
    print()
    print("=" * 80)
    print("📊 RÉSULTAT FINAL")
    print("=" * 80)
    print()
    
    # Statistiques globales
    print(f"✅ TOTAL : {len(df_unified):,} offres uniques")
    print()
    
    # Par source
    print("📊 Répartition par source :")
    for source, count in df_unified['source'].value_counts().items():
        pct = (count / len(df_unified)) * 100
        print(f"   • {source:20} {count:5,} offres ({pct:.1f}%)")
    
    print()
    
    # Par type de contrat
    print("📊 Répartition par type de contrat :")
    contract_counts = df_unified['contract_type'].value_counts()
    for contract, count in contract_counts.head(8).items():
        pct = (count / len(df_unified)) * 100
        print(f"   • {contract:20} {count:5,} offres ({pct:.1f}%)")
    
    print()
    
    # Télétravail
    print("🏠 Télétravail :")
    remote_counts = df_unified['remote'].value_counts()
    for remote, count in remote_counts.items():
        pct = (count / len(df_unified)) * 100
        print(f"   • {remote:20} {count:5,} offres ({pct:.1f}%)")
    
    print()
    
    # Qualité des données
    desc_count = df_unified['description'].notna().sum()
    desc_pct = (desc_count / len(df_unified)) * 100
    print(f"📝 Descriptions disponibles : {desc_count:,}/{len(df_unified):,} ({desc_pct:.1f}%)")
    
    company_count = df_unified['company'].notna().sum()
    company_pct = (company_count / len(df_unified)) * 100
    print(f"🏢 Entreprises renseignées : {company_count:,}/{len(df_unified):,} ({company_pct:.1f}%)")
    
    salary_count = df_unified['salary'].notna().sum()
    salary_pct = (salary_count / len(df_unified)) * 100
    print(f"💰 Salaires renseignés : {salary_count:,}/{len(df_unified):,} ({salary_pct:.1f}%)")
    
    print()
    
    # Aperçu
    print("👀 APERÇU (premières lignes) :")
    print("-" * 80)
    preview_cols = ['source', 'title', 'company', 'location', 'contract_type']
    print(df_unified[preview_cols].head(5).to_string(index=False))
    
    print()
    print("-" * 80)
    
    # Sauvegarder
    print()
    print(f"💾 Sauvegarde dans : {args.output}")
    df_unified.to_csv(args.output, index=False, encoding='utf-8')
    print(f"   ✅ {len(df_unified):,} lignes sauvegardées")
    
    print()
    print("=" * 80)
    print("✅ FUSION TERMINÉE AVEC SUCCÈS")
    print("=" * 80)
    print()
    print("🎯 PROCHAINE ÉTAPE :")
    print(f"   python apply_skills_extraction.py -i {args.output}")
    print()


if __name__ == "__main__":
    main()