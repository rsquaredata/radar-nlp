# Dockerfile pour RADAR
FROM python:3.11-slim

# Empêcher la création de fichiers .pyc et forcer le flush stdout
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Dépendances système minimales
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Répertoire de travail
WORKDIR /app

# Copier les fichiers de configuration principaux
COPY pyproject.toml README.md ./

# Copier le code source et l'app
COPY src ./src
COPY main.py ./main.py
COPY pages ./pages

# Créer les dossiers de données (seront montés en volume depuis l'hôte)
RUN mkdir -p data/db data/raw data/geo data/static scripts

# Copier les scripts (s'ils existent) et éventuellement des données statiques
COPY scripts ./scripts
COPY data/geo ./data/geo
COPY data/static ./data/static

# Installer les dépendances Python
RUN pip install --upgrade pip setuptools wheel \
    && pip install -e . \
    && pip install \
        streamlit \
        duckdb \
        pandas \
        numpy \
        scikit-learn \
        requests \
        beautifulsoup4 \
        lxml \
        spacy \
        sentence-transformers \
        matplotlib \
        plotly \
        wordcloud

# Exposer le port Streamlit
EXPOSE 8501

# Commande par défaut : lancer l'app Streamlit
CMD ["streamlit", "run", "main.py", "--server.address=0.0.0.0", "--server.port=8501"]