import streamlit as st
from config import DB_PATH, DEFAULT_TABLE
from db import query_df
from geo import map_points

st.title("🗺️ Carte interactive")

# Filtres
regions = query_df(str(DB_PATH), f"SELECT DISTINCT region FROM {DEFAULT_TABLE} WHERE region IS NOT NULL ORDER BY region")["region"].tolist()
clusters = query_df(str(DB_PATH), f"SELECT DISTINCT cluster_label FROM {DEFAULT_TABLE} WHERE cluster_label IS NOT NULL ORDER BY cluster_label")["cluster_label"].tolist()
sources = query_df(str(DB_PATH), f"SELECT DISTINCT source FROM {DEFAULT_TABLE} ORDER BY source")["source"].tolist()

c1, c2, c3 = st.columns(3)
with c1:
    region_sel = st.multiselect("Régions", regions, default=[])
with c2:
    cluster_sel = st.multiselect("Clusters", clusters, default=[])
with c3:
    source_sel = st.multiselect("Sources", sources, default=[])

where = []
params = {}
if region_sel:
    where.append("region IN (" + ",".join([f":r{i}" for i in range(len(region_sel))]) + ")")
    for i, r in enumerate(region_sel): params[f"r{i}"] = r
if cluster_sel:
    where.append("cluster_label IN (" + ",".join([f":c{i}" for i in range(len(cluster_sel))]) + ")")
    for i, c in enumerate(cluster_sel): params[f"c{i}"] = c
if source_sel:
    where.append("source IN (" + ",".join([f":s{i}" for i in range(len(source_sel))]) + ")")
    for i, s in enumerate(source_sel): params[f"s{i}"] = s

sql = f"SELECT uid,title,employer,region,dept_code,city,lat,lon,url,cluster_label,source FROM {DEFAULT_TABLE}"
if where:
    sql += " WHERE " + " AND ".join(where)

df = query_df(str(DB_PATH), sql, params=params)

st.caption(f"{len(df)} offres filtrées | {df[['lat','lon']].dropna().shape[0]} géocodées")
fig = map_points(df)
if fig:
    st.plotly_chart(fig, use_container_width=True)
else:
    st.warning("Aucune offre géocodée (lat/lon vides après filtres).")
