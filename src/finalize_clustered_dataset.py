import argparse
import pandas as pd


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--clustered_csv", required=True)
    ap.add_argument("--labels_csv", required=True)
    ap.add_argument("--out_csv", required=True)
    args = ap.parse_args()

    df = pd.read_csv(args.clustered_csv)
    labels = pd.read_csv(args.labels_csv)

    # --- normalisation des colonnes labels ---
    col_cluster = None
    col_label = None

    for c in labels.columns:
        lc = c.lower()
        if lc in ("cluster", "cluster_id"):
            col_cluster = c
        if lc in ("label", "cluster_label", "auto_label"):
            col_label = c

    if col_cluster is None or col_label is None:
        raise RuntimeError(
            f"Colonnes labels invalides. Trouvé: {list(labels.columns)}"
        )

    labels = labels[[col_cluster, col_label]]
    labels.columns = ["cluster", "cluster_label"]

    # --- normalisation du clustered_csv ---
    if "cluster" not in df.columns:
        raise RuntimeError("clustered_csv doit contenir une colonne 'cluster'")

    # --- merge ---
    out = df.merge(labels, on="cluster", how="left")

    out.to_csv(args.out_csv, index=False)
    print(f"✅ Dataset final créé : {args.out_csv}")
    print(out[["cluster", "cluster_label"]].drop_duplicates().head())


if __name__ == "__main__":
    main()
