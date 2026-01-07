import streamlit as st
import plotly.express as px
from utils.logic import inject_style, get_connection

# 1. CONFIGURATION INITIALE
st.set_page_config(page_title="RADAR Terminal", layout="wide")
inject_style()

# 2. LOGIQUE DE NAVIGATION
def run_app():
    # Définition des pages
    # Note : on crée une fonction pour le contenu de l'accueil pour l'intégrer proprement
    home_page = st.Page(show_home, title="Page d'accueil", icon="🏠", default=True)

    analytics = st.Page("pages/01_Analytics.py", title="Analytique Marché", icon="📊")
    carte = st.Page("pages/02_Cartographie.py", title="Carte Interactive", icon="🗺️")
    intelligence = st.Page("pages/03_Intelligence_Metier.py", title="Intelligence Métier", icon="🤖")
    candidater = st.Page("pages/06_Candidater.py", title="Assistant Candidature", icon="📝")
    explorateur = st.Page("pages/04_Explorateur.py", title="Explorateur", icon="🕵️")
    contribution = st.Page("pages/05_Contribution.py", title="Contribution", icon="🤝")

    # Organisation du menu
    pg = st.navigation({
        "Menu": [home_page],
        "Analyses": [analytics, carte],
        "Outils IA": [intelligence, candidater],
        "Gestion": [explorateur, contribution]
    })
    pg.run()

# 3. CONTENU DE LA PAGE D'ACCUEIL
def show_home():
    if 'user_xp' not in st.session_state: st.session_state.user_xp = 0

    st.markdown('<h1 class="main-title">RADAR TERMINAL v3.0</h1>', unsafe_allow_html=True)

    con = get_connection()
    df_full = con.execute("SELECT * FROM v_final_dashboard").df()
    con.close()

    # KPIs
    c1, c2, c3 = st.columns(3)
    with c1: st.markdown(f"<div class='metric-card'><h4>📦 Offres</h4><h2>{len(df_full)}</h2></div>", unsafe_allow_html=True)
    with c2: st.markdown(f"<div class='metric-card'><h4>📍 Villes</h4><h2>{df_full['departement'].nunique()}</h2></div>", unsafe_allow_html=True)
    with c3: st.markdown(f"<div class='metric-card'><h4>🎖️ XP</h4><h2>{st.session_state.user_xp}</h2></div>", unsafe_allow_html=True)

    st.write("### 📈 État du marché")
    g1, g2 = st.columns(2)
    with g1:
        top_villes = df_full['departement'].value_counts().head(10).reset_index()
        st.plotly_chart(px.bar(top_villes, x='count', y='departement', orientation='h', template="plotly_dark", color='count'), width="stretch")
    with g2:
        st.plotly_chart(px.pie(df_full, names='secteur', hole=0.5, template="plotly_dark"), width="stretch")

    st.write("---")
    st.progress(min((st.session_state.user_xp % 100) / 100, 1.0))
    st.caption(f"Progression : {st.session_state.user_xp % 100}/100 XP")

if __name__ == "__main__":
    run_app()
