import argparse
import pandas as pd
from pathlib import Path

def save(df, path):
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--in_csv", required=True)
    ap.add_argument("--out_dir", required=True)
    args = ap.parse_args()

    df = pd.read_csv(args.in_csv)
    out = Path(args.out_dir)

    # Taille des clusters
    size = df.groupby(["cluster_id", "cluster_label"]).size().reset_index(name="n_docs")
    save(size, out / "cluster_sizes.csv")

    # Top villes
    cities = (
        df.dropna(subset=["location"])
        .groupby(["cluster_id", "cluster_label", "location"])
        .size()
        .reset_index(name="count")
        .sort_values(["cluster_id", "count"], ascending=[True, False])
    )
    save(cities, out / "cities_by_cluster.csv")

    # Top entreprises
    companies = (
        df.dropna(subset=["company"])
        .groupby(["cluster_id", "cluster_label", "company"])
        .size()
        .reset_index(name="count")
        .sort_values(["cluster_id", "count"], ascending=[True, False])
    )
    save(companies, out / "companies_by_cluster.csv")

    # Types de contrat
    contracts = (
        df.dropna(subset=["contract_type"])
        .groupby(["cluster_id", "cluster_label", "contract_type"])
        .size()
        .reset_index(name="count")
    )
    save(contracts, out / "contracts_by_cluster.csv")

    print("✅ Stats par cluster générées")

if __name__ == "__main__":
    main()
