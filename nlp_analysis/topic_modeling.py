import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
from sklearn.decomposition import LatentDirichletAllocation, NMF
import pickle
import ast


class SkillTopicModeler:
    """Topic Modeling basé sur les compétences"""
    
    def __init__(self, n_topics: int = 6, method: str = 'lda'):
        """
        Args:
            n_topics: Nombre de profils à découvrir
            method: 'lda' ou 'nmf'
        """
        self.n_topics = n_topics
        self.method = method
        self.vectorizer = None
        self.model = None
        self.feature_names = None
        self.topics = None
    
    def prepare_skill_documents(self, competences_lists: list, savoir_etre_lists: list):
        """
        Transforme les listes de compétences en documents texte.
        
        Args:
            competences_lists: Liste de listes de compétences techniques
            savoir_etre_lists: Liste de listes de savoir-être
        
        Returns:
            Liste de documents (strings)
        """
        documents = []
        
        for comp, se in zip(competences_lists, savoir_etre_lists):
            # Parser si string
            if isinstance(comp, str):
                try:
                    comp = ast.literal_eval(comp)
                except:
                    comp = []
            
            if isinstance(se, str):
                try:
                    se = ast.literal_eval(se)
                except:
                    se = []
            
            # Combiner compétences et savoir-être
            all_skills = []
            
            if isinstance(comp, list):
                all_skills.extend(comp)
            
            if isinstance(se, list):
                all_skills.extend(se)
            
            # Joindre en texte
            doc = " ".join(all_skills) if all_skills else ""
            documents.append(doc)
        
        return documents
    
    def fit(self, skill_documents: list):
        """
        Entraîne le modèle de topics.
        
        Args:
            skill_documents: Liste de documents (compétences en string)
        """
        print(f"🧠 Découverte de {self.n_topics} profils basés sur les compétences...")
        print(f"   Documents: {len(skill_documents)}")
        
        # Vectorisation - CountVectorizer pour LDA
        print("   🔢 Vectorisation...")
        
        if self.method == 'lda':
            self.vectorizer = CountVectorizer(
                max_features=200,
                min_df=5,        # Compétence présente dans au moins 5 offres
                max_df=0.8,      # Pas plus de 80% des offres
                token_pattern=r'\b\w+\b'
            )
        else:  # NMF
            self.vectorizer = TfidfVectorizer(
                max_features=200,
                min_df=5,
                max_df=0.8,
                token_pattern=r'\b\w+\b'
            )
        
        matrix = self.vectorizer.fit_transform(skill_documents)
        self.feature_names = self.vectorizer.get_feature_names_out()
        
        print(f"   ✅ {len(self.feature_names)} compétences retenues")
        
        # Modèle
        print(f"   🎯 Entraînement {self.method.upper()}...")
        
        if self.method == 'lda':
            self.model = LatentDirichletAllocation(
                n_components=self.n_topics,
                max_iter=30,
                learning_method='online',
                random_state=42,
                n_jobs=-1
            )
        else:  # NMF
            self.model = NMF(
                n_components=self.n_topics,
                random_state=42,
                max_iter=300
            )
        
        self.model.fit(matrix)
        print("   ✅ Modèle entraîné !")
        
        self._extract_topics()
    
    def _extract_topics(self, n_skills: int = 15):
        """Extrait les compétences principales de chaque profil"""
        self.topics = []
        
        for topic_idx, topic in enumerate(self.model.components_):
            top_indices = topic.argsort()[-n_skills:][::-1]
            top_skills = [self.feature_names[i] for i in top_indices]
            top_weights = [topic[i] for i in top_indices]
            
            self.topics.append({
                'topic_id': topic_idx,
                'skills': top_skills,
                'weights': top_weights
            })
    
    def get_topics(self):
        """Retourne les profils découverts"""
        return self.topics
    
    def print_topics(self, n_skills: int = 12):
        """Affiche les profils avec leurs compétences clés"""
        topics = self.get_topics()
        
        print("\n" + "=" * 80)
        print(f"🎯 {self.n_topics} PROFILS DÉCOUVERTS")
        print("=" * 80)
        
        # Noms suggérés basés sur analyse manuelle
        profile_names = [
            "🤖 Data Scientist / ML Engineer",
            "⚙️ Data Engineer / Big Data",
            "☁️ Cloud / DevOps Engineer",
            "📊 Data Analyst / BI Developer",
            "🏗️ Data Architect / Lead",
            "🎨 Full Stack / Web Developer"
        ]
        
        for i, topic in enumerate(topics):
            name = profile_names[i] if i < len(profile_names) else f"Profil {i}"
            print(f"\n{name}")
            
            skills_display = []
            for skill, weight in zip(topic['skills'][:n_skills], topic['weights'][:n_skills]):
                skills_display.append(skill)
            
            print(f"   Compétences clés: {', '.join(skills_display)}")
    
    def assign_profiles(self, skill_documents: list):
        """
        Assigne un profil dominant à chaque offre.
        
        Returns:
            DataFrame avec profile_id et probability
        """
        matrix = self.vectorizer.transform(skill_documents)
        doc_topic_dist = self.model.transform(matrix)
        
        dominant_profiles = doc_topic_dist.argmax(axis=1)
        dominant_probs = doc_topic_dist.max(axis=1)
        
        return pd.DataFrame({
            'document_id': range(len(skill_documents)),
            'dominant_profile': dominant_profiles,
            'profile_probability': dominant_probs
        })
    
    def save_model(self, filepath: str):
        """Sauvegarde le modèle"""
        model_data = {
            'vectorizer': self.vectorizer,
            'model': self.model,
            'feature_names': self.feature_names,
            'topics': self.topics,
            'n_topics': self.n_topics,
            'method': self.method
        }
        with open(filepath, 'wb') as f:
            pickle.dump(model_data, f)
        print(f"✅ Modèle sauvegardé dans {filepath}")


if __name__ == "__main__":
    import sqlite3
    
    print("=" * 80)
    print("🧠 DÉCOUVERTE DE PROFILS - TOPIC MODELING SUR COMPÉTENCES")
    print("=" * 80)
    print()
    
    # Charger données
    print("📂 Chargement des données...")
    conn = sqlite3.connect('../database/jobs.db')
    
    # Récupérer compétences par offre via fact_offer_skill
    query = """
        SELECT 
            fo.offer_key,
            fo.title,
            GROUP_CONCAT(CASE WHEN ds.skill_type = 'competences' THEN ds.skill_name END) as competences,
            GROUP_CONCAT(CASE WHEN ds.skill_type = 'savoir_etre' THEN ds.skill_name END) as savoir_etre,
            dr.region_name as region
        FROM fact_offers fo
        LEFT JOIN fact_offer_skill fos ON fo.offer_key = fos.offer_key
        LEFT JOIN dim_skill ds ON fos.skill_key = ds.skill_key
        LEFT JOIN dim_region dr ON fo.region_key = dr.region_key
        GROUP BY fo.offer_key
    """
    
    df = pd.read_sql_query(query, conn)
    conn.close()
    
    print(f"   ✅ {len(df)} offres chargées")
    print()
    
    # Préparer documents (compétences)
    print("📝 Préparation des documents de compétences...")
    
    skill_docs = []
    for _, row in df.iterrows():
        skills = []
        
        if pd.notna(row['competences']):
            skills.extend(row['competences'].split(','))
        
        if pd.notna(row['savoir_etre']):
            skills.extend(row['savoir_etre'].split(','))
        
        skill_docs.append(" ".join(skills))
    
    print(f"   ✅ {len(skill_docs)} documents créés")
    print()
    
    # Entraîner
    modeler = SkillTopicModeler(n_topics=6, method='lda')
    modeler.fit(skill_docs)
    
    # Afficher profils
    modeler.print_topics(n_skills=12)
    
    # Assigner profils
    print("\n📊 Assignment des profils aux offres...")
    profile_assignments = modeler.assign_profiles(skill_docs)
    
    # Stats
    print("\n📊 Distribution des profils :")
    profile_counts = profile_assignments['dominant_profile'].value_counts().sort_index()
    
    profile_names_short = [
        "Data Scientist/ML",
        "Data Engineer",
        "Cloud/DevOps",
        "Data Analyst/BI",
        "Data Architect",
        "Full Stack"
    ]
    
    for profile_id, count in profile_counts.items():
        pct = (count / len(df)) * 100
        name = profile_names_short[profile_id] if profile_id < len(profile_names_short) else f"Profil {profile_id}"
        print(f"   {name:20} {count:4} offres ({pct:.1f}%)")
    
    # Analyser par région
    print("\n🗺️  Profils dominants par région (Top 5 régions) :")
    df_with_profile = pd.concat([df.reset_index(drop=True), profile_assignments], axis=1)
    
    top_regions = df_with_profile['region'].value_counts().head(5).index
    
    for region in top_regions:
        region_df = df_with_profile[df_with_profile['region'] == region]
        top_profile = region_df['dominant_profile'].mode()[0] if len(region_df) > 0 else 0
        profile_name = profile_names_short[top_profile] if top_profile < len(profile_names_short) else f"Profil {top_profile}"
        print(f"   {region:30} → {profile_name}")
    
    # Sauvegarder
    modeler.save_model('skill_topic_model.pkl')
    profile_assignments.to_csv('profile_assignments.csv', index=False)
    
    print("\n✅ Découverte de profils terminée !")