from __future__ import annotations

import argparse
import sqlite3
from pathlib import Path

import pandas as pd


def ensure_columns(con: sqlite3.Connection) -> None:
    """Add missing columns to offers table (safe)."""
    cur = con.cursor()
    cur.execute("PRAGMA table_info(offers)")
    existing = {row[1] for row in cur.fetchall()}  # column name at index 1

    # Add columns if missing
    if "cluster" not in existing:
        cur.execute("ALTER TABLE offers ADD COLUMN cluster INTEGER")
    if "cluster_label" not in existing:
        cur.execute("ALTER TABLE offers ADD COLUMN cluster_label TEXT")
    if "cluster_top_terms" not in existing:
        cur.execute("ALTER TABLE offers ADD COLUMN cluster_top_terms TEXT")

    # Helpful indexes (safe)
    cur.execute("CREATE INDEX IF NOT EXISTS idx_offers_uid ON offers(uid)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_offers_cluster ON offers(cluster)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_offers_region ON offers(region)")
    con.commit()


def sync_clusters(
    db_path: str,
    clustered_csv: str,
    labels_csv: str,
    batch_size: int = 5000,
) -> None:
    db_path = str(db_path)
    clustered_csv = str(clustered_csv)
    labels_csv = str(labels_csv)

    if not Path(db_path).exists():
        raise FileNotFoundError(f"DB introuvable: {db_path}")
    if not Path(clustered_csv).exists():
        raise FileNotFoundError(f"CSV introuvable: {clustered_csv}")
    if not Path(labels_csv).exists():
        raise FileNotFoundError(f"CSV introuvable: {labels_csv}")

    dfc = pd.read_csv(clustered_csv)
    required_c = {"uid", "cluster"}
    if not required_c.issubset(set(dfc.columns)):
        raise RuntimeError(f"{clustered_csv} doit contenir {sorted(required_c)}")

    dfl = pd.read_csv(labels_csv)
    required_l = {"cluster", "cluster_label"}
    if not required_l.issubset(set(dfl.columns)):
        raise RuntimeError(f"{labels_csv} doit contenir {sorted(required_l)}")

    # Build mapping cluster -> label/top_terms
    dfl = dfl.copy()
    if "top_terms" not in dfl.columns:
        dfl["top_terms"] = None

    map_label = dict(zip(dfl["cluster"].astype(int), dfl["cluster_label"].astype(str)))
    map_terms = dict(zip(dfl["cluster"].astype(int), dfl["top_terms"].astype(str)))

    # Attach label + terms to each uid row
    dfc = dfc[["uid", "cluster"]].copy()
    dfc["cluster"] = pd.to_numeric(dfc["cluster"], errors="coerce").astype("Int64")
    dfc = dfc.dropna(subset=["uid", "cluster"])
    dfc["cluster"] = dfc["cluster"].astype(int)
    dfc["cluster_label"] = dfc["cluster"].map(map_label).fillna("Unknown")
    dfc["cluster_top_terms"] = dfc["cluster"].map(map_terms).fillna("")

    # Write to SQLite
    con = sqlite3.connect(db_path)
    try:
        ensure_columns(con)
        cur = con.cursor()

        # Update in batches for speed
        total = len(dfc)
        print(f"✅ Rows to update: {total}")

        sql = """
        UPDATE offers
        SET cluster = ?,
            cluster_label = ?,
            cluster_top_terms = ?
        WHERE uid = ?
        """

        data = list(
            zip(
                dfc["cluster"].tolist(),
                dfc["cluster_label"].tolist(),
                dfc["cluster_top_terms"].tolist(),
                dfc["uid"].tolist(),
            )
        )

        for i in range(0, total, batch_size):
            chunk = data[i : i + batch_size]
            cur.executemany(sql, chunk)
            con.commit()
            if (i + batch_size) % 20000 == 0 or (i + batch_size) >= total:
                print(f"... updated {min(i + batch_size, total)}/{total}")

        # Quick sanity check
        cur.execute("SELECT COUNT(*) FROM offers WHERE cluster IS NOT NULL")
        n_has = cur.fetchone()[0]
        cur.execute("SELECT COUNT(DISTINCT cluster) FROM offers WHERE cluster IS NOT NULL")
        k = cur.fetchone()[0]
        print(f"📌 offers with cluster: {n_has} | distinct clusters: {k}")

    finally:
        con.close()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--db", required=True, help="Path to offers.sqlite")
    ap.add_argument("--clustered_csv", required=True, help="Path to clustered_k25.csv")
    ap.add_argument("--labels_csv", required=True, help="Path to clusters_labels_k25.csv")
    ap.add_argument("--batch_size", type=int, default=5000)
    args = ap.parse_args()

    sync_clusters(
        db_path=args.db,
        clustered_csv=args.clustered_csv,
        labels_csv=args.labels_csv,
        batch_size=args.batch_size,
    )
    print("✅ Done.")


if __name__ == "__main__":
    main()
