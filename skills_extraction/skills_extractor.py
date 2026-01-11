import re
import json
from pathlib import Path
from typing import List, Dict, Set, Tuple
from dataclasses import dataclass
from collections import defaultdict


@dataclass
class Skill:
    name: str
    category: str  
    type: str      
    confidence: float  


class SkillsExtractor:

    
    def __init__(self, skills_dict_path: str = None):
        """
        Args:
            skills_dict_path: Chemin vers skills_dict.json
        """
        if skills_dict_path is None:
            skills_dict_path = Path(__file__).parent / "skills_dict.json"
        
        # Charger le dictionnaire
        with open(skills_dict_path, 'r', encoding='utf-8') as f:
            self.skills_data = json.load(f)
        
        # Construire les patterns de recherche
        self._build_search_patterns()
    
    def _build_search_patterns(self):
        """
        Construit les patterns regex pour chaque compétence.
        """
        self.patterns = {}
        
        # Hard skills (competences)
        for category, data in self.skills_data['hard_skills'].items():
            for skill in data['skills']:
                pattern = rf'\b{re.escape(skill)}\b'
                
                self.patterns[skill] = {
                    'pattern': re.compile(pattern, re.IGNORECASE),
                    'category': category,
                    'type': 'competences'
                }
                
                # Variantes communes
                variations = self._generate_variations(skill)
                for var in variations:
                    if var not in self.patterns:
                        self.patterns[var] = {
                            'pattern': re.compile(rf'\b{re.escape(var)}\b', re.IGNORECASE),
                            'category': category,
                            'type': 'competences',
                            'canonical': skill
                        }
        
        # Soft skills (savoir_etre)
        for category, data in self.skills_data['soft_skills'].items():
            for skill in data['skills']:
                pattern = rf'\b{re.escape(skill)}\b'
                
                self.patterns[skill] = {
                    'pattern': re.compile(pattern, re.IGNORECASE),
                    'category': category,
                    'type': 'savoir_etre'
                }
        
        # Certifications (competences)
        for cert in self.skills_data['certifications']['skills']:
            pattern = rf'\b{re.escape(cert)}\b'
            self.patterns[cert] = {
                'pattern': re.compile(pattern, re.IGNORECASE),
                'category': 'certifications',
                'type': 'competences'
            }
    
    def _generate_variations(self, skill: str) -> List[str]:
        """
        Génère des variations courantes d'une compétence.
        """
        variations = []
        
        known_variations = {
            "Python": ["python3", "py"],
            "JavaScript": ["JS", "javascript"],
            "TypeScript": ["TS"],
            "PostgreSQL": ["Postgres", "psql"],
            "MySQL": ["mysql"],
            "MongoDB": ["mongo"],
            "TensorFlow": ["tf"],
            "PyTorch": ["torch"],
            "Scikit-learn": ["sklearn", "scikit learn"],
            "Natural Language Processing": ["NLP"],
            "Computer Vision": ["CV"],
            "Machine Learning": ["ML"],
            "Deep Learning": ["DL"],
            "Artificial Intelligence": ["AI", "IA"],
            "Amazon Web Services": ["AWS"],
            "Google Cloud Platform": ["GCP"],
            "Microsoft Azure": ["Azure"],
            "Kubernetes": ["k8s"],
        }
        
        if skill in known_variations:
            variations.extend(known_variations[skill])
        
        if "." in skill:
            variations.append(skill.replace(".", ""))
        
        if "-" in skill:
            variations.append(skill.replace("-", " "))
            variations.append(skill.replace("-", ""))
        
        return variations
    
    def extract(self, text: str, min_confidence: float = 0.5) -> List[Skill]:
        """
        Extrait les compétences d'un texte.
        
        Args:
            text: Texte à analyser (description d'offre)
            min_confidence: Score de confiance minimum
        
        Returns:
            Liste de compétences extraites
        """
        if not text or not isinstance(text, str):
            return []
        
        text = self._normalize_text(text)
        
        found_skills = {}
        
        for skill_name, pattern_data in self.patterns.items():
            matches = pattern_data['pattern'].finditer(text)
            
            for match in matches:
                confidence = self._calculate_confidence(match, text)
                
                if confidence < min_confidence:
                    continue
                
                canonical_name = pattern_data.get('canonical', skill_name)
                
                if canonical_name in found_skills:
                    if confidence > found_skills[canonical_name].confidence:
                        found_skills[canonical_name].confidence = confidence
                else:
                    found_skills[canonical_name] = Skill(
                        name=canonical_name,
                        category=pattern_data['category'],
                        type=pattern_data['type'],
                        confidence=confidence
                    )
        
        return sorted(found_skills.values(), key=lambda s: s.confidence, reverse=True)
    
    def _normalize_text(self, text: str) -> str:
        """Normalise le texte"""
        text = re.sub(r'\s+', ' ', text)
        text = re.sub(r'([A-Z])\.([A-Z])\.([A-Z])', r'\1\2\3', text)
        return text.strip()
    
    def _calculate_confidence(self, match, text: str) -> float:
        """Calcule un score de confiance"""
        confidence = 0.7
        
        matched_text = match.group(0)
        start_pos = match.start()
        
        if start_pos < 500:
            confidence += 0.2
        
        if matched_text[0].isupper():
            confidence += 0.1
        
        context_start = max(0, start_pos - 50)
        context_end = min(len(text), match.end() + 50)
        context = text[context_start:context_end].lower()
        
        positive_keywords = [
            'expérience', 'maîtrise', 'connaissance', 'compétence',
            'expertise', 'utilisation', 'développement', 'implémentation',
            'required', 'must', 'skill', 'experience', 'knowledge'
        ]
        
        for keyword in positive_keywords:
            if keyword in context:
                confidence += 0.05
                break
        
        return min(confidence, 1.0)
    
    def extract_by_type(self, text: str) -> Dict[str, List[str]]:
        """
        Extrait les compétences groupées par type.
        
        Returns:
            Dict {'competences': [...], 'savoir_etre': [...]}
        """
        skills = self.extract(text)
        
        by_type = {'competences': [], 'savoir_etre': []}
        for skill in skills:
            by_type[skill.type].append(skill.name)
        
        return by_type
    
    def extract_by_category(self, text: str) -> Dict[str, List[str]]:
        """
        Extrait les compétences groupées par catégorie.
        """
        skills = self.extract(text)
        
        by_category = defaultdict(list)
        for skill in skills:
            by_category[skill.category].append(skill.name)
        
        return dict(by_category)




def extract_skills_from_dataframe(df, text_column: str = 'description'):
    """
    Applique l'extraction sur un DataFrame pandas.
    
    Ajoute les colonnes :
    - competences : liste des hard skills
    - savoir_etre : liste des soft skills
    - skills_count : nombre total de compétences
    """
    import pandas as pd
    
    extractor = SkillsExtractor()
    
    print(f"Extraction des compétences sur {len(df)} offres...")
    
    results = []
    for idx, row in df.iterrows():
        text = row[text_column] if pd.notna(row[text_column]) else ""
        
        skills = extractor.extract(text)
        by_type = extractor.extract_by_type(text)
        
        results.append({
            'competences': by_type['competences'],
            'savoir_etre': by_type['savoir_etre'],
            'skills_count': len(skills),
            'skills_json': json.dumps([{
                'name': s.name,
                'category': s.category,
                'type': s.type,
                'confidence': s.confidence
            } for s in skills], ensure_ascii=False)
        })
        
        if (idx + 1) % 100 == 0:
            print(f"   Traité {idx + 1}/{len(df)}")
    
    results_df = pd.DataFrame(results)
    df_enriched = pd.concat([df, results_df], axis=1)
    
    print(f"Extraction terminée!")
    print(f"Moyenne: {df_enriched['skills_count'].mean():.1f} compétences/offre")
    
    return df_enriched


def get_global_skills_stats(df_enriched):
    """
    Calcule les statistiques globales sur les compétences.
    """
    from collections import Counter
    
    all_competences = []
    all_savoir_etre = []
    
    for comp_list in df_enriched['competences']:
        all_competences.extend(comp_list)
    
    for se_list in df_enriched['savoir_etre']:
        all_savoir_etre.extend(se_list)
    
    comp_counts = Counter(all_competences)
    se_counts = Counter(all_savoir_etre)
    
    return {
        'total_competences': len(comp_counts),
        'total_savoir_etre': len(se_counts),
        'total_mentions': sum(comp_counts.values()) + sum(se_counts.values()),
        'top_competences': comp_counts.most_common(20),
        'top_savoir_etre': se_counts.most_common(15),
        'avg_skills_per_offer': df_enriched['skills_count'].mean(),
        'median_skills_per_offer': df_enriched['skills_count'].median()
    }


if __name__ == "__main__":
    # Test simple
    extractor = SkillsExtractor()
    
    test_text = """
    Nous recherchons un Data Scientist expérimenté avec une forte expertise en Python et SQL.
    
    Compétences requises:
    - Maîtrise de Python (Pandas, NumPy, Scikit-learn)
    - Expérience avec TensorFlow ou PyTorch
    - Connaissance de AWS (S3, EMR, SageMaker)
    - SQL avancé (PostgreSQL)
    - Spark / PySpark pour le Big Data
    - Docker et Kubernetes
    
    Compétences appréciées:
    - MLflow, Airflow
    - Tableau ou Power BI
    - Méthodologie Agile
    
    Savoir-être:
    - Excellentes capacités de communication
    - Esprit d'équipe
    - Autonomie et rigueur
    """
    
    print("=" * 80)
    print("TEST EXTRACTION DE COMPÉTENCES")
    print("=" * 80)
    print()
    
    by_type = extractor.extract_by_type(test_text)
    
    print("COMPÉTENCES (Hard Skills):")
    for skill in by_type['competences']:
        print(f"• {skill}")
    
    print()
    print("SAVOIR-ÊTRE (Soft Skills):")
    for skill in by_type['savoir_etre']:
        print(f"• {skill}")
    
    print()
    print("=" * 80)