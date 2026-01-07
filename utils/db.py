import duckdb
import streamlit as st
import os

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DB_PATH = PROJECT_ROOT / "data" / "db" / "radar.duckdb"

def get_connection(read_only: bool = True):
    if not DB_PATH.exists():
        raise FileNotFoundError(
            f"Base DuckDB introuvable : {DB_PATH}\n"
            "Avez-vous exécuté le script d'initialisation ?"
        )

    return duckdb.connect(str(DB_PATH), read_only=read_only)

@st.cache_data
def load_filtered_data(metiers=None, regions=None):
    con = get_connection()
    query = "SELECT * FROM v_final_dashboard"
    params = []
    conditions = []
    if metiers:
        conditions.append("nom_metier = ANY(?)")
        params.append(metiers)
    if regions:
        conditions.append("region = ANY(?)")
        params.append(regions)
    if conditions:
        query += " WHERE " + " AND ".join(conditions)
    df = con.execute(query, params).df()
    con.close()
    return df
