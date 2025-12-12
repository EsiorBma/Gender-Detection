# 👤 Guide d'Utilisation - Gender Detection

## Pour un Nouvel Utilisateur

Ce guide explique comment utiliser le projet Gender Detection, que tu sois développeur ou utilisateur final.

---

## 🎯 Scénario 1 : Utilisateur Final (Interface Web)

### Étape 1 : Accéder à l'Application

1. Ouvre ton navigateur web
2. Va sur : `http://localhost:5000` (ou l'URL de déploiement)
3. Tu verras la page d'accueil avec un formulaire

### Étape 2 : Faire une Prédiction

1. **Entre un nom complet** dans le champ
   ```
   Exemple: AMEGANVI Koffi Ama
   ```

2. **Clique sur "Détecter le Genre"**

3. **Résultat affiché** :
   ```
   Nom de famille: AMEGANVI
   Prénom(s): Koffi, Ama
   Prénom principal: Ama
   Genre détecté: Femme ✓
   ```

4. **Confirme ou Corrige** :
   - Si correct : Clique sur "✓ Femme"
   - Si incorrect : Clique sur "✗ Homme"
   - Ton feedback aide à améliorer le modèle !

### Étape 3 : Tester avec d'Autres Noms

Exemples à essayer :
- `KOKOU Mensah` → Homme
- `DZIFA Akossiwa` → Femme
- `EDEM Kodjo` → Homme
- `AFIA Mawusi` → Femme

---

## 🔧 Scénario 2 : Développeur Python (Utiliser le Package)

### Installation

```bash
# Cloner le projet
git clone https://github.com/yourusername/gender-detection.git
cd gender-detection

# Créer environnement virtuel
python3 -m venv env
source env/bin/activate  # Linux/Mac
# ou: env\Scripts\activate  # Windows

# Installer le package
pip install -e .
```

### Utilisation dans ton Code

```python
from gender_detection import GenderClassifier

# Initialiser le classifier
classifier = GenderClassifier()

# Faire une prédiction
result = classifier.predict("AMEGANVI Koffi Ama")

# Afficher les résultats
print(f"Genre: {result['gender']}")
print(f"Nom: {result['surname']}")
print(f"Prénoms: {', '.join(result['first_names'])}")
print(f"Confiance: {result['predicted_value']}")
```

**Sortie :**
```
Genre: Femme
Nom: AMEGANVI
Prénoms: KOFFI, AMA
Confiance: 0
```

### Prédictions en Batch

```python
from gender_detection import GenderClassifier

classifier = GenderClassifier()

# Liste de noms
names = [
    "KOKOU Mensah",
    "DZIFA Akossiwa",
    "EDEM Kodjo",
    "AFIA Mawusi"
]

# Prédire pour chaque nom
for name in names:
    result = classifier.predict(name)
    print(f"{name:<30} → {result['gender']}")
```

**Sortie :**
```
KOKOU Mensah                   → Homme
DZIFA Akossiwa                 → Femme
EDEM Kodjo                     → Homme
AFIA Mawusi                    → Femme
```

### Entraîner ton Propre Modèle

```python
from gender_detection import GenderClassifier

# Créer un nouveau classifier
classifier = GenderClassifier()

# Entraîner avec ton dataset
result = classifier.train(
    dataset_path="data/my_custom_dataset.csv",
    save=True
)

print(f"Modèle entraîné avec {result['data_size']} exemples")
print(result['report'])
```

---

## 💻 Scénario 3 : Développeur API (Utiliser l'API REST)

### Démarrer l'API

```bash
# Mode développement
make run

# Mode production
make run-gunicorn
```

### Endpoint 1 : Prédiction

**Requête :**
```bash
curl -X POST http://localhost:5000/predict \
  -H "Content-Type: application/json" \
  -d '{"full_name": "AMEGANVI Koffi Ama"}'
```

**Réponse :**
```json
{
  "gender": "Femme",
  "predicted_value": 0,
  "surname": "AMEGANVI",
  "first_names": ["KOFFI", "AMA"],
  "main_first_name": "AMA",
  "feedback_id": 123
}
```

### Endpoint 2 : Feedback

**Requête :**
```bash
curl -X POST http://localhost:5000/feedback \
  -H "Content-Type: application/json" \
  -d '{
    "feedback_id": 123,
    "actual_gender": "Femme",
    "predicted_value": 0
  }'
```

**Réponse :**
```json
{
  "status": "success"
}
```

### Exemple avec Python `requests`

```python
import requests

# URL de l'API
API_URL = "http://localhost:5000"

# Faire une prédiction
response = requests.post(
    f"{API_URL}/predict",
    json={"full_name": "KOKOU Mensah"}
)

result = response.json()
print(f"Genre prédit: {result['gender']}")

# Envoyer un feedback
feedback_response = requests.post(
    f"{API_URL}/feedback",
    json={
        "feedback_id": result['feedback_id'],
        "actual_gender": "Homme",
        "predicted_value": result['predicted_value']
    }
)

print(f"Feedback: {feedback_response.json()['status']}")
```

### Exemple avec JavaScript (fetch)

```javascript
// Prédiction
const response = await fetch('http://localhost:5000/predict', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ full_name: 'AMEGANVI Koffi Ama' })
});

const result = await response.json();
console.log('Genre:', result.gender);

// Feedback
await fetch('http://localhost:5000/feedback', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    feedback_id: result.feedback_id,
    actual_gender: 'Femme',
    predicted_value: result.predicted_value
  })
});
```

---

## 🖥️ Scénario 4 : Administrateur Système (Ligne de Commande)

### Installation

```bash
pip install -e .
```

### Commandes CLI

#### 1. Prédiction Simple

```bash
gender-detect predict "AMEGANVI Koffi Ama"
```

**Sortie :**
```
Nom complet: AMEGANVI Koffi Ama
Nom de famille: AMEGANVI
Prénom(s): KOFFI, AMA
Prénom principal: AMA
Genre prédit: Femme
```

#### 2. Prédiction JSON

```bash
gender-detect predict "KOKOU Mensah" --json
```

**Sortie :**
```json
{
  "gender": "Homme",
  "predicted_value": 1,
  "surname": "KOKOU",
  "first_names": ["MENSAH"],
  "main_first_name": "MENSAH"
}
```

#### 3. Prédiction en Batch

Créer un fichier `names.txt` :
```
AMEGANVI Koffi Ama
KOKOU Mensah
DZIFA Akossiwa
EDEM Kodjo
```

Exécuter :
```bash
gender-detect predict --batch names.txt
```

**Sortie :**
```
Processing 4 names...

AMEGANVI Koffi Ama                       -> Femme
KOKOU Mensah                             -> Homme
DZIFA Akossiwa                           -> Femme
EDEM Kodjo                               -> Homme
```

#### 4. Entraîner le Modèle

```bash
gender-detect train
```

#### 5. Mettre à Jour avec Feedback

```bash
gender-detect update
```

#### 6. Voir les Statistiques

```bash
gender-detect stats
```

**Sortie :**
```
📊 Feedback Statistics
==================================================
Total predictions: 1523
With feedback: 342
Accuracy: 93.27%
Last feedback: 2025-12-11 10:30:15
```

---

## 🐳 Scénario 5 : DevOps (Déploiement Docker)

### Build et Run avec Docker

```bash
# Build l'image
docker build -t gender-detection:latest .

# Run le container
docker run -p 8000:8000 \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/models:/app/models \
  gender-detection:latest
```

### Avec Docker Compose

```bash
# Démarrer
docker-compose up -d

# Voir les logs
docker-compose logs -f

# Arrêter
docker-compose down
```

---

## 📊 Scénario 6 : Data Scientist (Analyse et Amélioration)

### Extraire les Features

```python
from gender_detection import FeatureExtractor
import pandas as pd

# Créer un dataset
df = pd.DataFrame({
    'full_name': ['AMEGANVI Koffi Ama', 'KOKOU Mensah']
})

# Extraire les features
extractor = FeatureExtractor()
features_df = extractor.extract_features(df)

# Voir les features
print(features_df[['first_name', 'vowel_count', 'gender_score']])
```

### Analyser l'Importance des Features

```python
import pandas as pd

# Lire l'importance des features
importance_df = pd.read_csv('feature_importance.csv')

# Top 10 features
print(importance_df.head(10))
```

### Entraîner avec des Hyperparamètres Personnalisés

```python
from gender_detection.model import GenderClassifier
from gender_detection.config import MODEL_CONFIG

# Modifier les hyperparamètres
MODEL_CONFIG['xgb_max_depth'] = 7
MODEL_CONFIG['rf_n_estimators'] = 500

# Entraîner
classifier = GenderClassifier()
result = classifier.train()
```

---

## 🔄 Happy Path Complet (Workflow Idéal)

### Pour un Nouveau Développeur

```bash
# 1. Cloner et installer
git clone https://github.com/yourusername/gender-detection.git
cd gender-detection
make init

# 2. Initialiser le projet
python scripts/init_project.py

# 3. Vérifier l'installation
make test

# 4. Entraîner le modèle
make train

# 5. Tester une prédiction en CLI
gender-detect predict "AMEGANVI Koffi Ama"

# 6. Lancer l'application web
make run

# 7. Tester dans le navigateur
# → http://localhost:5000

# 8. Utiliser dans ton code
python
>>> from gender_detection import GenderClassifier
>>> c = GenderClassifier()
>>> c.predict("KOKOU Mensah")
{'gender': 'Homme', ...}
```

### Pour un Utilisateur Final

1. **Accéder à l'application** → `http://ton-domaine.com`
2. **Entrer un nom** → "AMEGANVI Koffi Ama"
3. **Cliquer sur "Détecter"** → Résultat affiché
4. **Confirmer ou corriger** → Feedback enregistré
5. **Répéter** pour d'autres noms

---

## 🎓 Cas d'Usage Réels

### 1. Système de Gestion de CNI
```python
# Pré-remplir automatiquement le champ "sexe"
from gender_detection import GenderClassifier

classifier = GenderClassifier()

def process_id_application(full_name):
    result = classifier.predict(full_name)
    return {
        'surname': result['surname'],
        'first_names': result['first_names'],
        'suggested_gender': result['gender'],
        'confidence': result['predicted_value']
    }
```

### 2. Validation de Formulaires
```javascript
// Vérifier la cohérence nom/genre
async function validateForm(name, selectedGender) {
  const response = await fetch('/predict', {
    method: 'POST',
    body: JSON.stringify({ full_name: name })
  });
  
  const prediction = await response.json();
  
  if (prediction.gender !== selectedGender) {
    alert('Le genre sélectionné ne correspond pas au nom. Voulez-vous continuer?');
  }
}
```

### 3. Analyse de Base de Données
```python
# Détecter les incohérences dans une base existante
import pandas as pd
from gender_detection import GenderClassifier

classifier = GenderClassifier()
df = pd.read_csv('citizens_database.csv')

def check_consistency(row):
    prediction = classifier.predict(row['full_name'])
    return prediction['gender'] == row['declared_gender']

df['is_consistent'] = df.apply(check_consistency, axis=1)
inconsistencies = df[~df['is_consistent']]

print(f"{len(inconsistencies)} incohérences détectées")
```

---

## 📞 Support et Questions

- **Documentation** : Voir [README.md](../README.md)
- **Démarrage rapide** : Voir [QUICKSTART.md](../QUICKSTART.md)
- **Problèmes** : Ouvrir une issue sur GitHub
- **Email** : ericjohny87@gmail.com

---

## 🎯 Résumé des Commandes Essentielles

| Objectif | Commande |
|----------|----------|
| Installer | `pip install -e .` |
| Tester | `make test` |
| Lancer l'app | `make run` |
| Prédiction CLI | `gender-detect predict "Nom"` |
| Entraîner | `make train` |
| Voir stats | `gender-detect stats` |
| Docker | `docker-compose up` |

---

**Bon usage ! 🚀**
