<div align="center">

# 🎯 Job Radar

### *Analyse Territoriale des Offres d'Emploi par NLP & IA*

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.32+-red.svg)](https://streamlit.io/)
[![Docker](https://img.shields.io/badge/Docker-Ready-blue.svg)](https://www.docker.com/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![NLP](https://img.shields.io/badge/NLP-Text%20Mining-orange.svg)]()

*Un projet de Master SISE – NLP & Text Mining*  
*Université Lumière Lyon 2*

[🚀 Démo](#-démo) • [📖 Documentation](#-documentation) • [🐳 Installation](#-installation-docker) • [🎨 Fonctionnalités](#-fonctionnalités)

---

</div>

## 📋 Table des matières

- [🎯 Vue d'ensemble](#-vue-densemble)
- [✨ Points forts du projet](#-points-forts-du-projet)
- [🏗️ Architecture](#️-architecture)
- [🎨 Fonctionnalités](#-fonctionnalités)
- [🔬 Technologies & NLP](#-technologies--nlp)
- [🐳 Installation Docker](#-installation-docker)
- [⚙️ Installation Locale](#️-installation-locale)
- [📊 Sources de données](#-sources-de-données)
- [🗄️ Modélisation des données](#️-modélisation-des-données)
- [🤖 Intelligence Artificielle](#-intelligence-artificielle)
- [📸 Captures d'écran](#-captures-décran)
- [🔐 Configuration](#-configuration)
- [📈 Roadmap](#-roadmap)
- [🤝 Contribution](#-contribution)
- [📄 Licence](#-licence)

---

## 🎯 Vue d'ensemble

**Job Radar** est une plateforme d'analyse avancée des offres d'emploi en France, spécialisée dans les **métiers de la Data, IA et Analytics**. 

Combinant **NLP**, **Text Mining** et **visualisation interactive**, ce projet offre une vision territoriale unique du marché de l'emploi français.

### 🎓 Contexte académique

Projet réalisé dans le cadre du **Master SISE** – *NLP & Text Mining*  
Université Lumière Lyon 2 | 2024-2025

### 🔍 Objectifs

- 📊 **Analyser** plus de 2 500 offres d'emploi en temps réel
- 🗺️ **Cartographier** la répartition géographique des compétences
- 🧠 **Identifier** les compétences les plus demandées par région
- 📈 **Visualiser** les tendances du marché de l'emploi
- 🤖 **Assister** les utilisateurs via IA générative (Mistral)

---

## ✨ Points forts du projet

<table>
<tr>
<td width="50%">

### 🎨 Interface Moderne
- Design NASA-FBI professionnel
- Navigation fluide et intuitive
- Animations et effets visuels
- Responsive & mobile-friendly

</td>
<td width="50%">

### 🔄 Pipeline ETL Robuste
- Collecte automatisée (API + Scraping)
- Enrichissement géographique
- Gestion des doublons
- Base de données décisionnelle

</td>
</tr>
<tr>
<td width="50%">

### 🧠 NLP Avancé
- Extraction de compétences
- TF-IDF & Vectorisation
- Analyse de similarité
- Clustering intelligent

</td>
<td width="50%">

### 🐳 Déploiement Simplifié
- Dockerisé (1 commande)
- Prêt pour la production
- Persistance des données
- Variables d'environnement

</td>
</tr>
</table>

---

## 🏗️ Architecture

```
📦 projet_nlp/
│
├── 🎨 app/                          # Application Streamlit
│   ├── home.py                      # Page d'accueil
│   ├── pages/
│   │   ├── Explorer.py              # 💼 Exploration des 2500+ offres
│   │   ├── Geographie.py            # 🗺️ Cartographie interactive
│   │   ├── Analytics.py             # 📊 Statistiques avancées
│   │   ├── Intelligence.py          # 🧠 Analyses NLP & Clustering
│   │   ├── Assistant.py             # 🤖 Assistant IA (Mistral)
│   │   └── Contribuer.py            # ➕ Ajout dynamique d'offres
│   │
│   └── utils/                       # Utilitaires
│       ├── components.py            # Composants UI
│       ├── db.py                    # Gestion base de données
│       ├── nlp_utils.py             # Outils NLP
│       └── viz.py                   # Visualisations
│
├── 🗄️ database/                     # Base de données
│   ├── schema.sql                   # Schéma SQL (Star Schema)
│   ├── etl_pipeline.py              # Pipeline ETL complet
│   └── jobs.db                      # Base SQLite (2520 offres)
│
├── 🕷️ scraping/                     # Collecte de données
│   ├── france_travail_api.py        # API France Travail
│   └── hellowork_scraper.py         # Scraper HelloWork
│
├── 🌍 geographic_enrichment/        # Enrichissement géo
│   ├── enrich_geo.py                # Géolocalisation
│   └── regions_france.json          # Référentiel régions
│
├── 📊 data/                         # Données
│   ├── raw/                         # Données brutes
│   ├── processed/                   # Données traitées
│   └── exports/                     # Exports CSV/JSON
│
├── 🐳 Dockerfile                    # Image Docker
├── 📋 requirements.txt              # Dépendances Python
├── ⚙️ config.py                     # Configuration
├── 🔒 .env.example                  # Variables d'environnement
└── 📖 README.md                     # Ce fichier
```

---

## 🎨 Fonctionnalités

### 💼 Explorer – Navigation des offres

<table>
<tr>
<td width="60%">

**Fonctionnalités principales :**
- 🔍 Recherche intelligente (titre, compétences, entreprise)
- 🗺️ Filtrage par région (53 régions)
- 📋 Filtrage par type de contrat (CDI, CDD, Stage...)
- 🏠 Filtrage par mode de travail (Télétravail, Hybride, Sur site)
- 💎 Affichage des compétences requises
- 🎯 Score de pertinence par offre
- 🚀 **Redirection directe vers les sites d'offres**
- ⭐ Système de favoris
- 📊 Comparaison d'offres

</td>
<td width="40%">

```
📊 2,520 offres analysées
🏢 890+ entreprises
🗺️ 53 régions françaises
💎 500+ compétences uniques
🎯 Mise à jour quotidienne
```

</td>
</tr>
</table>

### 🗺️ Géographie – Cartographie interactive

- 📍 Carte de France interactive (Folium)
- 🔥 Heatmap des offres par région
- 📊 Distribution géographique des compétences
- 🎯 Zones de concentration des emplois
- 📈 Analyse comparative inter-régions

### 📊 Analytics – Statistiques avancées

- 📈 Évolution temporelle des offres
- 🏆 Top compétences par région
- 💼 Répartition par type de contrat
- 🏠 Taux de télétravail par région
- 📊 Graphiques interactifs (Plotly)
- 📥 Export des données (CSV, JSON)

### 🧠 Intelligence – NLP & Text Mining

<table>
<tr>
<td width="50%">

**Analyses NLP :**
- 📝 Extraction automatique de compétences
- 🎯 Analyse TF-IDF
- 🔍 Recherche par similarité
- 🧩 Clustering K-Means
- ☁️ Nuages de mots interactifs
- 📊 Analyse de co-occurrence

</td>
<td width="50%">

**Métriques :**
- Fréquence des termes
- Importance des compétences
- Similarité cosinus
- Distance euclidienne
- Score de pertinence

</td>
</tr>
</table>

### 🤖 Assistant – IA conversationnelle

- 💬 Assistant intelligent (Mistral AI)
- 🎯 Recommandations personnalisées
- 📊 Analyse de profil
- 💡 Suggestions de compétences à acquérir
- 🗣️ Interface conversationnelle naturelle

### ➕ Contribuer – Enrichissement dynamique

- ✏️ Ajout manuel d'offres
- 🔄 Enrichissement automatique
- ✅ Validation et détection de doublons
- 📊 Mise à jour en temps réel

---

## 🔬 Technologies & NLP

### Stack Technique

<div align="center">

| Catégorie | Technologies |
|-----------|-------------|
| **Backend** | Python 3.11+, SQLite, Pandas, NumPy |
| **Frontend** | Streamlit, HTML/CSS, JavaScript |
| **NLP** | scikit-learn, NLTK, spaCy, TF-IDF |
| **Visualisation** | Plotly, Folium, Matplotlib, Seaborn |
| **IA Générative** | Mistral AI API |
| **Scraping** | BeautifulSoup, Requests, Selenium |
| **Containerisation** | Docker, Docker Compose |
| **Géolocalisation** | Geopy, Nominatim |

</div>

### Techniques NLP Implémentées

```python
# Exemple de pipeline NLP
1. Nettoyage textuel (regex, normalisation)
   ↓
2. Tokenization et lemmatisation
   ↓
3. Extraction de compétences (patterns + NER)
   ↓
4. Vectorisation TF-IDF
   ↓
5. Clustering K-Means (3-5 clusters)
   ↓
6. Analyse de similarité (cosinus)
```

**Algorithmes utilisés :**
- 🎯 **TF-IDF** : Extraction de termes importants
- 🧩 **K-Means** : Clustering d'offres similaires
- 📏 **Similarité cosinus** : Recommandation d'offres
- 🔍 **NER** : Reconnaissance d'entités nommées
- ☁️ **WordCloud** : Visualisation de fréquences

---

## 🐳 Installation Docker

### Prérequis

- ✅ [Docker Desktop](https://www.docker.com/products/docker-desktop) installé
- ✅ Connexion Internet
- ✅ 4 GB RAM minimum

### Installation rapide (3 étapes)

#### 1️⃣ Cloner le dépôt

```bash
git clone https://github.com/votre-username/job-radar.git
cd job-radar
```

#### 2️⃣ Configurer les variables d'environnement

```bash
# Copier le fichier exemple
cp .env.example .env

# Éditer .env et ajouter vos clés API
nano .env
```

**Contenu du `.env` :**

```env
# Mistral AI (Assistant)
MISTRAL_API_KEY=votre_cle_mistral

# France Travail API
FRANCE_TRAVAIL_CLIENT_ID=votre_client_id
FRANCE_TRAVAIL_CLIENT_SECRET=votre_client_secret
```

#### 3️⃣ Lancer l'application

```bash
# Construire et lancer en une commande
docker-compose up --build

# Ou manuellement :
docker build -t job-radar .
docker run -p 8501:8501 --env-file .env job-radar
```

#### 🎉 Accéder à l'application

```
🌐 http://localhost:8501
```

### 💾 Persistance des données (Recommandé)

Pour conserver les données entre les redémarrages :

**Windows (PowerShell) :**
```powershell
docker run -p 8501:8501 `
  -v ${PWD}\database:/app/database `
  --env-file .env `
  job-radar
```

**Linux / macOS :**
```bash
docker run -p 8501:8501 \
  -v $(pwd)/database:/app/database \
  --env-file .env \
  job-radar
```

---

## ⚙️ Installation Locale

### Prérequis

- Python 3.11+
- pip
- virtualenv (recommandé)

### Installation

```bash
# 1. Cloner le dépôt
git clone https://github.com/votre-username/job-radar.git
cd job-radar

# 2. Créer un environnement virtuel
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows

# 3. Installer les dépendances
pip install -r requirements.txt

# 4. Configurer les variables d'environnement
cp .env.example .env
nano .env

# 5. Lancer l'application
streamlit run app/home.py
```

### 🔧 Configuration avancée

**Créer la base de données :**

```bash
# Exécuter le pipeline ETL
python database/etl_pipeline.py --input data/raw/jobs.csv --recreate

# Enrichir les données géographiques
python geographic_enrichment/enrich_geo.py
```

---

## 📊 Sources de données

### 🏢 France Travail API

- **Type** : API officielle
- **Volume** : ~1 500 offres
- **Mise à jour** : Quotidienne
- **Couverture** : France entière

### 🕷️ HelloWork (Scraping)

- **Type** : Web scraping
- **Volume** : ~1 000 offres
- **Mise à jour** : Hebdomadaire
- **Focus** : Métiers Data/IA

### 📈 Statistiques de collecte

```
📊 Total : 2,520 offres
🏢 Entreprises : 890+
🗺️ Régions : 53
💎 Compétences : 500+
📅 Période : Janvier 2025
```

---

## 🗄️ Modélisation des données

### Architecture en étoile (Star Schema)

```
┌─────────────────────────────────────────────────────────┐
│                    fact_offers                          │
│  ┌──────────────────────────────────────────────────┐  │
│  │ • offer_key (PK)                                 │  │
│  │ • uid (UNIQUE)                                   │  │
│  │ • title, description, salary                     │  │
│  │ • source_url ← URL de l'offre                   │  │
│  │ • source_key (FK) → dim_source                   │  │
│  │ • region_key (FK) → dim_region                   │  │
│  │ • company_key (FK) → dim_company                 │  │
│  │ • contract_key (FK) → dim_contract               │  │
│  └──────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
           ↓                ↓                ↓
    ┌──────────┐    ┌──────────┐    ┌──────────┐
    │dim_region│    │dim_company│   │dim_contract│
    └──────────┘    └──────────┘    └──────────┘
           ↓
    ┌──────────────────┐
    │ fact_offer_skill │  ← Table associative
    │  • offer_key     │
    │  • skill_key     │
    └──────────────────┘
           ↓
    ┌──────────┐
    │dim_skill │
    │• skill_name│
    │• skill_type│
    └──────────┘
```

### Vues matérialisées

- `v_offers_complete` : Offres avec toutes les dimensions
- `v_top_skills` : Top compétences avec statistiques
- `v_offers_by_region` : Agrégation par région
- `v_stats_global` : Métriques globales

---

## 🤖 Intelligence Artificielle

### Mistral AI Integration

L'assistant utilise **Mistral AI** pour :

- 💬 Dialogue naturel avec l'utilisateur
- 🎯 Recommandations personnalisées
- 📊 Analyse de profil et compétences
- 💡 Suggestions de formations
- 🔍 Recherche sémantique d'offres

**Exemple d'utilisation :**

```python
# Analyse de profil
utilisateur : "Je suis Data Scientist avec 3 ans d'expérience en Python"
assistant : "Voici les offres qui correspondent à votre profil..."

# Recommandation de compétences
utilisateur : "Quelles compétences devrais-je acquérir ?"
assistant : "D'après l'analyse du marché, je vous recommande..."
```

---

## 📸 Captures d'écran

<div align="center">

### Page Explorer
![Explorer](docs/screenshots/explorer.png)
*Navigation et filtrage des 2500+ offres*

### Cartographie
![Geo](docs/screenshots/geo.png)
*Visualisation géographique interactive*

### Analytics
![Analytics](docs/screenshots/analytics.png)
*Statistiques et graphiques avancés*

### Intelligence NLP
![Intelligence](docs/screenshots/intelligence.png)
*Clustering et analyses NLP*

</div>

---

## 🔐 Configuration

### Variables d'environnement requises

| Variable | Description | Obligatoire |
|----------|-------------|-------------|
| `MISTRAL_API_KEY` | Clé API Mistral AI | ⚠️ Oui (pour Assistant) |
| `FRANCE_TRAVAIL_CLIENT_ID` | Client ID France Travail | ⚠️ Oui (pour collecte) |
| `FRANCE_TRAVAIL_CLIENT_SECRET` | Secret France Travail | ⚠️ Oui (pour collecte) |
| `DATABASE_PATH` | Chemin vers la BDD | Non (par défaut: `database/jobs.db`) |

### Obtenir les clés API

**Mistral AI :**
1. Créer un compte sur [console.mistral.ai](https://console.mistral.ai)
2. Générer une clé API
3. Ajouter dans `.env` : `MISTRAL_API_KEY=votre_cle`

**France Travail :**
1. S'inscrire sur [francetravail.io](https://francetravail.io)
2. Créer une application
3. Récupérer Client ID et Secret
4. Ajouter dans `.env`

---

## 📈 Roadmap

### Version 1.0 ✅ (Actuelle)

- [x] Pipeline ETL complet
- [x] Interface Streamlit professionnelle
- [x] Analyses NLP avancées
- [x] Cartographie interactive
- [x] Assistant IA (Mistral)
- [x] Dockerisation

### Version 1.1 🚧 (En cours)

- [ ] Amélioration du scraping (plus de sources)
- [ ] Analyse prédictive des tendances
- [ ] Système de notifications
- [ ] API REST pour les développeurs
- [ ] Export PDF des analyses

### Version 2.0 🔮 (Futur)

- [ ] Machine Learning (prédiction de salaires)
- [ ] Recommandation personnalisée avancée
- [ ] Authentification utilisateur
- [ ] Dashboard personnalisé
- [ ] Version mobile (React Native)
- [ ] Intégration LinkedIn API

---

## 🤝 Contribution

Les contributions sont les bienvenues ! 🎉

### Comment contribuer ?

1. **Fork** le projet
2. Créer une branche (`git checkout -b feature/AmazingFeature`)
3. Commit (`git commit -m 'Add AmazingFeature'`)
4. Push (`git push origin feature/AmazingFeature`)
5. Ouvrir une **Pull Request**

### Guidelines

- Code propre et commenté
- Tests unitaires si applicable
- Documentation mise à jour
- Respect du style de code (PEP 8)

### Bugs & Suggestions

Ouvrir une **issue** sur GitHub avec :
- 🐛 Description du bug
- 📝 Étapes de reproduction
- 💡 Solution proposée (si applicable)

---

## 👥 Équipe

<div align="center">

**Développé par :**

[Votre Nom](https://github.com/votre-username)  
Master SISE – NLP & Text Mining  
Université Lumière Lyon 2

**Contact :**  
📧 email@example.com  
💼 [LinkedIn](https://linkedin.com/in/votre-profil)  
🐙 [GitHub](https://github.com/votre-username)

</div>

---

## 📄 Licence

Ce projet est sous licence **MIT**.

```
MIT License

Copyright (c) 2025 Votre Nom

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction...
```

Voir le fichier [LICENSE](LICENSE) pour plus de détails.

---

## 🙏 Remerciements

- 🎓 **Université Lumière Lyon 2** - Master SISE
- 🏢 **France Travail** - API officielle
- 🕷️ **HelloWork** - Source de données
- 🤖 **Mistral AI** - Intelligence artificielle
- 🐍 **Communauté Python** - Bibliothèques open source
- 📊 **Streamlit** - Framework web

---

## 📚 Ressources

### Documentation

- 📖 [Guide utilisateur](docs/USER_GUIDE.md)
- 🔧 [Guide développeur](docs/DEVELOPER_GUIDE.md)
- 🐳 [Guide Docker](docs/DOCKER_GUIDE.md)
- 📊 [Guide des données](docs/DATA_GUIDE.md)

### Articles & Références

- 📄 [Rapport de projet](docs/RAPPORT.pdf)
- 📊 [Présentation](docs/PRESENTATION.pptx)
- 🎥 [Démo vidéo](https://youtube.com/...)

---

<div align="center">

### ⭐ Si ce projet vous plaît, n'hésitez pas à lui donner une étoile !

[![Star](https://img.shields.io/github/stars/votre-username/job-radar?style=social)](https://github.com/votre-username/job-radar/stargazers)
[![Fork](https://img.shields.io/github/forks/votre-username/job-radar?style=social)](https://github.com/votre-username/job-radar/network/members)
[![Watch](https://img.shields.io/github/watchers/votre-username/job-radar?style=social)](https://github.com/votre-username/job-radar/watchers)

---

**Made with ❤️ for the Data & AI community**

*[Retour en haut ⬆️](#-job-radar)*

</div>