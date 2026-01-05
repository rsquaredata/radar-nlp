import argparse
import json
import re
import pandas as pd
from pathlib import Path
from typing import Optional, Tuple
import unicodedata


class GeographicEnricher:
    """Enrichisseur géographique"""
    
    def __init__(self, regions_file: str = "regions_france.json"):
        regions_path = Path(__file__).parent / regions_file
        
        with open(regions_path, 'r', encoding='utf-8') as f:
            self.data = json.load(f)
        
        self.regions = self.data['regions']
        self.dept_mapping = self.data['departement_to_region']
    
    def extract_region(self, location: str) -> Tuple[Optional[str], Optional[float], Optional[float]]:
        """Extrait la région depuis une location"""
        if not location or not isinstance(location, str):
            return None, None, None
        
        location_lower = location.lower().strip()
        location_normalized = self._normalize(location_lower)
        
        # 1. Extraction département (75, 69, 13, etc.)
        dept_match = re.search(r'\b(\d{2,3}|2[AB])\b', location)
        if dept_match:
            dept = dept_match.group(1)
            if dept in self.dept_mapping:
                region_name = self.dept_mapping[dept]
                region_data = self.regions[region_name]
                return region_name, region_data['latitude'], region_data['longitude']
        
        # 2. Recherche par nom de ville
        for region_name, region_data in self.regions.items():
            for ville in region_data['villes_principales']:
                ville_norm = self._normalize(ville.lower())
                if ville_norm in location_normalized or location_normalized in ville_norm:
                    return region_name, region_data['latitude'], region_data['longitude']
        
        # 3. Recherche nom de région
        for region_name in self.regions.keys():
            region_norm = self._normalize(region_name.lower())
            if region_norm in location_normalized:
                region_data = self.regions[region_name]
                return region_name, region_data['latitude'], region_data['longitude']
        
        return None, None, None
    
    def _normalize(self, text: str) -> str:
        """Normalise le texte (enlève accents, tirets)"""
        # Enlever accents
        text = unicodedata.normalize('NFKD', text)
        text = ''.join(c for c in text if not unicodedata.combining(c))
        # Enlever tirets, apostrophes
        text = re.sub(r"[-']", ' ', text)
        return text.lower().strip()
    
    def enrich_dataframe(self, df: pd.DataFrame, location_column: str = 'location') -> pd.DataFrame:
        """Enrichit un DataFrame"""
        print(f"🗺️  Enrichissement géographique sur {len(df):,} offres...")
        
        if location_column not in df.columns:
            print(f"⚠️  Colonne '{location_column}' introuvable")
            return df
        
        results = df[location_column].apply(self.extract_region)
        
        df['region'] = results.apply(lambda x: x[0])
        df['region_lat'] = results.apply(lambda x: x[1])
        df['region_lon'] = results.apply(lambda x: x[2])
        
        total = len(df)
        with_region = df['region'].notna().sum()
        coverage = (with_region / total) * 100 if total > 0 else 0
        
        print(f"   ✅ Régions identifiées : {with_region:,}/{total:,} ({coverage:.1f}%)")
        
        if with_region > 0:
            print()
            print("📊 Répartition par région :")
            top_regions = df['region'].value_counts().head(10)
            for region, count in top_regions.items():
                pct = (count / total) * 100
                print(f"   • {region:30} {count:4,} offres ({pct:.1f}%)")
        
        missing = df[df['region'].isna()]
        if len(missing) > 0:
            print()
            print(f"⚠️  {len(missing):,} offres sans région identifiée")
            print("   Exemples :")
            for loc in missing[location_column].dropna().head(5):
                print(f"   - {loc}")
        
        return df


def main():
    parser = argparse.ArgumentParser(description="Enrichissement géographique")
    parser.add_argument('-i', '--input', required=True, help="Fichier CSV d'entrée")
    parser.add_argument('-o', '--output', help="Fichier CSV de sortie")
    parser.add_argument('--location-column', default='location', help="Colonne location")
    
    args = parser.parse_args()
    
    if not args.output:
        input_path = Path(args.input)
        args.output = str(input_path.parent / f"{input_path.stem}_final.csv")
    
    print("=" * 80)
    print("🗺️  ENRICHISSEMENT GÉOGRAPHIQUE")
    print("=" * 80)
    print()
    print(f"📂 Fichier d'entrée  : {args.input}")
    print(f"💾 Fichier de sortie : {args.output}")
    print()
    
    # Charger
    print("📂 Chargement...")
    df = pd.read_csv(args.input)
    print(f"   ✅ {len(df):,} lignes chargées")
    print()
    
    # Enrichir
    enricher = GeographicEnricher()
    df_enriched = enricher.enrich_dataframe(df, location_column=args.location_column)
    
    # Sauvegarder
    print()
    print(f"💾 Sauvegarde dans : {args.output}")
    df_enriched.to_csv(args.output, index=False, encoding='utf-8')
    print(f"   ✅ Sauvegardé : {len(df_enriched):,} lignes")
    
    # Aperçu
    print()
    print("👀 APERÇU (première offre avec région) :")
    print("-" * 80)
    with_region = df_enriched[df_enriched['region'].notna()]
    if len(with_region) > 0:
        first = with_region.iloc[0]
        print(f"Titre    : {first.get('title', 'N/A')}")
        print(f"Location : {first.get('location', 'N/A')}")
        print(f"Région   : {first['region']}")
        print(f"GPS      : {first['region_lat']:.4f}, {first['region_lon']:.4f}")
    
    print()
    print("=" * 80)
    print("✅ ENRICHISSEMENT TERMINÉ")
    print("=" * 80)


if __name__ == "__main__":
    main()