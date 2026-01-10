import os
import re
from pathlib import Path
from typing import Optional, Dict, Any, List

import requests
from http_utils import RobustSession

# Import de la configuration centralisée
from config_metiers import DATA_AI_QUERIES_FT, DATA_AI_KEYWORDS_REGEX

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


class FranceTravailClient:
    """
    Client pour l'API France Travail (ex-Pôle Emploi).
    
    Utilise la configuration centralisée depuis config_metiers.py
    """
    
    def __init__(self):
        self.client_id = os.getenv("FRANCE_TRAVAIL_CLIENT_ID")
        self.client_secret = os.getenv("FRANCE_TRAVAIL_CLIENT_SECRET")
        self.scope = os.getenv("FRANCE_TRAVAIL_SCOPE", "api_offresdemploiv2 o2dsoffre")

        if not self.client_id or not self.client_secret:
            raise RuntimeError(
                "FRANCE_TRAVAIL_CLIENT_ID / FRANCE_TRAVAIL_CLIENT_SECRET manquants. "
                "Vérifie que le fichier .env est à la racine du projet et contient les clés."
            )

        self.rs = RobustSession()
        self._token: Optional[str] = None

    # -------------
    # Token OAuth2
    # -------------
    def token(self, force_refresh: bool = False) -> str:
        """Récupère ou rafraîchit le token OAuth2."""
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
            raise RuntimeError(f"Erreur réseau pendant la récupération du token: {e}") from e

        if r.status_code != 200:
            raise RuntimeError(f"Token error {r.status_code}: {r.text[:400]}")

        tok = r.json().get("access_token")
        if not tok:
            raise RuntimeError(f"access_token introuvable. Réponse: {r.text[:400]}")
        self._token = tok
        return self._token

    # -------------
    # Requêtes HTTP avec fallback
    # -------------
    def _get_with_fallback(
        self,
        path: str,
        params: Optional[Dict[str, Any]] = None,
        range_header: Optional[str] = None,
    ) -> requests.Response:
        """Effectue une requête GET avec fallback sur plusieurs hosts."""
        last_error: Optional[BaseException] = None

        for host in API_HOSTS:
            url = host + path
            headers = {
                "Authorization": f"Bearer {self.token()}",
                "Accept": "application/json",
            }
            if range_header:
                headers["Range"] = range_header

            try:
                r = self.rs.get(url, params=params or {}, headers=headers)

                # Refresh token 1 fois si besoin
                if r.status_code in (401, 403):
                    headers["Authorization"] = f"Bearer {self.token(force_refresh=True)}"
                    r = self.rs.get(url, params=params or {}, headers=headers)

                # 2xx/4xx: on renvoie (le caller gère)
                if r.status_code < 500:
                    return r

                last_error = RuntimeError(f"{host} -> HTTP {r.status_code}: {r.text[:200]}")

            except requests.exceptions.RequestException as e:
                last_error = e
                continue

        raise RuntimeError(f"Impossible de joindre l'API France Travail. Dernière erreur: {last_error}")

    # -------------
    # Recherche d'offres
    # -------------
    def search(
        self, 
        params: Optional[Dict[str, Any]] = None, 
        range_header: str = "0-149"
    ) -> Dict[str, Any]:
        """
        Recherche des offres d'emploi.
        
        Args:
            params: Paramètres de recherche (motsCles, commune, etc.)
            range_header: Range pour la pagination (ex: "0-149")
        
        Returns:
            Dict avec les résultats et le Content-Range
        """
        r = self._get_with_fallback(SEARCH_PATH, params=params, range_header=range_header)

        # 204 = No Content : pas de résultat (normal)
        if r.status_code == 204:
            return {"resultats": [], "_content_range": r.headers.get("Content-Range")}

        # 200 = OK, 206 = Partial Content (normal avec Range)
        if r.status_code not in (200, 206):
            raise RuntimeError(f"Search error {r.status_code}: {r.text[:400]}")

        out = r.json()
        out["_content_range"] = r.headers.get("Content-Range")
        return out

    # -------------
    # Détail d'une offre
    # -------------
    def detail(self, offer_id: str) -> Dict[str, Any]:
        """
        Récupère le détail complet d'une offre.
        
        Args:
            offer_id: ID de l'offre
        
        Returns:
            Dict avec tous les détails de l'offre
        """
        r = self._get_with_fallback(DETAIL_PATH + offer_id)

        if r.status_code != 200:
            raise RuntimeError(f"Detail error {r.status_code}: {r.text[:400]}")
        return r.json()

    # -------------
    # Recherche avec pagination
    # -------------
    def search_all(
        self,
        params: Optional[Dict[str, Any]] = None,
        max_results: int = 1500,
        chunk: int = 150,
    ) -> List[Dict[str, Any]]:
        """
        Recherche avec pagination automatique.
        
        Args:
            params: Paramètres de recherche
            max_results: Nombre max de résultats
            chunk: Taille des chunks (max 150)
        
        Returns:
            Liste de toutes les offres trouvées
        """
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

    # -------------
    # Normalisation
    # -------------
    @staticmethod
    def normalize_offer(raw: Dict[str, Any], query: Optional[str] = None) -> Dict[str, Any]:
        """
        Normalise une offre brute en format standard.
        
        Args:
            raw: Offre brute de l'API
            query: Requête utilisée pour trouver l'offre
        
        Returns:
            Offre normalisée
        """
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

    # -------------
    # Collecte Data & IA (utilise config_metiers.py)
    # -------------
    def collect_data_ai_offers(
        self,
        queries: Optional[List[str]] = None,
        max_per_query: int = 1200,
        chunk: int = 150,
        fetch_detail: bool = True,
        local_filter: bool = True,
    ) -> List[Dict[str, Any]]:
        """
        Collecte les offres Data & IA.
        
        Utilise la configuration centralisée depuis config_metiers.py
        
        Args:
            queries: Liste de requêtes (défaut: DATA_AI_QUERIES_FT)
            max_per_query: Max d'offres par requête
            chunk: Taille des chunks
            fetch_detail: Récupérer le détail de chaque offre
            local_filter: Appliquer un filtre local sur les résultats
        
        Returns:
            Liste d'offres normalisées
        """
        # Utiliser la config centralisée par défaut
        if queries is None:
            queries = DATA_AI_QUERIES_FT
        
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
                    try:
                        raw = self.detail(oid)
                    except Exception as e:
                        print(f"⚠️ Erreur détail {oid}: {e}")
                        continue

                norm = self.normalize_offer(raw, query=q)

                # Filtre local avec regex depuis config_metiers.py
                if local_filter:
                    text = f"{norm.get('title','')} {norm.get('description','')}"
                    if not DATA_AI_KEYWORDS_REGEX.search(text):
                        continue

                seen_ids.add(oid)
                out.append(norm)
                added += 1

            print(f"[FT] query='{q}' -> +{added} (cumul={len(out)})")

        return out


# ============================================================================
# EXEMPLE D'UTILISATION
# ============================================================================

if __name__ == "__main__":
    print("=" * 80)
    print("TEST FRANCE TRAVAIL CLIENT")
    print("=" * 80)
    print()
    
    try:
        client = FranceTravailClient()
        print("✅ Client initialisé")
        print()
        
        # Test de recherche simple
        print("🔍 Test : recherche 'data scientist' (10 résultats)")
        results = client.search_all(
            params={"motsCles": "data scientist"},
            max_results=10,
            chunk=10
        )
        
        print(f"✅ {len(results)} offres trouvées")
        
        if results:
            first = client.normalize_offer(results[0])
            print()
            print("📄 Première offre :")
            print(f"   • Titre : {first['title']}")
            print(f"   • Entreprise : {first['company']}")
            print(f"   • Localisation : {first['location']}")
        
    except Exception as e:
        print(f"❌ Erreur : {e}")