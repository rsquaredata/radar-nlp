import streamlit as st
import folium
from streamlit_folium import st_folium
from folium.plugins import MarkerCluster
from utils.db import load_filtered_data, get_connection
from utils.logic import inject_style

inject_style()

con = get_connection()
list_m = con.execute("SELECT DISTINCT nom_metier FROM dim_metier ORDER BY 1").df()['nom_metier'].tolist()
list_r = con.execute("SELECT DISTINCT nom_region FROM dim_region ORDER BY 1").df()['nom_region'].tolist()
con.close()

st.sidebar.title("🗺️ Filtres Carte")
sel_m = st.sidebar.multiselect("Métiers", list_m, default=list_m)
sel_r = st.sidebar.multiselect("Régions", list_r, default=list_r)

df = load_filtered_data(sel_m, sel_r)

st.title("📍 Cartographie nationale")

if 'latitude' in df.columns and 'longitude' in df.columns:
    df_geo = df.dropna(subset=['latitude', 'longitude'])
    with st.spinner(f"Chargement de {len(df_geo)} offres..."):
        m = folium.Map(location=[46.2276, 2.2137], zoom_start=6, tiles="CartoDB dark_matter")
        marker_cluster = MarkerCluster().add_to(m)
        for _, row in df_geo.iterrows():
            folium.Marker(
                location=[row['latitude'], row['longitude']], 
                popup=f"<b>{row['titre']}</b>",
                tooltip=row['nom_metier']
            ).add_to(marker_cluster)
        st_folium(m, width=1400, height=700, returned_objects=[])
else:
    st.error("Données GPS manquantes.")
