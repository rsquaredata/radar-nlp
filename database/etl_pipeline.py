import argparse
import sqlite3
import pandas as pd
import json
from pathlib import Path
from datetime import datetime
import sys


class ETLPipeline:
    """Pipeline ETL pour chargement des données"""
    
    def __init__(self, db_path: str = "jobs.db"):
        self.db_path = db_path
        self.conn = None
        self.stats = {
            'offers_inserted': 0,
            'offers_duplicates': 0,
            'skills_inserted': 0,
            'associations_created': 0
        }
    
    def connect(self):
        """Connexion à la base de données"""
        self.conn = sqlite3.connect(self.db_path)
        self.conn.execute("PRAGMA foreign_keys = ON")
        print(f"✅ Connecté à {self.db_path}")
    
    def create_schema(self, schema_file: str = "schema.sql"):
        """Crée le schéma de la base de données"""
        print("\n📋 Création du schéma...")
        
        with open(schema_file, 'r', encoding='utf-8') as f:
            schema_sql = f.read()
        
        # Exécuter le schéma
        self.conn.executescript(schema_sql)
        self.conn.commit()
        
        print("   ✅ Schéma créé avec succès")
    
    def load_dimensions(self, df: pd.DataFrame):
        """Charge les tables de dimensions"""
        print("\n📊 Chargement des dimensions...")
        
        # 1. dim_source
        sources = df['source'].dropna().unique()
        for source in sources:
            source_type = 'api' if 'france travail' in source.lower() else 'scraping'
            self.conn.execute(
                "INSERT OR IGNORE INTO dim_source (source_name, source_type) VALUES (?, ?)",
                (source, source_type)
            )
        print(f"   ✅ {len(sources)} sources")
        
        # 2. dim_region
        regions = df[['region', 'region_lat', 'region_lon']].dropna().drop_duplicates('region')
        for _, row in regions.iterrows():
            self.conn.execute(
                "INSERT OR IGNORE INTO dim_region (region_name, latitude, longitude) VALUES (?, ?, ?)",
                (row['region'], row['region_lat'], row['region_lon'])
            )
        print(f"   ✅ {len(regions)} régions")
        
        # 3. dim_company
        companies = df['company'].dropna().unique()
        for company in companies:
            self.conn.execute(
                "INSERT OR IGNORE INTO dim_company (company_name) VALUES (?)",
                (company,)
            )
        print(f"   ✅ {len(companies)} entreprises")
        
        # 4. dim_contract
        contracts = df['contract_type'].dropna().unique()
        for contract in contracts:
            self.conn.execute(
                "INSERT OR IGNORE INTO dim_contract (contract_type) VALUES (?)",
                (contract,)
            )
        print(f"   ✅ {len(contracts)} types de contrat")
        
        self.conn.commit()
    
    def load_skills(self, df: pd.DataFrame):
        """Charge les compétences dans dim_skill"""
        print("\n🎯 Chargement des compétences...")
        
        all_skills = set()
        
        for _, row in df.iterrows():
            # Compétences techniques
            if pd.notna(row.get('competences')):
                try:
                    competences = eval(row['competences']) if isinstance(row['competences'], str) else row['competences']
                    for skill in competences:
                        all_skills.add((skill, 'competences', 'unknown'))
                except:
                    pass
            
            # Savoir-être
            if pd.notna(row.get('savoir_etre')):
                try:
                    savoir_etre = eval(row['savoir_etre']) if isinstance(row['savoir_etre'], str) else row['savoir_etre']
                    for skill in savoir_etre:
                        all_skills.add((skill, 'savoir_etre', 'unknown'))
                except:
                    pass
        
        # Insérer
        for skill_name, skill_type, skill_category in all_skills:
            self.conn.execute(
                "INSERT OR IGNORE INTO dim_skill (skill_name, skill_type, skill_category) VALUES (?, ?, ?)",
                (skill_name, skill_type, skill_category)
            )
        
        self.conn.commit()
        self.stats['skills_inserted'] = len(all_skills)
        print(f"   ✅ {len(all_skills)} compétences uniques")
    
    def load_offers(self, df: pd.DataFrame):
        """Charge les offres dans fact_offers"""
        print("\n📝 Chargement des offres...")
        
        cursor = self.conn.cursor()
        
        for idx, row in df.iterrows():
            try:
                # Récupérer les clés étrangères
                source_key = self._get_key("dim_source", "source_name", row.get('source'))
                region_key = self._get_key("dim_region", "region_name", row.get('region'))
                company_key = self._get_key("dim_company", "company_name", row.get('company'))
                contract_key = self._get_key("dim_contract", "contract_type", row.get('contract_type'))
                
                # Compter les compétences
                competences_count = 0
                savoir_etre_count = 0
                
                if pd.notna(row.get('competences')):
                    try:
                        comp = eval(row['competences']) if isinstance(row['competences'], str) else row['competences']
                        competences_count = len(comp)
                    except:
                        pass
                
                if pd.notna(row.get('savoir_etre')):
                    try:
                        se = eval(row['savoir_etre']) if isinstance(row['savoir_etre'], str) else row['savoir_etre']
                        savoir_etre_count = len(se)
                    except:
                        pass
                
                skills_count = competences_count + savoir_etre_count
                
                # Insérer l'offre (si pas de doublon grâce à UNIQUE uid)
                cursor.execute("""
                    INSERT OR IGNORE INTO fact_offers 
                    (uid, offer_id, source_key, region_key, company_key, contract_key,
                     title, source_url, location, salary, remote, published_date, description,
                     skills_count, competences_count, savoir_etre_count, added_by)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'import')
                """, (
                    row['uid'], row['offer_id'], source_key, region_key, company_key, contract_key,
                    row['title'], row.get('source_url'), row.get('location'), 
                    row.get('salary'), row.get('remote'), row.get('published_date'), 
                    row.get('description'), skills_count, competences_count, savoir_etre_count
                ))
                
                if cursor.rowcount > 0:
                    self.stats['offers_inserted'] += 1
                else:
                    self.stats['offers_duplicates'] += 1
                
            except Exception as e:
                print(f"   ⚠️  Erreur ligne {idx}: {e}")
                continue
            
            if (idx + 1) % 100 == 0:
                print(f"   Traité {idx + 1}/{len(df)}")
        
        self.conn.commit()
        print(f"   ✅ {self.stats['offers_inserted']} offres insérées")
        print(f"   ⚠️  {self.stats['offers_duplicates']} doublons ignorés")
    
    def load_offer_skills(self, df: pd.DataFrame):
        """Charge les associations offre ↔ compétence"""
        print("\n🔗 Création des associations offre ↔ compétence...")
        
        cursor = self.conn.cursor()
        
        for idx, row in df.iterrows():
            # Récupérer offer_key
            cursor.execute("SELECT offer_key FROM fact_offers WHERE uid = ?", (row['uid'],))
            result = cursor.fetchone()
            
            if not result:
                continue
            
            offer_key = result[0]
            
            # Compétences techniques
            if pd.notna(row.get('competences')):
                try:
                    competences = eval(row['competences']) if isinstance(row['competences'], str) else row['competences']
                    for skill_name in competences:
                        skill_key = self._get_key("dim_skill", "skill_name", skill_name)
                        if skill_key:
                            cursor.execute(
                                "INSERT OR IGNORE INTO fact_offer_skill (offer_key, skill_key) VALUES (?, ?)",
                                (offer_key, skill_key)
                            )
                            if cursor.rowcount > 0:
                                self.stats['associations_created'] += 1
                except:
                    pass
            
            # Savoir-être
            if pd.notna(row.get('savoir_etre')):
                try:
                    savoir_etre = eval(row['savoir_etre']) if isinstance(row['savoir_etre'], str) else row['savoir_etre']
                    for skill_name in savoir_etre:
                        skill_key = self._get_key("dim_skill", "skill_name", skill_name)
                        if skill_key:
                            cursor.execute(
                                "INSERT OR IGNORE INTO fact_offer_skill (offer_key, skill_key) VALUES (?, ?)",
                                (offer_key, skill_key)
                            )
                            if cursor.rowcount > 0:
                                self.stats['associations_created'] += 1
                except:
                    pass
            
            if (idx + 1) % 100 == 0:
                print(f"   Traité {idx + 1}/{len(df)}")
        
        self.conn.commit()
        print(f"   ✅ {self.stats['associations_created']} associations créées")
    
    def _get_key(self, table: str, column: str, value):
        """Récupère la clé primaire d'une dimension"""
        if pd.isna(value):
            return None
        
        cursor = self.conn.cursor()
        key_column = table.replace('dim_', '') + '_key'
        cursor.execute(f"SELECT {key_column} FROM {table} WHERE {column} = ?", (value,))
        result = cursor.fetchone()
        return result[0] if result else None
    
    def print_stats(self):
        """Affiche les statistiques finales"""
        print("\n" + "=" * 80)
        print("📊 STATISTIQUES FINALES")
        print("=" * 80)
        
        cursor = self.conn.cursor()
        
        # Stats globales
        cursor.execute("SELECT * FROM v_stats_global")
        stats = cursor.fetchone()
        
        print(f"\n✅ Offres : {stats[0]:,}")
        print(f"✅ Régions : {stats[1]:,}")
        print(f"✅ Compétences totales : {stats[2]:,}")
        print(f"   • Compétences techniques : {stats[3]:,}")
        print(f"   • Savoir-être : {stats[4]:,}")
        print(f"✅ Moyenne compétences/offre : {stats[5]:.1f}")
        print(f"\n✅ Associations offre ↔ compétence : {self.stats['associations_created']:,}")
        
        # Top 10 compétences
        print("\n🏆 TOP 10 COMPÉTENCES :")
        cursor.execute("SELECT skill_name, offer_count, percentage FROM v_top_skills LIMIT 10")
        for skill_name, count, pct in cursor.fetchall():
            print(f"   • {skill_name:25} {count:4} offres ({pct:.1f}%)")
        
        # Top 5 régions
        print("\n🗺️  TOP 5 RÉGIONS :")
        cursor.execute("SELECT region_name, offer_count FROM v_offers_by_region LIMIT 5")
        for region, count in cursor.fetchall():
            print(f"   • {region:30} {count:4} offres")
    
    def close(self):
        """Ferme la connexion"""
        if self.conn:
            self.conn.close()
            print("\n✅ Connexion fermée")


def main():
    parser = argparse.ArgumentParser(description="Pipeline ETL - Chargement des données")
    parser.add_argument('-i', '--input', required=True, help="Fichier CSV d'entrée")
    parser.add_argument('--db', default='jobs.db', help="Nom de la base de données")
    parser.add_argument('--schema', default='schema.sql', help="Fichier schema SQL")
    parser.add_argument('--recreate', action='store_true', help="Recréer la base (supprime l'existante)")
    
    args = parser.parse_args()
    
    print("=" * 80)
    print("🗄️  PIPELINE ETL - CHARGEMENT BASE DE DONNÉES")
    print("=" * 80)
    print()
    print(f"📂 Fichier source : {args.input}")
    print(f"🗄️  Base de données : {args.db}")
    print()
    
    # Supprimer la base si --recreate
    if args.recreate and Path(args.db).exists():
        Path(args.db).unlink()
        print("⚠️  Base de données existante supprimée")
        print()
    
    # Charger les données CSV
    print("📂 Chargement du CSV...")
    df = pd.read_csv(args.input)
    print(f"   ✅ {len(df):,} lignes chargées")
    
    # Pipeline ETL
    etl = ETLPipeline(db_path=args.db)
    
    try:
        etl.connect()
        etl.create_schema(schema_file=args.schema)
        etl.load_dimensions(df)
        etl.load_skills(df)
        etl.load_offers(df)
        etl.load_offer_skills(df)
        etl.print_stats()
        
    except Exception as e:
        print(f"\n❌ ERREUR : {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        etl.close()
    
    print("\n" + "=" * 80)
    print("✅ PIPELINE ETL TERMINÉ")
    print("=" * 80)
    print()
    print(f"💡 La base de données '{args.db}' est prête à être utilisée !")
    print()


if __name__ == "__main__":
    main()