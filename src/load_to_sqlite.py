from __future__ import annotations

import argparse
import hashlib
import re
import sqlite3
from pathlib import Path
from typing import Optional

import pandas as pd


NAN_LIKE = {"nan", "none", "null", "nat", ""}


def norm_ws(x: object) -> str:
    """Normalize whitespace + convert NaN/None/'nan' to empty string."""
    if x is None:
        return ""
    # pandas NaN
    try:
        if pd.isna(x):
            return ""
    except Exception:
        pass
    s = str(x)
    s = re.sub(r"\s+", " ", s).strip()
    if s.lower() in NAN_LIKE:
        return ""
    return s


def sha1(s: str) -> str:
    return hashlib.sha1(s.encode("utf-8")).hexdigest()


def make_uid(source: str, url: str, offer_id: str, title: str, employer: str, location: str) -> str:
    """
    UID stable pour dédup:
    1) source + offer_id si offer_id existe
    2) source + url si url existe
    3) hash(source + title + employer + location) sinon
    """
    source = norm_ws(source).lower()
    url = norm_ws(url)
    offer_id = norm_ws(offer_id)
    title = norm_ws(title).lower()
    employer = norm_ws(employer).lower()
    location = norm_ws(location).lower()

    if offer_id:
        return sha1(f"{source}::id::{offer_id}")
    if url:
        return sha1(f"{source}::url::{url}")
    # fallback content-based
    return sha1(f"{source}::te::{title}::{employer}::{location}")


def create_schema(conn: sqlite3.Connection) -> None:
    conn.execute("""
    CREATE TABLE IF NOT EXISTS offers (
        uid TEXT PRIMARY KEY,
        source TEXT,
        offer_id TEXT,
        url TEXT,
        title TEXT,
        employer TEXT,
        location TEXT,
        contract_type TEXT,
        salary TEXT,
        remote TEXT,
        published_date TEXT,
        published_relative TEXT,
        seniority TEXT,
        raw_text TEXT,
        created_at TEXT DEFAULT (datetime('now'))
    );
    """)

    conn.execute("CREATE INDEX IF NOT EXISTS idx_offers_source ON offers(source);")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_offers_location ON offers(location);")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_offers_employer ON offers(employer);")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_offers_date ON offers(published_date);")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_offers_url ON offers(url);")


def upsert_offers(conn: sqlite3.Connection, df: pd.DataFrame, batch: int = 1000) -> int:
    cols = [
        "uid", "source", "offer_id", "url", "title", "employer",
        "location", "contract_type", "salary", "remote",
        "published_date", "published_relative", "seniority", "raw_text"
    ]
    for c in cols:
        if c not in df.columns:
            df[c] = ""

    df = df[cols].copy()

    sql = """
    INSERT INTO offers (
        uid, source, offer_id, url, title, employer,
        location, contract_type, salary, remote,
        published_date, published_relative, seniority, raw_text
    ) VALUES (
        :uid, :source, :offer_id, :url, :title, :employer,
        :location, :contract_type, :salary, :remote,
        :published_date, :published_relative, :seniority, :raw_text
    )
    ON CONFLICT(uid) DO UPDATE SET
        source=excluded.source,
        offer_id=excluded.offer_id,
        url=excluded.url,
        title=excluded.title,
        employer=excluded.employer,
        location=excluded.location,
        contract_type=excluded.contract_type,
        salary=excluded.salary,
        remote=excluded.remote,
        published_date=excluded.published_date,
        published_relative=excluded.published_relative,
        seniority=excluded.seniority,
        raw_text=excluded.raw_text;
    """

    records = df.to_dict(orient="records")
    for i in range(0, len(records), batch):
        conn.executemany(sql, records[i:i + batch])

    return len(records)


def main() -> None:
    ap = argparse.ArgumentParser(description="Load normalized offers CSV into SQLite.")
    ap.add_argument("--csv", required=True, help="Chemin vers le CSV normalisé")
    ap.add_argument("--db", default="../data/offers.sqlite", help="Chemin DB SQLite")
    ap.add_argument("--recreate", action="store_true", help="Supprime la table offers avant import")
    args = ap.parse_args()

    csv_path = Path(args.csv)
    if not csv_path.exists():
        raise FileNotFoundError(csv_path)

    db_path = Path(args.db)
    db_path.parent.mkdir(parents=True, exist_ok=True)

    df = pd.read_csv(csv_path)

    # normaliser colonnes attendues
    for c in [
        "source", "url", "offer_id", "title", "employer", "location",
        "contract_type", "salary", "remote", "published_date",
        "published_relative", "seniority", "raw_text"
    ]:
        if c not in df.columns:
            df[c] = ""
        df[c] = df[c].map(norm_ws)

    # UID robuste
    df["uid"] = df.apply(
        lambda r: make_uid(
            r.get("source", ""),
            r.get("url", ""),
            r.get("offer_id", ""),
            r.get("title", ""),
            r.get("employer", ""),
            r.get("location", ""),
        ),
        axis=1,
    )

    with sqlite3.connect(db_path) as conn:
        conn.execute("PRAGMA journal_mode=WAL;")
        conn.execute("PRAGMA synchronous=NORMAL;")
        conn.execute("PRAGMA temp_store=MEMORY;")

        create_schema(conn)

        if args.recreate:
            conn.execute("DROP TABLE IF EXISTS offers;")
            conn.commit()
            create_schema(conn)

        n = upsert_offers(conn, df)
        conn.commit()

        total = conn.execute("SELECT COUNT(*) FROM offers;").fetchone()[0]
        distinct_uid = conn.execute("SELECT COUNT(DISTINCT uid) FROM offers;").fetchone()[0]
        distinct_url = conn.execute("SELECT COUNT(DISTINCT url) FROM offers WHERE url<>'';").fetchone()[0]

    print(f"✅ Upsert attempted: {n} rows -> {db_path}")
    print(f"📦 Total rows in DB: {total}")
    print(f"🆔 Distinct uid: {distinct_uid}")
    print(f"🔗 Distinct urls (non-empty): {distinct_url}")


if __name__ == "__main__":
    main()
