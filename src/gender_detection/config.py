"""Configuration module for Gender Detection system."""

import os
from pathlib import Path

# Base directories
BASE_DIR = Path(__file__).resolve().parent.parent.parent
DATA_DIR = BASE_DIR / "data"
MODEL_DIR = BASE_DIR / "models"
LOG_DIR = BASE_DIR / "logs"

# Ensure directories exist
MODEL_DIR.mkdir(exist_ok=True)
LOG_DIR.mkdir(exist_ok=True)
DATA_DIR.mkdir(exist_ok=True)

# Database settings
FEEDBACK_DB_PATH = BASE_DIR / "feedback.db.sqlite3"
USERS_DB_PATH = BASE_DIR / "users.db.sqlite3"

# Model settings
MODEL_PATH = MODEL_DIR / "gender_classifier.joblib"
DATASET_PATH = DATA_DIR / "noms_prenoms_togo.csv"
FEATURE_IMPORTANCE_PATH = BASE_DIR / "feature_importance.csv"
TRAINING_REPORT_PATH = BASE_DIR / "training_report.txt"

# Feature names
FEATURE_NAMES = [
    'first_name_length',
    'nb_first_names',
    'ends_ewe_fem', 'ends_kabye_fem', 'ends_arabe_fem',
    'ends_ewe_masc', 'ends_kabye_masc', 'ends_arabe_masc',
    'starts_ewe_fem', 'starts_kabye_fem',
    'starts_ewe_masc', 'starts_kabye_masc',
    'vowel_count', 'vowel_ratio',
    'syllable_count', 'vowel_position',
    'gender_score',
    'is_exception', 'exception_value'
]

# Linguistic patterns for Togolese names
ENDINGS = {
    'ewe_fem': ['A', 'E', 'I', 'WE', 'YA', 'BA', 'TÉ', 'DÉ', 'VI', 'SI'],
    'ewe_masc': ['OU', 'O', 'GBE', 'KPO', 'TÔ', 'DZO', 'GBO', 'NU'],
    'kabye_fem': ['È', 'Ê', 'NÉ', 'SÉ', 'ZÉ', 'NYÉ', 'KPÉ'],
    'kabye_masc': ['DO', 'TO', 'KO', 'LO', 'KOU', 'TCHA', 'KPLE'],
    'arabe_fem': ['A', 'IA', 'OUMA', 'ATOU', 'ZA', 'NA', 'FA'],
    'arabe_masc': ['OU', 'DINE', 'ROU', 'FOU', 'DOU', 'MADOU']
}

PREFIXES = {
    'ewe_fem': ['MA', 'A', 'YA', 'AFI', 'ESI', 'DZO', 'ABL', 'EDO'],
    'ewe_masc': ['KO', 'KU', 'AK', 'KOFI', 'EDEM', 'KOD', 'AMEG'],
    'kabye_fem': ['NA', 'SEN', 'TCHA', 'FÉ', 'KPA', 'NYO'],
    'kabye_masc': ['TA', 'KA', 'TCHAK', 'KPLA', 'SOU', 'TÉL']
}

# Gender exceptions database
GENDER_EXCEPTIONS = {
    'KOMI': 0, 'MAWULI': 1, 'YAO': 1, 'DEDE': 0, 'KOKOU': 1, 'SENA': 0,
    'AFI': 0, 'AKOU': 1, 'ESSO': 1, 'AMEGAN': 1, 'EDEM': 1, 'KOMLAN': 1,
    'SELOM': 0, 'DZIFA': 0, 'EFIA': 0, 'MAWUSI': 0, 'AKOS': 0
}

# Flask settings
SECRET_KEY = os.environ.get('SECRET_KEY', os.urandom(24))
FLASK_ENV = os.environ.get('FLASK_ENV', 'production')
DEBUG = FLASK_ENV == 'development'

# Admin credentials (default)
DEFAULT_ADMIN_EMAIL = os.environ.get('ADMIN_EMAIL', 'ambroisekouwadan52@gmail.com')
DEFAULT_ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD', 'admin123')

# Training schedule
TRAINING_SCHEDULE_TIME = "02:00"

# Model hyperparameters
MODEL_CONFIG = {
    'test_size': 0.2,
    'random_state': 42,
    'xgb_scale_pos_weight': 1.7,
    'xgb_max_depth': 5,
    'xgb_learning_rate': 0.05,
    'xgb_subsample': 0.8,
    'xgb_reg_alpha': 0.1,
    'rf_n_estimators': 300,
    'rf_max_depth': 12,
    'rf_min_samples_split': 5,
    'rf_class_weight': {0: 1.3, 1: 1},
    'ensemble_weights': [1.5, 1, 1]
}
