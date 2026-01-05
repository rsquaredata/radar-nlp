from __future__ import annotations

"""
HelloWork HTML collector AMÉLIORÉ - extrait UNIQUEMENT la description de l'offre.
"""

import json
import re
import time
import unicodedata
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Set
from urllib.parse import urljoin, urlencode, urlparse, urlunparse, parse_qs

import pandas as pd
from bs4 import BeautifulSoup

# Assuming http_utils is available
try:
    from http_utils import RobustSession
except ImportError:
    import requests
    RobustSession = requests.Session  # Fallback


BASE = "https://www.hellowork.com"
UA = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/122.0 Safari/537.36"
    )
}

MODE_TO_SEGMENT = {
    "emploi": "emploi",
    "stage": "stage",
    "alternance": "alternance",
}


def slugify(s: str) -> str:
    s = (s or "").strip().lower()
    s = unicodedata.normalize("NFKD", s)
    s = "".join(ch for ch in s if not unicodedata.combining(ch))
    s = re.sub(r"[^a-z0-9\s-]", " ", s)
    s = re.sub(r"\s+", "-", s).strip("-")
    s = re.sub(r"-+", "-", s)
    return s


def set_query_param(url: str, **params: Any) -> str:
    u = urlparse(url)
    q = parse_qs(u.query)
    for k, v in params.items():
        if v is None:
            q.pop(k, None)
        else:
            q[k] = [str(v)]
    query = urlencode({k: v[0] for k, v in q.items()})
    return urlunparse((u.scheme, u.netloc, u.path, u.params, query, u.fragment))


def build_listing_url(mode: str, metier: str, city: Optional[str] = None, postal: Optional[str] = None) -> str:
    mode = (mode or "emploi").strip().lower()
    segment = MODE_TO_SEGMENT.get(mode, "emploi")

    metier_slug = slugify(metier)
    if not metier_slug:
        raise ValueError("Mot-clé / métier vide")

    if city:
        loc = city.strip()
        if postal:
            loc = f"{loc}-{str(postal).strip()}"
        loc_slug = slugify(loc)
        path = f"/fr-fr/{segment}/metier_{metier_slug}-ville_{loc_slug}.html"
    else:
        path = f"/fr-fr/{segment}/metier_{metier_slug}.html"

    return urljoin(BASE, path)


def html_to_text(html: str) -> str:
    """Convertit HTML complet en texte (pour regex d'extraction metadata)"""
    soup = BeautifulSoup(html, "lxml")
    for tag in soup(["script", "style", "noscript"]):
        tag.decompose()
    txt = soup.get_text("\n", strip=True)
    return re.sub(r"\s+", " ", txt).strip()


def extract_description_only(soup: BeautifulSoup) -> str:
    """
    🆕 NOUVELLE FONCTION : Extrait UNIQUEMENT la description de l'offre.
    
    Stratégie multi-niveaux :
    1. Chercher via JSON-LD structuré (le plus propre)
    2. Chercher via sélecteurs CSS spécifiques
    3. Fallback : extraire le plus grand bloc de texte pertinent
    """
    description_text = ""
    
    # ===========================
    # NIVEAU 1 : JSON-LD (structuré, le meilleur)
    # ===========================
    for script in soup.select('script[type="application/ld+json"]'):
        try:
            data = json.loads(script.get_text(strip=True) or "{}")
            if isinstance(data, dict):
                desc = data.get("description")
                if desc and len(str(desc)) > 100:
                    description_text = str(desc)
                    break
        except Exception:
            continue
    
    # ===========================
    # NIVEAU 2 : Sélecteurs CSS spécifiques HelloWork
    # ===========================
    if not description_text:
        selectors = [
            'div[class*="job-description"]',
            'div[class*="JobOffer_description"]',
            'section[class*="description"]',
            'div[id*="description"]',
            'div.tw-prose',  # Tailwind prose class souvent utilisé
        ]
        
        for selector in selectors:
            elements = soup.select(selector)
            for elem in elements:
                text = elem.get_text("\n", strip=True)
                if len(text) > len(description_text):
                    description_text = text
    
    # ===========================
    # NIVEAU 3 : Extraction intelligente par marqueurs
    # ===========================
    if not description_text or len(description_text) < 100:
        # Prendre tout le texte et extraire entre marqueurs
        full_text = soup.get_text("\n", strip=True)
        
        # Marqueurs de début
        start_patterns = [
            r"Détail du poste",
            r"Les missions du poste",
            r"Description du poste",
            r"Le poste :",
            r"Mission",
            r"Contexte",
        ]
        
        # Marqueurs de fin
        end_patterns = [
            r"Le profil recherché",
            r"Profil recherché",
            r"Voir plus",
            r"Les avantages",
            r"Publiée le",
            r"Créez une alerte",
        ]
        
        start_pos = 0
        for pattern in start_patterns:
            match = re.search(pattern, full_text, re.IGNORECASE)
            if match:
                start_pos = match.end()
                break
        
        end_pos = len(full_text)
        for pattern in end_patterns:
            match = re.search(pattern, full_text[start_pos:], re.IGNORECASE)
            if match:
                end_pos = start_pos + match.start()
                break
        
        if end_pos > start_pos:
            description_text = full_text[start_pos:end_pos].strip()
    
    # ===========================
    # NETTOYAGE FINAL
    # ===========================
    # Supprimer fragments HTML
    description_text = re.sub(r'<[^>]+>', '', description_text)
    
    # Supprimer URLs
    description_text = re.sub(r'https?://\S+', '', description_text)
    
    # Supprimer bruit UI
    noise = [
        r"Aller au contenu principal",
        r"Complétez votre profil",
        r"Téléchargez l'app",
        r"Postuler",
        r"Lire dans l'app",
        r"Mon espace",
        r"Hellowork",
    ]
    for pattern in noise:
        description_text = re.sub(pattern, '', description_text, flags=re.IGNORECASE)
    
    # Normaliser espaces
    description_text = re.sub(r'\s+', ' ', description_text).strip()
    
    # Limiter longueur
    return description_text[:5000]


def extract_offer_links(listing_html: str) -> List[str]:
    soup = BeautifulSoup(listing_html, "lxml")
    links: Set[str] = set()
    for a in soup.select("a[href]"):
        href = (a.get("href") or "").strip()
        if not href:
            continue
        if "/fr-fr/emplois/" in href and href.endswith(".html"):
            links.add(urljoin(BASE, href))
    return sorted(links)


def iter_listing_pages(rs: RobustSession, url: str, max_pages: int, sleep_s: float) -> Iterable[str]:
    for p in range(1, max_pages + 1):
        page_url = set_query_param(url, p=p) if p > 1 else url
        r = rs.get(page_url, headers=UA)
        if r.status_code != 200 or not r.text:
            break
        yield r.text
        time.sleep(sleep_s)


@dataclass
class Offer:
    source: str
    url: str
    offer_id: Optional[str]
    title: Optional[str]
    employer: Optional[str]
    location: Optional[str]
    contract_type: Optional[str]
    salary: Optional[str]
    remote: str
    published_relative: Optional[str]
    description: str  # 🆕 Champ renommé (était raw_text)


def _text_or_none(el) -> Optional[str]:
    if not el:
        return None
    t = el.get_text(" ", strip=True)
    return t or None


def parse_offer_page(html: str, url: str) -> Offer:
    """
    🆕 VERSION AMÉLIORÉE : extrait description propre + metadata
    """
    soup = BeautifulSoup(html, "lxml")

    m = re.search(r"/emplois/(\d+)\.html", url)
    offer_id = m.group(1) if m else None

    title = _text_or_none(soup.select_one("h1"))

    # Pour les regex d'extraction (location, salary, etc.), on garde le texte complet
    page_text_full = html_to_text(html)
    
    # 🆕 Pour la description, on utilise la nouvelle fonction
    description = extract_description_only(soup)

    # Extraction metadata (inchangé, utilise page_text_full)
    location = None
    mloc = re.search(r"\b([A-ZÉÈÊÀÂÎÏÔÙÛÇ][\w''\- ]+\s-\s\d{2})\b", page_text_full)
    if mloc:
        location = mloc.group(1).strip()

    contract_type = None
    mct = re.search(r"\b(CDI|CDD|Intérim|Stage|Alternance|Freelance|Indépendant|Franchise)\b", page_text_full, flags=re.IGNORECASE)
    if mct:
        contract_type = mct.group(1)

    salary = None
    msal = re.search(r"\b\d[\d\s\u202f]*\s?(?:-\s?\d[\d\s\u202f]*\s?)?€\s?/\s?(?:an|mois|heure)\b", page_text_full, flags=re.IGNORECASE)
    if msal:
        salary = re.sub(r"\s+", " ", msal.group(0)).strip()

    remote = "unknown"
    if re.search(r"\btélétravail\s+(complet|total)\b", page_text_full, flags=re.IGNORECASE):
        remote = "yes"
    elif re.search(r"\btélétravail\s+(partiel|hybride|occasionnel)\b", page_text_full, flags=re.IGNORECASE):
        remote = "yes"
    elif re.search(r"\bpas de télétravail\b", page_text_full, flags=re.IGNORECASE):
        remote = "no"

    published_relative = None
    mpub = re.search(r"\b(il y a \d+ (?:jour|jours|heure|heures|minute|minutes)|moins d'une heure)\b", page_text_full, flags=re.IGNORECASE)
    if mpub:
        published_relative = mpub.group(1)

    employer = None
    for script in soup.select('script[type="application/ld+json"]'):
        try:
            data = json.loads(script.get_text(strip=True) or "{}")
        except Exception:
            continue
        if isinstance(data, dict):
            hiring = data.get("hiringOrganization")
            if isinstance(hiring, dict) and hiring.get("name"):
                employer = str(hiring.get("name")).strip() or None
        if employer:
            break

    return Offer(
        source="hellowork.com",
        url=url,
        offer_id=offer_id,
        title=title,
        employer=employer,
        location=location,
        contract_type=contract_type,
        salary=salary,
        remote=remote,
        published_relative=published_relative,
        description=description,  # 🆕 Description propre uniquement
    )


def save_jsonl(rows: List[Dict[str, Any]], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")


def save_csv(rows: List[Dict[str, Any]], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    df = pd.DataFrame(rows)
    # Plus besoin de tronquer, la description est déjà propre et limitée
    df.to_csv(path, index=False, encoding="utf-8")


def scrape_hellowork(
    keywords: List[str],
    city: Optional[str] = None,
    postal: Optional[str] = None,
    mode: str = "emploi",
    max_pages: int = 10,
    max_urls: int = 400,
    sleep_s: float = 0.4,
    out_dir: str = "../data",
) -> Dict[str, Any]:
    """
    Main function - version améliorée avec descriptions propres
    """
    rs = RobustSession()
    urls: Set[str] = set()

    for kw in keywords:
        kw = (kw or "").strip()
        if not kw:
            continue

        listing_url = build_listing_url(mode=mode, metier=kw, city=city, postal=postal)

        try:
            for page_html in iter_listing_pages(rs, listing_url, max_pages=max_pages, sleep_s=sleep_s):
                for u in extract_offer_links(page_html):
                    urls.add(u)
                    if len(urls) >= max_urls:
                        break
                if len(urls) >= max_urls:
                    break
        except Exception:
            continue

    offer_urls = sorted(urls)
    print(f"[HelloWork] URLs collectées: {len(offer_urls)}")

    offers: List[Offer] = []
    for i, url in enumerate(offer_urls, start=1):
        try:
            r = rs.get(url, headers=UA)
            if r.status_code != 200 or not r.text:
                continue
            offers.append(parse_offer_page(r.text, url=url))
        except Exception:
            continue

        if i % 50 == 0:
            print(f"[HelloWork] Traité {i}/{len(offer_urls)}")
        time.sleep(sleep_s)

    rows = [asdict(o) for o in offers]

    out_path = Path(out_dir)
    out_path.mkdir(parents=True, exist_ok=True)

    tag = "france" if not city else slugify(f"{city}-{postal}" if postal else city)
    jsonl_path = out_path / f"hellowork_{mode}_{tag}_clean.jsonl"
    csv_path = out_path / f"hellowork_{mode}_{tag}_clean.csv"

    save_jsonl(rows, jsonl_path)
    save_csv(rows, csv_path)

    print(f"✅ Sauvegardé: {len(rows)} offres avec descriptions propres")
    return {
        "count": len(rows),
        "jsonl": str(jsonl_path),
        "csv": str(csv_path),
        "mode": mode,
        "tag": tag,
    }