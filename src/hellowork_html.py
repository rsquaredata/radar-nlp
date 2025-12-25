from __future__ import annotations

"""
HelloWork HTML collector (France entière ou filtré ville).

- Listing pages (emploi / stage / alternance):
  https://www.hellowork.com/fr-fr/emploi/metier_<metier_slug>.html
  https://www.hellowork.com/fr-fr/emploi/metier_<metier_slug>-ville_<city_slug>.html

- Offer pages:
  https://www.hellowork.com/fr-fr/emplois/<id>.html

Sorties:
- hellowork_<mode>_<tag>_raw.jsonl
- hellowork_<mode>_<tag>_raw.csv
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

from http_utils import RobustSession


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
        # ex: paris-75000
        loc = city.strip()
        if postal:
            loc = f"{loc}-{str(postal).strip()}"
        loc_slug = slugify(loc)
        path = f"/fr-fr/{segment}/metier_{metier_slug}-ville_{loc_slug}.html"
    else:
        path = f"/fr-fr/{segment}/metier_{metier_slug}.html"

    return urljoin(BASE, path)


def html_to_text(html: str) -> str:
    soup = BeautifulSoup(html, "lxml")
    for tag in soup(["script", "style", "noscript"]):
        tag.decompose()
    txt = soup.get_text("\n", strip=True)
    return re.sub(r"\s+", " ", txt).strip()


def extract_offer_links(listing_html: str) -> List[str]:
    soup = BeautifulSoup(listing_html, "lxml")
    links: Set[str] = set()
    for a in soup.select("a[href]"):
        href = (a.get("href") or "").strip()
        if not href:
            continue
        # Offer pages: /fr-fr/emplois/<id>.html
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
    remote: str  # yes/no/unknown
    published_relative: Optional[str]
    raw_text: str


def _text_or_none(el) -> Optional[str]:
    if not el:
        return None
    t = el.get_text(" ", strip=True)
    return t or None


def parse_offer_page(html: str, url: str) -> Offer:
    soup = BeautifulSoup(html, "lxml")

    m = re.search(r"/emplois/(\d+)\.html", url)
    offer_id = m.group(1) if m else None

    title = _text_or_none(soup.select_one("h1"))

    page_text = html_to_text(html)

    location = None
    mloc = re.search(r"\b([A-ZÉÈÊÀÂÎÏÔÙÛÇ][\w'’\- ]+\s-\s\d{2})\b", page_text)
    if mloc:
        location = mloc.group(1).strip()

    contract_type = None
    mct = re.search(r"\b(CDI|CDD|Intérim|Stage|Alternance|Freelance|Indépendant|Franchise)\b", page_text, flags=re.IGNORECASE)
    if mct:
        contract_type = mct.group(1)

    salary = None
    msal = re.search(r"\b\d[\d\s\u202f]*\s?(?:-\s?\d[\d\s\u202f]*\s?)?€\s?/\s?(?:an|mois|heure)\b", page_text, flags=re.IGNORECASE)
    if msal:
        salary = re.sub(r"\s+", " ", msal.group(0)).strip()

    remote = "unknown"
    if re.search(r"\btélétravail\s+(complet|total)\b", page_text, flags=re.IGNORECASE):
        remote = "yes"
    elif re.search(r"\btélétravail\s+(partiel|hybride|occasionnel)\b", page_text, flags=re.IGNORECASE):
        remote = "yes"
    elif re.search(r"\bpas de télétravail\b", page_text, flags=re.IGNORECASE):
        remote = "no"

    published_relative = None
    mpub = re.search(r"\b(il y a \d+ (?:jour|jours|heure|heures|minute|minutes)|moins d'une heure)\b", page_text, flags=re.IGNORECASE)
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
        raw_text=page_text[:12000],
    )


def save_jsonl(rows: List[Dict[str, Any]], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")


def save_csv(rows: List[Dict[str, Any]], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    df = pd.DataFrame(rows)
    if "raw_text" in df.columns:
        df["raw_text"] = df["raw_text"].astype(str).str.slice(0, 4000)
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
    Main function called by run_hellowork.py
    Returns info about saved files.
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
    print(f"[HelloWork] collected URLs: {len(offer_urls)}")

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
            print(f"[HelloWork] fetched {i}/{len(offer_urls)}")
        time.sleep(sleep_s)

    rows = [asdict(o) for o in offers]

    out_path = Path(out_dir)
    out_path.mkdir(parents=True, exist_ok=True)

    tag = "france" if not city else slugify(f"{city}-{postal}" if postal else city)
    jsonl_path = out_path / f"hellowork_{mode}_{tag}_raw.jsonl"
    csv_path = out_path / f"hellowork_{mode}_{tag}_raw.csv"

    save_jsonl(rows, jsonl_path)
    save_csv(rows, csv_path)

    print(f"✅ saved: {len(rows)} offers -> {out_path}")
    return {
        "count": len(rows),
        "jsonl": str(jsonl_path),
        "csv": str(csv_path),
        "mode": mode,
        "tag": tag,
    }
