from __future__ import annotations

import argparse
from pathlib import Path
from typing import List, Optional, Tuple

import pandas as pd


def _pick_col(cols: List[str], candidates: List[str]) -> Optional[str]:
    cols_low = {c.lower(): c for c in cols}
    for cand in candidates:
        if cand.lower() in cols_low:
            return cols_low[cand.lower()]
    return None


def infer_cluster_col(df: pd.DataFrame) -> Optional[str]:
    candidates = [
        "cluster_id", "cluster", "kmeans_cluster", "kmeans", "topic", "group",
        "label_id", "cluster_index"
    ]
    return _pick_col(list(df.columns), candidates)


def infer_label_col(df: pd.DataFrame) -> Optional[str]:
    candidates = [
        "label", "cluster_label", "name", "title", "auto_label", "generated_label",
        "cluster_name"
    ]
    return _pick_col(list(df.columns), candidates)


def ensure_int_cluster(series: pd.Series) -> pd.Series:
    # support "Cluster 12" / "12" / 12
    s = series.astype(str).str.extract(r"(\d+)")[0]
    return pd.to_numeric(s, errors="coerce").astype("Int64")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--clustered_csv", required=True, help="CSV avec la colonne cluster (ex: clustered_k25.csv)")
    ap.add_argument("--labels_csv", required=True, help="CSV des labels clusters (ex: clusters_labels_k25.csv)")
    ap.add_argument("--out_csv", required=True, help="Sortie CSV (ex: clustered_k25_labeled.csv)")
    args = ap.parse_args()

    clustered_path = Path(args.clustered_csv)
    labels_path = Path(args.labels_csv)
    out_path = Path(args.out_csv)

    df = pd.read_csv(clustered_path)
    lab = pd.read_csv(labels_path)

    # Detect columns
    df_cluster_col = infer_cluster_col(df)
    lab_cluster_col = infer_cluster_col(lab)
    lab_label_col = infer_label_col(lab)

    if df_cluster_col is None:
        raise RuntimeError(
            f"Impossible de trouver la colonne cluster dans {clustered_path.name}. "
            f"Colonnes: {list(df.columns)}"
        )
    if lab_cluster_col is None or lab_label_col is None:
        raise RuntimeError(
            f"Impossible de trouver (cluster + label) dans {labels_path.name}. "
            f"Colonnes: {list(lab.columns)}"
        )

    # Normalize cluster columns to int
    df["_cluster_id_tmp"] = ensure_int_cluster(df[df_cluster_col])
    lab["_cluster_id_tmp"] = ensure_int_cluster(lab[lab_cluster_col])

    if lab["_cluster_id_tmp"].isna().all():
        raise RuntimeError(
            "La colonne cluster du labels_csv n'a pas pu être convertie en entier. "
            "Vérifie son contenu."
        )

    # Build mapping table
    mapping = (
        lab[["_cluster_id_tmp", lab_label_col]]
        .dropna(subset=["_cluster_id_tmp"])
        .drop_duplicates(subset=["_cluster_id_tmp"])
        .rename(columns={lab_label_col: "cluster_label"})
    )

    # Merge
    out = df.merge(mapping, on="_cluster_id_tmp", how="left")

    # Add final columns (clean)
    out = out.drop(columns=["_cluster_id_tmp"])
    out = out.rename(columns={df_cluster_col: "cluster_id"})

    # If some clusters got no label
    missing = out["cluster_label"].isna().sum()
    if missing > 0:
        print(f"⚠️ Warning: {missing} lignes sans label (cluster_label manquant).")

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out.to_csv(out_path, index=False, encoding="utf-8")
    print(f"✅ Saved labeled CSV: {out_path} | rows={len(out)}")


if __name__ == "__main__":
    main()
