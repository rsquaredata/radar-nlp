from __future__ import annotations

import argparse
import json
import sqlite3
from datetime import datetime
from pathlib import Path

import pandas as pd


def ensure_table(con: sqlite3.Connection) -> None:
    con.execute(
        """
        CREATE TABLE IF NOT EXISTS clusters_meta (
            cluster INTEGER PRIMARY KEY,
            cluster_label TEXT,
            top_terms TEXT,
            score_debug TEXT,
            n_docs INTEGER,
            updated_at TEXT
        )
        """
    )
    con.commit()


def detect_col(df: pd.DataFrame, candidates: list[str]) -> str | None:
    cols = {c.lower(): c for c in df.columns}
    for cand in candidates:
        if cand.lower() in cols:
            return cols[cand.lower()]
    return None


def main() -> None:
    ap = argparse.ArgumentParser(description="Load clusters labels/meta into SQLite.")
    ap.add_argument("--db", required=True, help="Path to offers.sqlite")
    ap.add_argument("--labels_csv", required=True, help="Path to clusters_labels_k25.csv")
    args = ap.parse_args()

    db_path = Path(args.db)
    labels_path = Path(args.labels_csv)

    if not db_path.exists():
        raise FileNotFoundError(f"DB not found: {db_path}")
    if not labels_path.exists():
        raise FileNotFoundError(f"labels_csv not found: {labels_path}")

    df = pd.read_csv(labels_path)

    # detect columns robustly
    col_cluster = detect_col(df, ["cluster", "cluster_id"])
    col_label = detect_col(df, ["cluster_label", "label"])
    col_terms = detect_col(df, ["top_terms", "terms"])
    col_debug = detect_col(df, ["score_debug", "debug", "scores"])
    col_n = detect_col(df, ["n_docs", "n", "count"])

    if not col_cluster or not col_label:
        raise RuntimeError(
            "labels_csv doit contenir au minimum les colonnes cluster (ou cluster_id) et cluster_label (ou label)."
        )

    # optional cols
    if not col_terms:
        df["top_terms"] = ""
        col_terms = "top_terms"
    if not col_debug:
        df["score_debug"] = ""
        col_debug = "score_debug"
    if not col_n:
        df["n_docs"] = None
        col_n = "n_docs"

    now = datetime.utcnow().isoformat(timespec="seconds") + "Z"

    con = sqlite3.connect(str(db_path))
    try:
        ensure_table(con)

        rows = []
        for _, r in df.iterrows():
            try:
                cluster = int(r[col_cluster])
            except Exception:
                continue

            label = None if pd.isna(r[col_label]) else str(r[col_label]).strip()
            top_terms = None if pd.isna(r[col_terms]) else str(r[col_terms]).strip()
            score_debug = None if pd.isna(r[col_debug]) else str(r[col_debug]).strip()

            n_docs = None
            if col_n and not pd.isna(r[col_n]):
                try:
                    n_docs = int(r[col_n])
                except Exception:
                    n_docs = None

            rows.append((cluster, label, top_terms, score_debug, n_docs, now))

        con.executemany(
            """
            INSERT INTO clusters_meta(cluster, cluster_label, top_terms, score_debug, n_docs, updated_at)
            VALUES (?, ?, ?, ?, ?, ?)
            ON CONFLICT(cluster) DO UPDATE SET
                cluster_label=excluded.cluster_label,
                top_terms=excluded.top_terms,
                score_debug=excluded.score_debug,
                n_docs=excluded.n_docs,
                updated_at=excluded.updated_at
            """,
            rows,
        )
        con.commit()

        # quick check
        chk = pd.read_sql("SELECT count(*) AS n FROM clusters_meta", con)
        print(f"✅ clusters_meta loaded: {int(chk.iloc[0]['n'])} clusters")

    finally:
        con.close()


if __name__ == "__main__":
    main()
