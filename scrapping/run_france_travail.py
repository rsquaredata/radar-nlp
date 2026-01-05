from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List

import pandas as pd

from france_travail_api import FranceTravailClient


OUT_DIR = Path("../data")
OUT_DIR.mkdir(parents=True, exist_ok=True)


def save_jsonl(rows: List[Dict[str, Any]], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")


def save_csv(rows: List[Dict[str, Any]], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        pd.DataFrame([]).to_csv(path, index=False, encoding="utf-8")
        return
    df = pd.DataFrame(rows)
    if "description" in df.columns:
        df["description"] = df["description"].astype(str).str.slice(0, 4000)
    df.to_csv(path, index=False, encoding="utf-8")


def normalize_ft(rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    out = []
    for r in rows:
        out.append(
            {
                "source": r.get("source", "france-travail-api"),
                "offer_id": r.get("offer_id"),
                "url": r.get("url"),
                "title": r.get("title"),
                "company": r.get("company"),
                "location": r.get("location"),
                "published_date": r.get("published_date"),
                "contract_type": r.get("contract_type"),
                "salary": r.get("salary"),
                "query": r.get("query"),
                "description": r.get("description"),
            }
        )
    return out


def main() -> None:
    ft = FranceTravailClient()

    rows = ft.collect_data_ai_offers(
        max_per_query=600,
        chunk=150,
        local_filter=False
    )

    rows = normalize_ft(rows)

    print("France Travail:", len(rows))

    save_jsonl(rows, OUT_DIR / "france_travail.jsonl")
    save_csv(rows, OUT_DIR / "france_travail.csv")

    print("âœ… saved:")
    print(" -", (OUT_DIR / "france_travail.jsonl").resolve())
    print(" -", (OUT_DIR / "france_travail.csv").resolve())


if __name__ == "__main__":
    main()