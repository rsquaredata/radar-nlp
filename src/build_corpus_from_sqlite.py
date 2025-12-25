from __future__ import annotations

import argparse
import sqlite3
from pathlib import Path

import pandas as pd


def detect_table_and_text_column(con: sqlite3.Connection, table: str | None):
    # Auto-detect table if not provided
    if table is None:
        tables = pd.read_sql_query(
            "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;",
            con,
        )["name"].tolist()
        if not tables:
            raise RuntimeError("Aucune table trouvée dans la base SQLite.")
        # Prefer 'offers' if it exists
        table = "offers" if "offers" in tables else tables[0]

    cols = pd.read_sql_query(f"PRAGMA table_info({table});", con)["name"].tolist()
    if "raw_text" in cols:
        text_col = "raw_text"
    elif "description" in cols:
        text_col = "description"
    elif "text" in cols:
        text_col = "text"
    else:
        raise RuntimeError(
            f"Impossible de trouver une colonne texte dans '{table}'. "
            f"Colonnes disponibles: {cols}"
        )

    return table, cols, text_col


def main():
    ap = argparse.ArgumentParser(description="Build NLP corpus from SQLite offers DB.")
    ap.add_argument("--db", required=True, help="Chemin vers offers.sqlite")
    ap.add_argument("--table", default=None, help="Nom de table (par défaut auto-detect)")
    ap.add_argument("--out_dir", default="../data", help="Dossier de sortie")
    ap.add_argument("--limit", type=int, default=0, help="0 = tout, sinon limite")
    ap.add_argument("--min_len", type=int, default=200, help="Filtrer textes trop courts")
    ap.add_argument("--where", default="", help="Clause SQL WHERE sans le mot WHERE (optionnel)")
    args = ap.parse_args()

    db_path = Path(args.db)
    if not db_path.exists():
        raise FileNotFoundError(f"DB introuvable: {db_path}")

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    con = sqlite3.connect(str(db_path))

    table, cols, text_col = detect_table_and_text_column(con, args.table)

    # Choix des colonnes utiles si elles existent
    wanted = ["uid", "source", "site", "url", "title", "employer", "location", "date", "published_date", text_col]
    select_cols = [c for c in wanted if c in cols]

    if not select_cols:
        raise RuntimeError(f"Aucune colonne sélectionnable dans {table} (cols={cols})")

    sql = f"SELECT {', '.join(select_cols)} FROM {table}"
    if args.where.strip():
        sql += f" WHERE {args.where.strip()}"
    if args.limit and args.limit > 0:
        sql += f" LIMIT {args.limit}"

    df = pd.read_sql_query(sql, con)
    con.close()

    # Nettoyage minimal du corpus (sans NLP ici): enlever NaN, filtrer texte trop court
    df[text_col] = df[text_col].fillna("").astype(str)
    df["text_len"] = df[text_col].str.len()
    df = df[df["text_len"] >= args.min_len].copy()

    # Normaliser le nom de la colonne texte -> raw_text (pour la suite du pipeline)
    if text_col != "raw_text":
        df.rename(columns={text_col: "raw_text"}, inplace=True)

    # Export
    out_csv = out_dir / "corpus_raw.csv"
    out_jsonl = out_dir / "corpus_raw.jsonl"

    df.to_csv(out_csv, index=False, encoding="utf-8")
    df.to_json(out_jsonl, orient="records", lines=True, force_ascii=False)

    print(f"✅ Table utilisée: {table}")
    print(f"✅ Corpus construit: {len(df)} documents")
    print(f"✅ Export CSV : {out_csv}")
    print(f"✅ Export JSONL: {out_jsonl}")


if __name__ == "__main__":
    main()
