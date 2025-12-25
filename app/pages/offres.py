import streamlit as st
from config import DB_PATH, DEFAULT_TABLE, MAX_ROWS_TABLE
from db import query_df

st.title("📋 Liste des offres")

q = st.text_input("Recherche (titre / entreprise / texte)", value="")
region = st.text_input("Filtre région (exact, optionnel)", value="")
remote = st.selectbox("Télétravail", ["(tous)", "yes", "no", "unknown"], index=0)

where = []
params = {}

if q.strip():
    where.append("(title LIKE :q OR employer LIKE :q OR raw_text LIKE :q)")
    params["q"] = f"%{q.strip()}%"

if region.strip():
    where.append("region = :region")
    params["region"] = region.strip()

if remote != "(tous)":
    where.append("remote = :remote")
    params["remote"] = remote

sql = f"SELECT * FROM {DEFAULT_TABLE}"
if where:
    sql += " WHERE " + " AND ".join(where)
sql += " ORDER BY published_date DESC LIMIT :lim"
params["lim"] = MAX_ROWS_TABLE

df = query_df(str(DB_PATH), sql, params=params)

st.caption(f"Affichage limité à {MAX_ROWS_TABLE} lignes (ajuste MAX_ROWS_TABLE).")
st.dataframe(
    df,
    use_container_width=True,
    hide_index=True,
)

st.divider()
st.subheader("🔗 Postuler (liens cliquables)")
# petite table dédiée liens
if "url" in df.columns:
    links = df[["title", "employer", "url"]].dropna(subset=["url"]).head(50)
    st.dataframe(links, use_container_width=True, hide_index=True)
