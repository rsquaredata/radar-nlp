from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, date
from typing import Any, Dict, List, Optional, Tuple
import html
import re


# ============
# Types
# ============

@dataclass
class OffreNLP:
    """
    Représente une offre prête à être envoyée vers upsert_offre_complete().
    """
    source_name: str
    url: str
    date_publication: date

    ville_nom: Optional[str]
    code_postal: Optional[str]

    metier_id: Optional[int]  # sera résolu par ton module métier
    type_contrat: Optional[str]
    niveau_etude: Optional[str]

    salaire_min: Optional[float]
    salaire_max: Optional[float]
    salaire_brut_net_flag: Optional[str]

    texte: Dict[str, Optional[str]]  # {titre, missions, profil, competences, remuneration, texte_complet, texte_clean}

    skills: List[Tuple[int, float]]  # [(skill_id, importance)]
    hash_offre: Optional[str]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "source_name": self.source_name,
            "url": self.url,
            "date_publication": self.date_publication,
            "ville_nom": self.ville_nom,
            "code_postal": self.code_postal,
            "metier_id": self.metier_id,
            "type_contrat": self.type_contrat,
            "niveau_etude": self.niveau_etude,
            "salaire_min": self.salaire_min,
            "salaire_max": self.salaire_max,
            "salaire_brut_net_flag": self.salaire_brut_net_flag,
            "texte": self.texte,
            "skills": self.skills,
            "hash_offre": self.hash_offre,
        }


# ============
# Helpers NLP
# ============

def _clean_html_to_text(raw_html: str | None) -> str:
    """
    Nettoyage minimal de HTML => texte brut.
    TODO : remplacer par BeautifulSoup / html2text / ton outil favori.
    """
    if not raw_html:
        return ""

    # 1) unescape des entités HTML
    text = html.unescape(raw_html)

    # 2) enlever les balises - TODO version naïve à remplacer
    text = re.sub(r"<[^>]+>", " ", text)

    # 3) normalisation basique des espaces
    text = re.sub(r"\s+", " ", text).strip()

    return text


def _segmenter_texte(texte_clean: str) -> Dict[str, Optional[str]]:
    """
    Découpe le texte en blocs (missions, profil, compétences, etc.).
    TODO : squelette à améliorer.
    """
    # TODO : implémenter une vraie segmentation.
    # Pour l'instant, on renvoie tout dans texte_complet.
    return {
        "titre": None,           # éventuellement à partir de titre_raw plus tard
        "missions": None,
        "profil": None,
        "competences": None,
        "remuneration": None,
        "texte_complet": texte_clean,
        "texte_clean": texte_clean,  # TODO : appliquer d'autres nettoyages ici
    }


def _parse_date_publication(
    date_publication_raw: Optional[str],
    scraped_at_iso: Optional[str],
) -> date:
    """
    Transforme une date publication brute (ex.: 'Publié il y a 3 jours') en un objet date.
    Pour l'instant, fallback = date du scraping.
    TODO : implémenter une vraie logique de parsing relative.
    """
    if scraped_at_iso:
        try:
            scraped_dt = datetime.fromisoformat(scraped_at_iso.replace("Z", "+00:00"))
        except Exception:
            scraped_dt = datetime.utcnow()
    else:
        scraped_dt = datetime.utcnow()

    # TODO : si date_publication_raw contient une date explicite → la parser
    # TODO : si 'il y a X jours' → soustraire X jours à scraped_dt

    return scraped_dt.date()


def _normalize_lieu(lieu_raw: Optional[str]) -> Tuple[Optional[str], Optional[str]]:
    """
    Transforme le lieu brut en (ville_nom, code_postal).
    Ex : 'Lyon (69)' -> ('Lyon', None) ou ('Lyon', '69000') selon ta convention
    TODO : affiner avec des regex + référentiels CP.
    """
    if not lieu_raw:
        return None, None

    # Extraire la partie avant la parenthèse : par exemple, 'Lyon (69)' -> 'Lyon'
    m = re.match(r"^\s*([^()]+)", lieu_raw)
    ville_nom = m.group(1).strip() if m else lieu_raw.strip()

    # TODO : extraire le code postal si présent (75008 Paris, 69001 Lyon, etc.)
    code_postal = None

    return ville_nom, code_postal


def _normalize_type_contrat(raw: Optional[str]) -> Optional[str]:
    """
    Normalise les types de contrat (CDI, CDD, Stage, Alternance, Cifre, etc.)
    TODO : implémenter mapping plus robuste (regex, dictionnaire...).
    """
    if not raw:
        return None

    s = raw.lower()
    if "cdi" in s:
        return "CDI"
    if "cdd" in s:
        return "CDD"
    if "stage" in s:
        return "Stage"
    if "alternance" in s or "apprentissage" in s:
        return "Alternance"

    return raw.strip()


def _parse_salaire(raw: Optional[str]) -> Tuple[Optional[float], Optional[float], Optional[str]]:
    """
    Transforme un salaire brut en texte en seuils numériques approximatifs.
    Retourne (salaire_min, salaire_max, flag_brut_net).
    TODO : affiner les regex / unités.
    """
    if not raw:
        return None, None, None

    txt = raw.replace("\u202f", " ")  # espaces fines insécables
    txt = txt.replace("\xa0", " ")

    # Détection brut/net rudimentaire
    flag = None
    if "brut" in txt.lower():
        flag = "BRUT"
    elif "net" in txt.lower():
        flag = "NET"

    # Regex pour trouver des nombres genre 45k, 55 000, 45-55k, etc.
    # TODO : à améliorer.
    numbers = re.findall(r"(\d[\d\s]{0,5})", txt)
    nums: List[int] = []
    for n in numbers:
        n_clean = n.replace(" ", "")
        try:
            nums.append(int(n_clean))
        except ValueError:
            continue

    if not nums:
        return None, None, flag

    if len(nums) == 1:
        return float(nums[0]), float(nums[0]), flag
    else:
        return float(min(nums)), float(max(nums)), flag


def _infer_niveau_etude(texte_clean: str) -> Optional[str]:
    """
    Détecte un niveau d'étude approximatif à partir du texte.
    TODO : remplacer par logique plus fine (regex, modèle, etc.).
    """
    s = texte_clean.lower()
    if "bac+5" in s or "bac +5" in s:
        return "Bac+5"
    if "bac+3" in s or "bac +3" in s:
        return "Bac+3"
    if "bac+2" in s or "bac +2" in s:
        return "Bac+2"
    return None


def _match_metier_id(
    titre_raw: Optional[str],
    texte_clean: str,
) -> Optional[int]:
    """
    Détermine le metier_id en fonction du titre et/ou du texte.
    Pour l'instant renvoie None, à connecter au référentiel (dim_metier).
    TODO :
      - charger un mapping mots-clés -> metier_id
      - ou interroger la DB en lecture seule
      - ou utiliser un modèle de classification.
    """
    # Esquisse :
    # if titre_raw and "data scientist" in titre_raw.lower():
    #     return 101
    return None


def _detect_skills(texte_clean: str) -> List[Tuple[int, float]]:
    """
    Détecte les skills dans le texte et renvoie une liste (skill_id, importance).
    TODO :
      - soit lookup sur un fichier de référentiel skills + regex
      - soit modèle de NER / multi-label classification.
    """
    # Placeholder : aucune skill détectée
    return []


# ============
# Fonction principale
# ============

def process_offre(raw_job: Dict[str, Any]) -> Dict[str, Any]:
    """
    Étape 2 : NLP / pré-traitement.

    - Prend un raw_job (= sortie du scraping)
    - Nettoie / normalise / enrichit
    - Renvoie un dict 'offre_nlp' prêt pour upsert_offre_complete().
    """

    # 1) Source & URL
    source_name = raw_job.get("source", "").strip()
    url = raw_job.get("url", "").strip()

    # 2) Date de publication
    date_publication_raw = raw_job.get("date_publication_raw")
    scraped_at = raw_job.get("scraped_at")
    date_publication = _parse_date_publication(date_publication_raw, scraped_at)

    # 3) Lieu -> ville_nom / code_postal
    lieu_raw = raw_job.get("lieu_raw")
    ville_nom, code_postal = _normalize_lieu(lieu_raw)

    # 4) Texte : HTML brut -> texte propre + segmentation
    texte_complet_raw = raw_job.get("texte_complet_raw") or ""
    texte_clean = _clean_html_to_text(texte_complet_raw)
    blocs = _segmenter_texte(texte_clean)

    # 5) Type contrat & salaire & niveau d'étude (approximatif)
    type_contrat_raw = raw_job.get("type_contrat_raw")
    type_contrat = _normalize_type_contrat(type_contrat_raw)

    salaire_min, salaire_max, salaire_flag = _parse_salaire(raw_job.get("salaire_raw"))
    niveau_etude = _infer_niveau_etude(texte_clean)

    # 6) Métier
    titre_raw = raw_job.get("titre_raw")
    metier_id = _match_metier_id(titre_raw, texte_clean)

    # 7) Skills
    skills = _detect_skills(texte_clean)

    # 8) Hash (optionnel : à calculer au moment DB)
    hash_offre = None  # TODO : calculer éventuellement un hash stable à partir de url + texte

    # 9) Construire l'objet OffreNLP puis le transformer en dict
    offre = OffreNLP(
        source_name=source_name,
        url=url,
        date_publication=date_publication,
        ville_nom=ville_nom,
        code_postal=code_postal,
        metier_id=metier_id,
        type_contrat=type_contrat,
        niveau_etude=niveau_etude,
        salaire_min=salaire_min,
        salaire_max=salaire_max,
        salaire_brut_net_flag=salaire_flag,
        texte=blocs,
        skills=skills,
        hash_offre=hash_offre,
    )

    return offre.to_dict()
