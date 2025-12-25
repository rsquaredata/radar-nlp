from __future__ import annotations
import sqlite3
import pandas as pd
import streamlit as st
from typing import Optional, Dict, Any

@st.cache_resource
def get_conn(db_path: str) -> sqlite3.Connection:
    con = sqlite3.connect(db_path, check_same_thread=False)
    return con

@st.cache_data(ttl=60)
def query_df(db_path: str, sql: str, params: Optional[Dict[str, Any]] = None) -> pd.DataFrame:
    con = get_conn(db_path)
    return pd.read_sql(sql, con, params=params or {})

def exec_sql(db_path: str, sql: str, params: Optional[Dict[str, Any]] = None) -> None:
    con = get_conn(db_path)
    cur = con.cursor()
    cur.execute(sql, params or {})
    con.commit()
