from __future__ import annotations

import os
import json
import streamlit as st
from dotenv import load_dotenv

load_dotenv()
# pip install mistralai
try:
    from mistralai import Mistral
except Exception:
    Mistral = None

SYSTEM = (
    "Tu es un assistant d'analyse de clusters d'offres d'emploi.\n"
    "Tu dois rester FACTUEL et t'appuyer uniquement sur les informations fournies.\n"
    "Objectif: proposer un label court + une description claire + 5 mots clés.\n"
    "Ne pas inventer de technologies non présentes dans les termes/exemples.\n"
    "Réponds UNIQUEMENT en JSON valide, sans texte autour."
)

# ⚠️ IMPORTANT: JSON exemple -> accolades échappées {{ }}
USER_TEMPLATE = """
Voici un cluster d'offres d'emploi (Data/IA).
Retour attendu JSON EXACT (un seul objet JSON):

{{
  "label": "…",
  "summary": "…",
  "keywords": ["…", "…", "…", "…", "…"],
  "quality_flags": ["…"]
}}

Données:
- top_terms: {top_terms}
- skills: {skills}
- examples_titles: {examples_titles}
"""

def _safe_json_loads(text: str):
    """Tente de récupérer un JSON même si le modèle ajoute du texte autour."""
    text = (text or "").strip()

    # direct
    try:
        return json.loads(text)
    except Exception:
        pass

    # extrait premier bloc {...}
    start = text.find("{")
    end = text.rfind("}")
    if start != -1 and end != -1 and end > start:
        chunk = text[start:end+1]
        return json.loads(chunk)

    raise ValueError("Impossible de parser un JSON depuis la réponse Mistral.")

@st.cache_data(ttl=3600)
def mistral_label_cluster(
    top_terms: str,
    skills: list[str],
    examples_titles: list[str],
    model: str = "mistral-large-latest",
):
    api_key = os.getenv("MISTRAL_API_KEY", "").strip()
    if not api_key:
        return None, "MISTRAL_API_KEY manquant (variable d'environnement)."

    if Mistral is None:
        return None, "SDK mistralai non installé. Fais: pip install mistralai"

    client = Mistral(api_key=api_key)

    prompt = USER_TEMPLATE.format(
        top_terms=(top_terms or "")[:2000],
        skills=(skills or [])[:25],
        examples_titles=(examples_titles or [])[:10],
    )

    try:
        resp = client.chat.complete(
            model=model,
            messages=[
                {"role": "system", "content": SYSTEM},
                {"role": "user", "content": prompt},
            ],
            temperature=0.2,
        )
        text = resp.choices[0].message.content.strip()
        data = _safe_json_loads(text)
        return data, None
    except Exception as e:
        return None, f"Erreur Mistral / parsing JSON: {e}"

