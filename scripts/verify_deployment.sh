#!/bin/bash
# Comprehensive pre-deployment verification script

echo "🔍 VERIFICATION COMPLETE DE DEPLOIEMENT RAILWAY"
echo "================================================"
echo ""

ERRORS=0

# 1. Vérifier les fichiers essentiels
echo "📋 1. Vérification des fichiers essentiels..."
REQUIRED_FILES=(
    "Procfile"
    "runtime.txt"
    "requirements.txt"
    "setup.py"
    "src/gender_detection/app.py"
    "src/gender_detection/model.py"
    "data/noms_prenoms_togo.csv"
    ".dockerignore"
    ".railwayignore"
)

for file in "${REQUIRED_FILES[@]}"; do
    if [ -f "$file" ]; then
        echo "   ✅ $file"
    else
        echo "   ❌ MANQUANT: $file"
        ((ERRORS++))
    fi
done

# 2. Vérifier que les fichiers à NE PAS copier n'existent PAS ou sont ignorés
echo ""
echo "🚫 2. Vérification des fichiers à ignorer..."
SHOULD_NOT_DEPLOY=(
    "models/gender_classifier.joblib"
    "feedback.db.sqlite3"
    "users.db.sqlite3"
    "training_report.txt"
    "feature_importance.csv"
)

for file in "${SHOULD_NOT_DEPLOY[@]}"; do
    if grep -q "$file" .dockerignore 2>/dev/null || grep -q "$(dirname $file)/" .dockerignore 2>/dev/null; then
        echo "   ✅ $file est dans .dockerignore"
    else
        echo "   ⚠️  WARNING: $file devrait être dans .dockerignore"
    fi
done

# 3. Vérifier le dataset
echo ""
echo "📊 3. Vérification du dataset..."
if [ -f "data/noms_prenoms_togo.csv" ]; then
    LINES=$(wc -l < data/noms_prenoms_togo.csv)
    if [ $LINES -gt 100 ]; then
        echo "   ✅ Dataset présent avec $LINES lignes"
    else
        echo "   ❌ Dataset trop petit: $LINES lignes"
        ((ERRORS++))
    fi
else
    echo "   ❌ Dataset manquant!"
    ((ERRORS++))
fi

# 4. Vérifier les dépendances critiques
echo ""
echo "📦 4. Vérification des dépendances critiques..."
CRITICAL_DEPS=(
    "Flask"
    "gunicorn"
    "xgboost"
    "scikit-learn"
    "pandas"
    "joblib"
)

for dep in "${CRITICAL_DEPS[@]}"; do
    if grep -qi "^${dep}" requirements.txt; then
        echo "   ✅ $dep"
    else
        echo "   ❌ MANQUANT: $dep"
        ((ERRORS++))
    fi
done

# 5. Vérifier la configuration Gunicorn
echo ""
echo "⚙️  5. Vérification de la configuration Gunicorn..."
if grep -q "gunicorn.*--timeout.*[2-3][0-9][0-9]" Procfile; then
    echo "   ✅ Timeout suffisant dans Procfile (≥200s)"
else
    echo "   ⚠️  WARNING: Timeout peut-être trop court pour l'entraînement"
fi

if grep -q "gunicorn.*--workers.*[1-4]" Procfile; then
    echo "   ✅ Nombre de workers raisonnable (1-4)"
else
    echo "   ⚠️  WARNING: Nombre de workers non optimal"
fi

# 6. Vérifier la version Python
echo ""
echo "🐍 6. Vérification de la version Python..."
if [ -f "runtime.txt" ]; then
    PYTHON_VERSION=$(cat runtime.txt)
    echo "   ✅ Version spécifiée: $PYTHON_VERSION"
else
    echo "   ⚠️  WARNING: runtime.txt manquant"
fi

# 7. Vérifier l'initialisation de l'app
echo ""
echo "🚀 7. Vérification de l'initialisation..."
if grep -q "_initialize_app()" src/gender_detection/app.py; then
    echo "   ✅ Fonction d'initialisation présente"
else
    echo "   ❌ Fonction _initialize_app() manquante"
    ((ERRORS++))
fi

if grep -q "if classifier.model_data is None:" src/gender_detection/app.py; then
    echo "   ✅ Vérification du modèle au démarrage"
else
    echo "   ⚠️  WARNING: Pas de vérification du modèle"
fi

# 8. Vérifier les templates et static
echo ""
echo "🎨 8. Vérification des assets..."
TEMPLATES=(
    "templates/index.html"
    "templates/admin_login.html"
    "templates/admin_dashboard.html"
)

for template in "${TEMPLATES[@]}"; do
    if [ -f "$template" ]; then
        echo "   ✅ $template"
    else
        echo "   ❌ MANQUANT: $template"
        ((ERRORS++))
    fi
done

if [ -f "static/styles.css" ]; then
    echo "   ✅ static/styles.css"
else
    echo "   ⚠️  WARNING: static/styles.css manquant"
fi

# 9. Vérifier la structure du package
echo ""
echo "📂 9. Vérification de la structure du package..."
if [ -f "src/gender_detection/__init__.py" ]; then
    echo "   ✅ Package Python correctement structuré"
else
    echo "   ❌ __init__.py manquant dans src/gender_detection/"
    ((ERRORS++))
fi

# 10. Résumé final
echo ""
echo "================================================"
if [ $ERRORS -eq 0 ]; then
    echo "✅ TOUS LES TESTS PASSES - PRET A DEPLOYER!"
    echo ""
    echo "📝 Prochaines étapes:"
    echo "   1. git add ."
    echo "   2. git commit -m 'fix: complete deployment configuration'"
    echo "   3. git push origin deployment"
    echo "   4. Déployer sur Railway"
    echo ""
    echo "🔑 N'oublie pas de configurer sur Railway:"
    echo "   SECRET_KEY=<génère avec scripts/generate_secret_key.py>"
    echo "   DEFAULT_ADMIN_EMAIL=admin@example.com"
    echo "   DEFAULT_ADMIN_PASSWORD=<ton_mot_de_passe_securise>"
    echo "   DEBUG=False"
    exit 0
else
    echo "❌ $ERRORS ERREUR(S) TROUVEE(S) - CORRIGE AVANT DE DEPLOYER"
    exit 1
fi
