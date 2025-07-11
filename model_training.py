# ============= model_training.py =============
import joblib
import pandas as pd
from database import db
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier, VotingClassifier
from xgboost import XGBClassifier
from sklearn.metrics import classification_report, make_scorer, recall_score
from datetime import datetime, timedelta
import numpy as np
import re
import os
import time
from sklearn.model_selection import RandomizedSearchCV
import schedule
from sklearn.inspection import permutation_importance

# Charger les données originales
original_data = pd.read_csv('noms_prenoms_togo.csv')

# Préparation des features
features = [
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

# =================================================================
# FONCTION OPTIMISÉE DE FEATURE ENGINEERING
# =================================================================
def extract_features(df):
    # 1. Normalisation robuste
    df['full_name'] = df['full_name'].str.upper().str.strip().str.replace(r'\s+', ' ', regex=True)
    
    # 2. Séparation intelligente nom/prénoms
    split_names = df['full_name'].str.split(n=1, expand=True)
    df['surname'] = split_names[0]
    df['first_names'] = split_names[1].fillna('')
    
    # 3. Gestion des prénoms composés
    df['first_names'] = df['first_names'].str.replace('-', ' ').str.split()
    
    # 4. Extraction du prénom principal
    df['first_name'] = df['first_names'].apply(lambda x: x[-1] if x else '')
    
    # 5. Features de base
    df['first_name_length'] = df['first_name'].apply(len)
    df['nb_first_names'] = df['first_names'].apply(len)
    
    # 6. Dictionnaires ethniques enrichis (sources linguistiques vérifiées)
    endings = {
        'ewe_fem': ['A', 'E', 'I', 'WE', 'YA', 'BA', 'TÉ', 'DÉ', 'VI', 'SI'],
        'ewe_masc': ['OU', 'O', 'GBE', 'KPO', 'TÔ', 'DZO', 'GBO', 'NU'],
        'kabye_fem': ['È', 'Ê', 'NÉ', 'SÉ', 'ZÉ', 'NYÉ', 'KPÉ'],
        'kabye_masc': ['DO', 'TO', 'KO', 'LO', 'KOU', 'TCHA', 'KPLE'],
        'arabe_fem': ['A', 'IA', 'OUMA', 'ATOU', 'ZA', 'NA', 'FA'],
        'arabe_masc': ['OU', 'DINE', 'ROU', 'FOU', 'DOU', 'MADOU']
    }
    
    prefixes = {
        'ewe_fem': ['MA', 'A', 'YA', 'AFI', 'ESI', 'DZO', 'ABL', 'EDO'],
        'ewe_masc': ['KO', 'KU', 'AK', 'KOFI', 'EDEM', 'KOD', 'AMEG'],
        'kabye_fem': ['NA', 'SEN', 'TCHA', 'FÉ', 'KPA', 'NYO'],
        'kabye_masc': ['TA', 'KA', 'TCHAK', 'KPLA', 'SOU', 'TÉL']
    }
    
    # 7. Application des motifs ethniques
    for group, terms in endings.items():
        df[f'ends_{group}'] = df['first_name'].apply(
            lambda x: int(any(x.endswith(e) for e in terms)))
    
    for group, terms in prefixes.items():
        df[f'starts_{group}'] = df['first_name'].apply(
            lambda x: int(any(x.startswith(p) for p in terms)))
    
    # 8. Features phonétiques avancées
    df['vowel_count'] = df['first_name'].apply(lambda x: len(re.findall(r'[AEIOUYÉÈÊ]', x)))
    df['consonant_count'] = df['first_name'].apply(lambda x: len(re.findall(r'[BCDFGHJKLMNPQRSTVWXZ]', x)))
    df['vowel_ratio'] = df['vowel_count'] / (df['first_name_length'] + 1e-6)
    
    df['syllable_count'] = df['first_name'].apply(
        lambda x: len(re.findall(r'[AEIOUYÉÈÊ]+', x)))
    
    # 9. Position des voyelles stratégique
    def get_vowel_position(name):
        if not name:
            return 0
        match = re.search(r'[AEIOUYÉÈÊ]', name)
        return match.start() / len(name) if match else 0
    df['vowel_position'] = df['first_name'].apply(get_vowel_position)
    
    # 10. Gestion des exceptions critiques (cas fréquents mal classés)
    exceptions_db = {
        'KOMI': 0, 'MAWULI': 1, 'YAO': 1, 'DEDE': 0, 'KOKOU': 1, 'SENA': 0,
        'AFI': 0, 'AKOU': 1, 'ESSO': 1, 'AMEGAN': 1, 'EDEM': 1, 'KOMLAN': 1,
        'SELOM': 0, 'DZIFA': 0, 'EFIA': 0, 'MAWUSI': 0, 'AKOS': 0
    }
    df['is_exception'] = df['first_name'].apply(lambda x: 1 if x in exceptions_db else 0)
    df['exception_value'] = df['first_name'].apply(lambda x: exceptions_db.get(x, 0.5))
    
    # 11. Feature composite stratégique
    df['gender_score'] = (
        0.4 * (df['ends_ewe_fem'] + df['ends_kabye_fem'] + df['ends_arabe_fem']) -
        0.4 * (df['ends_ewe_masc'] + df['ends_kabye_masc'] + df['ends_arabe_masc']) +
        0.2 * (df['starts_ewe_fem'] + df['starts_kabye_fem']) -
        0.2 * (df['starts_ewe_masc'] + df['starts_kabye_masc']) +
        0.1 * df['vowel_ratio']
    )
    
    return df

# =================================================================
# FONCTIONS D'OPTIMISATION ET ENSEMBLE LEARNING
# =================================================================
def optimize_recall_female(X_train, y_train):
    """Optimise spécifiquement pour le recall des femmes"""
    base_model = XGBClassifier(
        scale_pos_weight=1.7,
        max_depth=5,
        learning_rate=0.05,
        subsample=0.8,
        reg_alpha=0.1,
        random_state=42
    )
    
    param_dist = {
        'scale_pos_weight': [1.5, 1.7, 2.0],
        'max_depth': [4, 5, 6],
        'learning_rate': [0.05, 0.1],
        'subsample': [0.7, 0.8],
        'reg_alpha': [0, 0.1],
        'reg_lambda': [1, 1.5]
    }
    
    # Focus sur le recall de la classe 0 (femmes)
    scorer = make_scorer(recall_score, pos_label=0)
    
    search = RandomizedSearchCV(
        base_model,
        param_distributions=param_dist,
        n_iter=30,
        scoring=scorer,
        cv=5,
        random_state=42,
        n_jobs=-1
    )
    
    search.fit(X_train, y_train)
    return search.best_estimator_

def create_ensemble(X_train, y_train):
    """Crée un ensemble optimisé"""
    # Calcul du ratio de déséquilibre
    class_ratio = np.sum(y_train == 1) / np.sum(y_train == 0)
    
    # Modèle 1: XGBoost optimisé pour les femmes
    xgb_fem = optimize_recall_female(X_train, y_train)
    
    # Modèle 2: Random Forest équilibré
    rf = RandomForestClassifier(
        n_estimators=300,
        max_depth=12,
        min_samples_split=5,
        class_weight={0: 1.3, 1: 1},
        random_state=42
    )
    
    # Modèle 3: XGBoost standard
    xgb_std = XGBClassifier(
        n_estimators=200,
        learning_rate=0.1,
        max_depth=6,
        scale_pos_weight=class_ratio,
        random_state=42
    )
    
    return VotingClassifier(
        estimators=[
            ('xgb_fem', xgb_fem),
            ('rf', rf),
            ('xgb_std', xgb_std)
        ],
        voting='soft',
        weights=[1.5, 1, 1] 
    )

def train_and_update_model():
    """Fonction principale pour l'entraînement et la mise à jour"""
    print(f"\n{datetime.now()} - Début de l'entraînement automatique")
               
    # Charger les nouveaux feedbacks
    feedback_data = db.get_new_feedback()
    
    if not feedback_data.empty:
        print(f"{len(feedback_data)} nouveaux feedbacks à intégrer")
        
        # Préparer les données de feedback
        feedback_data['gender'] = feedback_data['actual_gender']
        feedback_data = feedback_data[['full_name', 'gender']]
        
        # Combiner avec les données originales
        combined_data = pd.concat([original_data, feedback_data], ignore_index=True)
        
        # Supprimer les doublons
        combined_data = combined_data.drop_duplicates(subset=['full_name'])
        
        # Sauvegarder le nouveau dataset
        combined_data.to_csv('noms_prenoms_togo.csv', index=False)
        print(f"Nouveau dataset sauvegardé avec {len(combined_data)} entrées")
        # Extraire les features
        combined_data = extract_features(combined_data)
        
        # Sélectionner les features
        X = combined_data[features]
        y = combined_data['gender']
        
        # Séparation des données
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )
        
        # Créer et entraîner l'ensemble de modèles
        model = create_ensemble(X_train, y_train)
        model.fit(X_train, y_train)
        
        # Évaluation
        y_pred = model.predict(X_test)
        report = classification_report(y_test, y_pred)
        
        print("Nouvelles performances après mise à jour:")
        print(report)

        result = permutation_importance(model, X_test, y_test, n_repeats=10)
         # Créer un DataFrame d'importance
        importance_df = pd.DataFrame({
            'feature': features,
            'importance': result.importances_mean
        }).sort_values('importance', ascending=False)
        
        # Sauvegarder l'importance des features
        importance_df.to_csv('feature_importance.csv', index=False)
        print("Importance des features sauvegardée")
        
        # Sauvegarder le nouveau modèle
        model_data = {
            'model': model,
            'features': features,
            'extract_fn': extract_features,
            'training_date': datetime.now().isoformat(),
            'data_size': len(combined_data),
            'performance_report': report,
            'feature_importance': importance_df.to_dict(orient='records')  # Nouveau
        }
        
        joblib.dump(model_data, 'gender_classifier.joblib')
        
        # Sauvegarder le rapport de performance
        with open('training_report.txt', 'w') as f:
            f.write(f"Dernière mise à jour: {datetime.now()}\n")
            f.write(f"Taille du dataset: {len(combined_data)} entrées\n")
            f.write(f"Nouveaux feedbacks intégrés: {len(feedback_data)}\n\n")
            f.write(report)
            
        # Marquer les feedbacks comme utilisés (CORRECTION ICI)
        # On récupère les IDs depuis la base de données
        with db.get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM feedback WHERE used_for_training = 0")
            feedback_ids = [row[0] for row in cursor.fetchall()]
        
        if feedback_ids:
            db.mark_feedback_as_used(feedback_ids)
        
        print(f"Modèle mis à jour avec {len(feedback_data)} nouveaux exemples")
    else:
        print("Aucun nouveau feedback - Pas de mise à jour nécessaire")

# Planifier l'exécution tous les jours à 2h du matin
schedule.every().day.at("02:00").do(train_and_update_model)

if __name__ == "__main__":
    print("Démarrage du service d'entraînement automatique...")
    print("Prochain entraînement prévu à 02:00")
    
    # Exécuter immédiatement au premier lancement
    train_and_update_model()
    
    # Boucle principale pour exécuter les tâches planifiées
    while True:
        schedule.run_pending()
        time.sleep(60)  # Vérifier toutes les minutes