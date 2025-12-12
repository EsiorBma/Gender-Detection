# 🚀 Branche Deployment - Prête pour Railway

Cette branche contient le code **optimisé pour production** du projet Gender Detection.

## ⚡ Quick Deploy

[![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/new/template?template=https://github.com/EsiorBma/Gender-Detection/tree/deployment)

## 📋 Qu'est-ce qui est inclus ?

- ✅ **Application Flask** production-ready avec Gunicorn
- ✅ **Modèle ML** pré-entraîné (93% accuracy)
- ✅ **Dataset** de 7,859 noms togolais
- ✅ **API REST** pour prédictions en temps réel
- ✅ **Dashboard Admin** avec métriques et feedback
- ✅ **Réentraînement automatique** (daily à 2 AM)
- ✅ **Tests** (92% coverage)
- ✅ **Documentation** complète

## 🏗️ Structure

```
Gender-Detection/
├── src/gender_detection/    # Package principal
├── templates/                # HTML templates
├── static/                   # CSS, assets
├── models/                   # Modèle ML
├── data/                     # Dataset
├── Procfile                  # Railway start command
├── runtime.txt               # Python version
├── requirements.txt          # Dependencies
└── railway.json              # Railway config
```

## 🚂 Déployer sur Railway

### Méthode 1 : Via Dashboard

1. Va sur https://railway.app/
2. "New Project" → "Deploy from GitHub repo"
3. Sélectionne `EsiorBma/Gender-Detection`
4. Branche : `deployment`
5. Railway détecte automatiquement Python et déploie

### Méthode 2 : Via Railway CLI

```bash
# Installer Railway CLI
npm i -g @railway/cli

# Login
railway login

# Créer projet et déployer
railway init
railway up
```

## ⚙️ Variables d'Environnement

Railway configure automatiquement `PORT`. Optionnel :

```env
SECRET_KEY=your-secret-key-here
DEFAULT_ADMIN_EMAIL=admin@example.com
DEFAULT_ADMIN_PASSWORD=secure-password
DEBUG=False
```

## 🧪 Test Local

```bash
# Installer dépendances
pip install -r requirements.txt

# Lancer avec Gunicorn (comme en prod)
gunicorn --chdir src gender_detection.app:app --bind 127.0.0.1:8000

# Ou avec Flask (dev)
cd src && python -m gender_detection.app
```

Ouvre : http://127.0.0.1:8000

## 📊 Endpoints

```bash
# Homepage
GET /

# Prédiction
POST /predict
Body: {"full_name": "MENSAH Kofi"}

# Feedback
POST /feedback
Body: {"feedback_id": 1, "actual_gender": "Homme", "predicted_value": 1}

# Admin Dashboard
GET /admin
```

## 📚 Documentation

- [RAILWAY_DEPLOYMENT.md](RAILWAY_DEPLOYMENT.md) - Guide complet
- [DEPLOYMENT_STRUCTURE.md](DEPLOYMENT_STRUCTURE.md) - Architecture
- [README.md](README.md) - Documentation projet
- [docs/USER_GUIDE.md](docs/USER_GUIDE.md) - Guide utilisateur

## 🔍 Vérification

Avant de déployer, vérifie que tout est OK :

```bash
bash scripts/check_deployment.sh
```

Devrait afficher : ✅ TOUT EST PRÊT POUR LE DÉPLOIEMENT!

## 💡 Support

- **Issues** : https://github.com/EsiorBma/Gender-Detection/issues
- **Email** : ambroisekouwadan52@gmail.com

---

**Développé avec ❤️ par KOUWADAN Kodjo Prince Ambroise**
