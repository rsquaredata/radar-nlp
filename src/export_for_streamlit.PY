from __future__ import annotations

import argparse
import sqlite3
import pandas as pd


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--db", required=True)
    ap.add_argument("--out_csv", required=True)
    ap.add_argument("--where", default="", help="Optionnel: clause WHERE sans le mot WHERE")
    args = ap.parse_args()

    con = sqlite3.connect(args.db)

    base_query = """
    SELECT
        uid, source, offer_id, url, title, employer,
        location, city, postcode, dept_code, region,
        contract_type, salary, remote, published_date, seniority,
        lat, lon, geo_score, geo_source,
        raw_text, created_at
    FROM offers
    """

    if args.where.strip():
        q = base_query + " WHERE " + args.where
    else:
        q = base_query

    df = pd.read_sql(q, con)
    con.close()

    df.to_csv(args.out_csv, index=False, encoding="utf-8")
    print(f"✅ Exported {len(df)} rows -> {args.out_csv}")


if __name__ == "__main__":
    main()
