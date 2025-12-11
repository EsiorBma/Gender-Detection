#!/bin/bash

# Script de vérification avant déploiement Railway

echo "🔍 Vérification de la structure de déploiement..."
echo ""

# Couleurs
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Compteurs
errors=0
warnings=0

# Fonction de vérification
check_file() {
    if [ -f "$1" ]; then
        echo -e "${GREEN}✓${NC} $1"
    else
        echo -e "${RED}✗${NC} $1 (MANQUANT)"
        ((errors++))
    fi
}

check_dir() {
    if [ -d "$1" ]; then
        echo -e "${GREEN}✓${NC} $1/"
    else
        echo -e "${RED}✗${NC} $1/ (MANQUANT)"
        ((errors++))
    fi
}

check_optional() {
    if [ -f "$1" ]; then
        echo -e "${GREEN}✓${NC} $1 (optionnel)"
    else
        echo -e "${YELLOW}⚠${NC} $1 (optionnel, absent)"
        ((warnings++))
    fi
}

echo "📦 FICHIERS DE CONFIGURATION:"
check_file "requirements.txt"
check_file "runtime.txt"
check_file "Procfile"
check_file "railway.json"
check_file ".env.example"
check_file ".gitignore"
check_file ".railwayignore"

echo ""
echo "📁 STRUCTURE APPLICATION:"
check_dir "src"
check_dir "src/gender_detection"
check_file "src/gender_detection/__init__.py"
check_file "src/gender_detection/app.py"
check_file "src/gender_detection/config.py"
check_file "src/gender_detection/model.py"
check_file "src/gender_detection/features.py"
check_file "src/gender_detection/database.py"

echo ""
echo "🎨 TEMPLATES & STATIC:"
check_dir "templates"
check_file "templates/index.html"
check_file "templates/admin_login.html"
check_file "templates/admin_dashboard.html"
check_dir "static"
check_file "static/styles.css"

echo ""
echo "💾 DONNÉES & MODÈLE:"
check_dir "models"
check_file "models/gender_classifier.joblib"
check_dir "data"
check_file "data/noms_prenoms_togo.csv"

echo ""
echo "📚 DOCUMENTATION:"
check_file "README.md"
check_optional "QUICKSTART.md"
check_optional "docs/DEPLOYMENT.md"

echo ""
echo "═══════════════════════════════════════════════════════"

if [ $errors -eq 0 ]; then
    echo -e "${GREEN}✅ TOUT EST PRÊT POUR LE DÉPLOIEMENT!${NC}"
    echo ""
    echo "Prochaines étapes:"
    echo "  1. git add ."
    echo "  2. git commit -m 'chore: prepare deployment'"
    echo "  3. git push origin deployment"
    echo "  4. Connecter Railway à GitHub"
    exit 0
else
    echo -e "${RED}❌ $errors ERREUR(S) TROUVÉE(S)${NC}"
    echo -e "${YELLOW}⚠ $warnings AVERTISSEMENT(S)${NC}"
    echo ""
    echo "Corrige les erreurs avant de déployer!"
    exit 1
fi
