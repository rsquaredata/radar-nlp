# 📊 Guide des Données - Job Radar

<div align="center">

**Modélisation, ETL, et Analyse des Données**

*Comprendre la structure et le traitement des données*

[ Accueil](../README.md) • [ User](USER_GUIDE.md) • [🔧 Dev](DEVELOPER_GUIDE.md) • [ Docker](DOCKER_GUIDE.md)

---

</div>

## 📋 Table des matières

1. [Vue d'ensemble](#-vue-densemble)
2. [Sources de données](#-sources-de-données)
3. [Modèle de données](#-modèle-de-données)
4. [Pipeline ETL](#-pipeline-etl)
5. [Qualité des données](#-qualité-des-données)
6. [Requêtes SQL](#-requêtes-sql)
7. [Export & APIs](#-export--apis)
8. [Maintenance](#-maintenance)

---

##  Vue d'ensemble

### Chiffres clés

```
 2,520 offres d'emploi
 890+ entreprises
 53 régions françaises
 500+ compétences uniques
 Mise à jour quotidienne
 Données depuis novembre 2024
```

### Architecture des données

```
┌─────────────────────────────────────────────────────────┐
│                  ARCHITECTURE DONNÉES                     │
└─────────────────────────────────────────────────────────┘

  Sources                ETL              Stockage
┌─────────┐          ┌────────┐        ┌──────────┐
│ France  │─────────▶│Extract │───────▶│          │
│Travail  │          │        │        │ SQLite   │
│  API    │          │Transform│        │  Star    │
└─────────┘          │        │        │ Schema   │
                     │ Load   │        │          │
┌─────────┐          │        │        │  2,520   │
│HelloWork│─────────▶│NLP/Geo │───────▶│  Rows    │
│Scraping │          │Enrich  │        │          │
└─────────┘          └────────┘        └──────────┘
```

---

## 🔌 Sources de données

### 1. France Travail API

**Type :** API REST officielle  
**URL :** `https://api.francetravail.io/partenaire/offresdemploi/v2`  
**Volume :** ~1,500 offres  
**Fréquence :** Quotidienne

**Exemple de données :**

```json
{
  "id": "174XBFZ",
  "intitule": "Data Scientist H/F",
  "description": "Nous recherchons un Data Scientist...",
  "dateCreation": "2025-01-10T09:30:00Z",
  "lieuTravail": {
    "libelle": "75 - PARIS 15",
    "latitude": 48.8534,
    "longitude": 2.3488
  },
  "entreprise": {
    "nom": "GOOGLE FRANCE",
    "description": "Leader mondial..."
  },
  "typeContrat": "CDI",
  "salaire": {
    "libelle": "Annuel de 50000.00 Euros à 75000.00 Euros"
  },
  "competences": [
    {
      "libelle": "Python",
      "exigence": "E"
    },
    {
      "libelle": "Machine Learning",
      "exigence": "S"
    }
  ]
}
```

**Mapping vers notre modèle :**

| API Field | Notre Field | Transformation |
|-----------|-------------|----------------|
| `id` | `offer_id` | Direct |
| `intitule` | `title` | Nettoyage |
| `description` | `description` | NLP extraction |
| `entreprise.nom` | `company_name` | Normalisation |
| `typeContrat` | `contract_type` | Mapping CDI/CDD/... |
| `lieuTravail.libelle` | `location` | Géo-enrichissement |

### 2. HelloWork (Web Scraping)

**Type :** Scraping HTML  
**URL :** `https://www.hellowork.com/fr-fr/emplois/`  
**Volume :** ~1,000 offres  
**Fréquence :** Hebdomadaire

**Structure HTML :**

```html
<article class="job-card">
  <h2 class="job-title">Data Scientist Senior</h2>
  <p class="company-name">Google France</p>
  <span class="location">Paris (75)</span>
  <span class="contract">CDI</span>
  <a href="/emplois/123456.html" class="job-link">
    Voir l'offre
  </a>
  <div class="job-description">
    Nous recherchons un Data Scientist...
  </div>
</article>
```

**Code d'extraction :**

```python
from bs4 import BeautifulSoup

def scrape_hellowork(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    
    offers = []
    for card in soup.find_all('article', class_='job-card'):
        offer = {
            'title': card.find('h2').text.strip(),
            'company': card.find('p', class_='company-name').text.strip(),
            'location': card.find('span', class_='location').text.strip(),
            'contract_type': card.find('span', class_='contract').text.strip(),
            'url': 'https://www.hellowork.com' + card.find('a')['href'],
            'description': card.find('div', class_='job-description').text.strip()
        }
        offers.append(offer)
    
    return offers
```

---

##  Modèle de données

### Star Schema

```sql
                    ┌──────────────┐
                    │  dim_region  │
                    │──────────────│
                    │ region_key PK│
                    │ region_name  │
                    │ latitude     │
                    │ longitude    │
                    └──────┬───────┘
                           │
    ┌──────────┐          │        ┌─────────────┐
    │dim_source│          │        │ dim_company │
    │──────────│          │        │─────────────│
    │source_key│          │        │ company_key │
    │name      │          │        │ company_name│
    └────┬─────┘          │        └──────┬──────┘
         │                │               │
         │    ┌───────────┴───────────┐   │
         └────│    fact_offers        │───┘
              │───────────────────────│
              │ offer_key PK          │
              │ uid UNIQUE            │◀── Déduplication
              │ title                 │
              │ description           │
              │ source_url            │◀── Important !
              │ salary                │
              │ remote                │
              │ source_key FK         │
              │ region_key FK         │
              │ company_key FK        │
              │ contract_key FK       │
              └───────────┬───────────┘
                          │
                          │ N:M
                          │
                  ┌───────▼───────────┐
                  │fact_offer_skill   │
                  │───────────────────│
                  │ offer_key FK      │
                  │ skill_key FK      │
                  └───────────────────┘
                          │
                  ┌───────▼───────┐
                  │   dim_skill   │
                  │───────────────│
                  │ skill_key PK  │
                  │ skill_name    │
                  │ skill_type    │
                  │ skill_category│
                  └───────────────┘
```

### Tables de dimensions

#### 1. dim_region (53 lignes)

```sql
CREATE TABLE dim_region (
    region_key INTEGER PRIMARY KEY AUTOINCREMENT,
    region_name TEXT NOT NULL UNIQUE,
    latitude REAL,
    longitude REAL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Exemple
INSERT INTO dim_region (region_name, latitude, longitude)
VALUES ('Île-de-France', 48.8566, 2.3522);
```

**Données :**

| region_key | region_name | latitude | longitude |
|------------|-------------|----------|-----------|
| 1 | Île-de-France | 48.8566 | 2.3522 |
| 2 | Auvergne-Rhône-Alpes | 45.7640 | 4.8357 |
| 3 | Occitanie | 43.6047 | 1.4442 |
| ... | ... | ... | ... |

#### 2. dim_skill (500+ lignes)

```sql
CREATE TABLE dim_skill (
    skill_key INTEGER PRIMARY KEY AUTOINCREMENT,
    skill_name TEXT NOT NULL UNIQUE,
    skill_type TEXT CHECK(skill_type IN ('competences', 'savoir_etre')),
    skill_category TEXT,  -- 'languages', 'cloud', 'tools'...
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Exemples
INSERT INTO dim_skill (skill_name, skill_type, skill_category)
VALUES 
    ('Python', 'competences', 'languages'),
    ('Machine Learning', 'competences', 'ai'),
    ('Communication', 'savoir_etre', 'soft_skills');
```

**Top 20 compétences :**

| Rang | skill_name | Occurrences | % |
|------|------------|-------------|---|
| 1 | Python | 1,689 | 67% |
| 2 | SQL | 1,210 | 48% |
| 3 | Machine Learning | 1,134 | 45% |
| 4 | Docker | 1,058 | 42% |
| 5 | TensorFlow | 957 | 38% |
| 6 | Kubernetes | 882 | 35% |
| 7 | Cloud (AWS/GCP/Azure) | 831 | 33% |
| 8 | Spark | 756 | 30% |
| 9 | Airflow | 693 | 28% |
| 10 | Git | 630 | 25% |

#### 3. dim_company (890+ lignes)

```sql
CREATE TABLE dim_company (
    company_key INTEGER PRIMARY KEY AUTOINCREMENT,
    company_name TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**Top entreprises :**

| Entreprise | Offres |
|------------|--------|
| Google | 45 |
| Meta | 38 |
| Amazon | 35 |
| Microsoft | 32 |
| Apple | 28 |

### Table de faits

#### fact_offers (2,520 lignes)

```sql
CREATE TABLE fact_offers (
    offer_key INTEGER PRIMARY KEY AUTOINCREMENT,
    
    -- Identifiants
    uid TEXT NOT NULL UNIQUE,  -- MD5 hash pour déduplication
    offer_id TEXT NOT NULL,
    
    -- Clés étrangères
    source_key INTEGER,
    region_key INTEGER,
    company_key INTEGER,
    contract_key INTEGER,
    
    -- Attributs
    title TEXT NOT NULL,
    source_url TEXT,           
    location TEXT,
    salary TEXT,
    remote TEXT,
    published_date TEXT,
    description TEXT,
    
    -- Métriques
    skills_count INTEGER DEFAULT 0,
    competences_count INTEGER DEFAULT 0,
    savoir_etre_count INTEGER DEFAULT 0,
    
    -- Traçabilité
    added_by TEXT DEFAULT 'import',
    added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (source_key) REFERENCES dim_source(source_key),
    FOREIGN KEY (region_key) REFERENCES dim_region(region_key),
    FOREIGN KEY (company_key) REFERENCES dim_company(company_key),
    FOREIGN KEY (contract_key) REFERENCES dim_contract(contract_key)
);
```

**Exemple de ligne :**

```
offer_key: 1
uid: 84b8ca8df812d5a779f3fbafe55ce8a0
title: Data Scientist Senior IA
source_url: https://www.hellowork.com/fr-fr/emplois/72337185.html
company_name: Talan
region_name: Île-de-France
contract_type: CDI
remote: yes
skills_count: 12
```

### Index de performance

```sql
-- Index unique sur UID (évite doublons)
CREATE UNIQUE INDEX idx_offers_uid ON fact_offers(uid);

-- Index sur clés étrangères
CREATE INDEX idx_offers_source ON fact_offers(source_key);
CREATE INDEX idx_offers_region ON fact_offers(region_key);
CREATE INDEX idx_offers_company ON fact_offers(company_key);

-- Index sur colonnes de recherche
CREATE INDEX idx_offers_title ON fact_offers(title);
CREATE INDEX idx_offers_remote ON fact_offers(remote);
```

---

##  Pipeline ETL

### Processus complet

```
┌─────────────────────────────────────────────────┐
│              PIPELINE ETL DÉTAILLÉ              │
└─────────────────────────────────────────────────┘

1. EXTRACT (Extraction)
   ├─ France Travail API
   │  └─ GET /offresdemploi/v2/search
   │     → JSON response
   │     → ~1,500 offres
   │
   └─ HelloWork Scraping
      └─ Parse HTML avec BeautifulSoup
         → Liste d'offres
         → ~1,000 offres

2. TRANSFORM (Transformation)
   ├─ Nettoyage
   │  ├─ Suppression doublons
   │  ├─ Normalisation texte
   │  └─ Validation format
   │
   ├─ Enrichissement
   │  ├─ Extraction compétences (NLP)
   │  │  └─ Regex + patterns + NER
   │  ├─ Géolocalisation
   │  │  └─ Commune → Région
   │  └─ Génération UID
   │     └─ MD5(offer_id + source)
   │
   └─ Structuration
      └─ CSV → DataFrame Pandas

3. LOAD (Chargement)
   ├─ Dimensions (INSERT OR IGNORE)
   │  ├─ dim_region
   │  ├─ dim_company
   │  ├─ dim_contract
   │  └─ dim_skill
   │
   ├─ Faits (INSERT OR IGNORE)
   │  └─ fact_offers (avec uid unique)
   │
   └─ Associations (INSERT OR IGNORE)
      └─ fact_offer_skill (N:M)
```

### Code ETL (simplifié)

```python
# database/etl_pipeline.py

class ETLPipeline:
    def run(self, csv_path: str):
        # 1. EXTRACT
        df = pd.read_csv(csv_path)
        print(f"✅ {len(df)} offres extraites")
        
        # 2. TRANSFORM
        df = self.clean_data(df)
        df = self.enrich_data(df)
        df = self.deduplicate(df)
        print(f"✅ {len(df)} offres transformées")
        
        # 3. LOAD
        self.load_dimensions(df)
        self.load_facts(df)
        self.load_associations(df)
        print(f"✅ {len(df)} offres chargées")
    
    def clean_data(self, df):
        """Nettoyage"""
        df = df.dropna(subset=['title', 'company'])
        df['title'] = df['title'].str.strip()
        df['description'] = df['description'].str.lower()
        return df
    
    def enrich_data(self, df):
        """Enrichissement"""
        # Extraction compétences
        df['competences'] = df['description'].apply(
            self.extract_skills
        )
        
        # Géolocalisation
        df['region'] = df['location'].apply(
            self.geocode_region
        )
        
        # Génération UID
        df['uid'] = df.apply(
            lambda row: hashlib.md5(
                f"{row['offer_id']}{row['source']}".encode()
            ).hexdigest(),
            axis=1
        )
        
        return df
    
    def extract_skills(self, description):
        """Extraction NLP"""
        skills = []
        
        # Patterns regex
        patterns = {
            'Python': r'\bPython\b',
            'SQL': r'\bSQL\b',
            'Docker': r'\bDocker\b',
            'Machine Learning': r'\bMachine Learning\b|\bML\b'
        }
        
        for skill, pattern in patterns.items():
            if re.search(pattern, description, re.I):
                skills.append(skill)
        
        return skills
```

---

##  Qualité des données

### Métriques de qualité

```python
# Analyse de qualité
def data_quality_report(df):
    report = {
        'total_rows': len(df),
        'duplicates': df.duplicated(subset=['uid']).sum(),
        'missing_title': df['title'].isna().sum(),
        'missing_company': df['company'].isna().sum(),
        'missing_url': df['source_url'].isna().sum(),
        'invalid_dates': (df['published_date'] == 'N/A').sum(),
    }
    
    return report

# Exemple de résultat
{
    'total_rows': 2520,
    'duplicates': 0,           # ✅ Aucun doublon
    'missing_title': 0,        # ✅ 100% complétude
    'missing_company': 23,     # ⚠️ 0.9% manquant
    'missing_url': 0,          # ✅ Toutes les URLs présentes
    'invalid_dates': 156       # ⚠️ 6.2% dates invalides
}
```

### Validation des données

```sql
-- Vérifier les doublons
SELECT uid, COUNT(*) as count
FROM fact_offers
GROUP BY uid
HAVING count > 1;

-- Vérifier les URLs
SELECT COUNT(*) as offers_with_url
FROM fact_offers
WHERE source_url IS NOT NULL 
  AND source_url LIKE 'http%';

-- Vérifier la complétude
SELECT 
    COUNT(*) as total,
    SUM(CASE WHEN title IS NULL THEN 1 ELSE 0 END) as missing_title,
    SUM(CASE WHEN source_url IS NULL THEN 1 ELSE 0 END) as missing_url
FROM fact_offers;
```

---

## 🔍 Requêtes SQL

### Requêtes utiles

#### 1. Top 10 compétences

```sql
SELECT 
    ds.skill_name,
    COUNT(DISTINCT fos.offer_key) as offer_count,
    ROUND(COUNT(DISTINCT fos.offer_key) * 100.0 / 
          (SELECT COUNT(*) FROM fact_offers), 2) as percentage
FROM dim_skill ds
JOIN fact_offer_skill fos ON ds.skill_key = fos.skill_key
GROUP BY ds.skill_key
ORDER BY offer_count DESC
LIMIT 10;
```

#### 2. Offres par région

```sql
SELECT 
    dr.region_name,
    COUNT(fo.offer_key) as offer_count,
    AVG(fo.skills_count) as avg_skills
FROM dim_region dr
LEFT JOIN fact_offers fo ON dr.region_key = fo.region_key
GROUP BY dr.region_key
ORDER BY offer_count DESC;
```

#### 3. Compétences d'une offre

```sql
SELECT 
    fo.title,
    GROUP_CONCAT(ds.skill_name, ', ') as skills
FROM fact_offers fo
JOIN fact_offer_skill fos ON fo.offer_key = fos.offer_key
JOIN dim_skill ds ON fos.skill_key = ds.skill_key
WHERE fo.offer_key = 1
GROUP BY fo.offer_key;
```

#### 4. Offres avec télétravail par région

```sql
SELECT 
    dr.region_name,
    COUNT(CASE WHEN fo.remote IN ('yes', 'oui') THEN 1 END) as remote_count,
    COUNT(*) as total_count,
    ROUND(COUNT(CASE WHEN fo.remote IN ('yes', 'oui') THEN 1 END) * 100.0 / COUNT(*), 1) as remote_pct
FROM dim_region dr
JOIN fact_offers fo ON dr.region_key = fo.region_key
GROUP BY dr.region_key
ORDER BY remote_pct DESC;
```

---

## 📤 Export & APIs

### Export CSV

```python
# Export complet
df = load_offers_with_skills()
df.to_csv('exports/all_offers.csv', index=False, encoding='utf-8')

# Export filtré
df_filtered = df[df['region_name'] == 'Île-de-France']
df_filtered.to_csv('exports/idf_offers.csv', index=False)
```

### Export JSON

```python
# Format JSON pour APIs
offers = df.to_dict('records')

with open('exports/offers.json', 'w', encoding='utf-8') as f:
    json.dump(offers, f, ensure_ascii=False, indent=2)
```

### API REST (exemple Flask)

```python
from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/api/offers')
def get_offers():
    df = load_offers_with_skills()
    return jsonify(df.to_dict('records'))

@app.route('/api/offers/<int:offer_id>')
def get_offer(offer_id):
    offer = get_offer_by_id(offer_id)
    return jsonify(offer)

@app.route('/api/stats')
def get_stats():
    return jsonify({
        'total_offers': 2520,
        'total_companies': 890,
        'total_regions': 53
    })
```

---

## 🔧 Maintenance

### Backup régulier

```bash
# Backup quotidien
#!/bin/bash
DATE=$(date +%Y%m%d)
sqlite3 database/jobs.db ".backup database/backups/jobs_$DATE.db"

# Compression
gzip database/backups/jobs_$DATE.db

# Nettoyage (garde 30 jours)
find database/backups/ -mtime +30 -delete
```

### Mise à jour des données

```bash
# Script de mise à jour
python scraping/france_travail_api.py > data/raw/new_offers.csv
python database/etl_pipeline.py --input data/raw/new_offers.csv
```

### Optimisation

```sql
-- Reconstruire les index
REINDEX;

-- Analyser les tables
ANALYZE;

-- Vacuum (compacter la BDD)
VACUUM;
```

---

<div align="center">

** Données structurées = Analyses puissantes !**

[⬆️ Retour en haut](#-guide-des-données---job-radar)

</div>