import streamlit as st
import duckdb
import os
from dotenv import load_dotenv
from mistralai import Mistral

# Version 3.2 - Fix Mistral Imports
load_dotenv()

def get_connection():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(current_dir)
    db_path = os.path.join(project_root, "data", "db", "radar.duckdb")
    return duckdb.connect(db_path, read_only=True)

def inject_style():
    st.markdown("""
    <style>
        .stApp { background: #0E1117; color: #FAFAFA; }
        .main-title { 
            background: linear-gradient(135deg, #60a5fa 0%, #a78bfa 100%);
            -webkit-background-clip: text; -webkit-text-fill-color: transparent;
            font-size: 3.5rem; font-weight: 800; text-align: center;
            padding: 2rem 0;
        }
        .metric-card {
            background: rgba(30, 41, 59, 0.4);
            border: 1px solid rgba(99, 102, 241, 0.3);
            border-radius: 15px; padding: 1.5rem; text-align: center;
        }
    </style>
    """, unsafe_allow_html=True)

def get_mistral_feedback(cv_text, job_title):
    api_key = os.getenv("MISTRAL_API_KEY")
    if not api_key:
        return "⚠️ Clé API Mistral manquante dans le .env"

    try:
        # Nouvelle syntaxe Mistral v1.x
        client = Mistral(api_key=api_key)

        prompt = f"Tu es un expert RH Data. Analyse ce CV pour le poste de {job_title}. Donne un score d'adéquation sur 100 et 3 conseils. CV : {cv_text}"

        chat_response = client.chat.complete(
            model="mistral-tiny",
            messages=[
                {"role": "user", "content": prompt},
            ]
        )
        return chat_response.choices[0].message.content
    except Exception as e:
        return f"❌ Erreur Mistral : {str(e)}"
