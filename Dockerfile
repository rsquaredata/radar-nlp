# Utilisation d'une image Python légère
FROM python:3.11-slim

# Éviter la génération de fichiers .pyc et activer le mode non-interactif
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Installation des dépendances système nécessaires pour DuckDB et l'UI
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    software-properties-common \
    && rm -rf /var/lib/apt/lists/*

# Création du répertoire de travail
WORKDIR /app

# Copie des fichiers de dépendances
COPY requirements.txt .

# Installation des bibliothèques Python
RUN pip install --no-cache-dir -r requirements.txt

# Copie de l'intégralité du projet
COPY . .

# Exposition du port par défaut de Streamlit
EXPOSE 8501

# Commande de lancement
ENTRYPOINT ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
