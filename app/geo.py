import pandas as pd
import plotly.express as px

def map_points(df: pd.DataFrame):
    d = df.dropna(subset=["lat", "lon"]).copy()
    if d.empty:
        return None

    # couleur par cluster_label (ou source)
    color_col = "cluster_label" if "cluster_label" in d.columns else "source"

    fig = px.scatter_mapbox(
        d,
        lat="lat",
        lon="lon",
        color=color_col,
        hover_name="title" if "title" in d.columns else None,
        hover_data={
            "employer": True if "employer" in d.columns else False,
            "region": True if "region" in d.columns else False,
            "dept_code": True if "dept_code" in d.columns else False,
            "url": True if "url" in d.columns else False,
        },
        zoom=4,
        height=700,
        title="Carte des offres (points géocodés)",
    )
    # mapbox style gratuit (open-street-map)
    fig.update_layout(mapbox_style="open-street-map")
    return fig
