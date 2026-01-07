import streamlit as st
from utils.logic import inject_style

inject_style()

st.title("📝 Assistant Candidature")

if st.session_state.user_xp < 100:
    st.error(f"🔒 Accès restreint. Score actuel : {st.session_state.user_xp}/100 XP.")
    st.info("Contribuez via l'onglet dédié pour débloquer cet outil.")
else:
    st.success("🔓 Assistant débloqué. Génération de lettre de motivation disponible.")
    st.text_area("Rédacteur IA...")
