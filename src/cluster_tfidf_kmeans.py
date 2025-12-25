# cluster_tfidf_kmeans.py
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import silhouette_score


def top_terms_per_cluster(
    km: KMeans,
    feature_names: np.ndarray,
    top_n: int = 20,
) -> Dict[int, List[str]]:
    # km.cluster_centers_: (k, n_features)
    centers = km.cluster_centers_
    out: Dict[int, List[str]] = {}
    for c in range(centers.shape[0]):
        top_idx = np.argsort(centers[c])[::-1][:top_n]
        out[c] = [feature_names[i] for i in top_idx]
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--in_csv", required=True, help="corpus_clean.csv")
    ap.add_argument("--out_dir", required=True)
    ap.add_argument("--k", type=int, default=25)
    ap.add_argument("--max_features", type=int, default=80000)
    ap.add_argument("--ngram_max", type=int, default=2)
    ap.add_argument("--min_df", type=int, default=2)
    ap.add_argument("--max_df", type=float, default=0.9)
    ap.add_argument("--sample_silhouette", type=int, default=6000)
    ap.add_argument("--random_state", type=int, default=42)

    args = ap.parse_args()

    in_csv = Path(args.in_csv)
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    df = pd.read_csv(in_csv)
    if "clean_text" not in df.columns:
        raise RuntimeError("Il manque la colonne 'text' dans le corpus_clean.csv")

    texts = df["clean_text"].astype(str).tolist()
    print(f"✅ Docs for TF-IDF: {len(texts)}")

    vec = TfidfVectorizer(
        lowercase=True,
        stop_words="english",  # OK même si FR/EN mix, ça aide un peu
        max_features=args.max_features,
        ngram_range=(1, args.ngram_max),
        min_df=args.min_df,
        max_df=args.max_df,
    )

    X = vec.fit_transform(texts)
    print(f"✅ TF-IDF matrix: {X.shape}")

    km = KMeans(
        n_clusters=args.k,
        n_init=10,
        random_state=args.random_state,
    )
    labels = km.fit_predict(X)

    inertia = float(km.inertia_)

    # silhouette sur sample
    sil = None
    if args.sample_silhouette and args.sample_silhouette > 0:
        n = X.shape[0]
        s = min(args.sample_silhouette, n)
        rng = np.random.default_rng(args.random_state)
        idx = rng.choice(n, size=s, replace=False)
        sil = float(silhouette_score(X[idx], labels[idx]))
        print(f"📌 K={args.k} | inertia={inertia:.2f} | silhouette(sample={s})={sil:.4f}")
    else:
        print(f"📌 K={args.k} | inertia={inertia:.2f}")

    # add labels
    df_out = df.copy()
    df_out["cluster"] = labels

    out_csv = out_dir / f"clustered_k{args.k}.csv"
    df_out.to_csv(out_csv, index=False, encoding="utf-8")
    print(f"✅ Saved CSV: {out_csv}")

    # top terms
    feature_names = np.array(vec.get_feature_names_out())
    top_terms = top_terms_per_cluster(km, feature_names, top_n=25)

    meta = {
        "k": args.k,
        "inertia": inertia,
        "silhouette_sample": sil,
        "tfidf_shape": [int(X.shape[0]), int(X.shape[1])],
        "params": {
            "max_features": args.max_features,
            "ngram_max": args.ngram_max,
            "min_df": args.min_df,
            "max_df": args.max_df,
        },
        "top_terms": top_terms,
    }

    out_meta = out_dir / f"clusters_k{args.k}_top_terms.json"
    with open(out_meta, "w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)
    print(f"✅ Saved meta: {out_meta}")


if __name__ == "__main__":
    main()
