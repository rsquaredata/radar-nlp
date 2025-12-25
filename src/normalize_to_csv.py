from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple


# --------------------------
# Utils
# --------------------------

def clean_ws(s: Optional[str]) -> Optional[str]:
    if s is None:
        return None
    s = re.sub(r"\s+", " ", str(s)).strip()
    return s or None


def to_iso_date(s: Optional[str]) -> Optional[str]:
    """
    Best effort: if it's already ISO keep, else try parse common formats.
    If parse fails, return as-is.
    """
    s = clean_ws(s)
    if not s:
        return None

    # already ISO-ish
    if re.match(r"^\d{4}-\d{2}-\d{2}", s):
        return s

    # try a few patterns
    for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%d-%m-%Y"):
        try:
            return datetime.strptime(s, fmt).date().isoformat()
        except Exception:
            pass

    return s


def read_jsonl(path: Path) -> Iterable[Dict[str, Any]]:
    """
    Reads JSONL reliably. If user accidentally provided JSON list, handle it too.
    """
    with open(path, "r", encoding="utf-8") as f:
        first = f.read(1)
        f.seek(0)

        # If it's a JSON list
        if first == "[":
            data = json.load(f)
            if isinstance(data, list):
                for obj in data:
                    if isinstance(obj, dict):
                        yield obj
            return

        # Normal JSONL
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
                if isinstance(obj, dict):
                    yield obj
            except Exception:
                continue


def hash_id(*parts: Optional[str]) -> str:
    raw = "||".join([p or "" for p in parts]).encode("utf-8", errors="ignore")
    return hashlib.sha1(raw).hexdigest()


def detect_remote(text: str) -> str:
    """
    Heuristique simple: yes/no/unknown selon présence de mots.
    """
    t = (text or "").lower()

    yes_patterns = [
        r"télétravail",
        r"teletravail",
        r"full remote",
        r"remote\b",
        r"à distance",
        r"travail à distance",
        r"hybride",
        r"home office",
    ]
    no_patterns = [
        r"pas de télétravail",
        r"sans télétravail",
        r"présentiel",
        r"100% présentiel",
    ]

    if any(re.search(p, t) for p in no_patterns):
        return "no"
    if any(re.search(p, t) for p in yes_patterns):
        return "yes"
    return "unknown"


def normalize_contract_type(s: Optional[str]) -> Optional[str]:
    s = clean_ws(s)
    if not s:
        return None
    s_low = s.lower()

    mapping = {
        "cdi": "CDI",
        "cdd": "CDD",
        "stage": "Stage",
        "alternance": "Alternance",
        "interim": "Intérim",
        "intérim": "Intérim",
        "freelance": "Freelance",
        "indépendant": "Indépendant",
        "fonctionnaire": "Fonction publique",
    }

    # if it contains one key
    for k, v in mapping.items():
        if k in s_low:
            return v
    return s


# --------------------------
# Normalized schema
# --------------------------

@dataclass
class NormalizedJob:
    source: str
    source_offer_id: Optional[str]
    url: Optional[str]

    title: Optional[str]
    employer: Optional[str]
    location: Optional[str]

    contract_type: Optional[str]
    salary: Optional[str]
    remote: str  # yes/no/unknown

    published_date: Optional[str]  # iso or raw
    query: Optional[str]           # keyword or query that found it

    raw_text: Optional[str]

    # internal
    normalized_id: str


# --------------------------
# Mappers per source
# --------------------------

def map_france_travail(obj: Dict[str, Any]) -> NormalizedJob:
    source = "france_travail"
    url = clean_ws(obj.get("url"))
    offer_id = clean_ws(obj.get("offer_id"))
    title = clean_ws(obj.get("title"))
    employer = clean_ws(obj.get("company"))
    location = clean_ws(obj.get("location"))
    contract_type = normalize_contract_type(obj.get("contract_type"))
    salary = clean_ws(obj.get("salary"))
    published_date = to_iso_date(obj.get("published_date"))
    query = clean_ws(obj.get("query"))

    # FT sometimes stores raw text in "description"
    raw_text = obj.get("raw_text")
    if not raw_text:
        raw_text = obj.get("description")
    raw_text = clean_ws(raw_text)

    remote = detect_remote(raw_text or "")

    nid = hash_id(source, offer_id, url, title, employer, location)

    return NormalizedJob(
        source=source,
        source_offer_id=offer_id,
        url=url,
        title=title,
        employer=employer,
        location=location,
        contract_type=contract_type,
        salary=salary,
        remote=remote,
        published_date=published_date,
        query=query,
        raw_text=raw_text,
        normalized_id=nid,
    )


def map_hellowork(obj: Dict[str, Any]) -> NormalizedJob:
    source = "hellowork"
    url = clean_ws(obj.get("url"))
    offer_id = clean_ws(obj.get("offer_id"))
    title = clean_ws(obj.get("title"))
    employer = clean_ws(obj.get("employer"))
    location = clean_ws(obj.get("location"))
    contract_type = normalize_contract_type(obj.get("contract_type"))
    salary = clean_ws(obj.get("salary"))
    query = clean_ws(obj.get("query"))  # might not exist
    published_date = to_iso_date(obj.get("published_date"))  # might not exist

    raw_text = clean_ws(obj.get("raw_text"))

    # helloWork has a remote field sometimes
    remote = clean_ws(obj.get("remote"))
    if remote not in ("yes", "no", "unknown"):
        remote = detect_remote(raw_text or "")

    # published_relative exists -> keep in raw_text if you want, but we store in published_date if nothing else
    if not published_date:
        rel = clean_ws(obj.get("published_relative"))
        # keep it as "published_date" if user wants to see it
        published_date = rel

    nid = hash_id(source, offer_id, url, title, employer, location)

    return NormalizedJob(
        source=source,
        source_offer_id=offer_id,
        url=url,
        title=title,
        employer=employer,
        location=location,
        contract_type=contract_type,
        salary=salary,
        remote=remote,
        published_date=published_date,
        query=query,
        raw_text=raw_text,
        normalized_id=nid,
    )


def map_adzuna(obj: Dict[str, Any]) -> NormalizedJob:
    source = "adzuna"
    url = clean_ws(obj.get("url"))
    offer_id = clean_ws(obj.get("offer_id"))
    title = clean_ws(obj.get("title"))
    employer = clean_ws(obj.get("company"))
    location = clean_ws(obj.get("location"))
    contract_type = normalize_contract_type(obj.get("contract_type"))
    salary = clean_ws(obj.get("salary"))
    published_date = to_iso_date(obj.get("published_date"))
    query = clean_ws(obj.get("query"))
    raw_text = clean_ws(obj.get("raw_text"))

    remote = detect_remote(raw_text or "")

    nid = hash_id(source, offer_id, url, title, employer, location)

    return NormalizedJob(
        source=source,
        source_offer_id=offer_id,
        url=url,
        title=title,
        employer=employer,
        location=location,
        contract_type=contract_type,
        salary=salary,
        remote=remote,
        published_date=published_date,
        query=query,
        raw_text=raw_text,
        normalized_id=nid,
    )


# --------------------------
# Pipeline
# --------------------------

def deduplicate(jobs: List[NormalizedJob]) -> List[NormalizedJob]:
    """
    Dedup priority:
    1) same url
    2) else same normalized_id
    Keep first occurrence.
    """
    seen_url = set()
    seen_id = set()
    out: List[NormalizedJob] = []

    for j in jobs:
        u = (j.url or "").strip().lower()
        if u and u in seen_url:
            continue
        if j.normalized_id in seen_id:
            continue

        if u:
            seen_url.add(u)
        seen_id.add(j.normalized_id)
        out.append(j)

    return out


def save_jsonl(jobs: List[NormalizedJob], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        for j in jobs:
            f.write(json.dumps(asdict(j), ensure_ascii=False) + "\n")


def save_csv(jobs: List[NormalizedJob], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    rows = [asdict(j) for j in jobs]

    # avoid huge raw_text in CSV
    for r in rows:
        if r.get("raw_text"):
            r["raw_text"] = str(r["raw_text"])[:4000]

    fieldnames = list(rows[0].keys()) if rows else [f.name for f in NormalizedJob.__dataclass_fields__.values()]
    with open(path, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(rows)


def main() -> None:
    ap = argparse.ArgumentParser(description="Normalize 3 sources to a unified dataset.")
    ap.add_argument("--france_travail", required=True, help="Path to france_travail.jsonl")
    ap.add_argument("--hellowork", required=True, help="Path to hellowork_*.jsonl")
    ap.add_argument("--adzuna", required=True, help="Path to adzuna_*.jsonl")
    ap.add_argument("--out_dir", default="../data", help="Output directory")
    ap.add_argument("--dedup", action="store_true", help="Deduplicate by url/id")
    args = ap.parse_args()

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    jobs: List[NormalizedJob] = []

    # France Travail
    for obj in read_jsonl(Path(args.france_travail)):
        try:
            jobs.append(map_france_travail(obj))
        except Exception:
            continue

    # HelloWork
    for obj in read_jsonl(Path(args.hellowork)):
        try:
            jobs.append(map_hellowork(obj))
        except Exception:
            continue

    # Adzuna
    for obj in read_jsonl(Path(args.adzuna)):
        try:
            jobs.append(map_adzuna(obj))
        except Exception:
            continue

    print(f"[normalize] loaded: {len(jobs)} rows")

    if args.dedup:
        jobs = deduplicate(jobs)
        print(f"[normalize] after dedup: {len(jobs)} rows")

    save_jsonl(jobs, out_dir / "jobs_normalized.jsonl")
    save_csv(jobs, out_dir / "jobs_normalized.csv")

    print(f"✅ saved -> {out_dir / 'jobs_normalized.jsonl'}")
    print(f"✅ saved -> {out_dir / 'jobs_normalized.csv'}")


if __name__ == "__main__":
    main()
