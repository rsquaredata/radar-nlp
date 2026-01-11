# Guide Docker - RADAR

<div align="center">

**Déploiement et Containerisation**

*Docker, Docker Compose, et Production*

[ Accueil](../README.md) • [ User](USER_GUIDE.md) • [ Dev](DEVELOPER_GUIDE.md) • [ Data](DATA_GUIDE.md)

---

</div>

##  Table des matières

1. [Introduction](#introduction)
2. [Installation Docker](#installation-docker)
3. [Dockerfile](#dockerfile)
4. [Docker Compose](#docker-compose)
5. [Build & Run](#build--run)
6. [Volumes & Persistance](#volumes--persistance)
7. [Environnement Production](#environnement-production)
8. [Optimisations](#optimisations)
9. [Ressources](#ressources)

---

##  Introduction

### Pourquoi Docker ?

✅ **Portabilité** : Fonctionne partout (Win/Mac/Linux)
✅ **Isolation** : Environnement propre et reproductible
✅ **Simplicité** : Installation en 1 commande
✅ **Production-ready** : Prêt pour le déploiement

### Architecture Docker

```
┌────────────────────────────────────────────┐
│         DOCKER CONTAINER                   │
│  ┌──────────────────────────────────────┐  │
│  │  Streamlit App (Port 8501)           │  │
│  │  - Python 3.11                       │  │
│  │  - Dependencies installées           │  │
│  │  - Database SQLite                   │  │
│  └──────────────────────────────────────┘  │
│  ┌──────────────────────────────────────┐  │
│  │  Volume : /app/database              │  │
│  │  (Persistance données)               │  │
│  └──────────────────────────────────────┘  │
└────────────────────────────────────────────┘
         ↓ Port Mapping
    localhost:8501
```

---

##  Installation Docker

### Windows

```powershell
# 1. Télécharger Docker Desktop
https://www.docker.com/products/docker-desktop/

# 2. Installer et redémarrer

# 3. Vérifier l'installation
docker --version
docker-compose --version
```

### macOS

```bash
# 1. Via Homebrew
brew install --cask docker

# 2. Lancer Docker Desktop
open /Applications/Docker.app

# 3. Vérifier
docker --version
```

### Linux (Ubuntu/Debian)

```bash
# 1. Installer Docker
sudo apt update
sudo apt install docker.io docker-compose

# 2. Ajouter l'utilisateur au groupe docker
sudo usermod -aG docker $USER

# 3. Redémarrer la session
newgrp docker

# 4. Vérifier
docker --version
```

---

##  Dockerfile

### Structure

```dockerfile
# Image de base
FROM python:3.11-slim

# Métadonnées
LABEL maintainer="votre-email@example.com"
LABEL version="1.0"
LABEL description="Job Radar - Analyse emploi par NLP"

# Variables d'environnement
ENV PYTHONUNBUFFERED=1
ENV STREAMLIT_SERVER_PORT=8501
ENV STREAMLIT_SERVER_ADDRESS=0.0.0.0

# Créer le répertoire de travail
WORKDIR /app

# Copier les requirements
COPY requirements.txt .

# Installer les dépendances système
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    git \
    && rm -rf /var/lib/apt/lists/*

# Installer les dépendances Python
RUN pip install --no-cache-dir -r requirements.txt

# Copier le code source
COPY . .

# Créer les dossiers nécessaires
RUN mkdir -p database data/raw data/processed

# Exposer le port Streamlit
EXPOSE 8501

# Healthcheck
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8501/_stcore/health || exit 1

# Commande de démarrage
CMD ["streamlit", "run", "app/home.py", \
     "--server.port=8501", \
     "--server.address=0.0.0.0"]
```

### Optimisations

```dockerfile
# Multi-stage build (optimisé)
FROM python:3.11-slim AS builder

WORKDIR /app

# Installer uniquement les dépendances de build
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

# Stage final
FROM python:3.11-slim

WORKDIR /app

# Copier les packages depuis builder
COPY --from=builder /root/.local /root/.local

# Copier le code
COPY . .

# Ajouter les binaires Python au PATH
ENV PATH=/root/.local/bin:$PATH

EXPOSE 8501

CMD ["streamlit", "run", "app/home.py"]
```

### .dockerignore

```
# Fichier .dockerignore
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
venv/
env/
ENV/
.env
.git/
.gitignore
.vscode/
.idea/
*.md
Dockerfile
docker-compose.yml
tests/
docs/
*.log
.DS_Store
```

---

## 🐳 Docker Compose

### Configuration Basique

```yaml
# docker-compose.yml
version: '3.8'

services:
  job-radar:
    build: .
    container_name: job-radar-app
    ports:
      - "8501:8501"
    environment:
      - MISTRAL_API_KEY=${MISTRAL_API_KEY}
      - FRANCE_TRAVAIL_CLIENT_ID=${FRANCE_TRAVAIL_CLIENT_ID}
      - FRANCE_TRAVAIL_CLIENT_SECRET=${FRANCE_TRAVAIL_CLIENT_SECRET}
    volumes:
      - ./database:/app/database
      - ./data:/app/data
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8501/_stcore/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
```

### Configuration Avancée

```yaml
# docker-compose.prod.yml
version: '3.8'

services:
  job-radar:
    build:
      context: .
      dockerfile: Dockerfile.prod
    container_name: job-radar-prod
    ports:
      - "80:8501"
    environment:
      - ENVIRONMENT=production
      - LOG_LEVEL=INFO
    env_file:
      - .env.prod
    volumes:
      - db-data:/app/database:rw
      - app-logs:/app/logs:rw
    networks:
      - job-radar-network
    restart: always
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 2G
        reservations:
          cpus: '1'
          memory: 1G

volumes:
  db-data:
    driver: local
  app-logs:
    driver: local

networks:
  job-radar-network:
    driver: bridge
```

---

##  Build & Run

### Build Simple

```bash
# Construire l'image
docker build -t job-radar:latest .

# Options utiles
docker build -t job-radar:v1.0 --no-cache .  # Sans cache
docker build -t job-radar:latest --progress=plain .  # Logs détaillés
```

### Run Simple

```bash
# Lancer le conteneur
docker run -d \
  --name job-radar \
  -p 8501:8501 \
  --env-file .env \
  job-radar:latest

# Vérifier les logs
docker logs -f job-radar

# Arrêter
docker stop job-radar

# Supprimer
docker rm job-radar
```

### Docker Compose

```bash
# Build + Run en 1 commande
docker-compose up --build

# En arrière-plan
docker-compose up -d

# Arrêter
docker-compose down

# Arrêter et supprimer les volumes
docker-compose down -v
```

### Commandes utiles

```bash
# Lister les conteneurs
docker ps

# Lister les images
docker images

# Entrer dans le conteneur
docker exec -it job-radar bash

# Copier un fichier
docker cp job-radar:/app/database/jobs.db ./backup.db

# Voir les logs en temps réel
docker logs -f --tail 100 job-radar

# Statistiques d'utilisation
docker stats job-radar
```

---

##  Volumes & Persistance

### Types de volumes

**1. Bind Mount (recommandé pour dev)**

```bash
# Windows
docker run -p 8501:8501 \
  -v ${PWD}\database:/app/database \
  job-radar

# Linux/Mac
docker run -p 8501:8501 \
  -v $(pwd)/database:/app/database \
  job-radar
```

**2. Named Volume (recommandé pour prod)**

```bash
# Créer le volume
docker volume create job-radar-db

# Utiliser le volume
docker run -p 8501:8501 \
  -v job-radar-db:/app/database \
  job-radar

# Lister les volumes
docker volume ls

# Inspecter
docker volume inspect job-radar-db
```

**3. Volumes multiples**

```bash
docker run -p 8501:8501 \
  -v job-radar-db:/app/database \
  -v job-radar-data:/app/data \
  -v job-radar-logs:/app/logs \
  job-radar
```

### Backup & Restore

```bash
# Backup
docker run --rm \
  -v job-radar-db:/data \
  -v $(pwd):/backup \
  alpine tar czf /backup/db-backup-$(date +%Y%m%d).tar.gz /data

# Restore
docker run --rm \
  -v job-radar-db:/data \
  -v $(pwd):/backup \
  alpine tar xzf /backup/db-backup-20250110.tar.gz -C /
```

---

##  Environnement Production

### Dockerfile.prod

```dockerfile
FROM python:3.11-slim AS builder

WORKDIR /build
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

FROM python:3.11-slim

# Security : non-root user
RUN useradd -m -u 1000 appuser

WORKDIR /app

COPY --from=builder /root/.local /home/appuser/.local
COPY --chown=appuser:appuser . .

USER appuser
ENV PATH=/home/appuser/.local/bin:$PATH

EXPOSE 8501

CMD ["streamlit", "run", "app/home.py", \
     "--server.port=8501", \
     "--server.address=0.0.0.0", \
     "--server.maxUploadSize=10", \
     "--server.enableCORS=false"]
```

### Configuration Nginx (Reverse Proxy)

```nginx
# nginx.conf
upstream streamlit {
    server job-radar:8501;
}

server {
    listen 80;
    server_name job-radar.example.com;

    location / {
        proxy_pass http://streamlit;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 86400;
    }
}
```

### Docker Compose Production

```yaml
version: '3.8'

services:
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
      - ./ssl:/etc/nginx/ssl:ro
    depends_on:
      - job-radar
    networks:
      - prod-network

  job-radar:
    build:
      context: .
      dockerfile: Dockerfile.prod
    environment:
      - ENVIRONMENT=production
    env_file:
      - .env.prod
    volumes:
      - db-data:/app/database:rw
    networks:
      - prod-network
    restart: always

volumes:
  db-data:

networks:
  prod-network:
    driver: bridge
```

---

## ⚡ Optimisations

### 1. Réduire la taille de l'image

```dockerfile
# Avant : 1.2 GB
FROM python:3.11

# Après : 450 MB
FROM python:3.11-slim

# Encore mieux : 380 MB
FROM python:3.11-alpine
```

### 2. Cache des layers

```dockerfile
# ❌ Mauvais (cache invalidé à chaque changement de code)
COPY . .
RUN pip install -r requirements.txt

# ✅ Bon (cache réutilisé si requirements.txt n'a pas changé)
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
```

### 3. Multi-stage build

```dockerfile
# Séparer build et runtime
FROM python:3.11 AS builder
# ... build dependencies ...

FROM python:3.11-slim
COPY --from=builder /app /app
# Image finale plus légère
```

### 4. .dockerignore

```
# Exclure les fichiers inutiles
tests/
docs/
*.md
.git/
# → Réduction de 30% du contexte
```

---

## 🔧 Troubleshooting

### Problème 1 : Port déjà utilisé

```bash
# Erreur
Error: port 8501 already in use

# Solution 1 : Trouver le processus
# Windows
netstat -ano | findstr :8501

# Linux/Mac
lsof -i :8501

# Solution 2 : Utiliser un autre port
docker run -p 8502:8501 job-radar
```

### Problème 2 : Volumes non montés

```bash
# Vérifier le montage
docker inspect job-radar | grep -A 10 Mounts

# Tester l'écriture
docker exec job-radar touch /app/database/test.txt
docker exec job-radar ls -l /app/database/
```

### Problème 3 : Variables d'environnement manquantes

```bash
# Vérifier les variables
docker exec job-radar env | grep MISTRAL

# Passer les variables
docker run --env-file .env job-radar

# Ou individuellement
docker run -e MISTRAL_API_KEY=xxx job-radar
```

### Problème 4 : Permission denied

```bash
# Erreur
PermissionError: [Errno 13] Permission denied

# Solution : Changer les permissions
docker run --user $(id -u):$(id -g) job-radar

# Ou dans le Dockerfile
RUN chown -R appuser:appuser /app
USER appuser
```

### Problème 5 : Build lent

```bash
# Solution 1 : Utiliser BuildKit
DOCKER_BUILDKIT=1 docker build -t job-radar .

# Solution 2 : Cache externe
docker build --cache-from job-radar:latest -t job-radar .

# Solution 3 : Paralléliser
docker-compose build --parallel
```

---

##  Monitoring

### Logs

```bash
# Logs en temps réel
docker logs -f job-radar

# Les 100 dernières lignes
docker logs --tail 100 job-radar

# Depuis un timestamp
docker logs --since 2025-01-10T10:00:00 job-radar
```

### Statistiques

```bash
# CPU, RAM, Network
docker stats job-radar

# Format personnalisé
docker stats --format "table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}"
```

### Health Check

```bash
# Vérifier le status
docker ps | grep job-radar

# Détails du healthcheck
docker inspect job-radar | grep -A 20 Health
```

---

##  Déploiement

### Cloud Platforms

**1. AWS ECS**

```bash
# Build pour ARM64 (Graviton)
docker buildx build --platform linux/arm64 -t job-radar:arm64 .

# Push vers ECR
aws ecr get-login-password | docker login --username AWS --password-stdin
docker push xxx.ecr.amazonaws.com/job-radar:latest
```

**2. Google Cloud Run**

```bash
# Build et push
gcloud builds submit --tag gcr.io/PROJECT-ID/job-radar

# Deploy
gcloud run deploy job-radar \
  --image gcr.io/PROJECT-ID/job-radar \
  --platform managed \
  --port 8501
```

**3. Heroku**

```bash
# Login
heroku container:login

# Push
heroku container:push web -a job-radar

# Release
heroku container:release web -a job-radar
```

---

##  Ressources

### Documentation

- [Docker Docs](https://docs.docker.com/)
- [Docker Compose](https://docs.docker.com/compose/)
- [Streamlit Docker](https://docs.streamlit.io/knowledge-base/tutorials/deploy/docker)

### Commandes de référence

```bash
# Cheat Sheet Docker
docker build -t name .               # Build
docker run -p 8501:8501 name         # Run
docker ps                            # List containers
docker logs name                     # Logs
docker exec -it name bash            # Shell
docker stop name                     # Stop
docker rm name                       # Remove
docker images                        # List images
docker rmi name                      # Remove image
docker system prune -a               # Clean all
```

---

<div align="center">

**🐳 Docker rend le déploiement simple et reproductible !**

[⬆️ Retour en haut](#guide-docker---radar)

</div>
