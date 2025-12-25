# interpret_clusters.py
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Dict, List

import pandas as pd


def clean_ws(s: str) -> str:
    return re.sub(r"\s+", " ", (s or "")).strip()


def guess_label(top_terms: List[str]) -> str:
    """Petit heuristique pour proposer un label métier (optionnel)."""
    t = " ".join([x.lower() for x in top_terms])

    if any(k in t for k in ["spark", "hadoop", "kafka", "airflow", "etl", "pipeline"]):
        return "Data Engineer / ETL"
    if any(k in t for k in ["power bi", "tableau", "reporting", "bi", "dashboard"]):
        return "BI / Reporting"
    if any(k in t for k in ["machine learning", "deep learning", "tensorflow", "pytorch", "model", "nlp"]):
        return "ML / IA"
    if any(k in t for k in ["sql", "query", "database", "postgres", "mysql", "oracle"]):
        return "Data Analyst / SQL"
    if any(k in t for k in ["stat", "statistics", "bayesian", "r ", "sas"]):
        return "Stats / Quant"
    if any(k in t for k in ["python", "pandas", "scikit", "sklearn"]):
        return "Data Science (Python)"
    return "Data / Tech (mix)"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--clustered_csv", required=True, help="clustered_k25.csv")
    ap.add_argument("--meta_json", required=True, help="clusters_k25_top_terms.json")
    ap.add_argument("--out_dir", required=True)
    ap.add_argument("--examples_per_cluster", type=int, default=6)
    ap.add_argument("--max_raw_chars", type=int, default=450)
    args = ap.parse_args()

    clustered_csv = Path(args.clustered_csv)
    meta_json = Path(args.meta_json)
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    df = pd.read_csv(clustered_csv)
    if "cluster" not in df.columns:
        raise RuntimeError("Il manque la colonne 'cluster' dans le CSV clustered.")

    with open(meta_json, "r", encoding="utf-8") as f:
        meta = json.load(f)

    top_terms_map: Dict[str, List[str]] = meta.get("top_terms", {})
    # keys might be strings in JSON
    top_terms_map = {str(k): v for k, v in top_terms_map.items()}

    # Basic stats
    n = len(df)
    k = int(meta.get("k", df["cluster"].nunique()))
    print(f"✅ Loaded clustered data: {n} rows | k={k}")

    # Build per-cluster summary
    rows_summary = []
    rows_examples = []

    for c in sorted(df["cluster"].dropna().unique()):
        c_int = int(c)
        sub = df[df["cluster"] == c_int].copy()

        top_terms = top_terms_map.get(str(c_int), [])
        label_guess = guess_label(top_terms)

        # Counts
        size = len(sub)

        # Common fields if present
        top_sources = ""
        if "source" in sub.columns:
            top_sources = ", ".join(
                [f"{a}:{b}" for a, b in sub["source"].value_counts().head(3).items()]
            )

        top_locations = ""
        if "location" in sub.columns:
            loc_vc = sub["location"].fillna("").astype(str)
            loc_vc = loc_vc[loc_vc.str.strip() != ""]
            top_locations = ", ".join([f"{a}:{b}" for a, b in loc_vc.value_counts().head(3).items()])

        top_titles = ""
        if "title" in sub.columns:
            tt = sub["title"].fillna("").astype(str)
            tt = tt[tt.str.strip() != ""]
            top_titles = ", ".join([f"{a}:{b}" for a, b in tt.value_counts().head(3).items()])

        rows_summary.append(
            {
                "cluster": c_int,
                "size": size,
                "label_guess": label_guess,
                "top_terms": ", ".join(top_terms[:20]),
                "top_sources": top_sources,
                "top_locations": top_locations,
                "top_titles": top_titles,
            }
        )

        # Examples
        cols = df.columns.tolist()
        keep_cols = [c for c in ["source", "url", "title", "employer", "location", "contract_type", "salary"] if c in cols]
        # sample examples
        ex = sub.sample(n=min(args.examples_per_cluster, len(sub)), random_state=42)
        for _, r in ex.iterrows():
            raw = ""
            if "raw_text" in cols:
                raw = clean_ws(str(r.get("raw_text") or ""))[: args.max_raw_chars]
            rows_examples.append(
                {
                    "cluster": c_int,
                    **{k: r.get(k) for k in keep_cols},
                    "raw_excerpt": raw,
                }
            )

    df_summary = pd.DataFrame(rows_summary).sort_values(["size", "cluster"], ascending=[False, True])
    df_examples = pd.DataFrame(rows_examples).sort_values(["cluster"])

    out_summary = out_dir / "clusters_summary_k25.csv"
    out_examples = out_dir / "clusters_examples_k25.csv"
    out_md = out_dir / "clusters_report_k25.md"

    df_summary.to_csv(out_summary, index=False, encoding="utf-8")
    df_examples.to_csv(out_examples, index=False, encoding="utf-8")

    # Markdown report
    lines = []
    lines.append(f"# Rapport clusters (k=25)\n")
    lines.append(f"- Documents: **{n}**\n")
    lines.append(f"- k: **{k}**\n")
    lines.append(f"- Inertia: **{meta.get('inertia')}**\n")
    lines.append(f"- Silhouette(sample): **{meta.get('silhouette_sample')}**\n\n")

    for _, row in df_summary.iterrows():
        c = int(row["cluster"])
        lines.append(f"## Cluster {c} — {row['label_guess']} (n={row['size']})\n")
        lines.append(f"**Top termes :** {row['top_terms']}\n\n")
        if row.get("top_sources"):
            lines.append(f"**Sources :** {row['top_sources']}\n\n")
        if row.get("top_locations"):
            lines.append(f"**Lieux :** {row['top_locations']}\n\n")
        if row.get("top_titles"):
            lines.append(f"**Titres fréquents :** {row['top_titles']}\n\n")

        # add examples for this cluster
        subex = df_examples[df_examples["cluster"] == c].head(6)
        lines.append("**Exemples :**\n")
        for _, ex in subex.iterrows():
            title = ex.get("title", "")
            comp = ex.get("employer", "")
            loc = ex.get("location", "")
            url = ex.get("url", "")
            excerpt = ex.get("raw_excerpt", "")
            lines.append(f"- {title} | {comp} | {loc}\n")
            if isinstance(url, str) and url.strip():
                lines.append(f"  - URL: {url}\n")
            if isinstance(excerpt, str) and excerpt.strip():
                lines.append(f"  - Extrait: {excerpt}\n")
        lines.append("\n")

    out_md.write_text("".join(lines), encoding="utf-8")

    print(f"✅ Saved: {out_summary}")
    print(f"✅ Saved: {out_examples}")
    print(f"✅ Saved: {out_md}")


if __name__ == "__main__":
    main()
