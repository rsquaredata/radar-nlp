import streamlit as st
from utils.logic import inject_style

inject_style()

st.title("🤝 Contribution")

st.info("Atteignez 100 XP pour débloquer l'Assistant IA.")

c1, c2 = st.columns(2)
with c1:
    if st.button("Scraping 1 source (+10 XP)"):
        st.session_state.user_xp += 10
        st.success("Scraping source unique terminé.")
with c2:
    if st.button("Scraping TOTAL (+40 XP)"):
        st.session_state.user_xp += 40
        st.balloons()


with st.form("manual_entry"):
    job_t = st.text_input("Intitulé du poste")
    job_m = st.selectbox("Cluster", ["Data Scientist", "Data Analyst", "Data Engineer", "ML Ops"])
    job_d = st.text_area("Description")
    if st.form_submit_button("Enregistrer (+5 XP)"):
        if job_t:
            st.session_state.user_xp += 5
            st.success("Annonce ajoutée à la base !")
        else:
            st.error("Titre requis.")
