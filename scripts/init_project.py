#!/usr/bin/env python3
"""Script to initialize the project and prepare data."""

import os
import sys
from pathlib import Path
import shutil


def main():
    """Initialize the project structure."""
    base_dir = Path(__file__).parent.parent
    
    print("🚀 Initializing Gender Detection Project...")
    
    # Create necessary directories
    directories = ['data', 'models', 'logs']
    for dir_name in directories:
        dir_path = base_dir / dir_name
        dir_path.mkdir(exist_ok=True)
        print(f"✓ Created {dir_name}/ directory")
    
    # Move CSV file to data directory
    csv_source = base_dir / 'noms_prenoms_togo.csv'
    csv_dest = base_dir / 'data' / 'noms_prenoms_togo.csv'
    
    if csv_source.exists() and not csv_dest.exists():
        shutil.move(str(csv_source), str(csv_dest))
        print(f"✓ Moved dataset to data/noms_prenoms_togo.csv")
    
    # Move model file to models directory
    model_source = base_dir / 'gender_classifier.joblib'
    model_dest = base_dir / 'models' / 'gender_classifier.joblib'
    
    if model_source.exists() and not model_dest.exists():
        shutil.move(str(model_source), str(model_dest))
        print(f"✓ Moved model to models/gender_classifier.joblib")
    
    # Create .env if not exists
    env_example = base_dir / '.env.example'
    env_file = base_dir / '.env'
    
    if not env_file.exists() and env_example.exists():
        shutil.copy(str(env_example), str(env_file))
        print(f"✓ Created .env file (please update with your settings)")
    
    print("\n✅ Project initialized successfully!")
    print("\nNext steps:")
    print("  1. Update .env file with your settings")
    print("  2. Run 'make train' to train the model (if not already trained)")
    print("  3. Run 'make run' to start the development server")


if __name__ == '__main__':
    main()
