import streamlit as st
from config import DB_PATH, DEFAULT_TABLE
from db import query_df
from charts import kpis, fig_offers_by_region, fig_offers_by_cluster, fig_timeline

st.title("📊 Dashboard")

df = query_df(str(DB_PATH), f"SELECT * FROM {DEFAULT_TABLE}")

k = kpis(df)
c1, c2, c3, c4 = st.columns(4)
c1.metric("Offres", k["Offres"])
c2.metric("Régions", k["Régions"])
c3.metric("Clusters", k["Clusters"])
c4.metric("Sources", k["Sources"])

st.divider()

colA, colB = st.columns(2)
with colA:
    st.plotly_chart(fig_offers_by_region(df), use_container_width=True)
with colB:
    st.plotly_chart(fig_offers_by_cluster(df), use_container_width=True)

st.divider()
fig = fig_timeline(df)
if fig:
    st.plotly_chart(fig, use_container_width=True)
else:
    st.warning("Pas de colonne published_date exploitable pour la timeline.")
