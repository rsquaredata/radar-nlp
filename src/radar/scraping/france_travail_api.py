"""
Client d'accès à l'API France Travail.

Ce module encapsule :
- l'authentification à l'API France Travail,
- les requêtes paginées,
- la récupération brute des offres d'emploi.
"""
from __future__ import annotations

import os
import requests
from dotenv import load_dotenv

from typing import List, Dict, Any

load_dotenv()

CLIENT_ID = os.getenv("FRANCE_TRAVAIL_CLIENT_ID")
CLIENT_SECRET = os.getenv("FRANCE_TRAVAIL_CLIENT_SECRET")


class FranceTravailClient:
    """
    Client simplifié pour l'API France Travail.
    """

    BASE_URL = "https://api.francetravail.io/partenaire/offresdemploi/v2/offres/search"

    def __init__(self, api_key: str | None = None):
        self.api_key = api_key
        self.headers = {
            "Accept": "application/json",
        }
        if api_key:
            self.headers["Authorization"] = f"Bearer {api_key}"

    def collect_data_ai_offers(
        self,
        query: str,
        max_per_query: int = 600,
        chunk: int = 150,
        local_filter: bool = False,
    ) -> List[Dict[str, Any]]:
        """
        Collecte des offres France Travail pour un mot-clé donné.
        """
        results: List[Dict[str, Any]] = []
        start = 0

        while start < max_per_query:
            params = {
                "motsCles": query,
                "range": f"{start}-{start + chunk - 1}",
            }

            response = requests.get(
                self.BASE_URL,
                headers=self.headers,
                params=params,
                timeout=15,
            )

            if response.status_code != 200:
                break

            data = response.json()
            offers = data.get("resultats", [])

            if not offers:
                break

            for o in offers:
                results.append(
                    {
                        "offer_id": o.get("id"),
                        "title": o.get("intitule"),
                        "company": o.get("entreprise", {}).get("nom"),
                        "location": o.get("lieuTravail", {}).get("libelle"),
                        "url": o.get("origineOffre", {}).get("urlOrigine"),
                        "published_date": o.get("dateCreation"),
                        "contract_type": o.get("typeContrat"),
                        "salary": o.get("salaire", {}).get("libelle"),
                        "description": o.get("description"),
                    }
                )

            start += chunk

        return results
