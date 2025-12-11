#!/usr/bin/env python3
"""Génère une SECRET_KEY sécurisée pour Flask."""

import secrets

print("=" * 60)
print("🔐 GÉNÉRATION DE SECRET_KEY POUR RAILWAY")
print("=" * 60)
print()

# Génère une clé aléatoire sécurisée
secret_key = secrets.token_urlsafe(32)

print("📋 Copie cette clé dans Railway:")
print()
print(f"   SECRET_KEY={secret_key}")
print()
print("=" * 60)
print()
print("🚂 CONFIGURATION RAILWAY:")
print()
print("1. Va sur https://railway.app/")
print("2. Dashboard → ton projet → Settings → Variables")
print("3. Click 'New Variable'")
print("4. Name: SECRET_KEY")
print(f"5. Value: {secret_key}")
print("6. Click 'Add'")
print()
print("=" * 60)
print()
print("📄 TOUTES LES VARIABLES À CONFIGURER:")
print()
print(f"SECRET_KEY={secret_key}")
print("DEFAULT_ADMIN_EMAIL=admin@example.com")
print("DEFAULT_ADMIN_PASSWORD=ChangeMe123Secure!")
print("DEBUG=False")
print()
print("=" * 60)
print()
print("⚠️  IMPORTANT:")
print("   - Ne partage JAMAIS cette clé publiquement")
print("   - Ne la commit pas dans Git")
print("   - Régénère-la si compromise")
print()
