import os
import time
import logging
import requests
import base64
from pathlib import Path
from dotenv import load_dotenv
from typing import Any, Dict, List
from radar.scraping.base import BaseScraper

logger = logging.getLogger(__name__)

class FranceTravailClient(BaseScraper):
    def __init__(self, env_path: Path = None):
        if env_path is None:
            env_path = Path(__file__).resolve().parent.parent.parent.parent / ".env"
        load_dotenv(dotenv_path=env_path)
        self.client_id = os.getenv("FRANCE_TRAVAIL_CLIENT_ID")
        self.client_secret = os.getenv("FRANCE_TRAVAIL_CLIENT_SECRET")
        self.base_url = "https://api.francetravail.io/partenaire/offresdemploi/v2"

    def get_token(self):
        url = "https://entreprise.francetravail.fr/connexion/oauth2/access_token?realm=/partenaire"
        auth_str = f"{self.client_id}:{self.client_secret}"
        encoded_auth = base64.b64encode(auth_str.encode()).decode()

        headers = {
            "Authorization": f"Basic {encoded_auth}",
            "Content-Type": "application/x-www-form-urlencoded"
        }

        # On demande explicitement le scope de l'API v2
        payload = {
            "grant_type": "client_credentials",
            "scope": "api_offresdemploiv2"
        }

        res = requests.post(url, data=payload, headers=headers)

        if res.status_code != 200:
            logger.error(f"Erreur Auth : {res.status_code} - {res.text}")
            res.raise_for_status()

        data = res.json()
        # DEBUG : On affiche les droits réels du jeton obtenu
        logger.info(f"Jeton obtenu avec les droits (scope) : {data.get('scope')}")

        return data.get("access_token")

    def fetch_all(self, queries: List[str]) -> List[Dict[str, Any]]:
        all_offers = []
        try:
            token = self.get_token()
        except Exception as e:
            logger.error(f"Impossible d'obtenir le token : {e}")
            return []

        headers = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/json"
        }

        for q in queries:
            logger.info(f"Recherche FT : {q}")
            # Paramètres minimaux
            params = {"motsCles": q, "range": "0-49"}

            try:
                # Appel à l'API de recherche
                resp = requests.get(f"{self.base_url}/offres/search", params=params, headers=headers)

                if resp.status_code == 200:
                    hits = resp.json().get("resultats", [])
                    if hits:
                        all_offers.extend(hits)
                        logger.info(f" -> OK : {len(hits)} offres trouvées")
                elif resp.status_code == 204:
                    logger.info(" -> Aucun résultat (204)")
                elif resp.status_code == 403:
                    logger.error(f" -> [403 Forbidden] Ton jeton n'a pas accès à cette API. Réponse : {resp.text}")
                    # On ne s'arrête pas, on essaie le mot-clé suivant au cas où
                else:
                    logger.warning(f" -> Code {resp.status_code} : {resp.text}")

                time.sleep(1.1) # On respecte les 10 appels/sec très largement
            except Exception as e:
                logger.error(f"Erreur technique : {e}")

        # Déduplication finale
        unique_offers = {o['id']: o for o in all_offers}.values()
        return list(unique_offers)
