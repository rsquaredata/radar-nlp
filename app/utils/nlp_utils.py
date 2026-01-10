import pandas as pd
import numpy as np
from pathlib import Path
import pickle
from typing import Dict, List, Tuple, Any
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import io
import sys

sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from config import TOPIC_MODEL_PATH, CLUSTERING_MODEL_PATH, PROFILE_NAMES




def load_topic_model():
    """Charge le modèle de topic modeling"""
    if not TOPIC_MODEL_PATH.exists():
        return None
    
    with open(TOPIC_MODEL_PATH, 'rb') as f:
        model_data = pickle.load(f)
    
    return model_data


def load_clustering_model():
    """Charge le modèle de clustering"""
    if not CLUSTERING_MODEL_PATH.exists():
        return None
    
    with open(CLUSTERING_MODEL_PATH, 'rb') as f:
        model_data = pickle.load(f)
    
    return model_data




def get_topic_distribution(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calcule la distribution des topics dans le DataFrame.
    
    Args:
        df: DataFrame avec colonne 'dominant_profile' ou 'dominant_topic'
    
    Returns:
        DataFrame avec topic_id, count, percentage
    """
    topic_col = 'dominant_profile' if 'dominant_profile' in df.columns else 'dominant_topic'
    
    if topic_col not in df.columns:
        return pd.DataFrame()
    
    topic_counts = df[topic_col].value_counts().reset_index()
    topic_counts.columns = ['topic_id', 'count']
    topic_counts['percentage'] = (topic_counts['count'] / len(df)) * 100
    topic_counts['topic_name'] = topic_counts['topic_id'].map(PROFILE_NAMES)
    
    return topic_counts.sort_values('topic_id')


def get_topic_keywords(topic_model, topic_id: int, n_words: int = 10) -> List[str]:
    """
    Retourne les mots-clés d'un topic.
    
    Args:
        topic_model: Modèle chargé
        topic_id: ID du topic
        n_words: Nombre de mots
    
    Returns:
        Liste de mots-clés
    """
    if not topic_model or 'topics' not in topic_model:
        return []
    
    topics = topic_model['topics']
    
    if topic_id >= len(topics):
        return []
    
    return topics[topic_id]['skills'][:n_words]


def get_representative_offers(df: pd.DataFrame, 
                              topic_id: int,
                              n: int = 5) -> pd.DataFrame:
 
    topic_col = 'dominant_profile' if 'dominant_profile' in df.columns else 'dominant_topic'
    prob_col = 'profile_probability' if 'profile_probability' in df.columns else 'topic_probability'
    
    if topic_col not in df.columns or prob_col not in df.columns:
        return pd.DataFrame()
    
    # Filtrer le topic
    topic_df = df[df[topic_col] == topic_id]
    
    # Trier par probabilité
    return topic_df.nlargest(n, prob_col)




def get_cluster_centers_2d(clustering_model) -> np.ndarray:
   
    
    if not clustering_model or 'cluster_centers' not in clustering_model:
        return np.array([])
    
    return clustering_model['cluster_centers']


def get_cluster_coordinates(df: pd.DataFrame) -> Tuple[np.ndarray, np.ndarray]:
 
    if 'coord_x' not in df.columns or 'coord_y' not in df.columns:
        return np.array([]), np.array([])
    
    coords = df[['coord_x', 'coord_y']].values
    labels = df['cluster_id'].values if 'cluster_id' in df.columns else np.zeros(len(df))
    
    return coords, labels




def generate_wordcloud_image(text: str, 
                             width: int = 800,
                             height: int = 400,
                             colormap: str = 'viridis') -> bytes:
    
    if not text or len(text.strip()) == 0:
        return None
    
    # Générer word cloud
    wordcloud = WordCloud(
        width=width,
        height=height,
        background_color='white',
        colormap=colormap,
        max_words=100,
        relative_scaling=0.5,
        min_font_size=10
    ).generate(text)
    
    # Créer figure matplotlib
    fig, ax = plt.subplots(figsize=(width/100, height/100), dpi=100)
    ax.imshow(wordcloud, interpolation='bilinear')
    ax.axis('off')
    plt.tight_layout(pad=0)
    
    # Convertir en bytes
    buf = io.BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight', facecolor='white')
    buf.seek(0)
    plt.close()
    
    return buf.getvalue()


def generate_wordcloud_from_skills(skills: List[str], **kwargs) -> bytes:
 
    if not skills:
        return None
    
    # Créer texte (répéter selon fréquence)
    from collections import Counter
    skill_counts = Counter(skills)
    
    text_parts = []
    for skill, count in skill_counts.items():
        text_parts.extend([skill] * count)
    
    text = " ".join(text_parts)
    
    return generate_wordcloud_image(text, **kwargs)


def generate_regional_wordcloud(df: pd.DataFrame, 
                                region: str,
                                skill_column: str = 'all_skills') -> bytes:
    
    # Filtrer région
    region_df = df[df['region_name'] == region]
    
    if len(region_df) == 0:
        return None
    
    # Collecter toutes les compétences
    all_skills = []
    for skills in region_df[skill_column].dropna():
        if isinstance(skills, str):
            all_skills.extend(skills.split(','))
    
    if not all_skills:
        return None
    
    return generate_wordcloud_from_skills(all_skills)


# ============================================================================
# TF-IDF
# ============================================================================

def compute_tfidf_scores(documents: List[str], 
                        max_features: int = 50) -> pd.DataFrame:
    """
    Calcule les scores TF-IDF pour une liste de documents.
    
    Args:
        documents: Liste de textes
        max_features: Nombre max de features
    
    Returns:
        DataFrame avec termes et scores
    """
    from sklearn.feature_extraction.text import TfidfVectorizer
    
    vectorizer = TfidfVectorizer(
        max_features=max_features,
        min_df=2,
        token_pattern=r'\b\w+\b'
    )
    
    try:
        tfidf_matrix = vectorizer.fit_transform(documents)
        feature_names = vectorizer.get_feature_names_out()
        
        # Moyenne des scores
        mean_scores = tfidf_matrix.mean(axis=0).A1
        
        # Créer DataFrame
        df_tfidf = pd.DataFrame({
            'term': feature_names,
            'tfidf_score': mean_scores
        }).sort_values('tfidf_score', ascending=False)
        
        return df_tfidf
        
    except Exception as e:
        print(f"Erreur TF-IDF: {e}")
        return pd.DataFrame()


def compare_regional_tfidf(df: pd.DataFrame, 
                          region1: str,
                          region2: str,
                          skill_column: str = 'all_skills',
                          n_terms: int = 15) -> Dict[str, List[str]]:
    """
    Compare les termes TF-IDF de 2 régions.
    
    Args:
        df: DataFrame avec 'region_name' et skill_column
        region1: Première région
        region2: Deuxième région
        skill_column: Colonne des compétences
        n_terms: Nombre de termes
    
    Returns:
        Dict avec 'unique_region1', 'unique_region2', 'common'
    """
    # Documents région 1
    docs1 = df[df['region_name'] == region1][skill_column].dropna().tolist()
    tfidf1 = compute_tfidf_scores(docs1, max_features=n_terms)
    
    # Documents région 2
    docs2 = df[df['region_name'] == region2][skill_column].dropna().tolist()
    tfidf2 = compute_tfidf_scores(docs2, max_features=n_terms)
    
    # Termes
    terms1 = set(tfidf1['term'].head(n_terms).tolist())
    terms2 = set(tfidf2['term'].head(n_terms).tolist())
    
    return {
        'unique_region1': list(terms1 - terms2),
        'unique_region2': list(terms2 - terms1),
        'common': list(terms1 & terms2)
    }




def extract_top_skills_by_group(df: pd.DataFrame,
                                group_column: str,
                                skill_column: str = 'all_skills',
                                n_skills: int = 10) -> Dict[str, List[Tuple[str, int]]]:
    
    from collections import Counter
    
    results = {}
    
    for group in df[group_column].dropna().unique():
        group_df = df[df[group_column] == group]
        
        all_skills = []
        for skills in group_df[skill_column].dropna():
            if isinstance(skills, str):
                all_skills.extend(skills.split(','))
        
        skill_counts = Counter(all_skills)
        results[group] = skill_counts.most_common(n_skills)
    
    return results


def calculate_skill_correlation(df: pd.DataFrame,
                                skill_column: str = 'all_skills') -> pd.DataFrame:
  
    from sklearn.feature_extraction.text import CountVectorizer
    
    documents = df[skill_column].dropna().tolist()
    
    vectorizer = CountVectorizer(
        max_features=50,
        binary=True,
        token_pattern=r'\b\w+\b'
    )
    
    try:
        matrix = vectorizer.fit_transform(documents).toarray()
        feature_names = vectorizer.get_feature_names_out()
        
        # Corrélation
        corr_matrix = np.corrcoef(matrix.T)
        
        return pd.DataFrame(
            corr_matrix,
            index=feature_names,
            columns=feature_names
        )
        
    except Exception as e:
        print(f"Erreur corrélation: {e}")
        return pd.DataFrame()

