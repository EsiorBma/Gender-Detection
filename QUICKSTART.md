# 🚀 Guide de Démarrage Rapide

Ce guide te permet de tester rapidement ton projet restructuré.

## 📋 Prérequis

- Python 3.8+ installé
- Terminal ouvert dans le dossier `Gender-Detection`
- Environnement virtuel activé

## 🎯 Étape 1 : Activer l'environnement virtuel

```bash
source env/bin/activate
```

Tu devrais voir `(env)` devant ton prompt.

## 📦 Étape 2 : Installer le package en mode développement

```bash
pip install -e .
```

Cette commande installe ton package localement, ce qui te permet de:
- Importer `gender_detection` depuis n'importe où
- Modifier le code et voir les changements immédiatement

## 🗂️ Étape 3 : Organiser les fichiers

Déplace les fichiers de données vers les bons dossiers:

```bash
# Déplacer le dataset
mv noms_prenoms_togo.csv data/ 2>/dev/null || true

# Déplacer le modèle (si il existe)
mv gender_classifier.joblib models/ 2>/dev/null || true

# Ou utilise le script automatique
python scripts/init_project.py
```

## 🧪 Étape 4 : Tester les modules

### Test 1 : Extraction de features

```bash
python -c "
from gender_detection.features import FeatureExtractor
import pandas as pd

extractor = FeatureExtractor()
df = pd.DataFrame({'full_name': ['AMEGANVI Koffi Ama']})
result = extractor.extract_features(df)

print('✅ Feature extraction works!')
print(f'Extracted {len(result.columns)} features')
print(f'Main first name: {result[\"first_name\"].iloc[0]}')
"
```

### Test 2 : Base de données

```bash
python -c "
from gender_detection.database import FeedbackDatabase

db = FeedbackDatabase()
feedback_id = db.save_prediction('TEST Nom', 'TEST', \"['Nom']\", 'Nom', 1)

print('✅ Database works!')
print(f'Feedback ID: {feedback_id}')

stats = db.get_feedback_stats()
print(f'Total feedbacks: {stats[\"total\"]}')
"
```

### Test 3 : Entraîner le modèle

```bash
# Vérifier que le dataset existe
ls -lh data/noms_prenoms_togo.csv

# Entraîner le modèle (peut prendre 2-5 minutes)
cd src
PYTHONPATH=. python -c "
from gender_detection.model import train_model
train_model()
"
cd ..
```

### Test 4 : Faire une prédiction

```bash
python -c "
from gender_detection.model import GenderClassifier

classifier = GenderClassifier()
result = classifier.predict('AMEGANVI Koffi Ama')

print('✅ Prediction works!')
print(f'Nom: AMEGANVI Koffi Ama')
print(f'Genre prédit: {result[\"gender\"]}')
print(f'Prénom principal: {result[\"main_first_name\"]}')
"
```

## 🌐 Étape 5 : Lancer l'application web

```bash
# Option 1 : Avec Make
make run

# Option 2 : Manuellement
cd src
PYTHONPATH=. python -m gender_detection.app
```

Ouvre ton navigateur sur: **http://localhost:5000**

## 🧪 Étape 6 : Lancer les tests unitaires

```bash
# Installer pytest
pip install pytest pytest-cov

# Lancer tous les tests
make test

# Ou manuellement
pytest tests/ -v
```

## ✅ Étape 7 : Vérifier que tout fonctionne

### Test complet via l'API

```bash
# Dans un nouveau terminal, lance l'app
cd src
PYTHONPATH=. python -m gender_detection.app &
APP_PID=$!

# Attends 2 secondes
sleep 2

# Teste l'API
curl -X POST http://localhost:5000/predict \
  -H "Content-Type: application/json" \
  -d '{"full_name": "KOKOU Mensah"}'

# Tue l'app
kill $APP_PID
```

## 📊 Commandes Utiles du Makefile

```bash
make help              # Affiche toutes les commandes disponibles
make install           # Installe les dépendances
make install-dev       # Installe les dépendances de dev
make test              # Lance les tests
make test-quick        # Tests rapides sans coverage
make lint              # Vérifie le style du code
make format            # Formate le code avec Black
make clean             # Nettoie les fichiers générés
make run               # Lance le serveur de dev
make train             # Entraîne le modèle
make update-model      # Met à jour avec feedback
```

## 🐛 Résolution de problèmes

### Erreur : "Module not found"

```bash
# Assure-toi d'être dans le bon dossier
pwd  # Doit afficher: .../Gender-Detection

# Réinstalle le package
pip install -e .
```

### Erreur : "No such file: noms_prenoms_togo.csv"

```bash
# Vérifie où est le fichier
find . -name "noms_prenoms_togo.csv"

# Déplace-le vers data/
mv noms_prenoms_togo.csv data/
```

### Erreur : "Model not found"

```bash
# Entraîne le modèle
make train
```

## 🎓 Structure des Imports

Maintenant, tu peux importer les modules comme ceci:

```python
# Importer le classifier
from gender_detection import GenderClassifier

# Importer l'extracteur de features
from gender_detection import FeatureExtractor

# Importer depuis des sous-modules
from gender_detection.database import db, user_db
from gender_detection.config import FEATURE_NAMES
from gender_detection.features import extract_features
```

## 📝 Prochaines Étapes

1. ✅ Familiarise-toi avec la nouvelle structure
2. ✅ Lance les tests pour vérifier que tout marche
3. ✅ Essaye de faire des modifications dans `src/gender_detection/`
4. ✅ Relance les tests pour vérifier que ça marche toujours
5. ✅ Consulte le README.md pour la documentation complète

## 🎉 Félicitations !

Ton projet est maintenant:
- ✅ Structuré selon les normes PEP8
- ✅ Testable avec pytest
- ✅ Installable comme un vrai package Python
- ✅ Documenté professionnellement
- ✅ Déployable facilement

**Prêt pour GitHub et pour ton portfolio !** 🚀
