from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd


def find_existing(paths: list[Path]) -> Path | None:
    for p in paths:
        if p.exists():
            return p
    return None


def compute_cluster_sizes(df: pd.DataFrame) -> pd.DataFrame:
    # tolère "cluster" ou "cluster_id"
    if "cluster" in df.columns:
        ccol = "cluster"
    elif "cluster_id" in df.columns:
        ccol = "cluster_id"
    else:
        raise RuntimeError("Le fichier clustered doit contenir une colonne 'cluster' ou 'cluster_id'.")

    out = (
        df.groupby(ccol)
        .size()
        .reset_index(name="n_offers")
        .rename(columns={ccol: "cluster"})
        .sort_values("n_offers", ascending=False)
    )
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data_dir", default="../data", help="Dossier data (ex: ../data)")
    ap.add_argument("--clustered_csv", default="", help="CSV clustered final si tu veux forcer un chemin")
    ap.add_argument("--out_md", default="report.md", help="Nom du rapport markdown")
    args = ap.parse_args()

    data_dir = Path(args.data_dir).resolve()
    data_dir.mkdir(parents=True, exist_ok=True)

    # 1) Trouver le dataset clusterisé (priorité au final)
    candidates = []
    if args.clustered_csv:
        candidates.append(Path(args.clustered_csv))
    candidates += [
        data_dir / "clustered_k25_final.csv",
        data_dir / "clustered_k25_labeled.csv",
        data_dir / "clustered_k25.csv",
        data_dir / "clustered.csv",
    ]
    clustered_path = find_existing(candidates)
    if not clustered_path:
        raise FileNotFoundError(
            "Impossible de trouver un fichier clusterisé. "
            "Cherché: " + ", ".join(str(p) for p in candidates)
        )

    df = pd.read_csv(clustered_path)

    # 2) cluster_sizes.csv : s'il manque, on le calcule
    cluster_sizes_path = data_dir / "cluster_sizes.csv"
    if cluster_sizes_path.exists():
        sizes = pd.read_csv(cluster_sizes_path)
    else:
        sizes = compute_cluster_sizes(df)
        sizes.to_csv(cluster_sizes_path, index=False)
        print(f"✅ Généré: {cluster_sizes_path}")

    # 3) Charger fichiers optionnels si dispo
    skills_path = data_dir / "skills_by_cluster.csv"
    terms_path = data_dir / "top_terms_by_cluster.csv"
    labels_path = data_dir / "clusters_labels_k25.csv"

    skills = pd.read_csv(skills_path) if skills_path.exists() else None
    terms = pd.read_csv(terms_path) if terms_path.exists() else None
    labels = pd.read_csv(labels_path) if labels_path.exists() else None

    # 4) Déterminer les colonnes utiles dans df
    text_col = None
    for c in ["text", "raw_text", "clean_text", "content"]:
        if c in df.columns:
            text_col = c
            break

    url_col = "url" if "url" in df.columns else None
    title_col = "title" if "title" in df.columns else None

    # cluster label (si présent)
    label_col = "cluster_label" if "cluster_label" in df.columns else None

    # 5) Construire un mini résumé par cluster
    # exemples d'offres par cluster
    if "cluster" in df.columns:
        ccol = "cluster"
    elif "cluster_id" in df.columns:
        ccol = "cluster_id"
    else:
        raise RuntimeError("Le fichier clustered doit contenir 'cluster' ou 'cluster_id'.")

    examples_rows = []
    for cid, g in df.groupby(ccol):
        g2 = g.head(3)
        for _, row in g2.iterrows():
            examples_rows.append(
                {
                    "cluster": cid,
                    "cluster_label": row.get(label_col) if label_col else None,
                    "title": row.get(title_col) if title_col else None,
                    "url": row.get(url_col) if url_col else None,
                }
            )
    examples = pd.DataFrame(examples_rows)

    # 6) Générer rapport markdown
    out_md = data_dir / args.out_md

    def md_table(df_: pd.DataFrame, max_rows: int = 15) -> str:
        if df_ is None or df_.empty:
            return "_(vide)_\n"
        return df_.head(max_rows).to_markdown(index=False) + "\n"

    md = []
    md.append("# Rapport Text Mining – Clusters (K=25)\n")
    md.append(f"**Source fichier clusterisé :** `{clustered_path}`\n")
    md.append(f"**Nombre d'offres :** {len(df)}\n")
    md.append(f"**Fichier tailles clusters :** `{cluster_sizes_path}`\n\n")

    md.append("## 1) Taille des clusters\n")
    md.append(md_table(sizes, max_rows=25))

    if labels is not None:
        md.append("## 2) Labels de clusters (auto)\n")
        md.append(md_table(labels, max_rows=30))

    if terms is not None:
        md.append("## 3) Top termes par cluster\n")
        md.append(md_table(terms, max_rows=30))

    if skills is not None:
        md.append("## 4) Compétences détectées par cluster\n")
        md.append(md_table(skills, max_rows=30))

    md.append("## 5) Exemples d'offres (3 par cluster)\n")
    md.append(md_table(examples, max_rows=80))

    if text_col:
        md.append("## 6) Note\n")
        md.append(f"Le texte utilisé semble être dans la colonne: `{text_col}`.\n")

    out_md.write_text("\n".join(md), encoding="utf-8")
    print(f"✅ Rapport généré: {out_md}")


if __name__ == "__main__":
    main()
