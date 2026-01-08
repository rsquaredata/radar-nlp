from pydantic_ai import Agent
from pydantic_ai.models.mistral import MistralModel
import asyncio
import pandas as pd
from tqdm import tqdm
from dotenv import load_dotenv

load_dotenv()

# pour l'instant pas de sauvegarde dans un fichier ATTENTION
agent = Agent(
    model=MistralModel("mistral-large-latest"),
    system_prompt=(
        "Tu es un assistant chargé d'extraire des informations structurées à partir d'offres d'emploi françaises."
        "À partir du lien ci-dessous, extrais les informations suivantes et réponds uniquement en JSON valide :"
        "- employeur"
        "- localisation"
        "- type_contrat"
        "- temps_travail"
        "- teletravail"
        "- salaire"
        "- experience_min"
        "- management (true/false)"
        "- competences (liste courte)"
        "Si une information est absente, mets null."
        "Texte de l'offre :"
        "{RAW_TEXT}"
    ),
)


async def main():
    df = pd.read_csv(
        "corpus_clean.csv", sep=","
    )  # attention au sep ; pour corpus_offres_data
    for _, row in tqdm(df.iterrows(), total=len(df)):
        response = await agent.run(
            row["url"]
        )  # on peut mettre url aussi en précisant le lien au lieu du texte dans le prompt
        print(response.output)


if __name__ == "__main__":
    asyncio.run(main())
