# 🚂 Guide de Déploiement Railway

## 📋 Prérequis

- ✅ Compte GitHub avec le repo `Gender-Detection`
- ✅ Compte Railway (gratuit) : https://railway.app/
- ✅ Branche `deployment` prête

---

## 🚀 Étapes de Déploiement

### 1. **Préparer le Repo GitHub**

```bash
# S'assurer d'être sur la branche deployment
git checkout deployment

# Vérifier que tout est prêt
bash scripts/check_deployment.sh

# Commiter les changements
git add .
git commit -m "chore: prepare for Railway deployment"

# Pousser sur GitHub
git push origin deployment
```

### 2. **Créer un Nouveau Projet sur Railway**

1. Va sur https://railway.app/
2. Clique sur **"New Project"**
3. Sélectionne **"Deploy from GitHub repo"**
4. Autorise Railway à accéder à ton GitHub
5. Sélectionne le repo `EsiorBma/Gender-Detection`
6. Choisis la branche **`deployment`**

### 3. **Configuration des Variables d'Environnement**

Railway détectera automatiquement Python et utilisera :
- `runtime.txt` pour la version Python
- `requirements.txt` pour les dépendances
- `Procfile` pour la commande de démarrage

**Variables à configurer (optionnel) :**

Dans le dashboard Railway → Settings → Variables :

```env
# Port (automatique sur Railway)
PORT=8000

# Flask
FLASK_ENV=production
SECRET_KEY=ton-secret-super-long-et-aleatoire-ici

# Admin par défaut
DEFAULT_ADMIN_EMAIL=admin@example.com
DEFAULT_ADMIN_PASSWORD=change-me-in-production

# Debug (désactiver en prod)
DEBUG=False
```

### 4. **Déploiement Automatique**

Railway va :
1. ✅ Détecter Python 3.13.7 (depuis `runtime.txt`)
2. ✅ Installer les dépendances (`pip install -r requirements.txt`)
3. ✅ Exécuter la commande du `Procfile`
4. ✅ Assigner un domaine public (ex: `gender-detection-production.up.railway.app`)

**Durée** : ~3-5 minutes

### 5. **Vérification Post-Déploiement**

Une fois déployé, Railway te donne une URL :

```
https://your-app.up.railway.app
```

**Tests à faire :**

```bash
# Test de santé
curl https://your-app.up.railway.app/

# Test de prédiction
curl -X POST https://your-app.up.railway.app/predict \
  -H "Content-Type: application/json" \
  -d '{"full_name": "MENSAH Kofi"}'

# Devrait retourner :
# {"gender": "Homme", "surname": "MENSAH", ...}
```

**Interface Web :**
- Page d'accueil : `https://your-app.up.railway.app/`
- Admin login : `https://your-app.up.railway.app/admin`

---

## 📊 Monitoring & Logs

### Voir les Logs en Temps Réel

Dans Railway Dashboard :
1. Clique sur ton projet
2. Onglet **"Deployments"**
3. Clique sur le dernier deployment
4. **"View Logs"**

### Métriques

Railway affiche automatiquement :
- CPU usage
- Memory usage
- Network traffic
- Restart count

---

## 🔧 Configuration Avancée

### Augmenter les Workers Gunicorn

Édite `Procfile` :

```
web: gunicorn --chdir src gender_detection.app:app --bind 0.0.0.0:$PORT --workers 4 --timeout 120
```

**Formule** : `workers = (2 x CPU cores) + 1`

### Activer le Réentraînement Automatique

Le scheduler (2h du matin) fonctionne automatiquement car il tourne dans un thread daemon.

**Vérifier dans les logs** :
```
Automatic training scheduler started (runs daily at 2 AM)
Next automatic training scheduled at 2025-12-12 02:00:00
```

### Persister les Bases SQLite

⚠️ **Important** : Railway utilise un système de fichiers **éphémère**.

**Solutions** :

**Option 1 : Volumes Railway (Recommandé)**
```bash
# Dans Railway Dashboard → Settings → Volumes
# Créer un volume monté sur /app/data
```

**Option 2 : PostgreSQL (Production)**
```bash
# Ajouter un service PostgreSQL
# Modifier database.py pour utiliser PostgreSQL
```

**Option 3 : Accepter la perte** (OK pour démo)
Les DBs seront réinitialisées à chaque redéploiement.

---

## 🐛 Troubleshooting

### Erreur : "Application failed to respond"

**Cause** : Port incorrect

**Solution** : Vérifie que le Procfile utilise bien `$PORT` :
```
web: gunicorn ... --bind 0.0.0.0:$PORT
```

### Erreur : "Module not found"

**Cause** : Dépendance manquante dans `requirements.txt`

**Solution** :
```bash
pip freeze > requirements.txt
git add requirements.txt
git commit -m "fix: update requirements"
git push origin deployment
```

### Erreur : "Worker timeout"

**Cause** : L'app met trop de temps à démarrer (modèle lourd)

**Solution** : Augmente le timeout dans `Procfile` :
```
web: gunicorn ... --timeout 180
```

### Logs : "Model not found"

**Cause** : Le modèle n'est pas dans le repo

**Solution** : Vérifie que `models/gender_classifier.joblib` est bien commité :
```bash
git add models/gender_classifier.joblib -f
git commit -m "feat: add trained model"
git push origin deployment
```

---

## 💰 Coûts

**Plan Gratuit Railway** :
- ✅ 500 heures/mois (gratuites)
- ✅ $5 de crédit mensuel
- ✅ Suffisant pour une démo/portfolio

**Si tu dépasses** :
- ~$0.000231/minute (≈ $10/mois pour 24/7)

**Alternatives gratuites** :
- Render.com (gratuit avec limitations)
- Fly.io (gratuit jusqu'à 3 apps)
- Heroku (payant depuis 2022)

---

## 🔗 Liens Utiles

- **Railway Docs** : https://docs.railway.app/
- **Python on Railway** : https://docs.railway.app/guides/python
- **Gunicorn Config** : https://docs.gunicorn.org/en/stable/settings.html
- **Flask Deployment** : https://flask.palletsprojects.com/en/3.0.x/deploying/

---

## ✅ Checklist Finale

Avant de déployer :

- [ ] `bash scripts/check_deployment.sh` réussit
- [ ] Modèle entraîné présent dans `models/`
- [ ] Variables d'environnement configurées
- [ ] `.gitignore` exclut `env/`, `__pycache__/`
- [ ] Test local avec Gunicorn réussi
- [ ] Branche `deployment` poussée sur GitHub
- [ ] README.md à jour avec l'URL de déploiement

**Après déploiement :**

- [ ] URL publique accessible
- [ ] Test de prédiction fonctionne
- [ ] Dashboard admin accessible
- [ ] Logs ne montrent pas d'erreurs critiques
- [ ] Ajouter l'URL dans le README.md

---

**Besoin d'aide ?** Consulte les logs Railway ou demande de l'aide ! 🚀
