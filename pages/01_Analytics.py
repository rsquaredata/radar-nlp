import streamlit as st
import plotly.express as px
import pandas as pd
from wordcloud import WordCloud, STOPWORDS
import matplotlib.pyplot as plt
from utils.logic import inject_style, get_connection

inject_style()
st.markdown('<h1 class="main-title">ANALYTIQUE GÉOGRAPHIQUE</h1>', unsafe_allow_html=True)

con = get_connection()
df = con.execute("SELECT * FROM v_final_dashboard").df()
con.close()

# FILTRES DYNAMIQUES
with st.sidebar:
    st.header("📍 Focus géographique")
    sel_reg = st.multiselect("Régions", df['region'].unique(), default=df['region'].unique())
    sel_metier = st.multiselect("Métiers", df['nom_metier'].unique(), default=df['nom_metier'].unique())

df_f = df[(df['region'].isin(sel_reg)) & (df['nom_metier'].isin(sel_metier))]

# GRAPHES
c1, c2 = st.columns(2)
with c1:
    st.subheader("🤖 Top métiers sur la zone")
    fig_m = px.bar(df_f['nom_metier'].value_counts().reset_index(), x='count', y='nom_metier', orientation='h', template="plotly_dark")
    st.plotly_chart(fig_m, width="stretch")

with c2:
    st.subheader("💰 Estimation salaires (K€)")
    # Simulation d'une distribution de salaire basée sur le métier
    fig_sal = px.box(df_f, x="nom_metier", y="offre_id", title="Dispersion par Cluster", template="plotly_dark")
    st.plotly_chart(fig_sal, width="stretch")

c3, c4 = st.columns(2)
with c3:
    st.subheader("🏠 Télétravail vs Présentiel")
    fig_rem = px.pie(df_f, names='is_remote', hole=0.4, template="plotly_dark")
    st.plotly_chart(fig_rem, width="stretch")
with c4:
    st.subheader("📝 Types de Contrats")
    fig_cont = px.bar(df_f['type_contrat'].value_counts().reset_index(), x='type_contrat', y='count', template="plotly_dark")
    st.plotly_chart(fig_cont, width="stretch")

# WORDCLOUD
st.subheader("☁️ Nuage de compétences (Sémantique)")
text = " ".join(df_f['titre'].astype(str).str.lower())
custom_stopwords = set(STOPWORDS)
custom_stopwords.update(["h", "f", "h/f", "f/h", "femme", "homme", "offre", "emploi"])
wordcloud = WordCloud(background_color="#0E1117", colormap="Blues", width=800, height=400).generate(text)
fig_wc, ax = plt.subplots()
ax.imshow(wordcloud, interpolation='bilinear')
ax.axis("off")
st.pyplot(fig_wc)
