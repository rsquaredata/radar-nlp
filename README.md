# RADAR
**Analyse régionale des offres d'emploi - Scraping, Entrepôt DuckDB, NLP & Application Streamlit**

**RADAR** (Recherche Analytique Des Annonces Régionales) est un projet de NLP - Text Mining réalisé dans le cadre du **Master 2 SISE - Université Lyon 2**.

<img
    src="assets/authors.svg"
    alt="Auteurs : Mohamed Habib Bah, Thibaud Lecomte, Aya Mecheri, Rina Razafimahefa"
    width="600"
/>

Encadrement : Ricco Rakotomalala  

---

## Présentation générale

**RADAR** est un projet complet d'ingénierie et d'analyse de données permettant de :

1. **Collecter** des offres d'emploi (Indeed, APEC, Jooble API, Emploi-Territorial)  
2. **Stocker & modélieser** ces offres dansn un **entrepôt DuckDB** (schéma en snowflake)
3. **Enrichir les données** par un pipeline NLP (nettoyage, extraction de variables, détection de compétences, segmentation...)  
4. **Analyser** les tendances régionales (offres, métiers, compétences, texte)  
5. **Visualiser** via une application **Streamlit** modulaire.  

---

## Arborescence (simplifiée) du dépôt

```text
radar-nlp/  
├── main.py  
├── pages/  
│  
├── src/  
│   └── radar/  
│       ├── db/  
│       ├── nlp/  
│       ├── scraping/  
│       └── __init__.py  
│  
├── data/  
├── scripts/  
├── pyproject.toml  
└── README.md  
```

---

## Installation locale (sans Docker)

### 1. Cloner le dépôt

```bash
git clone https://github.com/rsquaredata/radar-nlp
cd radar-nlp
```

### 2. Créer l'environnement conda

```bash
conva env create -f environment.yml
conda activate radar-nlp
```

### 3. Installer le package local (editable)

---

## Scraper & mettre à jour le corpus (mode CLI)

Exemples typiques :

```bash
# Scraper Indeed / APEC / Jooble / Emploi Territorial
python scripts/scrape_indeed.py
python scripts/scrape_apec.py
python scripts/scrape_jooble.py
python scripts/scrape.emploi_territorial.py

# Mettre à jour l'entrepôt (lecture JSON → process_offre → DuckDB)
python scripts/update_corpus.py
```

Les offres bruites sont stockées dans `data/raw/`, l'entrepôt analysé dans `data/db/radar.duckdb`.

---

## Lancer l'application Streamlit (local)

Depuis la racine du dépôt :

```bash
streamlit run main.py
```

L'application propose plusieurs pages :  
- **Accueil** : vue globale et navigation  
- **Carte** : choroplethèe par région  
- **Analyse NLP** : topics LDA, TF-IDF, clustering, projection 2D  
- **Comparaison** : comparaisons régions/métiers  
- **Ajout d'offre** : ajout d'une offre par URL  

---

## Utilisation avec Docker

Une image Docker est prévue pour exécuter RADAR sans installation locale.

### 1. Constuire l'image Docker et initialiser la base DuckDB

```bash
Dockerfile build -t radar-nlp
docker run --rm -it -v "$(pwd)/data:/app/data" radar-nlp python -m radar.db.schema
```

### 2. Lancer l'application Streamlit

```bash
docker run --rm -p 8501:8501 -v "$(pwd)/data:/app/data" radar-nlp
```

Puis ouvrir dans le navigateur :

```
http://localhost:8501
```

### 3. Exécuter un script

Par exemple, mettre à jour le corpus :

```bash
docker run --rm -it -v "$(pwd)/data:/app/data" radar-nlp python scripts_/update_corpus.py
```

---

## Utilitaires

### Script `run.sh`

Un petit scrpit (local) est fourni pour ajouter `src/` au `PYTHONPATH` si besoin et lancer Streamlit.

```bash
chmod +x run.sh
./run.sh
```

---

## Entrepôt et NLP - Résumé

- Entrepôt : *DuckDB* (fichier unique, performant, portable)
- Modélisation : schéma en **snowflake** avec :
  - fact_offre
  - dim_date, dim_source, dim_metier, dim_skill
  - dim_ville → dim_departement → dim_region
  - dim_texte, fact_offre_skill
- NLP :
  - nettoyage & normalisation du texte
  - extraction des champs structurés (contrat, salaire, lieu...)
  - topics LDA, TF-IDF + KMeans, SVD/LSA 2D
  - analyse des compétences demandeés

---

Perspectives

- UMAP / t-SNE pour une projection plus fine des documents
- Embeddings pour la similarité entre offres
- Classification automatique des métiers
- Comparaison interactive région/métier (page 5)
- Export automatique de rapports (PDF/HMTL) à partir des analyses Streamlit

---

## Licence

Projet pédagogique - Université Lyon 2
Réutilisation libre dans un cadre personnel, universitaire ou non commercial.

</details>
