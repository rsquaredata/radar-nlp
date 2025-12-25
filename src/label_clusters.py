from __future__ import annotations

import argparse
import json
import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer


# -----------------------------
# Utils
# -----------------------------
def clean_ws(s: str) -> str:
    return re.sub(r"\s+", " ", (s or "")).strip()


def safe_lower(s: Optional[str]) -> str:
    return (s or "").strip().lower()


def guess_text_column(df: pd.DataFrame) -> str:
    # on supporte plusieurs noms possibles
    for c in ["text", "raw_text", "content", "description", "full_text"]:
        if c in df.columns:
            return c
    raise RuntimeError(
        "Impossible de trouver une colonne texte. Colonnes attendues: text/raw_text/content/description/full_text"
    )


def guess_cluster_column(df: pd.DataFrame) -> str:
    for c in ["cluster", "cluster_id", "kmeans_cluster", "label", "topic"]:
        if c in df.columns:
            return c
    raise RuntimeError(
        "Impossible de trouver une colonne cluster. Colonnes attendues: cluster/cluster_id/kmeans_cluster/label/topic"
    )


# -----------------------------
# Read meta_json (robuste)
# -----------------------------
def parse_meta_json(meta: Any) -> Dict[int, List[str]]:
    """
    Essaie d'extraire {cluster_id: [top_terms]} depuis différents formats possibles.

    Supporte notamment:
    - {"clusters": {"0": ["term1", ...], "1": [...]}}
    - {"top_terms": {"0": ["..."]}}
    - {"cluster_top_terms": {...}}
    - {"0": ["..."], "1": ["..."]}  (dict direct)
    - [{"cluster":0,"top_terms":[...]}, ...]  (list d'objets)
    - {"k":25, "clusters":[{"id":0,"terms":[...]} ...]}
    """
    clusters: Dict[int, List[str]] = {}

    if meta is None:
        return clusters

    # Case 1: dict
    if isinstance(meta, dict):
        # dict direct {"0":[...]}
        if all(re.fullmatch(r"\d+", str(k)) for k in meta.keys()):
            for k, v in meta.items():
                cid = int(k)
                if isinstance(v, list):
                    clusters[cid] = [clean_ws(str(x)) for x in v if clean_ws(str(x))]
            return clusters

        # nested common keys
        for key in ["clusters", "top_terms", "cluster_top_terms", "clusters_top_terms", "terms_by_cluster"]:
            if key in meta and isinstance(meta[key], dict):
                return parse_meta_json(meta[key])

        # list-like clusters inside dict
        for key in ["clusters", "items", "data"]:
            if key in meta and isinstance(meta[key], list):
                return parse_meta_json(meta[key])

        return clusters

    # Case 2: list
    if isinstance(meta, list):
        for obj in meta:
            if not isinstance(obj, dict):
                continue
            # cluster id keys
            cid = None
            for k in ["cluster", "cluster_id", "id", "k"]:
                if k in obj:
                    try:
                        cid = int(obj[k])
                        break
                    except Exception:
                        pass
            if cid is None:
                continue

            # terms keys
            terms = None
            for tk in ["top_terms", "terms", "keywords", "words"]:
                if tk in obj and isinstance(obj[tk], list):
                    terms = obj[tk]
                    break
            if terms:
                clusters[cid] = [clean_ws(str(x)) for x in terms if clean_ws(str(x))]
        return clusters

    return clusters


# -----------------------------
# Recompute top terms from clustered CSV
# -----------------------------
def compute_top_terms_by_cluster(
    df: pd.DataFrame,
    cluster_col: str,
    text_col: str,
    top_n: int = 20,
    max_features: int = 80000,
    ngram_max: int = 2,
) -> Dict[int, List[str]]:
    texts = df[text_col].astype(str).fillna("")
    clusters = df[cluster_col].astype(int)

    vec = TfidfVectorizer(
        max_features=max_features,
        ngram_range=(1, ngram_max),
        stop_words="english",  # on ajoute un stoplist FR ci-dessous via pre-clean
        lowercase=True,
    )

    # mini-clean FR+EN : enlève tokens courts + chiffres
    cleaned = texts.apply(lambda s: re.sub(r"\b\d+\b", " ", safe_lower(s)))
    X = vec.fit_transform(cleaned)

    feature_names = vec.get_feature_names_out()

    top_terms: Dict[int, List[str]] = {}
    for cid in sorted(clusters.unique()):
        idx = (clusters == cid).to_numpy().nonzero()[0]
        if len(idx) == 0:
            top_terms[cid] = []
            continue
        # moyenne TF-IDF sur les docs du cluster
        mean_vec = X[idx].mean(axis=0)
        mean_arr = mean_vec.A1
        top_idx = mean_arr.argsort()[-top_n:][::-1]
        terms = [feature_names[i] for i in top_idx if mean_arr[i] > 0]
        top_terms[int(cid)] = terms

    return top_terms


# -----------------------------
# Labeling (rule-based + scoring)
# -----------------------------
LABEL_RULES: Dict[str, List[str]] = {
    "Data Scientist / ML": [
        "data scientist", "machine learning", "ml", "deep learning", "model", "classification",
        "regression", "feature", "tensorflow", "pytorch", "sklearn", "scikit", "xgboost",
        "nlp", "computer vision", "cv", "embedding"
    ],
    "Data Analyst / BI": [
        "data analyst", "bi", "business intelligence", "dashboard", "reporting", "power bi",
        "tableau", "qlik", "kpi", "excel", "analytics", "visualisation", "dataviz"
    ],
    "Data Engineer": [
        "data engineer", "etl", "elt", "pipeline", "airflow", "dbt", "spark", "hadoop",
        "kafka", "databricks", "bigquery", "snowflake", "redshift", "lakehouse", "ingestion"
    ],
    "Cloud / DevOps Data": [
        "aws", "azure", "gcp", "kubernetes", "docker", "terraform", "ci/cd", "devops",
        "serverless", "lambda", "cloud"
    ],
    "LLM / GenAI / RAG": [
        "llm", "rag", "retrieval", "prompt", "transformers", "langchain", "vector",
        "embedding", "chatgpt", "openai", "mistral", "gpt", "fine-tuning"
    ],
    "Quant / Finance": [
        "quant", "pricing", "risk", "trading", "portfolio", "market", "volatility",
        "credit", "fintech", "actuary", "actuarial"
    ],
    "Data Architecture": [
        "data architect", "architecture", "data model", "warehouse", "data warehouse",
        "dimensional", "star schema", "governance", "catalog", "master data", "mdm"
    ],
    "Software / Backend (data-related)": [
        "backend", "api", "microservice", "python", "java", "golang", "node", "typescript",
        "sql", "postgres", "mysql", "mongodb"
    ],
}


def score_label(terms: List[str], text_blob: str) -> Tuple[str, Dict[str, int]]:
    """
    Score chaque label via occurrences dans:
    - top terms
    - un blob (title+text extrait du cluster)
    """
    tset = [safe_lower(t) for t in terms]
    blob = safe_lower(text_blob)

    scores: Dict[str, int] = {}
    for label, hints in LABEL_RULES.items():
        s = 0
        for h in hints:
            h2 = safe_lower(h)
            # poids +2 si match dans top_terms, +1 si match dans blob
            if any(h2 in tt for tt in tset):
                s += 2
            if h2 in blob:
                s += 1
        scores[label] = s

    best = max(scores.items(), key=lambda x: x[1])
    if best[1] <= 0:
        return "Other / Mixed", scores
    return best[0], scores


def build_cluster_blob(
    df: pd.DataFrame,
    cluster_col: str,
    text_col: str,
    title_col: Optional[str] = None,
    per_cluster_max_docs: int = 200,
) -> Dict[int, str]:
    blobs: Dict[int, str] = {}
    for cid, g in df.groupby(cluster_col):
        sample = g.head(per_cluster_max_docs)
        parts = []
        if title_col and title_col in sample.columns:
            parts.append(" ".join(sample[title_col].astype(str).fillna("").tolist()))
        parts.append(" ".join(sample[text_col].astype(str).fillna("").tolist()))
        blobs[int(cid)] = clean_ws(" ".join(parts))[:200000]  # limite
    return blobs


# -----------------------------
# Main
# -----------------------------
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--meta_json", required=True)
    ap.add_argument("--clustered_csv", required=True)
    ap.add_argument("--out_csv", required=True)

    ap.add_argument("--top_n", type=int, default=20)
    ap.add_argument("--ngram_max", type=int, default=2)
    ap.add_argument("--max_features", type=int, default=80000)

    ap.add_argument("--out_labeled_csv", default=None, help="Optionnel: clustered csv + cluster_label")

    args = ap.parse_args()

    clustered_path = Path(args.clustered_csv)
    meta_path = Path(args.meta_json)
    out_path = Path(args.out_csv)

    df = pd.read_csv(clustered_path)
    cluster_col = guess_cluster_column(df)
    text_col = guess_text_column(df)
    title_col = "title" if "title" in df.columns else None

    # 1) meta_json -> clusters terms
    meta_obj = None
    try:
        with open(meta_path, "r", encoding="utf-8") as f:
            meta_obj = json.load(f)
    except Exception:
        meta_obj = None

    cluster_terms = parse_meta_json(meta_obj)

    # 2) fallback: compute top terms if empty
    if not cluster_terms:
        print("⚠️ meta_json non exploitable -> recalcul des top_terms depuis clustered_csv")
        cluster_terms = compute_top_terms_by_cluster(
            df,
            cluster_col=cluster_col,
            text_col=text_col,
            top_n=args.top_n,
            max_features=args.max_features,
            ngram_max=args.ngram_max,
        )

    # 3) build blobs for scoring
    blobs = build_cluster_blob(df, cluster_col=cluster_col, text_col=text_col, title_col=title_col)

    # 4) label each cluster
    rows = []
    for cid in sorted(cluster_terms.keys()):
        terms = cluster_terms.get(cid, [])[: args.top_n]
        blob = blobs.get(cid, "")
        label, scores = score_label(terms, blob)

        rows.append(
            {
                "cluster": cid,
                "cluster_label": label,
                "top_terms": ", ".join(terms),
                "score_debug": json.dumps(scores, ensure_ascii=False),
                "n_docs": int((df[cluster_col].astype(int) == int(cid)).sum()),
            }
        )

    out_path.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(rows).sort_values("cluster").to_csv(out_path, index=False, encoding="utf-8")
    print(f"✅ Saved labels: {out_path} | clusters={len(rows)}")

    # 5) optional: write labeled clustered csv
    if args.out_labeled_csv:
        labels_map = {r["cluster"]: r["cluster_label"] for r in rows}
        df["cluster_label"] = df[cluster_col].astype(int).map(labels_map)
        out2 = Path(args.out_labeled_csv)
        out2.parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(out2, index=False, encoding="utf-8")
        print(f"✅ Saved clustered labeled CSV: {out2}")


if __name__ == "__main__":
    main()
