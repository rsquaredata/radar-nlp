from __future__ import annotations

import plotly.express as px
import pandas as pd


def fig_jobs_map(
    df: pd.DataFrame,
    color_by: str = "cluster_label",
    zoom: int = 5,
    height: int = 650,
):
    """
    Construit une carte interactive des offres.

    Hypothèses simples et robustes :
    - le DataFrame contient des colonnes 'lat' et 'lon'
    - 'lat' et 'lon' sont numériques ou convertibles en numérique
    - color_by est une colonne du df (cluster_label, region, source, etc.)
    """

    if df.empty:
        return None

    if "lat" not in df.columns or "lon" not in df.columns:
        return None

    df_map = df.copy()

    # Conversion sécurisée
    df_map["lat"] = pd.to_numeric(df_map["lat"], errors="coerce")
    df_map["lon"] = pd.to_numeric(df_map["lon"], errors="coerce")

    df_map = df_map.dropna(subset=["lat", "lon"])
    if df_map.empty:
        return None

    # Colonnes pour le hover
    hover_cols = [
        "title",
        "employer",
        "region",
        "dept_name",
        "city",
        "source",
        "cluster_label",
        "contract_type",
        "remote_label",
        "salary_str",
    ]
    hover_data = {c: True for c in hover_cols if c in df_map.columns}

    # Couleur des points
    color_arg = color_by if color_by in df_map.columns else None

    fig = px.scatter_mapbox(
        df_map,
        lat="lat",
        lon="lon",
        color=color_arg,
        hover_name="title" if "title" in df_map.columns else None,
        hover_data=hover_data,
        zoom=zoom,
        height=height,
    )

    fig.update_layout(
        mapbox_style="open-street-map",  # fond clair, pas de token
        margin=dict(l=0, r=0, t=0, b=0),
        legend=dict(
            bgcolor="rgba(248,250,252,0.9)",
            bordercolor="rgba(148,163,184,0.7)",
            borderwidth=1,
            font=dict(color="#020617", size=11),
        ),
    )

    fig.update_traces(
        marker=dict(
            size=9,
            opacity=0.85,
        )
    )

    return fig
