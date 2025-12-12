# 🚀 Guide de Déploiement - Gender Detection API

## Héberger l'Application Web avec l'API

Ce guide explique comment déployer ton application en production sur différentes plateformes.

---

## 📋 Table des Matières

1. [Prérequis](#prérequis)
2. [Préparation](#préparation)
3. [Option 1 : Heroku (Gratuit)](#option-1--heroku)
4. [Option 2 : Railway (Gratuit)](#option-2--railway)
5. [Option 3 : Render (Gratuit)](#option-3--render)
6. [Option 4 : VPS (DigitalOcean, AWS, etc.)](#option-4--vps)
7. [Option 5 : Docker sur VPS](#option-5--docker-sur-vps)
8. [Configuration Post-Déploiement](#configuration-post-déploiement)

---

## 🔧 Prérequis

- Compte GitHub
- Code dans un repository Git
- Python 3.8+
- Modèle entraîné (`models/gender_classifier.joblib`)
- Dataset (`data/noms_prenoms_togo.csv`)

---

## 📦 Préparation

### 1. Créer une Branche de Déploiement

```bash
# Créer et basculer sur la branche deployment
git checkout -b deployment

# S'assurer que tous les changements sont commités
git add .
git commit -m "Prepare for deployment"
```

### 2. Fichiers Nécessaires

Vérifie que tu as :
- ✅ `requirements.txt`
- ✅ `Procfile` (pour Heroku)
- ✅ `runtime.txt` (optionnel)
- ✅ `gunicorn` dans requirements.txt

### 3. Créer un Procfile

```bash
cat > Procfile << 'EOF'
web: cd src && gunicorn --workers 4 --bind 0.0.0.0:$PORT --timeout 120 gender_detection.app:app
EOF
```

### 4. Spécifier la Version Python

```bash
echo "python-3.10.13" > runtime.txt
```

### 5. Vérifier requirements.txt

Assure-toi que `gunicorn` est dans `requirements.txt` :

```bash
grep -q "gunicorn" requirements.txt || echo "gunicorn==20.1.0" >> requirements.txt
```

---

## 🌐 Option 1 : Heroku (Gratuit)

Heroku est simple et offre un tier gratuit (avec limitations).

### Étape 1 : Installer Heroku CLI

```bash
# Linux/Mac
curl https://cli-assets.heroku.com/install.sh | sh

# Ou avec brew (Mac)
brew tap heroku/brew && brew install heroku
```

### Étape 2 : Login et Créer l'App

```bash
# Se connecter
heroku login

# Créer l'application
heroku create gender-detection-togo

# Ou avec un nom personnalisé
heroku create ton-nom-unique
```

### Étape 3 : Configurer les Variables d'Environnement

```bash
# Générer une clé secrète
python -c "import secrets; print(secrets.token_hex(32))"

# Configurer les variables
heroku config:set SECRET_KEY="ta-cle-secrete-ici"
heroku config:set FLASK_ENV=production
heroku config:set ADMIN_EMAIL=ton-email@example.com
heroku config:set ADMIN_PASSWORD=ton-mot-de-passe-securise
```

### Étape 4 : Configurer les Fichiers Volumineux (Git LFS)

Si ton modèle est > 50MB :

```bash
# Installer Git LFS
git lfs install

# Tracker les fichiers volumineux
git lfs track "*.joblib"
git lfs track "*.csv"

# Ajouter .gitattributes
git add .gitattributes
git commit -m "Add Git LFS configuration"
```

**Alternative : Télécharger le modèle au démarrage**

Créer `scripts/download_model.py` :
```python
import urllib.request
import os

MODEL_URL = "https://ton-stockage.com/gender_classifier.joblib"
MODEL_PATH = "models/gender_classifier.joblib"

if not os.path.exists(MODEL_PATH):
    print("Downloading model...")
    urllib.request.urlretrieve(MODEL_URL, MODEL_PATH)
    print("Model downloaded!")
```

Modifier `Procfile` :
```
web: python scripts/download_model.py && cd src && gunicorn --workers 4 --bind 0.0.0.0:$PORT gender_detection.app:app
```

### Étape 5 : Déployer

```bash
# Pousser vers Heroku
git push heroku deployment:main

# Voir les logs
heroku logs --tail

# Ouvrir l'app
heroku open
```

### Étape 6 : Configurer la Base de Données

Heroku utilise un système de fichiers éphémère. Pour persister les données :

```bash
# Ajouter Heroku Postgres (gratuit)
heroku addons:create heroku-postgresql:mini

# Ou utiliser SQLite sur un volume persistant
heroku config:set DATABASE_URL="sqlite:///app.db"
```

---

## 🚂 Option 2 : Railway (Gratuit)

Railway offre $5/mois gratuit et est très simple.

### Étape 1 : Créer un Compte

- Va sur [railway.app](https://railway.app)
- Connecte-toi avec GitHub

### Étape 2 : Nouveau Projet

1. Clique sur "New Project"
2. Sélectionne "Deploy from GitHub repo"
3. Choisis ton repository
4. Sélectionne la branche `deployment`

### Étape 3 : Configurer les Variables

Dans l'interface Railway :
1. Va dans "Variables"
2. Ajoute :
   ```
   SECRET_KEY=ta-cle-secrete
   FLASK_ENV=production
   ADMIN_EMAIL=ton-email@example.com
   ADMIN_PASSWORD=ton-mot-de-passe
   PORT=8000
   ```

### Étape 4 : Configurer le Build

Railway détecte automatiquement Python. Si besoin, crée `railway.toml` :

```toml
[build]
builder = "NIXPACKS"

[deploy]
startCommand = "cd src && gunicorn --workers 4 --bind 0.0.0.0:$PORT gender_detection.app:app"
```

### Étape 5 : Déployer

Railway déploie automatiquement ! Attends quelques minutes.

### Étape 6 : Obtenir l'URL

1. Va dans "Settings"
2. Génère un domaine public
3. Ton app sera accessible à : `https://ton-app.up.railway.app`

---

## 🎨 Option 3 : Render (Gratuit)

Render offre un tier gratuit avec SSL automatique.

### Étape 1 : Créer un Compte

- Va sur [render.com](https://render.com)
- Connecte-toi avec GitHub

### Étape 2 : Nouveau Web Service

1. Clique sur "New +" → "Web Service"
2. Connecte ton repository GitHub
3. Nomme ton service : `gender-detection`

### Étape 3 : Configuration

```yaml
# Build Command
pip install -r requirements.txt

# Start Command
cd src && gunicorn --workers 4 --bind 0.0.0.0:$PORT gender_detection.app:app

# Environment
- Python 3.10
```

### Étape 4 : Variables d'Environnement

Ajoute dans l'interface :
```
SECRET_KEY=ta-cle-secrete
FLASK_ENV=production
ADMIN_EMAIL=ton-email@example.com
ADMIN_PASSWORD=ton-mot-de-passe
```

### Étape 5 : Déployer

Clique sur "Create Web Service". Le déploiement prend ~5 minutes.

### Étape 6 : SSL Gratuit

Render active automatiquement HTTPS ! Ton app sera à :
`https://gender-detection.onrender.com`

---

## 💻 Option 4 : VPS (DigitalOcean, AWS, Linode)

Pour plus de contrôle et de performance.

### Étape 1 : Créer un VPS

Sur DigitalOcean par exemple :
1. Crée un Droplet Ubuntu 22.04
2. Taille minimale : 1GB RAM
3. Note l'adresse IP

### Étape 2 : Se Connecter au Serveur

```bash
ssh root@ton-ip-serveur
```

### Étape 3 : Installer les Dépendances

```bash
# Mise à jour du système
apt update && apt upgrade -y

# Installer Python et outils
apt install -y python3.10 python3-pip python3-venv nginx git

# Installer certbot pour SSL
apt install -y certbot python3-certbot-nginx
```

### Étape 4 : Cloner le Projet

```bash
# Créer un utilisateur
adduser appuser
su - appuser

# Cloner le projet
git clone https://github.com/ton-username/gender-detection.git
cd gender-detection
git checkout deployment
```

### Étape 5 : Installer l'Application

```bash
# Créer environnement virtuel
python3 -m venv env
source env/bin/activate

# Installer dépendances
pip install -r requirements.txt
pip install -e .

# Initialiser
python scripts/init_project.py
```

### Étape 6 : Configurer l'Environnement

```bash
# Créer .env
cp .env.example .env
nano .env
```

Modifier :
```bash
SECRET_KEY=une-cle-tres-securisee
FLASK_ENV=production
ADMIN_EMAIL=ton-email@example.com
ADMIN_PASSWORD=mot-de-passe-fort
WORKERS=4
BIND=127.0.0.1:8000
```

### Étape 7 : Configurer Systemd

Créer `/etc/systemd/system/gender-detection.service` :

```ini
[Unit]
Description=Gender Detection Service
After=network.target

[Service]
Type=notify
User=appuser
WorkingDirectory=/home/appuser/gender-detection
Environment="PATH=/home/appuser/gender-detection/env/bin"
EnvironmentFile=/home/appuser/gender-detection/.env
ExecStart=/home/appuser/gender-detection/env/bin/gunicorn \
    --workers 4 \
    --bind 127.0.0.1:8000 \
    --timeout 120 \
    --chdir /home/appuser/gender-detection/src \
    gender_detection.app:app

Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

### Étape 8 : Configurer Nginx

Créer `/etc/nginx/sites-available/gender-detection` :

```nginx
server {
    listen 80;
    server_name ton-domaine.com www.ton-domaine.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /static {
        alias /home/appuser/gender-detection/static;
    }
}
```

Activer :
```bash
ln -s /etc/nginx/sites-available/gender-detection /etc/nginx/sites-enabled/
nginx -t
systemctl restart nginx
```

### Étape 9 : Activer SSL (HTTPS)

```bash
certbot --nginx -d ton-domaine.com -d www.ton-domaine.com
```

### Étape 10 : Démarrer l'Application

```bash
# Activer et démarrer le service
systemctl enable gender-detection
systemctl start gender-detection

# Vérifier le statut
systemctl status gender-detection

# Voir les logs
journalctl -u gender-detection -f
```

### Étape 11 : Tester

```bash
curl https://ton-domaine.com
```

---

## 🐳 Option 5 : Docker sur VPS

La méthode la plus moderne et portable.

### Étape 1 : Installer Docker sur le VPS

```bash
# Installer Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# Installer Docker Compose
apt install -y docker-compose
```

### Étape 2 : Cloner et Préparer

```bash
git clone https://github.com/ton-username/gender-detection.git
cd gender-detection
git checkout deployment
```

### Étape 3 : Créer docker-compose.prod.yml

```yaml
version: '3.8'

services:
  web:
    build: .
    ports:
      - "8000:8000"
    environment:
      - FLASK_ENV=production
      - SECRET_KEY=${SECRET_KEY}
      - ADMIN_EMAIL=${ADMIN_EMAIL}
      - ADMIN_PASSWORD=${ADMIN_PASSWORD}
    volumes:
      - ./data:/app/data
      - ./models:/app/models
      - ./logs:/app/logs
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/"]
      interval: 30s
      timeout: 10s
      retries: 3

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - /etc/letsencrypt:/etc/letsencrypt
    depends_on:
      - web
    restart: unless-stopped
```

### Étape 4 : Créer nginx.conf

```nginx
events {
    worker_connections 1024;
}

http {
    upstream app {
        server web:8000;
    }

    server {
        listen 80;
        server_name ton-domaine.com;

        location / {
            proxy_pass http://app;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
        }
    }
}
```

### Étape 5 : Configurer .env

```bash
cat > .env << EOF
SECRET_KEY=$(openssl rand -hex 32)
FLASK_ENV=production
ADMIN_EMAIL=ton-email@example.com
ADMIN_PASSWORD=mot-de-passe-securise
EOF
```

### Étape 6 : Build et Run

```bash
# Build
docker-compose -f docker-compose.prod.yml build

# Run
docker-compose -f docker-compose.prod.yml up -d

# Voir les logs
docker-compose -f docker-compose.prod.yml logs -f
```

### Étape 7 : SSL avec Certbot

```bash
# Installer Certbot
apt install -y certbot

# Obtenir le certificat
certbot certonly --standalone -d ton-domaine.com

# Modifier nginx.conf pour HTTPS
# ...puis redémarrer
docker-compose -f docker-compose.prod.yml restart nginx
```

---

## ⚙️ Configuration Post-Déploiement

### 1. Vérifier que l'App Fonctionne

```bash
curl https://ton-domaine.com
```

### 2. Tester l'API

```bash
curl -X POST https://ton-domaine.com/predict \
  -H "Content-Type: application/json" \
  -d '{"full_name": "AMEGANVI Koffi Ama"}'
```

### 3. Accéder au Dashboard Admin

```
https://ton-domaine.com/admin
Email: ton-email@example.com
Password: ton-mot-de-passe
```

### 4. Configurer les Backups

```bash
# Script de backup
cat > /home/appuser/backup.sh << 'EOF'
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
tar -czf /backups/gender-detection-$DATE.tar.gz \
    /home/appuser/gender-detection/data \
    /home/appuser/gender-detection/models \
    /home/appuser/gender-detection/*.db.sqlite3
EOF

chmod +x /home/appuser/backup.sh

# Cron pour backup quotidien
crontab -e
# Ajouter :
0 2 * * * /home/appuser/backup.sh
```

### 5. Monitoring

```bash
# Installer htop pour monitoring
apt install -y htop

# Voir l'utilisation
htop

# Logs en temps réel
tail -f /var/log/nginx/access.log
journalctl -u gender-detection -f
```

---

## 📊 Comparaison des Options

| Option | Coût | Facilité | Performance | SSL | Contrôle |
|--------|------|----------|-------------|-----|----------|
| Heroku | Gratuit/Payant | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ✅ Auto | ⭐⭐ |
| Railway | Gratuit/Payant | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ✅ Auto | ⭐⭐ |
| Render | Gratuit/Payant | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ✅ Auto | ⭐⭐⭐ |
| VPS | ~$5/mois | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | 🔧 Manuel | ⭐⭐⭐⭐⭐ |
| Docker VPS | ~$5/mois | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | 🔧 Manuel | ⭐⭐⭐⭐⭐ |

### Recommandations :

- **Débutant / MVP** : Railway ou Render (gratuit, facile)
- **Production légère** : Heroku (stable, bien documenté)
- **Production sérieuse** : VPS avec Docker (contrôle total, scalable)
- **Haute performance** : VPS dédié (DigitalOcean, AWS)

---

## 🔒 Sécurité

### Checklist de Sécurité

- [ ] SECRET_KEY forte et unique
- [ ] Mots de passe admin sécurisés
- [ ] HTTPS activé (SSL/TLS)
- [ ] Variables d'environnement (pas de secrets dans le code)
- [ ] Firewall configuré
- [ ] Mise à jour régulières
- [ ] Backups automatiques
- [ ] Logs activés
- [ ] Rate limiting (optionnel)

### Ajouter Rate Limiting

```python
# Dans src/gender_detection/app.py
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

limiter = Limiter(
    app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)

@app.route('/predict', methods=['POST'])
@limiter.limit("10 per minute")
def predict():
    # ...
```

---

## 📝 Checklist Finale

Avant de mettre en production :

- [ ] Tests passent : `make test`
- [ ] Modèle entraîné et sauvegardé
- [ ] Variables d'environnement configurées
- [ ] SSL/HTTPS activé
- [ ] Firewall configuré
- [ ] Backups automatiques
- [ ] Monitoring en place
- [ ] Documentation à jour
- [ ] Admin credentials changés
- [ ] Test de charge effectué

---

## 🆘 Dépannage

### Erreur : "Module not found"

```bash
pip install -r requirements.txt
pip install -e .
```

### Erreur : "Port already in use"

```bash
# Trouver le processus
lsof -i :8000

# Tuer le processus
kill -9 <PID>
```

### L'app ne démarre pas

```bash
# Vérifier les logs
journalctl -u gender-detection -n 50

# Ou avec Docker
docker-compose logs web
```

---

**Bon déploiement ! 🚀**
