from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import pandas as pd


def load_meta_top_terms(meta_json: Optional[str]) -> Dict[int, List[str]]:
    """
    Supporte plusieurs formats possibles:
      A) {"0": ["term1",...], "1":[...]}
      B) {"clusters": {"0": {...}, "1": {...}}}
      C) [{"cluster":0, "top_terms":[...]}, ...]
      D) {"0": [{"term":"x","score":...}, ...], ...}
    Retourne: {cluster_id: [term,...]}
    """
    if not meta_json:
        return {}

    path = Path(meta_json)
    if not path.exists():
        return {}

    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}

    def normalize_terms(x: Any) -> List[str]:
        if x is None:
            return []
        if isinstance(x, list):
            out = []
            for it in x:
                if isinstance(it, str):
                    out.append(it)
                elif isinstance(it, dict):
                    # dict style: {"term": "..."} or {"ngram":"..."}
                    for k in ("term", "ngram", "token", "word"):
                        if k in it and isinstance(it[k], str):
                            out.append(it[k])
                            break
            return out
        if isinstance(x, dict):
            # maybe {"term":score,...}
            out = []
            for k, v in x.items():
                if isinstance(k, str):
                    out.append(k)
            return out
        return []

    out: Dict[int, List[str]] = {}

    # A) direct dict mapping
    if isinstance(data, dict):
        if "clusters" in data and isinstance(data["clusters"], dict):
            data = data["clusters"]

        # try dict of cluster -> terms
        all_keys = list(data.keys())
        # if keys look like integers, we treat as clusters
        if all(isinstance(k, str) and k.strip("-").isdigit() for k in all_keys):
            for k, v in data.items():
                try:
                    cid = int(k)
                except Exception:
                    continue

                # v can be list[str] or dict containing "top_terms"
                if isinstance(v, dict):
                    terms = normalize_terms(
                        v.get("top_terms")
                        or v.get("terms")
                        or v.get("top")
                        or v.get("keywords")
                        or v
                    )
                else:
                    terms = normalize_terms(v)

                out[cid] = [t for t in terms if isinstance(t, str)][:30]
            return out

        # B) maybe already in another structure
        if "top_terms" in data and isinstance(data["top_terms"], dict):
            for k, v in data["top_terms"].items():
                if str(k).strip("-").isdigit():
                    out[int(k)] = normalize_terms(v)[:30]
            return out

    # C) list of objects
    if isinstance(data, list):
        for obj in data:
            if not isinstance(obj, dict):
                continue
            cid = obj.get("cluster") or obj.get("cluster_id") or obj.get("id")
            if cid is None:
                continue
            try:
                cid = int(cid)
            except Exception:
                continue
            terms = normalize_terms(
                obj.get("top_terms")
                or obj.get("terms")
                or obj.get("keywords")
                or obj.get("top")
            )
            out[cid] = terms[:30]
        return out

    return {}


def pick_col(df: pd.DataFrame, candidates: List[str]) -> Optional[str]:
    for c in candidates:
        if c in df.columns:
            return c
    return None


def top_sources(series: pd.Series, topn: int = 3) -> str:
    if series is None or series.empty:
        return ""
    vc = series.fillna("").astype(str)
    vc = vc[vc != ""]
    if vc.empty:
        return ""
    counts = vc.value_counts().head(topn)
    total = counts.sum()
    parts = []
    for k, v in counts.items():
        pct = 100.0 * v / max(1, vc.shape[0])
        parts.append(f"{k} ({v}, {pct:.1f}%)")
    return " | ".join(parts)


def safe_str(x: Any) -> str:
    if x is None:
        return ""
    s = str(x).strip()
    return s


def build_markdown_report(
    quality_df: pd.DataFrame,
    examples_df: pd.DataFrame,
    top_terms: Dict[int, List[str]],
    out_path: Path,
    examples_per_cluster: int = 6,
) -> None:
    lines: List[str] = []
    lines.append("# Cluster Quality Report\n")
    lines.append("## Summary table\n")
    # markdown table
    table_cols = [
        "cluster",
        "label",
        "n_offers",
        "share_pct",
        "dominant_sources",
        "avg_text_len",
        "has_title_pct",
        "has_location_pct",
        "has_company_pct",
        "unique_urls",
    ]
    show = quality_df[table_cols].copy()
    lines.append(show.to_markdown(index=False))
    lines.append("\n")

    lines.append("## Per-cluster details\n")
    for _, row in quality_df.sort_values("cluster").iterrows():
        cid = int(row["cluster"])
        label = safe_str(row.get("label"))
        lines.append(f"### Cluster {cid} — {label}\n")
        lines.append(f"- Offers: **{int(row['n_offers'])}** ({row['share_pct']:.2f}%)")
        lines.append(f"- Dominant sources: {safe_str(row.get('dominant_sources'))}")
        lines.append(f"- Avg text length: {int(row.get('avg_text_len', 0))}")
        lines.append(
            f"- Coverage: title={row.get('has_title_pct', 0):.1f}%, "
            f"company={row.get('has_company_pct', 0):.1f}%, "
            f"location={row.get('has_location_pct', 0):.1f}%"
        )
        lines.append(f"- Unique URLs: {int(row.get('unique_urls', 0))}")

        terms = top_terms.get(cid) or []
        if terms:
            lines.append("\n**Top terms**: " + ", ".join(terms[:20]))
        else:
            lines.append("\n**Top terms**: (none)")

        # examples
        ex = examples_df[examples_df["cluster"] == cid].head(examples_per_cluster)
        if not ex.empty:
            lines.append("\n**Examples**:\n")
            for _, exr in ex.iterrows():
                title = safe_str(exr.get("title"))
                company = safe_str(exr.get("employer"))
                loc = safe_str(exr.get("location"))
                url = safe_str(exr.get("url"))
                src = safe_str(exr.get("source"))
                lines.append(f"- [{src}] {title} — {company} — {loc} — {url}")
        lines.append("\n---\n")

    out_path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    ap = argparse.ArgumentParser(description="Evaluate cluster quality and export reports.")
    ap.add_argument("--clustered_csv", required=True, help="CSV produced by cluster_tfidf_kmeans.py (e.g., clustered_k25.csv)")
    ap.add_argument("--labels_csv", required=False, help="CSV produced by label_clusters.py (e.g., clusters_labels_k25.csv)")
    ap.add_argument("--meta_json", required=False, help="JSON produced by cluster_tfidf_kmeans.py (e.g., clusters_k25_top_terms.json)")
    ap.add_argument("--out_dir", required=True, help="Output directory")
    ap.add_argument("--examples_per_cluster", type=int, default=6)
    args = ap.parse_args()

    clustered_path = Path(args.clustered_csv)
    if not clustered_path.exists():
        raise FileNotFoundError(f"clustered_csv not found: {clustered_path}")

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    df = pd.read_csv(clustered_path)

    # detect key columns
    cluster_col = pick_col(df, ["cluster", "cluster_id", "kmeans_cluster"])
    if not cluster_col:
        raise RuntimeError("Cannot find cluster column. Expected one of: cluster, cluster_id, kmeans_cluster.")

    url_col = pick_col(df, ["url", "offer_url", "link"])
    source_col = pick_col(df, ["source", "site", "origin"])
    title_col = pick_col(df, ["title", "job_title", "position"])
    company_col = pick_col(df, ["employer", "company", "hiring_organization"])
    location_col = pick_col(df, ["location", "city", "region"])
    text_col = pick_col(df, ["text", "raw_text", "description", "content"])

    # load labels if provided
    labels_map: Dict[int, str] = {}
    if args.labels_csv:
        lp = Path(args.labels_csv)
        if lp.exists():
            ldf = pd.read_csv(lp)
            # support columns: cluster, label OR cluster_id, cluster_label
            ccol = pick_col(ldf, ["cluster", "cluster_id"])
            lcol = pick_col(ldf, ["label", "cluster_label", "name"])
            if ccol and lcol:
                for _, r in ldf.iterrows():
                    try:
                        labels_map[int(r[ccol])] = safe_str(r[lcol])
                    except Exception:
                        pass

    # meta top terms
    top_terms = load_meta_top_terms(args.meta_json)

    # compute quality stats per cluster
    df["_cluster"] = df[cluster_col].astype(int)
    n_total = len(df)

    def pct_has(col: Optional[str]) -> pd.Series:
        if not col:
            return pd.Series([0.0] * (df["_cluster"].nunique()), index=sorted(df["_cluster"].unique()))
        x = df[col].fillna("").astype(str).str.strip()
        return df.assign(_has=(x != "")).groupby("_cluster")["_has"].mean() * 100.0

    has_title = pct_has(title_col)
    has_company = pct_has(company_col)
    has_location = pct_has(location_col)

    avg_text_len = None
    if text_col:
        tl = df[text_col].fillna("").astype(str).map(len)
        avg_text_len = df.assign(_len=tl).groupby("_cluster")["_len"].mean()
    else:
        avg_text_len = pd.Series([0.0] * df["_cluster"].nunique(), index=sorted(df["_cluster"].unique()))

    unique_urls = None
    if url_col:
        unique_urls = df.groupby("_cluster")[url_col].nunique(dropna=True)
    else:
        unique_urls = df.groupby("_cluster").size() * 0

    dominant_sources = None
    if source_col:
        dominant_sources = df.groupby("_cluster")[source_col].apply(lambda s: top_sources(s, topn=3))
    else:
        dominant_sources = df.groupby("_cluster").size().map(lambda _: "")

    counts = df["_cluster"].value_counts().sort_index()

    quality = pd.DataFrame({
        "cluster": counts.index.astype(int),
        "n_offers": counts.values.astype(int),
    })
    quality["share_pct"] = quality["n_offers"] * 100.0 / max(1, n_total)
    quality["label"] = quality["cluster"].map(lambda c: labels_map.get(int(c), f"cluster_{int(c)}"))
    quality["dominant_sources"] = quality["cluster"].map(lambda c: dominant_sources.get(int(c), "") if dominant_sources is not None else "")
    quality["avg_text_len"] = quality["cluster"].map(lambda c: float(avg_text_len.get(int(c), 0.0)))
    quality["has_title_pct"] = quality["cluster"].map(lambda c: float(has_title.get(int(c), 0.0)))
    quality["has_company_pct"] = quality["cluster"].map(lambda c: float(has_company.get(int(c), 0.0)))
    quality["has_location_pct"] = quality["cluster"].map(lambda c: float(has_location.get(int(c), 0.0)))
    quality["unique_urls"] = quality["cluster"].map(lambda c: int(unique_urls.get(int(c), 0)) if unique_urls is not None else 0)

    # examples: pick varied rows per cluster (prefer rows with title+url)
    ex_cols = ["cluster"]
    for col in [source_col, url_col, title_col, company_col, location_col]:
        if col:
            ex_cols.append(col)
    ex_df = df.copy()
    ex_df["cluster"] = ex_df["_cluster"]

    # rank rows to pick best examples
    score = pd.Series([0] * len(ex_df))
    if title_col:
        score += (ex_df[title_col].fillna("").astype(str).str.strip() != "").astype(int)
    if url_col:
        score += (ex_df[url_col].fillna("").astype(str).str.strip() != "").astype(int)
    if company_col:
        score += (ex_df[company_col].fillna("").astype(str).str.strip() != "").astype(int)
    if location_col:
        score += (ex_df[location_col].fillna("").astype(str).str.strip() != "").astype(int)
    ex_df["_score"] = score

    examples = (
        ex_df.sort_values(["cluster", "_score"], ascending=[True, False])
            .groupby("cluster", as_index=False)
            .head(args.examples_per_cluster)
    )

    # rename to canonical names in output
    rename_map = {}
    if source_col and source_col != "source":
        rename_map[source_col] = "source"
    if url_col and url_col != "url":
        rename_map[url_col] = "url"
    if title_col and title_col != "title":
        rename_map[title_col] = "title"
    if company_col and company_col != "employer":
        rename_map[company_col] = "employer"
    if location_col and location_col != "location":
        rename_map[location_col] = "location"

    examples_out = examples[["cluster"] + [c for c in ex_cols if c != "cluster"]].rename(columns=rename_map)
    quality_out = quality.sort_values("cluster")

    # save outputs
    quality_csv = out_dir / "clusters_quality.csv"
    examples_csv = out_dir / "clusters_examples_per_cluster.csv"
    report_md = out_dir / "clusters_quality_report.md"

    quality_out.to_csv(quality_csv, index=False, encoding="utf-8")
    examples_out.to_csv(examples_csv, index=False, encoding="utf-8")

    build_markdown_report(
        quality_df=quality_out,
        examples_df=examples_out,
        top_terms=top_terms,
        out_path=report_md,
        examples_per_cluster=args.examples_per_cluster,
    )

    print(f"✅ Saved: {quality_csv}")
    print(f"✅ Saved: {examples_csv}")
    print(f"✅ Saved: {report_md}")
    print(f"📦 Total docs: {n_total} | clusters: {quality_out.shape[0]}")


if __name__ == "__main__":
    main()
