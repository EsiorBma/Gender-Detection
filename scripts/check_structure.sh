#!/bin/bash
# Script pour vérifier que tout est en place

echo "🔍 Vérification de la structure du projet..."
echo ""

# Couleurs
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color

check_file() {
    if [ -f "$1" ]; then
        echo -e "${GREEN}✓${NC} $1"
    else
        echo -e "${RED}✗${NC} $1 (manquant)"
    fi
}

check_dir() {
    if [ -d "$1" ]; then
        echo -e "${GREEN}✓${NC} $1/"
    else
        echo -e "${RED}✗${NC} $1/ (manquant)"
    fi
}

echo "📁 Dossiers:"
check_dir "src/gender_detection"
check_dir "tests"
check_dir "docs"
check_dir "scripts"
check_dir "data"
check_dir "models"
check_dir "config"
check_dir "templates"
check_dir "static"

echo ""
echo "📄 Fichiers de configuration:"
check_file "setup.py"
check_file "pyproject.toml"
check_file "Makefile"
check_file "requirements.txt"
check_file "requirements-dev.txt"
check_file ".gitignore"
check_file ".env.example"
check_file "Dockerfile"
check_file "docker-compose.yml"
check_file "LICENSE"

echo ""
echo "📚 Documentation:"
check_file "README.md"
check_file "QUICKSTART.md"
check_file "MIGRATION.md"
check_file "SUMMARY.md"

echo ""
echo "🐍 Modules Python:"
check_file "src/gender_detection/__init__.py"
check_file "src/gender_detection/config.py"
check_file "src/gender_detection/features.py"
check_file "src/gender_detection/model.py"
check_file "src/gender_detection/database.py"
check_file "src/gender_detection/app.py"
check_file "src/gender_detection/cli.py"

echo ""
echo "🧪 Tests:"
check_file "tests/test_features.py"
check_file "tests/test_model.py"
check_file "tests/test_database.py"
check_file "tests/conftest.py"

echo ""
echo "🔧 Scripts:"
check_file "scripts/init_project.py"
check_file "scripts/update_model.py"

echo ""
echo "📊 Résumé:"
total_files=$(find . -type f -not -path './env/*' -not -path './.git/*' -not -path './__pycache__/*' | wc -l)
echo "Total de fichiers: $total_files"

echo ""
echo "✅ Vérification terminée!"
