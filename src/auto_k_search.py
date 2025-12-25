from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import silhouette_score


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--in_csv", required=True, help="corpus_clean.csv")
    ap.add_argument("--out_dir", required=True)
    ap.add_argument("--text_col", default="clean_text")

    ap.add_argument("--k_min", type=int, default=5)
    ap.add_argument("--k_max", type=int, default=40)
    ap.add_argument("--k_step", type=int, default=1)

    ap.add_argument("--max_features", type=int, default=80000)
    ap.add_argument("--min_df", type=int, default=3)
    ap.add_argument("--max_df", type=float, default=0.6)
    ap.add_argument("--ngram_max", type=int, default=2)

    ap.add_argument("--sample_silhouette", type=int, default=6000, help="0=full")
    ap.add_argument("--seed", type=int, default=42)
    args = ap.parse_args()

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    df = pd.read_csv(args.in_csv, encoding="utf-8", low_memory=False)
    if args.text_col not in df.columns:
        raise RuntimeError(f"Colonne texte introuvable: {args.text_col}")

    texts = df[args.text_col].fillna("").astype(str)
    texts = texts[texts.str.strip() != ""].tolist()

    print(f"✅ Docs: {len(texts)}")

    vectorizer = TfidfVectorizer(
        max_features=args.max_features,
        min_df=args.min_df,
        max_df=args.max_df,
        ngram_range=(1, args.ngram_max),
        sublinear_tf=True,
    )
    X = vectorizer.fit_transform(texts)
    print(f"✅ TF-IDF: {X.shape}")

    # sample for silhouette to speed up
    if args.sample_silhouette == 0 or args.sample_silhouette >= X.shape[0]:
        sample_idx = None
        X_s = X
        print("ℹ️ Silhouette sur 100% des docs")
    else:
        rng = np.random.default_rng(args.seed)
        sample_idx = rng.choice(X.shape[0], size=args.sample_silhouette, replace=False)
        X_s = X[sample_idx]
        print(f"ℹ️ Silhouette sur sample={args.sample_silhouette}")

    rows = []
    for k in range(args.k_min, args.k_max + 1, args.k_step):
        km = KMeans(n_clusters=k, random_state=args.seed, n_init="auto", max_iter=300)
        labels = km.fit_predict(X)

        if sample_idx is None:
            sil = float(silhouette_score(X, labels))
        else:
            sil = float(silhouette_score(X_s, np.array(labels)[sample_idx]))

        inertia = float(km.inertia_)
        rows.append({"k": k, "inertia": inertia, "silhouette": sil})

        print(f"📌 k={k:2d} | inertia={inertia:.2f} | silhouette={sil:.4f}")

    res = pd.DataFrame(rows).sort_values("k")
    out_csv = out_dir / "k_search_results.csv"
    res.to_csv(out_csv, index=False, encoding="utf-8")

    # quick recommendation: best silhouette
    best = res.loc[res["silhouette"].idxmax()]
    print("\n✅ Saved:", out_csv)
    print(f"🏆 Best silhouette: k={int(best['k'])} | sil={best['silhouette']:.4f}")

if __name__ == "__main__":
    main()
