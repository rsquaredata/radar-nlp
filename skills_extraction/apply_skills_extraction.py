import argparse
import pandas as pd
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent))

from skills_extractor import extract_skills_from_dataframe, get_global_skills_stats


def main():
    parser = argparse.ArgumentParser(description="Extraction de compétences sur données scrapées")
    parser.add_argument('-i', '--input', required=True, help="Fichier CSV d'entrée")
    parser.add_argument('-o', '--output', help="Fichier CSV de sortie (défaut: input_with_skills.csv)")
    parser.add_argument('--text-column', default='description', help="Colonne contenant le texte")
    
    args = parser.parse_args()
    
    if not args.output:
        input_path = Path(args.input)
        args.output = str(input_path.parent / f"{input_path.stem}_with_skills.csv")
    
    print("=" * 80)
    print("🔍 EXTRACTION DE COMPÉTENCES ET SAVOIR-ÊTRE")
    print("=" * 80)
    print()
    print(f"📂 Fichier d'entrée  : {args.input}")
    print(f"💾 Fichier de sortie : {args.output}")
    print()
    
    # Charger données
    print("📂 Chargement...")
    df = pd.read_csv(args.input)
    print(f"   ✅ {len(df):,} lignes chargées")
    print()
    
    # Vérifier colonne description
    if args.text_column not in df.columns:
        print(f"❌ Colonne '{args.text_column}' introuvable")
        print(f"   Colonnes disponibles: {', '.join(df.columns)}")
        return
    
    # Extraction
    df_enriched = extract_skills_from_dataframe(df, text_column=args.text_column)
    
    # Stats globales
    print()
    print("📊 STATISTIQUES GLOBALES")
    print("-" * 80)
    
    stats = get_global_skills_stats(df_enriched)
    
    print(f"   • Compétences techniques : {stats['total_competences']}")
    print(f"   • Savoir-être : {stats['total_savoir_etre']}")
    print(f"   • Mentions totales : {stats['total_mentions']:,}")
    print(f"   • Moyenne par offre : {stats['avg_skills_per_offer']:.1f}")
    print(f"   • Médiane par offre : {stats['median_skills_per_offer']:.0f}")
    
    print()
    print("🏆 TOP 15 COMPÉTENCES TECHNIQUES:")
    for skill, count in stats['top_competences'][:15]:
        pct = (count / len(df_enriched)) * 100
        print(f"   • {skill:25} {count:4} offres ({pct:.1f}%)")
    
    print()
    print("🌟 TOP 15 SAVOIR-ÊTRE:")
    for skill, count in stats['top_savoir_etre'][:15]:
        pct = (count / len(df_enriched)) * 100
        print(f"   • {skill:25} {count:4} offres ({pct:.1f}%)")
    
    # Sauvegarder
    print()
    print(f"💾 Sauvegarde dans : {args.output}")
    
    df_enriched.to_csv(args.output, index=False, encoding='utf-8')
    
    print(f"   ✅ Sauvegardé : {len(df_enriched):,} lignes")
    
    # Aperçu
    print()
    print("👀 APERÇU (première offre):")
    print("-" * 80)
    first_row = df_enriched.iloc[0]
    print(f"Titre: {first_row.get('title', 'N/A')}")
    print(f"Compétences ({len(first_row['competences'])}): {', '.join(first_row['competences'][:10])}")
    if len(first_row['competences']) > 10:
        print(f"   ... et {len(first_row['competences']) - 10} autres")
    print(f"Savoir-être ({len(first_row['savoir_etre'])}): {', '.join(first_row['savoir_etre'][:5])}")
    if len(first_row['savoir_etre']) > 5:
        print(f"   ... et {len(first_row['savoir_etre']) - 5} autres")
    
    print()
    print("=" * 80)
    print("✅ TRAITEMENT TERMINÉ")
    print("=" * 80)


if __name__ == "__main__":
    main()