import streamlit as st
from config import APP_TITLE

st.set_page_config(
    page_title=APP_TITLE,
    page_icon="🧠",
    layout="wide",
)

st.title("🧠 Job Market Explorer — Data & IA (France)")
st.caption("Multi-sources (France Travail, HelloWork, Adzuna) • Clustering TF-IDF/KMeans • Carte interactive • Ajout dynamique • LLM (optionnel)")

st.info(
    "Utilise la sidebar pour naviguer. "
    "Les pages sont dans le dossier `pages/` (Streamlit multi-pages)."
)
