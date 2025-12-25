# Projet NLP – Analyse du marché de l’emploi Data/IA (France)
Pipeline complet : **extraction multi-sources → normalisation → stockage SQLite → enrichissement géographique → préparation corpus → TF-IDF + KMeans → labellisation clusters → app Streamlit interactive**

## 0) Objectif
Constituer une base d’offres d’emploi **Data/IA en France** à partir de 3 sources :
- **France Travail** (API)
- **HelloWork** (scraping HTML)
- **Adzuna** (API)

Puis :
- **normaliser** les champs (schéma commun)
- **stocker** en base **SQLite**
- ajouter une dimension **géographique** (lat/lon/ville/département/région)
- construire un **corpus NLP**
- faire un **clustering** de type KMeans (TF-IDF)
- produire des **labels de clusters** et des sorties interprétables
- afficher tout ça dans une **application Streamlit** (cartes + graphes interactifs)

---

## 1) Structure du projet (recommandée)
projet_nlp/
data/ # fichiers générés (jsonl, csv, sqlite, models)
src/ # scripts pipeline (CLI)
app/ # streamlit multi-pages
Home.py
pages/
README.md

yaml
Copier le code

---

## 2) Installation & environnement
### 2.1 Créer l’environnement (exemple conda)
```bash
conda create -n nlp_project python=3.11 -y
conda activate nlp_project
pip install -r requirements.txt
2.2 Variables d’environnement (API)
France Travail (obligatoire pour FT)
FT_CLIENT_ID

FT_CLIENT_SECRET

FRANCE_TRAVAIL_SCOPE (optionnel, défaut : api_offresdemploiv2)

Adzuna (obligatoire pour Adzuna)
ADZUNA_APP_ID

ADZUNA_APP_KEY

Sous Windows (PowerShell) :

powershell
Copier le code
setx FT_CLIENT_ID "xxx"
setx FT_CLIENT_SECRET "xxx"
setx ADZUNA_APP_ID "xxx"
setx ADZUNA_APP_KEY "xxx"
3) Étape A — Extraction des données
On génère des fichiers RAW (jsonl/csv) par source.

A1) Extraction France Travail (API)
➡️ Sortie attendue : data/france_travail.jsonl (et éventuellement .csv)

Commande (exemple) :

bash
Copier le code
python src/run_france_travail.py --out_dir ../data --max_pages 200 --sleep_s 0.2
A2) Extraction HelloWork (scraping HTML)
➡️ Sortie attendue : data/hellowork_emploi_france_raw.jsonl (et .csv)

Commande (exemple) :

bash
Copier le code
python src/run_hellowork.py --out_dir ../data --max_urls 40000 --max_pages 30 --sleep_s 0.4
A3) Extraction Adzuna (API)
➡️ Sortie attendue : data/adzuna_fr_data_ia.jsonl (et .csv)

Commande (exemple) :

bash
Copier le code
python src/run_adzuna.py --country fr --out_dir ../data --what "data" --max_pages 200 --sleep_s 0.2
✅ À la fin de l’étape A, on doit avoir 3 fichiers jsonl (au minimum) :

../data/france_travail.jsonl

../data/hellowork_emploi_france_raw.jsonl

../data/adzuna_fr_data_ia.jsonl

4) Étape B — Normalisation (schéma commun)
On fusionne et normalise les 3 sources dans un seul dataset.

➡️ Sortie attendue :

data/jobs_normalized.csv

(optionnel) data/jobs_normalized.jsonl

Commande :

bash
Copier le code
python src/normalize_to_csv.py --france_travail ../data/france_travail.jsonl --hellowork ../data/hellowork_emploi_france_raw.jsonl --adzuna ../data/adzuna_fr_data_ia.jsonl --out_dir ../data --dedup
Champs normalisés (principaux) :

uid (hash stable) + source + url

title, employer, location

contract_type, salary, remote

published_date / published_relative

raw_text (texte pour NLP)

5) Étape C — Stockage en base SQLite (upsert / anti-doublon)
On charge jobs_normalized.csv dans SQLite.

➡️ Sortie attendue :

data/offers.sqlite (table offers)

Commande :

bash
Copier le code
python src/load_to_sqlite.py --csv ../data/jobs_normalized.csv --db ../data/offers.sqlite
Notes :

uid est clé unique → permet upsert (insert/update) sans doublons.

La base contient tous les champs normalisés.

6) Étape D — Enrichissement géographique (dimension territoriale)
Objectif : compléter la table offers avec :

city, postcode, dept_code, region

lat, lon

geo_score, geo_source

Commande :

bash
Copier le code
python src/enrich_geo_sqlite.py --db ../data/offers.sqlite --sleep_s 0.15
✅ Résultat : cartes interactives possibles côté Streamlit (Plotly Map / choropleth régions).

7) Étape E — Construction du corpus depuis SQLite
On exporte un corpus (uid + texte) depuis la table offers.

Sorties :

data/corpus_raw.csv

data/corpus_raw.jsonl

Commande :

bash
Copier le code
python src/build_corpus_from_sqlite.py --db ../data/offers.sqlite --out_dir ../data --min_len 0
8) Étape F — Préprocessing du corpus
Nettoyage NLP : lower, suppression bruit, tokens…

Sortie :

data/corpus_clean.csv

Commande :

bash
Copier le code
python src/preprocess_corpus.py --in_csv ../data/corpus_raw.csv --out_dir ../data --min_tokens 1
9) Étape G — Clustering (TF-IDF + KMeans)
G1) (Optionnel) Recherche automatique du meilleur k
Sortie :

data/k_search_results.csv

Commande :

bash
Copier le code
python src/auto_k_search.py --in_csv ../data/corpus_clean.csv --out_dir ../data --k_min 5 --k_max 40 --k_step 1 --ngram_max 2 --sample_silhouette 6000
G2) Clustering final (k choisi)
Sorties :

data/clustered_k25.csv

data/clusters_k25_top_terms.json

Commande (exemple k=25) :

bash
Copier le code
python src/cluster_tfidf_kmeans.py --in_csv ../data/corpus_clean.csv --out_dir ../data --k 25 --ngram_max 2 --sample_silhouette 6000
10) Étape H — Interprétation & exemples par cluster
Sorties :

data/clusters_summary_k25.csv

data/clusters_examples_k25.csv

data/clusters_report_k25.md

Commande :

bash
Copier le code
python src/interpret_clusters.py --clustered_csv ../data/clustered_k25.csv --meta_json ../data/clusters_k25_top_terms.json --out_dir ../data --examples_per_cluster 6
11) Étape I — Labellisation automatique des clusters
Sortie :

data/clusters_labels_k25.csv (colonnes : cluster, cluster_label, top_terms, …)

Commande :

bash
Copier le code
python src/label_clusters.py --meta_json ../data/clusters_k25_top_terms.json --clustered_csv ../data/clustered_k25.csv --out_csv ../data/clusters_labels_k25.csv
12) Étape J — Injection cluster & label dans SQLite (si utilisé)
On met à jour la table offers avec cluster et cluster_label.

Commande (si script dédié) :

bash
Copier le code
python src/update_clusters_in_sqlite.py --db ../data/offers.sqlite --clustered_csv ../data/clustered_k25.csv --labels_csv ../data/clusters_labels_k25.csv
(si ton projet utilise un autre script, garder cette logique : join par uid)

13) Étape K — Extraction des skills par cluster (analyse)
Sortie :

data/skills_by_cluster.csv

data/top_terms_by_cluster.csv

Commande :

bash
Copier le code
python src/extract_skills_by_cluster.py --in_csv ../data/clustered_k25_labeled.csv --out_dir ../data
14) Étape L — Mise à jour “nouvelles offres” (pipeline incrémental)
Objectif : ne traiter que les nouvelles offres ajoutées en base.

utilise modèles sauvegardés : data/models/tfidf_k25.joblib + data/models/kmeans_k25.joblib

applique transform + predict (pas de refit sur 5 samples)

Commande :

bash
Copier le code
python src/update_new_offers_pipeline.py --db ../data/offers.sqlite --labels_csv ../data/clusters_labels_k25.csv --k 25 --retrain_if_missing
15) Application Streamlit
15.1 Lancer l’application
bash
Copier le code
streamlit run app/Home.py
15.2 Pages principales (exemple)
Dashboard (KPIs + tendances)

Carte interactive (offres par région/ville)

Clusters (top termes + filtres + exemples)

Offres (table complète + lien “postuler”)

Mise à jour (bouton “Mettre à jour les nouvelles offres”)

16) Vérification rapide (SQL)
Lister quelques offres :

bash
Copier le code
python -c "import sqlite3,pandas as pd; con=sqlite3.connect(r'../data/offers.sqlite'); df=pd.read_sql