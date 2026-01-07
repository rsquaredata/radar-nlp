import streamlit as st
import plotly.graph_objects as go
import numpy as np
from utils.logic import inject_style, get_connection, get_mistral_feedback

inject_style()

st.markdown('<h1 class="main-title">INTELLIGENCE MÉTIER</h1>', unsafe_allow_html=True)

con = get_connection()
metiers = con.execute("SELECT DISTINCT nom_metier FROM dim_metier").df()['nom_metier'].tolist()
con.close()

st.subheader("📊 Comparaison de clusters")
c1, c2 = st.columns(2)
sel1 = c1.selectbox("Métier A", metiers, index=0)
sel2 = c2.selectbox("Métier B", metiers, index=1)

# Radar Chart
skills = ['Python', 'SQL', 'Cloud', 'Spark', 'Machine Learning', 'BI']
v1 = np.random.randint(40, 95, 6) 
v2 = np.random.randint(40, 95, 6)

fig = go.Figure()
fig.add_trace(go.Scatterpolar(r=v1, theta=skills, fill='toself', name=sel1, line_color='#60a5fa'))
fig.add_trace(go.Scatterpolar(r=v2, theta=skills, fill='toself', name=sel2, line_color='#a78bfa'))
fig.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 100])), template="plotly_dark")
st.plotly_chart(fig, width="stretch")

st.divider()
st.subheader("🎯 Matching Profil vs Marché (LLM)")
target = st.selectbox("Métier visé", metiers, key="match_target")
cv_text = st.text_area("Collez le texte de votre CV ici pour l'analyse Mistral AI", height=200)

if st.button("Lancer l'analyse LLM"):
    if cv_text:
        with st.spinner("Analyse sémantique par Mistral..."):
            res = get_mistral_feedback(cv_text, target)
            st.markdown("### 🤖 Diagnostic de l'IA")
            st.write(res)
    else:
        st.warning("Veuillez coller votre CV.")
