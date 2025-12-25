from pathlib import Path
import json
import pandas as pd
from adzuna_api import collect_adzuna_data_ia

OUT_DIR = Path("../data")
OUT_DIR.mkdir(exist_ok=True)

def save_jsonl(rows, path):
    with open(path, "w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")

def save_csv(rows, path):
    df = pd.DataFrame(rows)
    df["raw_text"] = df["raw_text"].astype(str).str.slice(0, 4000)
    df.to_csv(path, index=False)

def main():
    rows = collect_adzuna_data_ia(max_pages=40)
    print("ADZUNA France:", len(rows))
    save_jsonl(rows, OUT_DIR / "adzuna_fr_data_ia.jsonl")
    save_csv(rows, OUT_DIR / "adzuna_fr_data_ia.csv")

if __name__ == "__main__":
    main()
