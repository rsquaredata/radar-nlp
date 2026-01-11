from pydantic_ai import Agent
from pydantic_ai.models.mistral import MistralModel
import asyncio
import pandas as pd
from tqdm import tqdm
from dotenv import load_dotenv
import json
import re

load_dotenv()


# pour l'instant pas de sauvegarde dans un fichier ATTENTION
agent = Agent(
    model=MistralModel("mistral-large-latest"),
    system_prompt=(
        """
        Tu es un assistant chargé d'extraire des informations structurées à partir d'offres d'emploi françaises.
        À partir du texte ci-dessous, extrais les informations suivantes :
        Champs attendus :
        - title (string)
        - company_name (string)
        - location (string)
        - contract_type (string)
        - remote (string: "oui" | "non" | "partiel" | null)
        - salary (string ou null)
        - experience_min (number ou null)
        - management (boolean)
        - competences (liste courte de strings)
        - published_date (date ISO ou null)

        Si une information est absente, mets null.
        Réponds STRICTEMENT en JSON valide.
        Ne mets aucun texte avant ou après.
        Ne mets pas de balises markdown.
        Texte de l'offre :
        {RAW_TEXT}"""
    ),
)


def clean_llm_json(text: str) -> dict:
    text = text.strip()

    # enlève ```json et ```
    text = re.sub(r"^```json", "", text)
    text = re.sub(r"```$", "", text)
    text = text.strip()

    return json.loads(text)


async def main():
    unique_offers = []

    with open("emploi_territorial_mistral_raw.jsonl", "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                unique_offers.append(json.loads(line))
    """
    df = pd.read_csv(
        "corpus_clean.csv", sep=","
    )  # attention au sep ; pour corpus_offres_data
    """
    rows = []
    for row in tqdm(unique_offers):
        response = await agent.run(row["description"])
        llm_data = clean_llm_json(response.output)
        rows.append(llm_data)
        # print(response.output)
    df = pd.DataFrame(rows)

    output_path = "emploit_territorial_mistral_enriched.csv"
    df.to_csv(output_path, index=False, encoding="utf-8")

    print(f"✅ CSV généré : {output_path}")


if __name__ == "__main__":
    asyncio.run(main())
