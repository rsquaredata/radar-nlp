from __future__ import annotations

import argparse
import re
from pathlib import Path
from typing import List, Optional

import pandas as pd


# Petite liste de stopwords FR/EN pour éviter les mots parasites
STOPWORDS = {
    "de", "des", "du", "la", "le", "les", "un", "une", "et", "ou", "en", "dans", "sur", "pour",
    "avec", "sans", "au", "aux", "ce", "cet", "cette", "ces", "vos", "votre", "notre", "nous",
    "you", "your", "the", "a", "an", "to", "in", "on", "for", "with", "and", "or", "of", "as",
    "is", "are", "be", "by", "from"
}


# Liste skills/tools (simple mais efficace) — tu peux l’enrichir
SKILL_PATTERNS = [
    r"\bpython\b",
    r"\bsql\b",
    r"\br\b",
    r"\bscala\b",
    r"\bjava\b",
    r"\bjavascript\b|\bjs\b",
    r"\btypescript\b|\bts\b",
    r"\bpower\s?bi\b",
    r"\btableau\b",
    r"\bexcel\b",
    r"\bairflow\b",
    r"\bdbt\b",
    r"\bspark\b|\bpyspark\b",
    r"\bhadoop\b",
    r"\bkafka\b",
    r"\bdocker\b",
    r"\bkubernetes\b|\bk8s\b",
    r"\bazure\b",
    r"\baws\b",
    r"\bgcp\b|\bgoogle cloud\b",
    r"\bsnowflake\b",
    r"\bbigquery\b",
    r"\bredshift\b",
    r"\bpostgres\b|\bpostgresql\b",
    r"\bmysql\b",
    r"\bmongodb\b",
    r"\belasticsearch\b",
    r"\bml\b|\bmachine learning\b",
    r"\bdeep learning\b",
    r"\bnlp\b",
    r"\bcomputer vision\b",
    r"\bllm\b",
    r"\brag\b",
    r"\btransformers\b",
    r"\bpytorch\b",
    r"\btensorflow\b",
    r"\bscikit[- ]?learn\b",
    r"\bpandas\b",
    r"\bnumpy\b",
    r"\bfastapi\b",
    r"\bstreamlit\b",
]


def pick_existing_col(cols: List[str], candidates: List[str]) -> Optional[str]:
    lower = {c.lower(): c for c in cols}
    for cand in candidates:
        if cand.lower() in lower:
            return lower[cand.lower()]
    return None


def normalize_text(s: str) -> str:
    s = (s or "").lower()
    s = re.sub(r"\s+", " ", s).strip()
    return s


def extract_skills(text: str) -> List[str]:
    t = normalize_text(text)
    found = []
    seen = set()
    for pat in SKILL_PATTERNS:
        if re.search(pat, t, flags=re.IGNORECASE):
            # label propre = pattern simplifié
            label = re.sub(r"\\b|\(|\)|\||\?|\s\?", "", pat)
            label = label.replace("\\", "")
            label = label.replace("[- ]?", "-")
            label = label.replace("s?", "s")
            label = label.strip()
            # quelques normalisations manuelles
            label = label.replace("scikit-learn", "scikit-learn")
            label = label.replace("power bi", "power bi")
            label = label.replace("google cloud", "gcp")
            if label not in seen:
                seen.add(label)
                found.append(label)
    return found


def top_terms(texts: List[str], top_n: int = 20) -> List[str]:
    freq = {}
    for txt in texts:
        t = normalize_text(txt)
        tokens = re.findall(r"[a-zA-ZÀ-ÿ0-9\+\#\-]{2,}", t)
        for tok in tokens:
            tok = tok.strip("-")
            if not tok or tok in STOPWORDS or tok.isdigit():
                continue
            freq[tok] = freq.get(tok, 0) + 1
    return [w for w, _ in sorted(freq.items(), key=lambda x: x[1], reverse=True)[:top_n]]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--in_csv", required=True)
    ap.add_argument("--out_dir", required=True)
    ap.add_argument("--top_terms", type=int, default=20)
    args = ap.parse_args()

    in_path = Path(args.in_csv)
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    df = pd.read_csv(in_path)

    # détecter colonnes
    cluster_col = pick_existing_col(list(df.columns), ["cluster", "cluster_id", "kmeans_cluster", "topic"])
    label_col = pick_existing_col(list(df.columns), ["cluster_label", "label", "name"])
    text_col = pick_existing_col(list(df.columns), ["raw_text", "text", "clean_text", "description"])

    if cluster_col is None:
        raise RuntimeError(f"Colonne cluster introuvable. Colonnes: {df.columns.tolist()}")
    if label_col is None:
        raise RuntimeError(f"Colonne cluster_label introuvable. Colonnes: {df.columns.tolist()}")
    if text_col is None:
        raise RuntimeError(f"Colonne texte introuvable (raw_text/text). Colonnes: {df.columns.tolist()}")

    # extraction par cluster
    rows_skills = []
    rows_terms = []

    for (cid, clabel), g in df.groupby([cluster_col, label_col], dropna=False):
        texts = g[text_col].fillna("").astype(str).tolist()

        # skills
        all_sk = []
        for txt in texts:
            all_sk.extend(extract_skills(txt))

        # comptage
        sk_freq = {}
        for sk in all_sk:
            sk_freq[sk] = sk_freq.get(sk, 0) + 1

        top_sk = sorted(sk_freq.items(), key=lambda x: x[1], reverse=True)[:25]
        for sk, cnt in top_sk:
            rows_skills.append({
                "cluster_id": cid,
                "cluster_label": clabel,
                "skill": sk,
                "count": cnt,
                "share_in_cluster": cnt / max(len(texts), 1)
            })

        # top terms (mots fréquents)
        tterms = top_terms(texts, top_n=args.top_terms)
        rows_terms.append({
            "cluster_id": cid,
            "cluster_label": clabel,
            "n_docs": len(texts),
            "top_terms": ", ".join(tterms)
        })

    out_skills = out_dir / "skills_by_cluster.csv"
    out_terms = out_dir / "top_terms_by_cluster.csv"

    pd.DataFrame(rows_skills).to_csv(out_skills, index=False, encoding="utf-8")
    pd.DataFrame(rows_terms).to_csv(out_terms, index=False, encoding="utf-8")

    print(f"✅ Saved: {out_skills}")
    print(f"✅ Saved: {out_terms}")


if __name__ == "__main__":
    main()
