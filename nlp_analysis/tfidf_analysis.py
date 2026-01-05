import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from collections import defaultdict
import json


class RegionalTFIDF:
    """Analyse TF-IDF par région"""
    
    def __init__(self, max_features: int = 50):
        """
        Args:
            max_features: Nombre de termes à extraire par région
        """
        self.max_features = max_features
        self.vectorizers = {}
        self.regional_terms = {}
    
    def analyze_by_region(self, df: pd.DataFrame, text_column: str = 'skills'):
        """
        Analyse TF-IDF par région.
        
        Args:
            df: DataFrame avec colonnes 'region' et text_column
            text_column: Nom de la colonne contenant le texte
        """
        print("🗺️  Analyse TF-IDF par région...")
        print(f"   Colonne analysée: {text_column}")
        print()
        
        regions = df['region'].dropna().unique()
        print(f"   Régions détectées: {len(regions)}")
        
        for region in regions:
            # Filtrer les offres de cette région
            region_df = df[df['region'] == region]
            
            if len(region_df) < 5:
                continue
            
            # Combiner tous les textes de la région
            region_texts = region_df[text_column].dropna().tolist()
            
            if not region_texts:
                continue
            
            # TF-IDF pour cette région
            vectorizer = TfidfVectorizer(
                max_features=self.max_features,
                min_df=2,
                token_pattern=r'\b\w+\b'
            )
            
            try:
                tfidf_matrix = vectorizer.fit_transform(region_texts)
                
                # Moyenne TF-IDF par terme
                mean_tfidf = tfidf_matrix.mean(axis=0).A1
                feature_names = vectorizer.get_feature_names_out()
                
                # Trier par score TF-IDF
                top_indices = mean_tfidf.argsort()[-20:][::-1]
                top_terms = [(feature_names[i], mean_tfidf[i]) for i in top_indices]
                
                self.regional_terms[region] = top_terms
                self.vectorizers[region] = vectorizer
                
            except Exception as e:
                print(f"   ⚠️  Erreur pour {region}: {e}")
                continue
        
        print(f"   ✅ {len(self.regional_terms)} régions analysées")
    
    def print_regional_terms(self, n_terms: int = 15):
        """Affiche les termes caractéristiques par région"""
        print("\n" + "=" * 80)
        print("🗺️  TERMES CARACTÉRISTIQUES PAR RÉGION")
        print("=" * 80)
        
        # Trier régions par nombre d'offres (implicite dans l'ordre)
        for region, terms in self.regional_terms.items():
            print(f"\n📍 {region}")
            
            terms_display = []
            for term, score in terms[:n_terms]:
                terms_display.append(f"{term} ({score:.3f})")
            
            print(f"   {', '.join([t.split(' ')[0] for t, _ in terms[:n_terms]])}")
    
    def compare_regions(self, region1: str, region2: str, n_terms: int = 10):
        """
        Compare les termes caractéristiques de 2 régions.
        
        Args:
            region1: Première région
            region2: Deuxième région
            n_terms: Nombre de termes à comparer
        """
        if region1 not in self.regional_terms or region2 not in self.regional_terms:
            print("⚠️  Une des régions n'a pas été analysée")
            return
        
        terms1 = set([t for t, _ in self.regional_terms[region1][:n_terms]])
        terms2 = set([t for t, _ in self.regional_terms[region2][:n_terms]])
        
        print(f"\n🔍 Comparaison : {region1} vs {region2}")
        print("=" * 80)
        
        # Termes uniques à région 1
        unique1 = terms1 - terms2
        if unique1:
            print(f"\n✅ Spécifique à {region1}:")
            print(f"   {', '.join(list(unique1)[:10])}")
        
        # Termes uniques à région 2
        unique2 = terms2 - terms1
        if unique2:
            print(f"\n✅ Spécifique à {region2}:")
            print(f"   {', '.join(list(unique2)[:10])}")
        
        # Termes communs
        common = terms1 & terms2
        if common:
            print(f"\n🤝 Termes communs:")
            print(f"   {', '.join(list(common)[:10])}")
    
    def get_regional_specializations(self):
        """
        Identifie les spécialisations par région.
        
        Returns:
            Dict {region: specialization_keywords}
        """
        specializations = {}
        
        # Mots-clés indicateurs de spécialisation
        tech_keywords = {
            'cloud': ['aws', 'azure', 'gcp', 'cloud', 'kubernetes', 'docker'],
            'ml_ai': ['machine', 'learning', 'deep', 'tensorflow', 'pytorch', 'nlp'],
            'big_data': ['spark', 'hadoop', 'kafka', 'big', 'data', 'streaming'],
            'bi': ['power', 'bi', 'tableau', 'looker', 'dashboard', 'reporting'],
            'web': ['react', 'javascript', 'node', 'django', 'flask', 'api'],
            'data_eng': ['airflow', 'etl', 'pipeline', 'warehouse', 'dbt']
        }
        
        for region, terms in self.regional_terms.items():
            region_terms_lower = [t.lower() for t, _ in terms[:20]]
            
            scores = defaultdict(int)
            for category, keywords in tech_keywords.items():
                for keyword in keywords:
                    if any(keyword in term for term in region_terms_lower):
                        scores[category] += 1
            
            # Top spécialisation
            if scores:
                top_spec = max(scores.items(), key=lambda x: x[1])
                specializations[region] = top_spec[0]
            else:
                specializations[region] = 'généraliste'
        
        return specializations
    
    def export_results(self, filepath: str):
        """Exporte les résultats en JSON"""
        results = {}
        
        for region, terms in self.regional_terms.items():
            results[region] = {
                'top_terms': [
                    {'term': term, 'tfidf_score': float(score)}
                    for term, score in terms
                ]
            }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        
        print(f"✅ Résultats exportés: {filepath}")


if __name__ == "__main__":
    import sqlite3
    
    print("=" * 80)
    print("🗺️  ANALYSE TF-IDF PAR RÉGION")
    print("=" * 80)
    print()
    
    # Charger données
    print("📂 Chargement des données...")
    conn = sqlite3.connect('../database/jobs.db')
    
    query = """
        SELECT 
            fo.offer_key,
            fo.title,
            GROUP_CONCAT(ds.skill_name) as skills,
            dr.region_name as region
        FROM fact_offers fo
        LEFT JOIN fact_offer_skill fos ON fo.offer_key = fos.offer_key
        LEFT JOIN dim_skill ds ON fos.skill_key = ds.skill_key
        LEFT JOIN dim_region dr ON fo.region_key = dr.region_key
        WHERE dr.region_name IS NOT NULL
        GROUP BY fo.offer_key
    """
    
    df = pd.read_sql_query(query, conn)
    conn.close()
    
    print(f"   ✅ {len(df)} offres chargées")
    print()
    
    # Analyse TF-IDF
    analyzer = RegionalTFIDF(max_features=50)
    analyzer.analyze_by_region(df, text_column='skills')
    
    # Afficher résultats
    analyzer.print_regional_terms(n_terms=15)
    
    # Spécialisations
    print("\n" + "=" * 80)
    print("🎯 SPÉCIALISATIONS RÉGIONALES")
    print("=" * 80)
    
    specializations = analyzer.get_regional_specializations()
    
    spec_labels = {
        'cloud': '☁️ Cloud/DevOps',
        'ml_ai': '🤖 ML/IA',
        'big_data': '⚙️ Big Data',
        'bi': '📊 BI/Analytics',
        'web': '🌐 Web/Full Stack',
        'data_eng': '🔧 Data Engineering',
        'généraliste': '📋 Généraliste'
    }
    
    for region, spec in sorted(specializations.items(), key=lambda x: x[0]):
        label = spec_labels.get(spec, spec)
        print(f"   {region:30} → {label}")
    
    # Comparaisons intéressantes
    print("\n" + "=" * 80)
    print("🔍 COMPARAISONS RÉGIONALES")
    print("=" * 80)
    
    # Île-de-France vs Auvergne-Rhône-Alpes
    if 'Île-de-France' in analyzer.regional_terms and 'Auvergne-Rhône-Alpes' in analyzer.regional_terms:
        analyzer.compare_regions('Île-de-France', 'Auvergne-Rhône-Alpes', n_terms=15)
    
    # Export
    analyzer.export_results('regional_tfidf_results.json')
    
    print("\n✅ Analyse TF-IDF terminée !")