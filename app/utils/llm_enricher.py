"""
Module d'enrichissement LLM pour les offres d'emploi
Utilise Mistral pour extraire des informations structurées
"""

from pydantic_ai import Agent
from pydantic_ai.models.mistral import MistralModel
import asyncio
import json
import re
from typing import List, Dict, Optional
from dotenv import load_dotenv

load_dotenv()


class LLMEnricher:
    """Enrichisseur LLM pour extraire des informations structurées des offres"""

    def __init__(self):
        """Initialise l'agent Mistral"""
        self.agent = Agent(
            model=MistralModel("mistral-large-latest"),
            system_prompt=(
                """Tu es un assistant chargé d'extraire des informations structurées à partir d'offres d'emploi françaises.
                À partir du texte ci-dessous, extrais les informations suivantes :
                
                Champs attendus :
                - title (string) : titre du poste
                - company_name (string) : nom de l'entreprise/collectivité
                - location (string) : lieu de travail (ville, département)
                - contract_type (string) : type de contrat (CDI, CDD, Mutation, Détachement, etc.)
                - remote (string: "oui" | "non" | "partiel" | "hybride" | null)
                - salary (string ou null) : fourchette de salaire si mentionnée
                - experience_min (number ou null) : années d'expérience minimum requises
                - management (boolean) : poste avec management d'équipe ?
                - competences (liste de strings) : compétences techniques clés (max 10)
                - savoir_etre (liste de strings) : qualités comportementales (max 5)
                - published_date (date ISO ou null) : date de publication si trouvée
                
                IMPORTANT :
                - Si une information est absente ou peu claire, mets null
                - Pour les compétences, focus sur les compétences techniques (logiciels, langages, méthodologies)
                - Pour savoir_etre, focus sur les soft skills (autonomie, rigueur, etc.)
                - Réponds STRICTEMENT en JSON valide
                - Ne mets AUCUN texte avant ou après le JSON
                - Ne mets PAS de balises markdown (pas de ```json)
                
                Texte de l'offre :
                {RAW_TEXT}"""
            ),
        )

    @staticmethod
    def clean_llm_json(text: str) -> dict:
        """Nettoie la réponse LLM et parse le JSON"""
        text = text.strip()

        # Enlève les balises markdown
        text = re.sub(r"^```json\s*", "", text)
        text = re.sub(r"^```\s*", "", text)
        text = re.sub(r"\s*```$", "", text)
        text = text.strip()

        try:
            return json.loads(text)
        except json.JSONDecodeError as e:
            print(f"⚠️ Erreur parsing JSON: {e}")
            print(f"Texte reçu: {text[:200]}...")
            return None

    async def enrich_offer(self, offer: Dict) -> Dict:
        """
        Enrichit une offre avec le LLM

        Args:
            offer: Dict contenant au minimum 'description'

        Returns:
            Dict enrichi avec les champs extraits par le LLM
        """
        description = offer.get("description", "")

        if not description:
            print("⚠️ Description vide, skip LLM")
            return offer

        try:
            # Appel LLM
            response = await self.agent.run(description)
            llm_data = self.clean_llm_json(response.output)

            if llm_data is None:
                print("⚠️ LLM n'a pas retourné de JSON valide")
                return offer

            # Merge des données LLM avec l'offre originale
            # Les données LLM écrasent les données existantes si présentes
            enriched_offer = {**offer, **llm_data}

            # S'assurer que les champs essentiels sont présents
            if not enriched_offer.get("title"):
                enriched_offer["title"] = offer.get("title", "Sans titre")

            if not enriched_offer.get("company_name"):
                enriched_offer["company_name"] = offer.get(
                    "company_name", "Collectivité"
                )

            if not enriched_offer.get("location"):
                enriched_offer["location"] = offer.get("location", "")

            # Convertir les listes en format compatible
            if "competences" in llm_data and isinstance(llm_data["competences"], list):
                enriched_offer["competences"] = llm_data["competences"]
            else:
                enriched_offer["competences"] = []

            if "savoir_etre" in llm_data and isinstance(llm_data["savoir_etre"], list):
                enriched_offer["savoir_etre"] = llm_data["savoir_etre"]
            else:
                enriched_offer["savoir_etre"] = []

            # Calculer skills_count
            enriched_offer["skills_count"] = len(enriched_offer["competences"]) + len(
                enriched_offer["savoir_etre"]
            )
            enriched_offer["competences_count"] = len(enriched_offer["competences"])
            enriched_offer["savoir_etre_count"] = len(enriched_offer["savoir_etre"])

            return enriched_offer

        except Exception as e:
            print(f"❌ Erreur enrichissement LLM: {e}")
            return offer

    async def enrich_offers_batch(
        self, offers: List[Dict], show_progress: bool = True
    ) -> List[Dict]:
        """
        Enrichit un batch d'offres

        Args:
            offers: Liste d'offres à enrichir
            show_progress: Afficher la progression

        Returns:
            Liste d'offres enrichies
        """
        enriched_offers = []
        total = len(offers)

        for idx, offer in enumerate(offers):
            enriched = await self.enrich_offer(offer)
            enriched_offers.append(enriched)

            if show_progress and (idx + 1) % 5 == 0:
                print(f"   🔄 Enrichissement LLM: {idx + 1}/{total}")

        return enriched_offers


# Fonction standalone pour une utilisation simple
async def enrich_offers_with_llm(offers: List[Dict]) -> List[Dict]:
    """
    Fonction helper pour enrichir des offres avec le LLM

    Args:
        offers: Liste d'offres à enrichir

    Returns:
        Liste d'offres enrichies
    """
    enricher = LLMEnricher()
    return await enricher.enrich_offers_batch(offers)


# Script de test standalone
async def test_enricher():
    """Test l'enrichisseur sur un exemple"""
    test_offer = {
        "source": "test",
        "title": "Chargé de mission SIG",
        "company_name": "Ville de Lyon",
        "location": "Lyon, Rhône-Alpes",
        "description": """
        La Ville de Lyon recrute un Chargé de mission SIG H/F pour son service urbanisme.
        
        Missions principales :
        - Gestion et mise à jour des bases de données géographiques
        - Création de cartes thématiques avec QGIS
        - Support aux utilisateurs des outils SIG
        - Développement d'applications cartographiques web
        
        Profil recherché :
        - Formation Bac+5 en géomatique ou équivalent
        - Maîtrise de QGIS, PostgreSQL/PostGIS
        - Connaissance de Python et des bibliothèques cartographiques
        - Autonomie, rigueur et sens du service public
        
        Conditions :
        - Poste en CDI
        - Rémunération selon grille fonction publique territoriale
        - Télétravail possible 2 jours/semaine
        """,
    }

    enricher = LLMEnricher()
    enriched = await enricher.enrich_offer(test_offer)

    print("\n" + "=" * 80)
    print("RÉSULTAT DE L'ENRICHISSEMENT LLM")
    print("=" * 80)
    print(json.dumps(enriched, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    # Test l'enrichisseur
    asyncio.run(test_enricher())
