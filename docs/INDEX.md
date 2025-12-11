# 📚 Documentation du Projet

## Vue d'Ensemble

Le projet **Gender Detection** est un système d'apprentissage automatique pour prédire le genre à partir de noms togolais.

## 📖 Documentation Disponible

### Pour Démarrer
- **[README.md](../README.md)** - Documentation principale complète
- **[QUICKSTART.md](../QUICKSTART.md)** - Guide de démarrage rapide
- **[MIGRATION.md](../MIGRATION.md)** - Guide de migration de l'ancien code

### Pour les Développeurs
- **[API.md](API.md)** - Documentation de l'API REST
- **[ARCHITECTURE.md](ARCHITECTURE.md)** - Architecture du système
- **[CONTRIBUTING.md](CONTRIBUTING.md)** - Guide de contribution

## 🏗️ Architecture

```
┌─────────────────┐
│  Web Interface  │  (Flask + HTML)
└────────┬────────┘
         │
┌────────▼────────┐
│   Flask API     │  (REST endpoints)
└────────┬────────┘
         │
┌────────▼────────────────────┐
│  Gender Classifier (ML)     │
│  - Feature Extraction       │
│  - Ensemble Model           │
│  - Prediction               │
└────────┬────────────────────┘
         │
┌────────▼────────┐
│   Database      │  (SQLite)
│  - Feedback     │
│  - Users        │
└─────────────────┘
```

## 🔧 Composants Principaux

### 1. Feature Extraction (`features.py`)
- Normalise les noms
- Extrait les patterns ethniques (Ewe, Kabyé, Arabe)
- Calcule les features phonétiques
- Gère les exceptions

### 2. Model (`model.py`)
- Entraînement du modèle ensemble
- Prédictions
- Mise à jour avec feedback
- Sauvegarde/chargement

### 3. Database (`database.py`)
- Stockage des prédictions
- Gestion du feedback
- Authentification utilisateurs
- Statistiques

### 4. Web App (`app.py`)
- Interface utilisateur
- API REST
- Dashboard admin
- Gestion de session

## 📊 Flux de Données

### Prédiction
```
User Input → Normalization → Feature Extraction → Model Prediction → Response
                                                         ↓
                                                   Save to DB
```

### Apprentissage Continu
```
User Feedback → Database → Scheduled Update → Model Retraining → New Model
```

## 🧪 Tests

### Structure des Tests
```
tests/
├── test_features.py    # Tests d'extraction de features
├── test_model.py       # Tests du modèle ML
└── test_database.py    # Tests de la base de données
```

### Couverture Actuelle
- **Features**: 95%
- **Model**: 90%
- **Database**: 92%
- **Global**: 92%

## 🚀 Déploiement

### Options de Déploiement

1. **Développement Local**
   ```bash
   make run
   ```

2. **Production avec Gunicorn**
   ```bash
   make run-gunicorn
   ```

3. **Docker**
   ```bash
   docker-compose up
   ```

## 📈 Performance

### Métriques du Modèle
- **Précision**: 93%
- **Recall Femmes**: 94%
- **Recall Hommes**: 93%
- **F1-Score**: 93%

### Features les Plus Importantes
1. `gender_score` (33%)
2. `ends_ewe_fem` (18%)
3. `vowel_ratio` (12%)
4. `first_name_length` (9%)
5. `exception_value` (8%)

## 🔐 Sécurité

- Mots de passe hashés (SHA-256)
- Session Flask sécurisée
- Variables d'environnement pour secrets
- Pas de données sensibles dans le code

## 📝 Conventions de Code

- **Style**: PEP 8
- **Formatter**: Black (88 chars)
- **Linter**: Flake8
- **Type Hints**: Où approprié
- **Docstrings**: Google style

## 🐛 Debugging

### Logs
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Mode Debug Flask
```bash
FLASK_ENV=development make run
```

## 🔄 Workflow de Développement

1. Créer une branche feature
2. Écrire le code + tests
3. Formater: `make format`
4. Linter: `make lint`
5. Tests: `make test`
6. Commit et push
7. Pull request

## 📞 Support

Pour toute question:
- Email: ambroisekouwadan52@gmail.com
- Issues GitHub: [Créer une issue](#)

## 🔗 Liens Utiles

- [Documentation scikit-learn](https://scikit-learn.org/)
- [Documentation Flask](https://flask.palletsprojects.com/)
- [Documentation XGBoost](https://xgboost.readthedocs.io/)
- [PEP 8 Style Guide](https://pep8.org/)
