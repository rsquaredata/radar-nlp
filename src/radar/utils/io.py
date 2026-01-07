import json
import pandas as pd
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

def save_jsonl(rows: List[Dict[str, Any]], path: Path) -> None:
    if not rows:
        logger.warning(f"Aucune donnée à sauvegarder dans {path}")
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    logger.info(f"Sauvegarde réussie : {len(rows)} lignes dans {path}")

def save_csv(rows: List[Dict[str, Any]], path: Path, limit_description: Optional[int] = 4000) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        pd.DataFrame([]).to_csv(path, index=False, encoding="utf-8")
        return
    df = pd.DataFrame(rows)
    if limit_description and "description" in df.columns:
        df["description"] = df["description"].astype(str).str.slice(0, limit_description)
    df.to_csv(path, index=False, encoding="utf-8")
    logger.info(f"Sauvegarde CSV réussie : {path}")

def load_jsonl(path: Path) -> List[Dict[str, Any]]:
    if not path.exists(): return []
    with open(path, "r", encoding="utf-8") as f:
        return [json.loads(line) for line in f]