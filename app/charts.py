import pandas as pd
import plotly.express as px

def kpis(df: pd.DataFrame) -> dict:
    return {
        "Offres": int(df["uid"].nunique()) if "uid" in df else len(df),
        "Régions": int(df["region"].nunique()) if "region" in df else 0,
        "Clusters": int(df["cluster"].nunique()) if "cluster" in df else 0,
        "Sources": int(df["source"].nunique()) if "source" in df else 0,
    }

def fig_offers_by_region(df: pd.DataFrame):
    g = df.groupby("region", dropna=False)["uid"].nunique().reset_index(name="n")
    g = g.sort_values("n", ascending=False).head(15)
    return px.bar(g, x="region", y="n", title="Top régions (nb offres)")

def fig_offers_by_cluster(df: pd.DataFrame):
    g = df.groupby("cluster_label", dropna=False)["uid"].nunique().reset_index(name="n")
    g = g.sort_values("n", ascending=False).head(20)
    return px.bar(g, x="cluster_label", y="n", title="Top clusters (nb offres)")

def fig_timeline(df: pd.DataFrame):
    if "published_date" not in df.columns:
        return None
    d = df.copy()
    d["published_date"] = pd.to_datetime(d["published_date"], errors="coerce")
    d = d.dropna(subset=["published_date"])
    d["day"] = d["published_date"].dt.date
    g = d.groupby("day")["uid"].nunique().reset_index(name="n")
    return px.line(g, x="day", y="n", title="Offres publiées dans le temps")
