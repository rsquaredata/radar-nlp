import streamlit as st
from utils.logic import inject_style, get_connection

inject_style()
st.title("🕵️ Explorateur d'annonces")

# 1. FILTRES
with st.expander("🔍 Recherche et filtres", expanded=True):
    col1, col2, col3 = st.columns([2, 1, 1])
    search = col1.text_input("Mots-clés (compétences, outils...)")
    sal_range = col2.select_slider("Salaire (K€)", options=range(20, 121, 5), value=(35, 70))
    remote_only = col3.checkbox("Télétravail / Hybride")

# 2. REQUÊTE AVEC EXCLUSIONS
con = get_connection()
# On exclut les métiers polluants par mots-clés dans le titre
exclusions = ['barman', 'psychiatre', 'droit des affaires', 'droit social', 'juriste', 'comptable']
exclusion_query = " AND " + " AND ".join([f"titre NOT ILIKE '%{ex}%'" for ex in exclusions])

query = f"""
    SELECT * FROM v_final_dashboard 
    WHERE nom_metier NOT IN ('Autre', 'RH')
    {exclusion_query}
"""
params = []

if search:
    query += " AND (titre ILIKE ? OR nom_metier ILIKE ?)"
    params.extend([f"%{search}%", f"%{search}%"])

if remote_only:
    query += " AND is_remote = TRUE"

df = con.execute(query, params).df()
con.close()

# Nettoyage Source dynamique
df.loc[df['url'].str.contains('hellowork', na=False), 'source'] = 'Hellowork'
df.loc[df['url'].str.contains('adzuna', na=False), 'source'] = 'Adzuna'

st.write(f"**{len(df)}** offres pertinentes trouvées")
st.dataframe(
    df[['date_publication', 'titre', 'nom_metier', 'region', 'source', 'url']], 
    width="stretch", 
    hide_index=True
)
