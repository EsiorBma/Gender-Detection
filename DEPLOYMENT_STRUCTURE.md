# 🚀 Structure de Déploiement - Railway

## 📂 Organisation des Fichiers pour Production

```
Gender-Detection/
├── 📱 APPLICATION (Flask)
│   ├── src/gender_detection/          # Package Python principal
│   │   ├── __init__.py
│   │   ├── app.py                     # ✅ Application Flask
│   │   ├── config.py                  # ✅ Configuration
│   │   ├── model.py                   # ✅ ML Model
│   │   ├── features.py                # ✅ Feature engineering
│   │   ├── database.py                # ✅ SQLite database
│   │   └── cli.py                     # CLI (optionnel en prod)
│   │
│   ├── templates/                     # ✅ Templates HTML
│   │   ├── index.html
│   │   ├── admin_login.html
│   │   └── admin_dashboard.html
│   │
│   ├── static/                        # ✅ CSS, JS, images
│   │   ├── styles.css
│   │   └── gender.ico
│   │
├── 💾 DONNÉES & MODÈLE
│   ├── models/
│   │   └── gender_classifier.joblib   # ✅ Modèle ML entraîné
│   │
│   ├── data/
│   │   └── noms_prenoms_togo.csv      # ✅ Dataset
│   │
│   ├── *.db.sqlite3                   # ✅ Bases SQLite (créées auto)
│   │
├── ⚙️ CONFIGURATION DEPLOYMENT
│   ├── requirements.txt               # ✅ Dependencies Python
│   ├── runtime.txt                    # ✅ Version Python
│   ├── Procfile                       # ✅ Commande de démarrage
│   ├── .env.example                   # ✅ Variables d'environnement
│   ├── railway.json                   # ⚡ Config Railway (à créer)
│   │
├── 🐳 DOCKER (optionnel)
│   ├── Dockerfile
│   └── docker-compose.yml
│   │
├── 📚 DOCUMENTATION
│   ├── README.md
│   ├── QUICKSTART.md
│   ├── docs/
│   │   ├── DEPLOYMENT.md
│   │   └── USER_GUIDE.md
│   │
├── 🧪 TESTS (non déployés)
│   └── tests/                         # Ignoré en production
│   
└── 🔧 DÉVELOPPEMENT (non déployés)
    ├── scripts/
    ├── .vscode/
    ├── __pycache__/
    └── env/

```

## ✅ Fichiers Essentiels pour Railway

### 1. **requirements.txt** (déjà présent)
```txt
flask>=3.0.0
pandas>=2.0.0
numpy>=1.24.0
scikit-learn>=1.3.0
xgboost>=2.0.0
imbalanced-learn>=0.11.0
joblib>=1.3.0
gunicorn==20.1.0
```

### 2. **Procfile** (déjà présent)
```
web: gunicorn --chdir src gender_detection.app:app --bind 0.0.0.0:$PORT
```

### 3. **runtime.txt** (déjà présent)
```
python-3.13.7
```

### 4. **railway.json** (à créer)
Configuration spécifique Railway pour builder correctement.

### 5. **.env.example** (déjà présent)
Variables d'environnement à configurer sur Railway.

---

## 🎯 Prochaines Étapes

1. ✅ Créer `railway.json` pour configuration build
2. ✅ Vérifier que tous les fichiers essentiels sont bien commités
3. ✅ Créer `.railwayignore` pour exclure fichiers inutiles
4. ✅ Tester localement avec Gunicorn
5. ✅ Push sur GitHub branche `deployment`
6. ✅ Connecter à Railway et déployer

---

## 📋 Checklist Déploiement

- [ ] Modèle `gender_classifier.joblib` dans `models/`
- [ ] Dataset dans `data/noms_prenoms_togo.csv`
- [ ] Templates HTML dans `templates/`
- [ ] Static CSS dans `static/`
- [ ] `requirements.txt` à jour
- [ ] `Procfile` correct
- [ ] `runtime.txt` correct
- [ ] Variables d'environnement configurées
- [ ] `.gitignore` exclut `env/`, `__pycache__/`, `*.pyc`
- [ ] Bases SQLite initialisées au démarrage
- [ ] Logs configurés pour production

