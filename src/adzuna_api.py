from __future__ import annotations

import os
import time
import requests
from typing import Any, Dict, List
from dotenv import load_dotenv

load_dotenv()

ADZUNA_APP_ID = os.getenv("ADZUNA_APP_ID")
ADZUNA_APP_KEY = os.getenv("ADZUNA_APP_KEY")

if not ADZUNA_APP_ID or not ADZUNA_APP_KEY:
    raise RuntimeError("ADZUNA_APP_ID / ADZUNA_APP_KEY manquants dans .env")

BASE_URL = "https://api.adzuna.com/v1/api/jobs/fr/search"

DATA_IA_KEYWORDS = [
    "data scientist", "data analyst", "data engineer", "data architect",
    "business intelligence", "bi developer", "analyste décisionnel",
    "statisticien", "quant",
    "machine learning", "machine learning engineer", "ml engineer",
    "deep learning", "computer vision", "nlp",
    "ingénieur ia", "ai engineer",
    "llm", "rag", "transformers",
]


def collect_adzuna_data_ia(
    keywords: List[str] = DATA_IA_KEYWORDS,
    max_pages: int = 50,
    sleep_s: float = 0.3,
) -> List[Dict[str, Any]]:
    """
    Récupère les offres DATA / IA en France via l'API Adzuna
    """
    rows: List[Dict[str, Any]] = []

    for kw in keywords:
        print(f"[ADZUNA] keyword='{kw}'")
        for page in range(1, max_pages + 1):
            url = f"{BASE_URL}/{page}"
            params = {
                "app_id": ADZUNA_APP_ID,
                "app_key": ADZUNA_APP_KEY,
                "results_per_page": 50,
                "what": kw,
                "content-type": "application/json",
            }

            r = requests.get(url, params=params, timeout=30)
            if r.status_code != 200:
                break

            data = r.json()
            results = data.get("results", [])
            if not results:
                break

            for o in results:
                rows.append({
                    "source": "adzuna.fr",
                    "offer_id": o.get("id"),
                    "url": o.get("redirect_url"),
                    "title": o.get("title"),
                    "company": (o.get("company") or {}).get("display_name"),
                    "location": (o.get("location") or {}).get("display_name"),
                    "contract_type": o.get("contract_type"),
                    "salary": o.get("salary_is_predicted"),
                    "published_date": o.get("created"),
                    "query": kw,
                    "raw_text": o.get("description", "")[:12000],
                })

            time.sleep(sleep_s)

    return rows
