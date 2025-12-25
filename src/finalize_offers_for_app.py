from __future__ import annotations

import argparse
import sqlite3
from pathlib import Path

import pandas as pd


def table_columns(con: sqlite3.Connection, table: str) -> set[str]:
    rows = con.execute(f"PRAGMA table_info({table})").fetchall()
    return {r[1] for r in rows}


def ensure_indexes(con: sqlite3.Connection) -> None:
    # indexes for fast filtering in Streamlit
    con.execute("CREATE INDEX IF NOT EXISTS idx_offers_source ON offers(source)")
    con.execute("CREATE INDEX IF NOT EXISTS idx_offers_cluster ON offers(cluster)")
    con.execute("CREATE INDEX IF NOT EXISTS idx_offers_region ON offers(region)")
    con.execute("CREATE INDEX IF NOT EXISTS idx_offers_dept_code ON offers(dept_code)")
    con.execute("CREATE INDEX IF NOT EXISTS idx_offers_city ON offers(city)")
    con.execute("CREATE INDEX IF NOT EXISTS idx_offers_postcode ON offers(postcode)")
    con.execute("CREATE INDEX IF NOT EXISTS idx_offers_remote ON offers(remote)")
    con.execute("CREATE INDEX IF NOT EXISTS idx_offers_published_date ON offers(published_date)")
    con.execute("CREATE INDEX IF NOT EXISTS idx_offers_uid ON offers(uid)")
    con.commit()


def create_view(con: sqlite3.Connection) -> None:
    # Drop view if exists
    con.execute("DROP VIEW IF EXISTS offers_enriched")

    # Build SELECT with columns that exist (robust)
    offers_cols = table_columns(con, "offers")

    # core columns (order for app)
    preferred = [
        "uid", "source", "offer_id", "url",
        "title", "employer",
        "location", "city", "postcode", "dept_code", "region",
        "contract_type", "salary", "remote",
        "published_date", "published_relative", "seniority",
        "lat", "lon", "geo_score", "geo_source",
        "raw_text", "created_at",
        "cluster",
    ]

    # keep only those that exist
    selected = [c for c in preferred if c in offers_cols]

    # add remaining columns (if any) for completeness
    remaining = sorted(list(offers_cols - set(selected)))
    selected_all = selected + remaining

    select_sql = ",\n       ".join([f"o.{c}" for c in selected_all])

    # join clusters_meta (label + top_terms)
    view_sql = f"""
    CREATE VIEW offers_enriched AS
    SELECT
       {select_sql},
       cm.cluster_label AS cluster_label,
       cm.top_terms AS cluster_top_terms,
       cm.n_docs AS cluster_n_docs
    FROM offers o
    LEFT JOIN clusters_meta cm
      ON o.cluster = cm.cluster
    """
    con.execute(view_sql)
    con.commit()


def export_csv(con: sqlite3.Connection, out_csv: Path) -> None:
    df = pd.read_sql("SELECT * FROM offers_enriched", con)
    out_csv.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(out_csv, index=False, encoding="utf-8")
    print(f"✅ Export CSV: {out_csv} | rows={len(df)}")


def quick_checks(con: sqlite3.Connection) -> None:
    # 1) how many rows / how many have labels
    df = pd.read_sql(
        """
        SELECT
          COUNT(*) AS n_rows,
          SUM(CASE WHEN cluster IS NOT NULL THEN 1 ELSE 0 END) AS n_clustered,
          SUM(CASE WHEN cluster_label IS NOT NULL AND TRIM(cluster_label) <> '' THEN 1 ELSE 0 END) AS n_labeled
        FROM offers_enriched
        """,
        con,
    )
    print("📦 Checks:", df.iloc[0].to_dict())

    # 2) top clusters
    top = pd.read_sql(
        """
        SELECT cluster, cluster_label, COUNT(*) AS n
        FROM offers_enriched
        WHERE cluster IS NOT NULL
        GROUP BY cluster, cluster_label
        ORDER BY n DESC
        LIMIT 10
        """,
        con,
    )
    print("🏷️ Top clusters:\n", top.to_string(index=False))


def main() -> None:
    ap = argparse.ArgumentParser(description="Finalize SQLite for Streamlit: create offers_enriched view + export.")
    ap.add_argument("--db", required=True, help="Path to offers.sqlite")
    ap.add_argument("--out_csv", default="", help="Optional CSV export path (ex: ../data/offers_enriched.csv)")
    ap.add_argument("--no_export", action="store_true", help="Do not export CSV")
    args = ap.parse_args()

    db_path = Path(args.db)
    if not db_path.exists():
        raise FileNotFoundError(f"DB not found: {db_path}")

    con = sqlite3.connect(str(db_path))
    try:
        # must exist
        cols = table_columns(con, "clusters_meta")
        if not cols:
            raise RuntimeError("clusters_meta introuvable. Lance d'abord load_clusters_meta.py")

        ensure_indexes(con)
        create_view(con)
        quick_checks(con)

        if not args.no_export:
            out_csv = Path(args.out_csv) if args.out_csv else (db_path.parent / "offers_enriched.csv")
            export_csv(con, out_csv)

        print("✅ Done. View created: offers_enriched")

    finally:
        con.close()


if __name__ == "__main__":
    main()
