import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.metrics import silhouette_score
import matplotlib.pyplot as plt
import seaborn as sns
import pickle


class OfferClusterer:
    """Clustering des offres d'emploi"""
    
    def __init__(self, n_clusters: int = 6):
        """
        Args:
            n_clusters: Nombre de clusters
        """
        self.n_clusters = n_clusters
        self.vectorizer = None
        self.kmeans = None
        self.pca = None
        self.cluster_centers = None
        self.labels = None
        self.coords_2d = None
    
    def prepare_skill_documents(self, competences_lists: list, savoir_etre_lists: list):
        """Transforme les compétences en documents texte"""
        import ast
        
        documents = []
        
        for comp, se in zip(competences_lists, savoir_etre_lists):
            if isinstance(comp, str):
                try:
                    comp = ast.literal_eval(comp) if comp else []
                except:
                    comp = []
            
            if isinstance(se, str):
                try:
                    se = ast.literal_eval(se) if se else []
                except:
                    se = []
            
            all_skills = []
            if isinstance(comp, list):
                all_skills.extend(comp)
            if isinstance(se, list):
                all_skills.extend(se)
            
            documents.append(" ".join(all_skills) if all_skills else "")
        
        return documents
    
    def fit(self, skill_documents: list):
        """
        Entraîne le clustering.
        
        Args:
            skill_documents: Liste de documents (compétences)
        """
        print(f"🎯 Clustering K-Means avec {self.n_clusters} clusters...")
        print(f"   Documents: {len(skill_documents)}")
        
        # Vectorisation TF-IDF
        print("   🔢 Vectorisation TF-IDF...")
        self.vectorizer = TfidfVectorizer(
            max_features=200,
            min_df=5,
            max_df=0.8,
            token_pattern=r'\b\w+\b'
        )
        
        tfidf_matrix = self.vectorizer.fit_transform(skill_documents)
        print(f"   ✅ Matrice: {tfidf_matrix.shape}")
        
        # K-Means
        print(f"   🎯 Clustering K-Means ({self.n_clusters} clusters)...")
        self.kmeans = KMeans(
            n_clusters=self.n_clusters,
            random_state=42,
            n_init=10,
            max_iter=300
        )
        
        self.labels = self.kmeans.fit_predict(tfidf_matrix)
        
        # Score silhouette
        silhouette = silhouette_score(tfidf_matrix, self.labels)
        print(f"   ✅ Score silhouette: {silhouette:.3f}")
        
        # PCA pour visualisation 2D
        print("   📊 Réduction PCA (2D)...")
        self.pca = PCA(n_components=2, random_state=42)
        self.coords_2d = self.pca.fit_transform(tfidf_matrix.toarray())
        
        variance = self.pca.explained_variance_ratio_
        print(f"   ✅ Variance expliquée: {variance[0]:.1%} + {variance[1]:.1%} = {variance.sum():.1%}")
        
        # Centres des clusters en 2D
        cluster_centers_full = self.kmeans.cluster_centers_
        self.cluster_centers = self.pca.transform(cluster_centers_full)
    
    def get_cluster_top_skills(self, n_skills: int = 10):
        """
        Extrait les compétences principales de chaque cluster.
        
        Returns:
            Dict {cluster_id: [skills]}
        """
        feature_names = self.vectorizer.get_feature_names_out()
        cluster_skills = {}
        
        for cluster_id in range(self.n_clusters):
            center = self.kmeans.cluster_centers_[cluster_id]
            top_indices = center.argsort()[-n_skills:][::-1]
            top_skills = [feature_names[i] for i in top_indices]
            cluster_skills[cluster_id] = top_skills
        
        return cluster_skills
    
    def print_clusters(self, n_skills: int = 12):
        """Affiche les clusters avec leurs compétences clés"""
        cluster_skills = self.get_cluster_top_skills(n_skills)
        
        print("\n" + "=" * 80)
        print(f"🎯 {self.n_clusters} CLUSTERS DÉCOUVERTS")
        print("=" * 80)
        
        cluster_names = [
            "🤖 ML/AI Specialists",
            "⚙️ Data Engineers",
            "☁️ Cloud/DevOps",
            "📊 BI Analysts",
            "🏗️ Data Architects",
            "🎨 Full Stack Devs"
        ]
        
        # Compter offres par cluster
        unique, counts = np.unique(self.labels, return_counts=True)
        cluster_counts = dict(zip(unique, counts))
        
        for cluster_id in range(self.n_clusters):
            name = cluster_names[cluster_id] if cluster_id < len(cluster_names) else f"Cluster {cluster_id}"
            count = cluster_counts.get(cluster_id, 0)
            pct = (count / len(self.labels)) * 100
            
            print(f"\n{name} - {count} offres ({pct:.1f}%)")
            skills = cluster_skills[cluster_id]
            print(f"   {', '.join(skills)}")
    
    def plot_clusters(self, df: pd.DataFrame = None, save_path: str = None):
        """
        Visualise les clusters en 2D.
        
        Args:
            df: DataFrame avec colonnes 'title', 'region' (optionnel)
            save_path: Chemin pour sauvegarder la figure
        """
        plt.figure(figsize=(14, 10))
        
        # Palette de couleurs
        colors = sns.color_palette("husl", self.n_clusters)
        
        # Scatter plot
        for cluster_id in range(self.n_clusters):
            mask = self.labels == cluster_id
            plt.scatter(
                self.coords_2d[mask, 0],
                self.coords_2d[mask, 1],
                c=[colors[cluster_id]],
                label=f'Cluster {cluster_id}',
                alpha=0.6,
                s=50
            )
        
        # Centres des clusters
        plt.scatter(
            self.cluster_centers[:, 0],
            self.cluster_centers[:, 1],
            c='black',
            marker='X',
            s=300,
            edgecolors='white',
            linewidths=2,
            label='Centres'
        )
        
        plt.xlabel('Composante principale 1', fontsize=12)
        plt.ylabel('Composante principale 2', fontsize=12)
        plt.title(f'Clustering K-Means - {self.n_clusters} Clusters', fontsize=14, fontweight='bold')
        plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"✅ Visualisation sauvegardée: {save_path}")
        
        plt.show()
    
    def get_cluster_assignments(self):
        """
        Retourne les assignments de clusters.
        
        Returns:
            DataFrame avec cluster_id
        """
        return pd.DataFrame({
            'document_id': range(len(self.labels)),
            'cluster_id': self.labels,
            'coord_x': self.coords_2d[:, 0],
            'coord_y': self.coords_2d[:, 1]
        })
    
    def save_model(self, filepath: str):
        """Sauvegarde le modèle"""
        model_data = {
            'vectorizer': self.vectorizer,
            'kmeans': self.kmeans,
            'pca': self.pca,
            'labels': self.labels,
            'coords_2d': self.coords_2d,
            'cluster_centers': self.cluster_centers,
            'n_clusters': self.n_clusters
        }
        
        with open(filepath, 'wb') as f:
            pickle.dump(model_data, f)
        
        print(f"✅ Modèle sauvegardé: {filepath}")


if __name__ == "__main__":
    import sqlite3
    
    print("=" * 80)
    print("🎯 CLUSTERING K-MEANS - REGROUPEMENT DES OFFRES")
    print("=" * 80)
    print()
    
    # Charger données
    print("📂 Chargement des données...")
    conn = sqlite3.connect('../database/jobs.db')
    
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
    
    # Préparer documents
    clusterer = OfferClusterer(n_clusters=6)
    
    skill_docs = []
    for _, row in df.iterrows():
        skills = []
        if pd.notna(row['competences']):
            skills.extend(row['competences'].split(','))
        if pd.notna(row['savoir_etre']):
            skills.extend(row['savoir_etre'].split(','))
        skill_docs.append(" ".join(skills))
    
    # Clustering
    clusterer.fit(skill_docs)
    
    # Afficher clusters
    clusterer.print_clusters(n_skills=12)
    
    # Visualisation
    print("\n📊 Génération de la visualisation...")
    clusterer.plot_clusters(df, save_path='clustering_visualization.png')
    
    # Assignments
    assignments = clusterer.get_cluster_assignments()
    
    # Analyse par région
    print("\n🗺️  Clusters dominants par région (Top 5):")
    df_with_cluster = pd.concat([df.reset_index(drop=True), assignments], axis=1)
    
    top_regions = df_with_cluster['region'].value_counts().head(5).index
    for region in top_regions:
        region_df = df_with_cluster[df_with_cluster['region'] == region]
        top_cluster = region_df['cluster_id'].mode()[0] if len(region_df) > 0 else 0
        count = len(region_df[region_df['cluster_id'] == top_cluster])
        pct = (count / len(region_df)) * 100
        print(f"   {region:30} → Cluster {top_cluster} ({count} offres, {pct:.1f}%)")
    
    # Sauvegarder
    clusterer.save_model('clustering_model.pkl')
    assignments.to_csv('cluster_assignments.csv', index=False)
    
    print("\n Clustering terminé !")