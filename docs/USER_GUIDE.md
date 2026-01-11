#  Guide Utilisateur - Job Radar

<div align="center">

**Version 1.0 | Janvier 2025**

*Guide complet pour utiliser Job Radar comme un pro*

[ Accueil](../README.md) • [ Guide Dev](DEVELOPER_GUIDE.md) • [ Docker](DOCKER_GUIDE.md) • [ Données](DATA_GUIDE.md)

---

</div>

## Table des matières

1. [Introduction](#introduction)
2. [Démarrage rapide](#démarrage-rapide)
3. [Navigation](#navigation)
4. [Page Explorer](#page-explorer)
5. [Page Géographie](#page-géographie)
6. [Page Analytics](#page-analytics)
7. [Page Intelligence](#page-intelligence)
8. [Assistant IA](#assistant-ia)
9. [Contribuer](#contribuer)
10. [Astuces & Conseils](#astuces--conseils)
11. [FAQ](#faq)
12. [Résolution de problèmes](#résolution-de-problèmes)

---

## Introduction

### Qu'est-ce que RADAR ?

**RADAR** est votre assistant intelligent pour explorer le marché de l'emploi dans la Data, l'IA et l'Analytics en France. Il vous permet de :

-  **Découvrir** plus de 2 500 offres d'emploi ciblées
-  **Visualiser** la répartition géographique des opportunités
-  **Analyser** les tendances et compétences demandées
-  **Comprendre** le marché grâce à l'IA et au NLP
-  **Dialoguer** avec un assistant intelligent

### À qui s'adresse ce guide ?

-  **Étudiants** cherchant leur premier emploi
-  **Professionnels** en reconversion
-  **Recruteurs** analysant le marché
-  **Analystes** étudiant les tendances RH
-  **Curieux** du marché de la Data

---

## Démarrage rapide

### Accéder à Job Radar

**Option 1 : Version déployée**
```
 https://job-radar.streamlit.app
```

**Option 2 : Version locale**
```bash
streamlit run app/home.py
```

**Option 3 : Docker**
```bash
docker run -p 8501:8501 job-radar
# Accès : http://localhost:8501
```

### Premier lancement

1. **Page d'accueil** : Vous arrivez sur le dashboard principal
2. **Navigation** : Menu latéral avec 6 pages
3. **Statistiques** : Vue d'ensemble des données
4. **Actions rapides** : Boutons d'accès direct

<div align="center">

```
┌─────────────────────────────────────────────────────────┐
│   Job Radar                              ☰ Menu         │
├─────────────────────────────────────────────────────────┤
│                                                         │
│   Statistiques Globales                                 │
│  ┌────────┬────────┬────────┬────────┐                  │
│  │ 2,520  │  890   │   53   │  500   │                  │
│  │ Offres │Entrep. │Régions │Compét. │                  │
│  └────────┴────────┴────────┴────────┘                  │
│                                                         │
│   Actions Rapides                                       │
│  [Explorer] [Carte] [Stats] [IA]                        │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

</div>

---

## Navigation

### Menu principal

Le menu latéral (icône ☰) donne accès à 6 pages :

| Page | Icône | Description |
|------|-------|-------------|
| **Explorer** |  | Recherche et filtrage des offres |
| **Géographie** |  | Cartographie interactive |
| **Analytics** |  | Statistiques et graphiques |
| **Intelligence** |  | Analyses NLP avancées |
| **Assistant** |  | IA conversationnelle |
| **Contribuer** |  | Ajout d'offres |

### Raccourcis clavier

| Touche | Action |
|--------|--------|
| `Ctrl + R` | Recharger la page |
| `Ctrl + F` | Rechercher dans la page |
| `Esc` | Fermer le menu latéral |

---

## Page Explorer

### Vue d'ensemble

La page **Explorer** est votre point d'entrée pour naviguer parmi les 2 520 offres.

### Interface

```
┌─────────────────────────────────────────────────────────┐
│   Trouvez Votre Job Idéal                               │
│  Plus de 2 500 opportunités Data • IA • Cloud           │
├─────────────────────────────────────────────────────────┤
│   Rechercher des Offres                                 │
│  ┌────────────────────────────────────────────────┐     │
│  │  Data Scientist, Python, Machine Learning      │     │
│  └────────────────────────────────────────────────┘     │
│                                                         │
│   Région              Type de contrat                   │
│  [Île-de-France    ▼]   [CDI              ▼]            │
│                                                         │
│  [ Rechercher]                                          │
└─────────────────────────────────────────────────────────┘
```

###  Recherche

#### Recherche par mot-clé

**Exemples de recherches :**

```
"Data Scientist"        → Trouve tous les postes DS
"Python Machine Learning" → Offres avec ces compétences
"Google"                → Offres de Google
"Paris"                 → Offres à Paris
```

**Conseils :**
-  Utilisez des mots-clés simples
-  Combinez plusieurs termes
-  La recherche est insensible à la casse

#### Filtres avancés

**1. Par région**

```
Toutes les régions
Île-de-France
Auvergne-Rhône-Alpes
Occitanie
...
```

**2. Par type de contrat**

```
Tous les contrats
CDI                    ← Le plus courant
CDD
Freelance
Stage
Alternance
```

**3. Combinaison**

```
Recherche : "Data Scientist"
Région : Île-de-France
Contrat : CDI
→ 23 offres trouvées
```

### Résultats

#### Statistiques

Après une recherche, 4 cartes affichent :

```
┌────────┬────────┬────────┬────────┐
│   23   │   12   │    1   │   18   │
│ Offres │Entrep. │ Région │Télétrav│
└────────┴────────┴────────┴────────┘
```

#### Liste des offres

Chaque offre affiche :

```
╔═══════════════════════════════════════════════════════╗
║ Data Scientist Senior                     Score 92%║
║  Google France                                      ║
║  Île-de-France •  CDI •  Télétravail           ║
║  60K-90K € •  15 compétences                      ║
║                                                        ║
║ 💎 Python  Machine Learning  SQL  TensorFlow  Docker ║
║                                                        ║
║ ┌────────────┬────────────┬──────────────────┐       ║
║ │ Détails  │ Favoris  │ Postuler      │       ║
║ └────────────┴────────────┴──────────────────┘       ║
╚═══════════════════════════════════════════════════════╝
```

#### Actions disponibles

**1.  Voir la description**

Cliquez pour afficher :
- Description complète (200-500 mots)
- Compétences détaillées
- Informations entreprise
- Lien vers l'offre originale

**2.  Ajouter aux favoris**

- Marque l'offre pour la retrouver plus tard
- Accessible depuis toutes les pages
- Compteur de favoris dans le footer

**3.  Postuler**

- **S'ouvre dans un nouvel onglet**
- Redirige vers le site d'origine
- HelloWork, France Travail, etc.

###  Cas d'usage

#### Cas 1 : Chercher un CDI Data Scientist à Paris

```
1. Recherche : "Data Scientist"
2. Région : Île-de-France
3. Contrat : CDI
4. Clic :  Rechercher
→ Résultat : 23 offres
```

#### Cas 2 : Stage Machine Learning Lyon

```
1. Recherche : "Machine Learning"
2. Région : Auvergne-Rhône-Alpes
3. Contrat : Stage
4. Clic :  Rechercher
→ Résultat : 8 offres
```

#### Cas 3 : Freelance Python télétravail

```
1. Recherche : "Python Freelance"
2. Région : Toutes les régions
3. Contrat : Freelance
4. Regarder les badges  pour le télétravail
→ Résultat : 156 offres, dont 89 en télétravail
```

---

## Page Géographie

### Vue d'ensemble

Visualisez la répartition géographique des offres sur une carte interactive de France.

### Carte interactive

```
┌─────────────────────────────────────────────────┐
│   Cartographie des Offres d'Emploi           │
├─────────────────────────────────────────────────┤
│                                                  │
│               CARTE DE FRANCE                 │
│                                                  │
│      ●  Île-de-France (1,234)                  │
│                                                  │
│         ● Auvergne (342)                       │
│                                                  │
│                    ● Occitanie (456)           │
│                                                  │
│  Légende :                                      │
│  ● Faible   ● Moyen   ● Élevé                 │
└─────────────────────────────────────────────────┘
```

### Interactions

**Zoom :**
- Molette de la souris
- Boutons `+` et `-`
- Double-clic pour zoomer

**Navigation :**
- Clic-glisser pour déplacer
- Bouton  pour recentrer

**Informations :**
- Survol : Nom de la région
- Clic : Détails complets
  - Nombre d'offres
  - Top 5 compétences
  - Types de contrat
  - Entreprises principales

### Filtres

```
Compétence : [Python        ▼]
Type contrat : [CDI          ▼]
```

**Exemple :**
```
Compétence : Python
→ La carte montre où Python est le plus demandé
```

### Heatmap

Visualisation en chaleur :
-  Bleu : Peu d'offres
-  Jaune : Nombre moyen
-  Rouge : Forte concentration

---

## Page Analytics

### Vue d'ensemble

Statistiques avancées et graphiques interactifs.

### Sections disponibles

#### 1.  Évolution temporelle

```
Graphique linéaire : Nombre d'offres / mois
→ Identifiez les périodes de recrutement
```

#### 2.  Top Compétences

```
┌─────────────────────────────────────┐
│  Top 10 Compétences                 │
├─────────────────────────────────────┤
│  1. Python            ████████ 67%  │
│  2. Machine Learning  ██████░ 54%  │
│  3. SQL               █████░░ 48%  │
│  4. Docker            ████░░░ 42%  │
│  5. TensorFlow        ███░░░░ 38%  │
│  ...                               │
└─────────────────────────────────────┘
```

#### 3.  Répartition des contrats

```
Graphique circulaire :
CDI : 62%
CDD : 18%
Freelance : 12%
Stage : 5%
Alternance : 3%
```

#### 4.  Top Régions

```
Graphique en barres horizontales
Île-de-France    ████████████████ 1,234
Auvergne-Rhône   ██████████░░░░░░   456
Occitanie        ████████░░░░░░░░   342
...
```

#### 5.  Télétravail

```
Taux de télétravail par région
Île-de-France : 78%
PACA : 65%
Auvergne : 72%
...
```

### Graphiques interactifs

Tous les graphiques sont **interactifs** (Plotly) :

**Actions disponibles :**
-  Zoom : Sélectionner une zone
-  Hover : Détails au survol
-  Screenshot : Bouton en haut à droite
-  Export : Télécharger en PNG
-  Reset : Double-clic

### Filtres globaux

```
Période : [Derniers 30 jours ▼]
Région : [Toutes ▼]
Compétence : [Toutes ▼]
```

### Export de données

```
[ Exporter en CSV]
[ Exporter en JSON]
[ Exporter en Excel]
```

**Contenu exporté :**
- Toutes les offres filtrées
- Métadonnées complètes
- Statistiques agrégées

---

## Page Intelligence

### Vue d'ensemble

Analyses NLP avancées et clustering.

### Sections disponibles

#### 1.  Nuage de mots

```
         Python
    Machine          Data
  Learning    SQL        Analysis
      TensorFlow  Docker
   Deep     Cloud    Kubernetes
      Learning  AWS    Spark
```

**Interprétation :**
- Taille = Fréquence
- Couleur = Importance (TF-IDF)

#### 2. 🧩 Clustering

```
K-Means clustering (5 clusters)

Cluster 1 : Data Scientists (456 offres)
  Mots-clés : Python, ML, Statistics

Cluster 2 : Data Engineers (342 offres)
  Mots-clés : SQL, ETL, Airflow

Cluster 3 : ML Engineers (298 offres)
  Mots-clés : TensorFlow, PyTorch, MLOps

...
```

**Visualisation :**
- Graphique 2D (PCA)
- Points colorés par cluster
- Hover pour détails

#### 3.  Analyse de similarité

```
Recherche par similarité
┌────────────────────────────────────────┐
│ Sélectionnez une offre de référence   │
│ [Data Scientist - Google          ▼]  │
└────────────────────────────────────────┘

Offres similaires :
1. Data Scientist Senior - Meta (95%)
2. ML Engineer - Amazon (89%)
3. Data Scientist - Apple (87%)
```

#### 4.  TF-IDF

```
Top termes par importance

Python          ████████████ 0.89
Machine Learning ███████████░ 0.76
Deep Learning   ██████████░░ 0.68
SQL             █████████░░░ 0.62
```

### Options d'analyse

```
Nombre de clusters : [5 ▼]
Algorithme : [K-Means ▼]
Méthode TF-IDF : [Scikit-learn ▼]
```

---

## Assistant IA

### Vue d'ensemble

Dialoguez avec un assistant intelligent propulsé par **Mistral AI**.

### Interface

```
┌─────────────────────────────────────────────────┐
│   Assistant Job Radar                         │
│  Propulsé par Mistral AI                        │
├─────────────────────────────────────────────────┤
│   Conversation                                │
│  ┌───────────────────────────────────────────┐ │
│  │ Vous : Bonjour !                          │ │
│  │                                           │ │
│  │  : Bonjour ! Je suis votre assistant   │ │
│  │ pour analyser le marché de l'emploi.     │ │
│  │ Comment puis-je vous aider ?             │ │
│  └───────────────────────────────────────────┘ │
│                                                  │
│  ┌───────────────────────────────────────────┐ │
│  │ Votre message...                          │ │
│  └───────────────────────────────────────────┘ │
│  [Envoyer]                                      │
└─────────────────────────────────────────────────┘
```

### Exemples de questions

#### 1. Analyse de profil

```
Vous : Je suis Data Scientist avec 3 ans d'expérience 
       en Python et ML. Quelles offres me correspondent ?

     : D'après votre profil, je vous recommande 23 offres
     dont :
     - Data Scientist Senior chez Google
     - ML Engineer chez Meta
     - Data Analyst Lead chez Amazon
     
     Vos points forts matchent particulièrement avec
     les offres nécessitant Python et Machine Learning.
```

#### 2. Recommandation de compétences

```
Vous : Quelles compétences devrais-je acquérir pour
       progresser ?

 : D'après l'analyse du marché :
     
      Compétences en forte demande :
     1. Docker (+45% d'offres)
     2. Kubernetes (+38%)
     3. MLOps (+52%)
     
      Je recommande de vous former sur Docker
     en priorité, c'est demandé dans 67% des offres
     senior.
```

#### 3. Analyse géographique

```
Vous : Où trouver le plus d'offres Data Scientist ?

 : Top 3 régions pour Data Scientist :
     
     1. Île-de-France : 456 offres (78% télétravail)
     2. Auvergne-Rhône-Alpes : 123 offres
     3. Occitanie : 89 offres
     
     💡 Si vous cherchez du télétravail, l'Île-de-France
     est la meilleure option avec 356 postes en remote.
```

#### 4. Comparaison de régions

```
Vous : Compare Paris et Lyon pour un Data Engineer

 : Comparaison Paris vs Lyon :
     
      Paris (Île-de-France)
     - 234 offres Data Engineer
     - Salaire moyen : 55K-75K €
     - 82% télétravail
     - Compétences : Python, SQL, Airflow
     
      Lyon (Auvergne-Rhône-Alpes)
     - 67 offres Data Engineer
     - Salaire moyen : 45K-60K €
     - 68% télétravail
     - Compétences : SQL, ETL, Cloud
```

### Suggestions de prompts

Le système propose des questions :

```
 Suggestions :
• Analyse mon profil
• Quelles compétences acquérir ?
• Compare Paris et Lyon
• Tendances du marché
• Salaires par région
```

---

## Contribuer

### Vue d'ensemble

Ajoutez vos propres offres à la base de données.

### Formulaire

```
┌─────────────────────────────────────────────────┐
│  ➕ Ajouter une Offre d'Emploi                  │
├─────────────────────────────────────────────────┤
│  Titre du poste *                               │
│  ┌───────────────────────────────────────────┐ │
│  │ Data Scientist Senior                     │ │
│  └───────────────────────────────────────────┘ │
│                                                  │
│  Entreprise *                                   │
│  ┌───────────────────────────────────────────┐ │
│  │ Google France                             │ │
│  └───────────────────────────────────────────┘ │
│                                                  │
│  Région *                                       │
│  [Île-de-France                            ▼] │
│                                                  │
│  Type de contrat *                              │
│  [CDI                                      ▼] │
│                                                  │
│  URL de l'offre *                               │
│  ┌───────────────────────────────────────────┐ │
│  │ https://careers.google.com/...           │ │
│  └───────────────────────────────────────────┘ │
│                                                  │
│  Description *                                  │
│  ┌───────────────────────────────────────────┐ │
│  │ Nous recherchons un Data Scientist...    │ │
│  │                                           │ │
│  └───────────────────────────────────────────┘ │
│                                                  │
│  [ Ajouter l'offre]                           │
└─────────────────────────────────────────────────┘
```

### Validation

Le système vérifie automatiquement :
-  Absence de doublons (via URL)
-  Complétude des champs obligatoires
-  Format de l'URL
-  Extraction des compétences

### Confirmation

```
 Offre ajoutée avec succès !

L'offre "Data Scientist Senior - Google France"
a été ajoutée à la base de données.

• 12 compétences détectées
• Région : Île-de-France
• Type : CDI

[Voir l'offre] [Ajouter une autre]
```

---

## Astuces & Conseils

### Recherche efficace

**1. Utilisez des synonymes**
```
"Data Scientist" = "Scientist Données" = "DS"
"Machine Learning" = "ML" = "Apprentissage automatique"
```

**2. Combinez les filtres**
```
Recherche + Région + Contrat = Résultats précis
```

**3. Sauvegardez vos favoris**
```
Marquez les offres intéressantes pour les retrouver
```

### Analyse avancée

**1. Utilisez l'assistant IA**
```
Posez des questions complexes pour des insights
```

**2. Comparez les régions**
```
Utilisez Analytics pour identifier les meilleures zones
```

**3. Analysez les tendances**
```
Regardez l'évolution temporelle pour anticiper
```

### Export de données

**1. CSV pour Excel**
```
Analyse dans Excel/Google Sheets
```

**2. JSON pour développeurs**
```
Intégration dans vos propres outils
```

---

## FAQ

### Questions fréquentes

**Q : Combien d'offres sont disponibles ?**
> R : Plus de 2 520 offres, mises à jour quotidiennement.

**Q : Les offres sont-elles à jour ?**
> R : Oui, collecte automatique quotidienne via API et scraping.

**Q : Puis-je postuler directement ?**
> R : Oui, le bouton "🚀 Postuler" redirige vers le site d'origine.

**Q : Les favoris sont-ils sauvegardés ?**
> R : Oui, pendant votre session. Pensez à exporter si besoin.

**Q : L'assistant IA est-il gratuit ?**
> R : Oui, propulsé par Mistral AI.

**Q : Puis-je exporter les données ?**
> R : Oui, en CSV, JSON ou Excel depuis Analytics.

**Q : Comment ajouter une offre ?**
> R : Via la page "Contribuer" avec le formulaire.

**Q : Les données sont-elles anonymisées ?**
> R : Oui, aucune donnée personnelle n'est collectée.

---

## Résolution de problèmes

### Problèmes courants

#### 1. La page ne charge pas

**Solutions :**
```
1. Rafraîchir la page (Ctrl+R)
2. Vider le cache navigateur
3. Vérifier la connexion Internet
4. Essayer un autre navigateur
```

#### 2. Bouton "Postuler" grisé

**Cause :** Pas d'URL pour cette offre

**Solution :** Rechercher l'offre manuellement sur le site source

#### 3. Carte géographique ne s'affiche pas

**Solutions :**
```
1. Autoriser JavaScript
2. Désactiver bloqueurs de pub
3. Attendre le chargement complet
```

#### 4. Assistant IA ne répond pas

**Solutions :**
```
1. Vérifier la clé API Mistral
2. Attendre quelques secondes
3. Reformuler la question
```

#### 5. Export CSV vide

**Solutions :**
```
1. Appliquer d'abord des filtres
2. Vérifier qu'il y a des résultats
3. Réessayer l'export
```



**Informations à fournir :**
- Description du problème
- Étapes de reproduction
- Navigateur et version
- Captures d'écran (si possible)

---

## Support

### Besoin d'aide ?

**Documentation :**
- 🔧 [Guide Développeur](DEVELOPER_GUIDE.md)
- 🐳 [Guide Docker](DOCKER_GUIDE.md)
- 📊 [Guide Données](DATA_GUIDE.md)


---

<div align="center">

**Merci d'utiliser Job Radar ! 🎯**

*N'hésitez pas à partager ce guide avec vos collègues*

[⬆️ Retour en haut](#guide-utilisateur---job-radar)

</div>
