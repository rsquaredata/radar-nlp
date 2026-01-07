<div align="center">

<img src="https://raw.githubusercontent.com/votre-repo/assets/logo_radar.png" width="450px" alt="RADAR Logo"/>

# RADAR : Intelligence Artificielle & Marché Data

[![Python](https://img.shields.io/badge/Python-3.11-blue.svg)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.41-FF4B4B.svg)](https://streamlit.io/)
[![DuckDB](https://img.shields.io/badge/Database-DuckDB-yellow.svg)](https://duckdb.org/)
[![MistralAI](https://img.shields.io/badge/AI-Mistral-orange.svg)](https://mistral.ai/)

### Observatoire Analytique des Offres d'Emploi Data en France

</div>

**RADAR** (Recherche Analytique Des Annonces Régionales) est un terminal d'intelligence métier conçu pour collecter, traiter et analyser le marché de la Data. Il combine des pipelines de scraping automatisés, un entrepôt de données DuckDB haute performance et une couche d'IA sémantique (Mistral) pour le matching profil-poste.

---

## Fonctionnalités Clés

- **Collecte Multi-sources** : Scraping automatisé (France Travail, Jooble, Emploi-Territorial, Welcome to the Jungle).
- **Entrepôt Snowflake** : Architecture DuckDB optimisée pour le traitement analytique (18 000+ offres).
- **Intelligence Métier** : Comparaison sémantique de clusters de métiers via Radar Charts.
- **Matching CV IA** : Analyse d'adéquation en temps réel entre un profil (CV) et une offre via le LLM **Mistral AI**.
- **Explorateur Dynamique** : Moteur de recherche avec filtres de salaire, télétravail et nettoyage sémantique des "faux positifs".
- **Gamification** : Système de progression (XP) pour débloquer les fonctionnalités avancées de l'assistant IA.

---

## Installation & Quick Start

### 1. Cloner et configurer l'environnement

```bash
git clone [https://github.com/votre-user/radar-nlp.git](https://github.com/main/radar-nlp.git)
cd radar-nlp
conda env create -f environment.yml
conda activate radarenv
```

### 2. Configuration des secrets

Créez un fichier `.env` à la racine pour l'IA :

```env
MISTRAL_API_KEY="votre_clef_api_mistral_ici"
```

### 3. Lancer le terminal RADAR

```bash
streamlit run app.py
```

---

## 🐳 Déploiement Docker

Pour une portabilité totale, RADAR est entièrement dockerisé.

```bash
# Build de l'image
docker build -t radar-terminal .

# Lancement de l'application
docker run -p 8501:8501 --env-file .env radar-terminal
```

---

## 📊 Architecture du Pipeline NLP

Le projet repose sur un pipeline de traitement rigoureux :

1. **Ingestion** : Scripts de scraping → Stockage JSON brut.

2. **Traitement** : Nettoyage sémantique (Regex, Stopwords) et correction de labeling (Hellowork/Adzuna).

3. **Modélisation** : Clustering K-Means & LDA pour la définition des 6 familles de métiers Data.

4. **Visualisation** : Interface Streamlit avec analyses géographiques (Top Villes, Régions) et Wordclouds.

---

## 📂 Structure du Projet

```plaintext
radar-nlp/
├── app.py              # Point d'entrée (Home & Navigation)
├── pages/              # Modules de l'application
│   ├── 01_Analytics.py # Analyses Géo & Métiers
│   ├── 03_Intelligence_Metier.py # Comparateur & Matching CV
│   └── ...
├── utils/              # Logique métier & Connexion DB
├── data/db/            # Base DuckDB (Snowflake Schema)
├── scripts/            # Automates de scraping
├── Dockerfile          # Configuration Docker
└── .env                # Clé API Mistral (non versionné)
```

---

## 🤖 Module Intelligence Artificielle

L'onglet **Intelligence Métier** utilise le modèle mistral-tiny pour fournir un feedback contextuel :
- **Extraction sémantique** : Analyse des compétences dans le texte brut du CV.
- **Score d'adéquation** : Calcul de la distance entre le profil et le cluster de destination.
- **Conseils RH** : Recommandations personnalisées générées par l'IA.

---

## 👥 Auteurs & Encadrement

Projet réalisé dans le cadre du Master 2 SISE - Université Lyon 2.

- Étudiants : Mohamed Habib Bah, Thibaud Lecomte, Aya Mecheri, Rina Razafimahefa

- Supervision : Ricco Rakotomalala

***

## 📄 Licence

Ce projet est distribué sous licence MIT. Utilisation libre dans un cadre académique ou personnel.

---

<div align="center"> <sub>Projet Master SISE 2026 - RADAR</sub> </div>
