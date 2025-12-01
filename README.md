# RADAR — Recherche Analytique Des Annonces Régionales

**RADAR** (Recherche Analytique Des Annonces Régionales) est un projet de text mining et d'analyse NLP des offres d’emploi en France, avec un focus sur les métiers de la **data** et de l’**intelligence artificielle**.

L’objectif est de construire :

- Un **corpus d’offres d’emploi** collectées automatiquement (web scraping) depuis plusieurs plateformes.
- Un **entrepôt de données** alimenté par ces offres (titre, texte, géographie, compétences, etc.).
- Une **application web interactive** (Streamlit) permettant d’explorer :
  - la répartition régionale des offres,
  - les compétences et technologies demandées,
  - la typologie des métiers (clustering, topics),
  - des comparaisons entre régions, métiers, périodes, etc.
- Une **image Docker** permettant de déployer l’application facilement.

Ce projet est réalisé dans le cadre du Master 2 SISE (Université Lyon 2) pour l’UE *NLP – Text Mining*.

---

## 1. Objectifs du projet

1. **Constituer un corpus** d’offres d’emploi liées à la data / IA en France :
   - data scientist, data analyst, data engineer, machine learning engineer, MLOps, etc.
   - sur plusieurs mois récents.
   - avec une dimension régionale explicite (régions administratives françaises).

2. **Modéliser une base de données / entrepôt** :
   - table de faits des offres,
   - dimensions (région, date, source, type de métier, etc.),
   - stockage dans un SGBD libre (SQLite ou DuckDB).

3. **Appliquer des techniques de text mining / NLP** pour :
   - nettoyer et normaliser les textes (tokenisation, lemmatisation, etc.),
   - extraire des compétences et technologies (hard skills, soft skills),
   - identifier des thèmes (topics) ou familles d’offres (clustering sémantique),
   - analyser les différences régionales.

4. **Proposer une application web interactive** :
   - visualisations cartographiques (répartition des offres, intensité des compétences),
   - graphiques interactifs (Plotly, etc.),
   - filtres par région, métier, technologie, période,
   - ajout dynamique de nouvelles offres (par URL ou par scraping).

5. **Fournir un environnement de déploiement** :
   - image Docker,
   - script d’initialisation de la base,
   - documentation d’installation et d’utilisation.

---

## 2. Architecture du projet

L’arborescence prévisionnelle du projet est la suivante :

```text
radar-nlp/
├── README.md
├── .gitignore
├── environment.yml
├── src/
│   └── radar/
│       ├── __init__.py
│       ├── config.py
│       ├── db/
│       │   ├── __init__.py
│       │   ├── schema.py
│       │   └── io.py
│       ├── scraping/
│       │   ├── __init__.py
│       │   ├── base.py
│       │   ├── indeed.py
│       │   └── apec.py
│       ├── nlp/
│       │   ├── __init__.py
│       │   ├── preprocess.py
│       │   ├── features.py
│       │   ├── topics.py
│       │   └── embeddings.py
│       └── app/
│           ├── __init__.py
│           └── main.py
├── data/
│   ├── raw/
│   ├── processed/
│   └── db/
├── notebooks/
│   ├── exploration_nlp.ipynb
│   └── tests_cartes.ipynb
├── scripts/
│   ├── init_db.py
│   ├── scrape_indeed.py
│   ├── scrape_apec.py
│   └── update_corpus.py
├── docker/
│   ├── Dockerfile
│   └── entrypoint.sh
└── reports/
    └── radar_report.tex
```

---

Auteurs

- Aya MECHERI
- Mohamed Habib BAH
- Rina RAZAFIMAHEFA
- Thibaud LECOMTE
