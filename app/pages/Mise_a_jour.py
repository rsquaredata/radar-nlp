from __future__ import annotations

import os
import sqlite3
import subprocess
import sys
from datetime import datetime, timedelta
from pathlib import Path

import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="Mise à jour des offres",
    page_icon="🔄",
    layout="wide",
)

# ----------------------------
# Helpers
# ----------------------------
def db_connect(db_path: str) -> sqlite3.Connection:
    return sqlite3.connect(db_path)


def read_table(con: sqlite3.Connection, query: str) -> pd.DataFrame:
    return pd.read_sql(query, con)


def nice_dt(dt_str: str | None) -> str:
    if not dt_str:
        return ""
    try:
        # SQLite format "YYYY-MM-DD HH:MM:SS"
        return datetime.strptime(dt_str, "%Y-%m-%d %H:%M:%S").strftime("%d/%m/%Y %H:%M")
    except Exception:
        return str(dt_str)


def run_pipeline(
    python_exe: str,
    script_path: str,
    db_path: str,
    labels_csv: str,
    k: int,
    retrain_if_missing: bool,
    limit_new: int,
) -> tuple[int, str]:
    cmd = [
        python_exe,
        script_path,
        "--db", db_path,
        "--labels_csv", labels_csv,
        "--k", str(k),
    ]
    if retrain_if_missing:
        cmd.append("--retrain_if_missing")
    if limit_new and limit_new > 0:
        cmd += ["--limit_new", str(limit_new)]

    # Important on Windows: force UTF-8 so logs aren’t broken
    env = os.environ.copy()
    env["PYTHONIOENCODING"] = "utf-8"

    p = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        env=env,
    )
    out = (p.stdout or "") + ("\n" + (p.stderr or "") if p.stderr else "")
    return p.returncode, out


# ----------------------------
# UI
# ----------------------------
st.title("🔄 Mise à jour des nouvelles offres")
st.caption("Ajoute/clusterise uniquement les nouvelles offres détectées (pas de retraitement global).")

colA, colB, colC = st.columns([1.2, 1.2, 1.0], vertical_alignment="top")

with colA:
    db_path = st.text_input(
        "Chemin vers SQLite (.sqlite)",
        value=str(Path("../data/offers.sqlite")),
        help="Ex: ../data/offers.sqlite",
    )
    labels_csv = st.text_input(
        "Chemin vers labels clusters (CSV)",
        value=str(Path("../data/clusters_labels_k25.csv")),
        help="Ex: ../data/clusters_labels_k25.csv",
    )

with colB:
    k = st.number_input("K (clusters)", min_value=2, max_value=200, value=25, step=1)
    retrain_if_missing = st.toggle(
        "Ré-entraîner les modèles si manquants (TF-IDF + KMeans)",
        value=False,
        help="À cocher uniquement si les fichiers joblib n’existent pas encore.",
    )
    limit_new = st.number_input(
        "Limiter le nombre de nouvelles offres traitées (0 = pas de limite)",
        min_value=0,
        max_value=200000,
        value=0,
        step=50,
    )

with colC:
    st.markdown("### ⚙️ Exécution")
    run_btn = st.button("✅ Mettre à jour les nouvelles offres", use_container_width=True)
    st.info(
        "Le pipeline utilisé : `src/update_new_offers_pipeline.py`\n\n"
        "Il fait : TF-IDF.transform → KMeans.predict → update SQLite."
    )

st.divider()

# ----------------------------
# Paths
# ----------------------------
SCRIPT_PATH = str(Path(__file__).resolve().parents[2] / "src" / "update_new_offers_pipeline.py")
PYTHON_EXE = sys.executable  # same env as streamlit

# ----------------------------
# RUN
# ----------------------------
if run_btn:
    if not Path(db_path).exists():
        st.error(f"Base introuvable: {db_path}")
        st.stop()
    if not Path(labels_csv).exists():
        st.error(f"Labels CSV introuvable: {labels_csv}")
        st.stop()
    if not Path(SCRIPT_PATH).exists():
        st.error(f"Script pipeline introuvable: {SCRIPT_PATH}")
        st.stop()

    with st.spinner("Mise à jour en cours..."):
        code, logs = run_pipeline(
            python_exe=PYTHON_EXE,
            script_path=SCRIPT_PATH,
            db_path=db_path,
            labels_csv=labels_csv,
            k=int(k),
            retrain_if_missing=bool(retrain_if_missing),
            limit_new=int(limit_new),
        )

    st.subheader("📜 Logs")
    st.code(logs.strip() if logs else "(aucun log)", language="text")

    if code != 0:
        st.error(f"❌ Pipeline terminé avec erreur (code={code}). Regarde les logs.")
    else:
        st.success("✅ Pipeline exécuté avec succès.")

st.divider()

# ----------------------------
# Dashboard (DB Stats + last updates)
# ----------------------------
if Path(db_path).exists():
    con = db_connect(db_path)

    # Stats
    total = read_table(con, "SELECT COUNT(*) AS n FROM offers").iloc[0]["n"]
    processed = read_table(
        con, "SELECT COUNT(*) AS n FROM offers WHERE processed_at IS NOT NULL AND processed_at <> ''"
    ).iloc[0]["n"]
    clustered = read_table(con, "SELECT COUNT(*) AS n FROM offers WHERE cluster IS NOT NULL").iloc[0]["n"]

    c1, c2, c3 = st.columns(3)
    c1.metric("📦 Total offres", int(total))
    c2.metric("✅ Offres traitées (processed_at)", int(processed))
    c3.metric("🧠 Offres clusterisées", int(clustered))

    st.markdown("### 🆕 Dernières offres mises à jour")
    # last updates: show last 200 by processed_at
    df_last = read_table(
        con,
        """
        SELECT
            uid, source, title, employer, city, region,
            contract_type, salary, remote,
            cluster, cluster_label,
            url, processed_at
        FROM offers
        WHERE processed_at IS NOT NULL AND processed_at <> ''
        ORDER BY processed_at DESC
        LIMIT 200
        """,
    )

    if df_last.empty:
        st.warning("Aucune offre 'processed_at' trouvée pour l’instant.")
    else:
        df_last["processed_at"] = df_last["processed_at"].map(nice_dt)

        # Link column
        def make_apply_link(u: str) -> str:
            if not u or not isinstance(u, str):
                return ""
            return f"[Postuler]({u})"

        df_last["postuler"] = df_last["url"].map(make_apply_link)

        # reorder + drop raw url (keep clickable)
        cols = [
            "processed_at", "source", "title", "employer", "city", "region",
            "contract_type", "salary", "remote",
            "cluster", "cluster_label",
            "postuler",
        ]
        df_show = df_last[cols].copy()

        st.dataframe(
            df_show,
            use_container_width=True,
            hide_index=True,
            column_config={
                "postuler": st.column_config.LinkColumn("Postuler", display_text="Postuler"),
            },
        )

    con.close()
else:
    st.warning("Renseigne un chemin DB valide pour voir les stats.")
