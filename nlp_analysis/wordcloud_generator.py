import pandas as pd
import numpy as np
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from collections import Counter
import os


class WordCloudGenerator:
    """Générateur de Word Clouds"""
    
    def __init__(self, output_dir: str = 'wordclouds'):
        """
        Args:
            output_dir: Dossier de sortie pour les images
        """
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
    
    def generate_wordcloud(self, text: str, title: str, output_filename: str = None):
        """
        Génère un word cloud.
        
        Args:
            text: Texte source
            title: Titre du word cloud
            output_filename: Nom du fichier de sortie
        """
        if not text or len(text.strip()) == 0:
            print(f"   ⚠️  Pas de texte pour {title}")
            return
        
        # Créer le word cloud
        wordcloud = WordCloud(
            width=1200,
            height=600,
            background_color='white',
            colormap='viridis',
            max_words=100,
            relative_scaling=0.5,
            min_font_size=10
        ).generate(text)
        
        # Visualisation
        plt.figure(figsize=(15, 8))
        plt.imshow(wordcloud, interpolation='bilinear')
        plt.axis('off')
        plt.title(title, fontsize=20, fontweight='bold', pad=20)
        plt.tight_layout(pad=0)
        
        # Sauvegarder
        if output_filename:
            filepath = os.path.join(self.output_dir, output_filename)
            plt.savefig(filepath, dpi=300, bbox_inches='tight', facecolor='white')
            print(f"   ✅ {title} → {filepath}")
        
        plt.close()
    
    def generate_regional_wordclouds(self, df: pd.DataFrame, skills_column: str = 'skills'):
        """
        Génère un word cloud pour chaque région.
        
        Args:
            df: DataFrame avec colonnes 'region' et skills_column
            skills_column: Nom de la colonne contenant les compétences
        """
        print("🎨 Génération des Word Clouds par région...")
        print()
        
        regions = df['region'].dropna().value_counts()
        
        for region, count in regions.items():
            # Filtrer les offres de cette région
            region_df = df[df['region'] == region]
            
            # Combiner toutes les compétences
            all_skills = []
            for skills in region_df[skills_column].dropna():
                if isinstance(skills, str):
                    all_skills.extend(skills.split(','))
            
            if not all_skills:
                continue
            
            # Créer le texte (répéter chaque compétence selon sa fréquence)
            text = " ".join(all_skills)
            
            # Générer word cloud
            title = f"{region} ({count} offres)"
            filename = f"wordcloud_{region.lower().replace(' ', '_').replace('-', '_')}.png"
            
            self.generate_wordcloud(text, title, filename)
    
    def generate_comparison_wordcloud(self, df: pd.DataFrame, region1: str, region2: str, 
                                     skills_column: str = 'skills'):
        """
        Génère un word cloud comparatif de 2 régions.
        
        Args:
            df: DataFrame
            region1: Première région
            region2: Deuxième région
            skills_column: Colonne des compétences
        """
        print(f"\n🔍 Comparaison : {region1} vs {region2}")
        
        fig, axes = plt.subplots(1, 2, figsize=(20, 8))
        
        for idx, region in enumerate([region1, region2]):
            region_df = df[df['region'] == region]
            
            all_skills = []
            for skills in region_df[skills_column].dropna():
                if isinstance(skills, str):
                    all_skills.extend(skills.split(','))
            
            if all_skills:
                text = " ".join(all_skills)
                
                wordcloud = WordCloud(
                    width=800,
                    height=600,
                    background_color='white',
                    colormap='viridis' if idx == 0 else 'plasma',
                    max_words=80
                ).generate(text)
                
                axes[idx].imshow(wordcloud, interpolation='bilinear')
                axes[idx].axis('off')
                axes[idx].set_title(f"{region} ({len(region_df)} offres)", 
                                   fontsize=16, fontweight='bold')
        
        plt.tight_layout()
        
        filename = f"comparison_{region1.lower().replace(' ', '_')}_vs_{region2.lower().replace(' ', '_')}.png"
        filepath = os.path.join(self.output_dir, filename)
        plt.savefig(filepath, dpi=300, bbox_inches='tight', facecolor='white')
        print(f"   ✅ Comparaison sauvegardée → {filepath}")
        
        plt.close()
    
    def generate_global_wordcloud(self, df: pd.DataFrame, skills_column: str = 'skills'):
        """
        Génère un word cloud global de toutes les offres.
        
        Args:
            df: DataFrame
            skills_column: Colonne des compétences
        """
        print("\n🌍 Word Cloud global...")
        
        all_skills = []
        for skills in df[skills_column].dropna():
            if isinstance(skills, str):
                all_skills.extend(skills.split(','))
        
        if all_skills:
            text = " ".join(all_skills)
            
            self.generate_wordcloud(
                text=text,
                title=f"Compétences Data/IA en France ({len(df)} offres)",
                output_filename="wordcloud_global.png"
            )
    
    def generate_skill_type_wordclouds(self, df: pd.DataFrame):
        """
        Génère des word clouds séparés pour compétences techniques et savoir-être.
        
        Args:
            df: DataFrame avec colonnes 'competences' et 'savoir_etre'
        """
        print("\n🎯 Word Clouds par type de compétence...")
        
        # Compétences techniques
        if 'competences' in df.columns:
            all_comp = []
            for comp in df['competences'].dropna():
                if isinstance(comp, str):
                    try:
                        import ast
                        comp_list = ast.literal_eval(comp)
                        all_comp.extend(comp_list)
                    except:
                        all_comp.extend(comp.split(','))
            
            if all_comp:
                text = " ".join(all_comp)
                self.generate_wordcloud(
                    text=text,
                    title="Compétences Techniques (Hard Skills)",
                    output_filename="wordcloud_competences_techniques.png"
                )
        
        # Savoir-être
        if 'savoir_etre' in df.columns:
            all_se = []
            for se in df['savoir_etre'].dropna():
                if isinstance(se, str):
                    try:
                        import ast
                        se_list = ast.literal_eval(se)
                        all_se.extend(se_list)
                    except:
                        all_se.extend(se.split(','))
            
            if all_se:
                text = " ".join(all_se)
                self.generate_wordcloud(
                    text=text,
                    title="Savoir-Être (Soft Skills)",
                    output_filename="wordcloud_savoir_etre.png"
                )


if __name__ == "__main__":
    import sqlite3
    
    print("=" * 80)
    print("🎨 GÉNÉRATION DE WORD CLOUDS")
    print("=" * 80)
    print()
    
    # Charger données
    print("📂 Chargement des données...")
    conn = sqlite3.connect('../database/jobs.db')
    
    # Requête avec compétences agrégées
    query = """
        SELECT 
            fo.offer_key,
            fo.title,
            GROUP_CONCAT(ds.skill_name) as skills,
            GROUP_CONCAT(CASE WHEN ds.skill_type = 'competences' THEN ds.skill_name END) as competences,
            GROUP_CONCAT(CASE WHEN ds.skill_type = 'savoir_etre' THEN ds.skill_name END) as savoir_etre,
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
    
    # Générer word clouds
    generator = WordCloudGenerator(output_dir='wordclouds')
    
    # 1. Word cloud global
    generator.generate_global_wordcloud(df, skills_column='skills')
    
    # 2. Word clouds par type
    generator.generate_skill_type_wordclouds(df)
    
    # 3. Word clouds par région
    generator.generate_regional_wordclouds(df, skills_column='skills')
    
    # 4. Comparaisons intéressantes
    if 'Île-de-France' in df['region'].values and 'Auvergne-Rhône-Alpes' in df['region'].values:
        generator.generate_comparison_wordcloud(
            df, 'Île-de-France', 'Auvergne-Rhône-Alpes', skills_column='skills'
        )
    
    if 'Occitanie' in df['region'].values and 'Bretagne' in df['region'].values:
        generator.generate_comparison_wordcloud(
            df, 'Occitanie', 'Bretagne', skills_column='skills'
        )
    
    print("\n" + "=" * 80)
    print("✅ GÉNÉRATION TERMINÉE")
    print("=" * 80)
    print()
    print(f"📁 Tous les word clouds sont dans le dossier: wordclouds/")
    print()