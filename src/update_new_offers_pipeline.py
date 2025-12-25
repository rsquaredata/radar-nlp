from __future__ import annotations

import argparse
import re
import sqlite3
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, Tuple

import pandas as pd

# ML
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans

try:
    import joblib
except Exception as e:
    raise RuntimeError("Installe joblib: pip install joblib") from e


# ---- UTF-8 safe for Windows console ----
try:
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
except Exception:
    pass


def now_sql() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def clean_text_basic(s: str) -> str:
    """Basic cleaning similar to your corpus_clean (lightweight)."""
    s = (s or "").lower()
    s = re.sub(r"http\S+", " ", s)
    s = re.sub(r"[^a-zàâçéèêëîïôûùüÿñæœ0-9\s\-_/]", " ", s, flags=re.IGNORECASE)
    s = re.sub(r"\s+", " ", s).strip()
    return s


def ensure_columns(con: sqlite3.Connection) -> None:
    """Add needed columns if missing (safe)."""
    cur = con.cursor()

    # check existing columns
    cols = pd.read_sql("PRAGMA table_info(offers)", con)["name"].tolist()
    wanted = {
        "clean_text": "TEXT",
        "n_tokens": "INTEGER",
        "cluster": "INTEGER",
        "cluster_label": "TEXT",
        "processed_at": "TEXT",
    }
    for c, ctype in wanted.items():
        if c not in cols:
            cur.execute(f"ALTER TABLE offers ADD COLUMN {c} {ctype}")
    con.commit()


def load_labels(labels_csv: str) -> Dict[int, str]:
    df = pd.read_csv(labels_csv)
    # accept either (cluster, cluster_label) or (cluster_id, label)
    if {"cluster", "cluster_label"}.issubset(df.columns):
        mp = dict(zip(df["cluster"].astype(int), df["cluster_label"].astype(str)))
        return mp
    if {"cluster_id", "label"}.issubset(df.columns):
        mp = dict(zip(df["cluster_id"].astype(int), df["label"].astype(str)))
        return mp
    raise RuntimeError("labels_csv doit contenir (cluster, cluster_label) ou (cluster_id, label)")


def fetch_training_corpus(con: sqlite3.Connection) -> pd.DataFrame:
    """Corpus for training (all offers that have raw_text)."""
    df = pd.read_sql(
        """
        SELECT uid, raw_text
        FROM offers
        WHERE raw_text IS NOT NULL AND length(raw_text) > 0
        """,
        con,
    )
    df["clean_text"] = df["raw_text"].astype(str).map(clean_text_basic)
    df["n_tokens"] = df["clean_text"].map(lambda x: len(x.split()))
    # keep minimal quality
    df = df[df["n_tokens"] >= 1].copy()
    return df


def fetch_new_offers(con: sqlite3.Connection, limit: int | None = None) -> pd.DataFrame:
    """
    New offers = those not processed yet OR without cluster.
    """
    q = """
    SELECT uid, raw_text
    FROM offers
    WHERE (processed_at IS NULL OR processed_at = '')
       OR cluster IS NULL
    """
    if limit:
        q += f" LIMIT {int(limit)}"

    df = pd.read_sql(q, con)
    if df.empty:
        return df

    df["clean_text"] = df["raw_text"].fillna("").astype(str).map(clean_text_basic)
    df["n_tokens"] = df["clean_text"].map(lambda x: len(x.split()))
    df = df[df["n_tokens"] >= 1].copy()
    return df


def train_and_save_models(
    con: sqlite3.Connection,
    k: int,
    tfidf_path: Path,
    kmeans_path: Path,
    max_features: int = 80000,
    ngram_max: int = 2,
) -> Tuple[TfidfVectorizer, KMeans]:
    df = fetch_training_corpus(con)
    print(f"[MODEL] Training corpus: {len(df)} docs")

    vectorizer = TfidfVectorizer(
        max_features=max_features,
        ngram_range=(1, ngram_max),
        min_df=2,
        max_df=0.95,
    )
    X = vectorizer.fit_transform(df["clean_text"].tolist())

    km = KMeans(n_clusters=k, random_state=42, n_init=10)
    km.fit(X)

    tfidf_path.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(vectorizer, tfidf_path)
    joblib.dump(km, kmeans_path)
    print(f"[MODEL] Saved TF-IDF -> {tfidf_path}")
    print(f"[MODEL] Saved KMeans  -> {kmeans_path}")
    return vectorizer, km


def load_models(
    con: sqlite3.Connection,
    k: int,
    tfidf_path: Path,
    kmeans_path: Path,
    retrain_if_missing: bool = True,
) -> Tuple[TfidfVectorizer, KMeans]:
    if tfidf_path.exists() and kmeans_path.exists():
        vectorizer = joblib.load(tfidf_path)
        km = joblib.load(kmeans_path)
        # safety check
        if getattr(km, "n_clusters", None) != k:
            print(f"[WARN] Model K={km.n_clusters} but requested K={k}. Retraining.")
            return train_and_save_models(con, k, tfidf_path, kmeans_path)
        return vectorizer, km

    if not retrain_if_missing:
        raise RuntimeError(
            "Models not found. Either provide existing joblib models or set retrain_if_missing=True."
        )

    print("[MODEL] Models missing -> training once on full DB...")
    return train_and_save_models(con, k, tfidf_path, kmeans_path)


def update_offers_in_db(con: sqlite3.Connection, df_new: pd.DataFrame) -> None:
    cur = con.cursor()
    rows = df_new[["clean_text", "n_tokens", "cluster", "cluster_label", "uid"]].values.tolist()
    cur.executemany(
        """
        UPDATE offers
        SET clean_text = ?,
            n_tokens = ?,
            cluster = ?,
            cluster_label = ?,
            processed_at = ?
        WHERE uid = ?
        """,
        [(ct, int(nt), int(cl), lbl, now_sql(), uid) for ct, nt, cl, lbl, uid in rows],
    )
    con.commit()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--db", required=True)
    ap.add_argument("--labels_csv", required=True)
    ap.add_argument("--k", type=int, default=25)

    ap.add_argument("--tfidf_model", default="../data/models/tfidf_k{K}.joblib")
    ap.add_argument("--kmeans_model", default="../data/models/kmeans_k{K}.joblib")

    ap.add_argument("--limit_new", type=int, default=0, help="0 = no limit")
    ap.add_argument("--retrain_if_missing", action="store_true")

    args = ap.parse_args()

    db_path = args.db
    con = sqlite3.connect(db_path)
    ensure_columns(con)

    label_map = load_labels(args.labels_csv)

    tfidf_path = Path(args.tfidf_model.format(K=args.k))
    kmeans_path = Path(args.kmeans_model.format(K=args.k))

    vectorizer, km = load_models(
        con,
        k=args.k,
        tfidf_path=tfidf_path,
        kmeans_path=kmeans_path,
        retrain_if_missing=args.retrain_if_missing,
    )

    df_new = fetch_new_offers(con, limit=(args.limit_new or None))
    print(f"[PIPELINE] New offers detected: {len(df_new)}")

    if df_new.empty:
        print("[PIPELINE] Nothing to do.")
        return

    X_new = vectorizer.transform(df_new["clean_text"].tolist())
    df_new["cluster"] = km.predict(X_new)

    df_new["cluster_label"] = df_new["cluster"].map(lambda c: label_map.get(int(c), "Unknown"))
    update_offers_in_db(con, df_new)

    print(f"[PIPELINE] Updated: {len(df_new)} new offers")
    con.close()


if __name__ == "__main__":
    main()
