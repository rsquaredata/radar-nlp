import os
import re
from pathlib import Path
from typing import Optional, Dict, Any, List

import requests
from http_utils import RobustSession

# =========================
# Chargement du .env (robuste)
# =========================
ROOT = Path(__file__).resolve().parents[1]  # .../projet_nlp
from dotenv import load_dotenv
load_dotenv(ROOT / ".env")

# =========================
# Endpoints France Travail
# =========================
TOKEN_URL = "https://entreprise.pole-emploi.fr/connexion/oauth2/access_token?realm=/partenaire"

# Fallback multi-hosts
API_HOSTS: List[str] = [
    "https://api.francetravail.io",
    "https://api.emploi-store.fr",
]

SEARCH_PATH = "/partenaire/offresdemploi/v2/offres/search"
DETAIL_PATH = "/partenaire/offresdemploi/v2/offres/"

# =========================
# RequÃªtes Data & IA
# =========================
DATA_AI_QUERIES: List[str] = [
    # mÃ©tiers data
    "data scientist",
    "data analyst",
    "data engineer",
    "data architect",
    "business intelligence",
    "bi developer",
    "analyste dÃ©cisionnel",
    "statisticien",
    "statistician",
    "quant",
    # IA / ML
    "machine learning",
    "machine learning engineer",
    "ml engineer",
    "deep learning",
    "computer vision",
    "nlp",
    "ingÃ©nieur ia",
    "ingenieur ia",
    "ai engineer",
    # LLM
    "llm",
    "rag",
    "transformers",
    # skills (rattrapage)
    "python data",
    "python sql",
    "spark",
    "pyspark",
    "airflow",
    "dbt",
    "tensorflow",
    "pytorch",
]

# Filtre local (au cas oÃ¹ certaines requÃªtes rÃ©cupÃ¨rent du bruit)
DATA_AI_KEYWORDS_REGEX = re.compile(
    r"\b("
    r"data\s*(scientist|analyst|engineer|architect|science|platform|warehouse)|"
    r"machine\s*learning|deep\s*learning|\bml\b|"
    r"nlp|computer\s*vision|vision\b|"
    r"intelligence\s*artificielle|ingÃ©nieur\s*ia|ingenieur\s*ia|"
    r"llm|rag|transformers|"
    r"business\s*intelligence|\bbi\b|dÃ©cisionnel|"
    r"python|sql|spark|pyspark|airflow|dbt|tensorflow|pytorch"
    r")\b",
    flags=re.IGNORECASE,
)


class FranceTravailClient:
    def __init__(self):
        self.client_id = os.getenv("FRANCE_TRAVAIL_CLIENT_ID")
        self.client_secret = os.getenv("FRANCE_TRAVAIL_CLIENT_SECRET")
        self.scope = os.getenv("FRANCE_TRAVAIL_SCOPE", "api_offresdemploiv2 o2dsoffre")

        if not self.client_id or not self.client_secret:
            raise RuntimeError(
                "FRANCE_TRAVAIL_CLIENT_ID / FRANCE_TRAVAIL_CLIENT_SECRET manquants. "
                "VÃ©rifie que le fichier .env est Ã  la racine du projet et contient les clÃ©s."
            )

        self.rs = RobustSession()
        self._token: Optional[str] = None

    # -------------
    # Token OAuth2
    # -------------
    def token(self, force_refresh: bool = False) -> str:
        if self._token and not force_refresh:
            return self._token

        data = {
            "grant_type": "client_credentials",
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "scope": self.scope,
        }

        try:
            r = self.rs.post(
                TOKEN_URL,
                data=data,
                headers={"Content-Type": "application/x-www-form-urlencoded"},
            )
        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"Erreur rÃ©seau pendant la rÃ©cupÃ©ration du token: {e}") from e

        if r.status_code != 200:
            raise RuntimeError(f"Token error {r.status_code}: {r.text[:400]}")

        tok = r.json().get("access_token")
        if not tok:
            raise RuntimeError(f"access_token introuvable. RÃ©ponse: {r.text[:400]}")
        self._token = tok
        return self._token

    # -------------------------
    # GET avec fallback hosts + refresh token si 401/403
    # -------------------------
    def _get_with_fallback(
        self,
        path: str,
        params: Optional[Dict[str, Any]] = None,
        range_header: Optional[str] = None,
    ) -> requests.Response:
        last_error: Optional[BaseException] = None

        for host in API_HOSTS:
            url = host + path
            headers = {
                "Authorization": f"Bearer {self.token()}",
                "Accept": "application/json",
            }
            if range_header:
                headers["Range"] = range_header  # Range standard

            try:
                r = self.rs.get(url, params=params or {}, headers=headers)

                # refresh token 1 fois si besoin
                if r.status_code in (401, 403):
                    headers["Authorization"] = f"Bearer {self.token(force_refresh=True)}"
                    r = self.rs.get(url, params=params or {}, headers=headers)

                # 2xx/4xx: on renvoie (le caller gÃ¨re)
                if r.status_code < 500:
                    return r

                last_error = RuntimeError(f"{host} -> HTTP {r.status_code}: {r.text[:200]}")

            except requests.exceptions.RequestException as e:
                last_error = e
                continue

        raise RuntimeError(f"Impossible de joindre l'API France Travail. DerniÃ¨re erreur: {last_error}")

    # -------------
    # Search (1 page via Range)
    # -------------
    def search(self, params: Optional[Dict[str, Any]] = None, range_header: str = "0-149") -> Dict[str, Any]:
        r = self._get_with_fallback(SEARCH_PATH, params=params, range_header=range_header)

        # 204 = No Content : pas de rÃ©sultat (normal)
        if r.status_code == 204:
            return {"resultats": [], "_content_range": r.headers.get("Content-Range")}

        # 200 = OK, 206 = Partial Content (normal avec Range)
        if r.status_code not in (200, 206):
            raise RuntimeError(f"Search error {r.status_code}: {r.text[:400]}")

        out = r.json()
        out["_content_range"] = r.headers.get("Content-Range")
        return out

    # -------------
    # Detail (1 offre)
    # -------------
    def detail(self, offer_id: str) -> Dict[str, Any]:
        r = self._get_with_fallback(DETAIL_PATH + offer_id)

        if r.status_code != 200:
            raise RuntimeError(f"Detail error {r.status_code}: {r.text[:400]}")
        return r.json()

    # ============================================================
    # BULK: rÃ©cupÃ©rer plusieurs pages via Range (0-149, 150-299...)
    # ============================================================
    def search_all(
        self,
        params: Optional[Dict[str, Any]] = None,
        max_results: int = 1500,
        chunk: int = 150,
    ) -> List[Dict[str, Any]]:
        all_results: List[Dict[str, Any]] = []
        start = 0
        while start < max_results:
            end = start + (chunk - 1)
            res = self.search(params=params, range_header=f"{start}-{end}")
            offers = res.get("resultats", [])

            if not offers:
                break

            all_results.extend(offers)

            if len(offers) < chunk:
                break

            start += chunk

        return all_results

    # ==========================================
    # Normalisation offre (format plat)
    # ==========================================
    @staticmethod
    def normalize_offer(raw: Dict[str, Any], query: Optional[str] = None) -> Dict[str, Any]:
        title = raw.get("intitule")
        desc = raw.get("description")
        company = (raw.get("entreprise") or {}).get("nom")
        location = (raw.get("lieuTravail") or {}).get("libelle") or (raw.get("lieuTravail") or {}).get("commune")
        published = raw.get("dateCreation") or raw.get("dateActualisation")
        contract = raw.get("typeContratLibelle") or raw.get("typeContrat")
        url = (raw.get("origineOffre") or {}).get("urlOrigine") or (raw.get("origineOffre") or {}).get("url")

        salary = None
        sal = raw.get("salaire") or {}
        if isinstance(sal, dict):
            salary = sal.get("libelle") or sal.get("commentaire")

        return {
            "source": "france-travail-api",
            "offer_id": raw.get("id"),
            "title": title,
            "company": company,
            "location": location,
            "published_date": published,
            "contract_type": contract,
            "salary": salary,
            "url": url,
            "query": query,
            "description": desc,
        }

    # ============================================================
    # COLLECT Data & IA : multi-queries + detail + dÃ©dup + filtre
    # ============================================================
    def collect_data_ai_offers(
        self,
        queries: List[str] = DATA_AI_QUERIES,
        max_per_query: int = 1200,
        chunk: int = 150,
        fetch_detail: bool = True,
        local_filter: bool = True,
    ) -> List[Dict[str, Any]]:
        seen_ids = set()
        out: List[Dict[str, Any]] = []

        for q in queries:
            params = {"motsCles": q}
            offers = self.search_all(params=params, max_results=max_per_query, chunk=chunk)

            added = 0
            for o in offers:
                oid = o.get("id")
                if not oid or oid in seen_ids:
                    continue

                raw = o
                if fetch_detail:
                    raw = self.detail(oid)

                norm = self.normalize_offer(raw, query=q)

                if local_filter:
                    text = f"{norm.get('title','')} {norm.get('description','')}"
                    if not DATA_AI_KEYWORDS_REGEX.search(text):
                        continue

                seen_ids.add(oid)
                out.append(norm)
                added += 1

            print(f"[FT] query='{q}' -> +{added} cumul={len(out)}")

        return out