from flask import Flask, request, jsonify, render_template, redirect, url_for, session, send_from_directory
import joblib
import pandas as pd
from database import db, UserDB
import re
import os
from datetime import datetime, timedelta
import logging
from model_training import extract_features

logging.basicConfig(level=logging.DEBUG)
app = Flask(__name__)
app.secret_key = os.urandom(24)  # Clé secrète pour les sessions

# Initialisation des bases de données
user_db = UserDB()

@app.template_filter('datetimeformat')
def datetimeformat(value, format='%d/%m/%Y %H:%M'):
    if value is None:
        return ''
    if isinstance(value, str):
        # Convertir la chaîne en objet datetime
        try:
            value = datetime.fromisoformat(value)
        except:
            return value
    return value.strftime(format) 

# Charger le modèle
def load_model():
    try:
        return joblib.load('gender_classifier.joblib')
    except FileNotFoundError:
        return None

model_data = load_model()

# Routes pour les prédictions
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    if model_data is None:
        return jsonify({'error': 'Modèle non disponible'}), 500
    
    try:    
        data = request.get_json()
        full_name = data.get('full_name', '')
        
        if not full_name:
            return jsonify({'error': 'Full name is required'}), 400
        
        # Prétraitement du nom
        surname, first_names, main_first_name = preprocess_name(full_name)
        
        # Créer un DataFrame pour l'extraction des features
        temp_df = pd.DataFrame([{'full_name': full_name}])
        temp_df = model_data['extract_fn'](temp_df)
        
        # S'assurer que toutes les features sont présentes
        for feature in model_data['features']:
            if feature not in temp_df.columns:
                temp_df[feature] = 0
        
        # Prédiction
        prediction = int(model_data['model'].predict(temp_df[model_data['features']])[0])
        gender_str = "Homme" if prediction == 1 else "Femme"
        
        # Convertir first_names en liste si c'est un string
        if isinstance(first_names, str):
            first_names = [first_names] if first_names else []
            
        # Sauvegarder la prédiction pour feedback futur
        feedback_id = db.save_prediction(
            full_name, surname, str(first_names), main_first_name, prediction
        )
        
        return jsonify({
            'surname': surname,
            'first_names': first_names,
            'main_first_name': main_first_name,
            'gender': gender_str,
            'predicted_value': prediction,
            'feedback_id': feedback_id
        })
    except Exception as e:
        app.logger.error(f"Erreur lors de la prédiction: {str(e)}")
        return jsonify({'error': 'Erreur interne du serveur'}), 500

@app.route('/feedback', methods=['POST'])
def receive_feedback():
    data = request.json
    feedback_id = data.get('feedback_id')
    actual_gender = data.get('actual_gender')  # "Homme" ou "Femme"
    predicted_value = data.get('predicted_value')  # 0 ou 1
    
    if actual_gender not in ['Homme', 'Femme']:
        return jsonify({'error': 'Invalid gender value'}), 400
    
    gender_value = 1 if actual_gender == 'Homme' else 0
    is_correct = 1 if gender_value == predicted_value else 0
    db.update_feedback(feedback_id, gender_value, is_correct)
    
    # Ajouter le feedback au CSV pour réentraînement
    full_name = db.get_full_name(feedback_id)
    if full_name:
        add_to_csv(full_name, gender_value)
    
    return jsonify({'status': 'success'})

def add_to_csv(full_name, gender):
    """Ajoute une nouvelle entrée au fichier CSV"""
    try:
        new_entry = pd.DataFrame({
            'full_name': [full_name],
            'gender': [gender]
        })
        
        # Ajouter sans écraser le fichier existant
        new_entry.to_csv('noms_prenoms_togo.csv', mode='a', header=False, index=False)
    except Exception as e:
        app.logger.error(f"Erreur lors de l'ajout au CSV: {str(e)}")

# Authentification admin
@app.route('/admin', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        if user_db.authenticate(email, password):
            session['admin_logged_in'] = True
            return redirect(url_for('admin_dashboard'))
        else:
            return render_template('admin_login.html', error="Identifiants incorrects")
    
    return render_template('admin_login.html')

@app.route('/dashboard')
def admin_dashboard():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    
    if model_data is None:
        return "Modèle non disponible", 500
        
    # Lire le rapport de performance
    try:
        with open('training_report.txt', 'r') as f:
            performance_report = f.read()
    except FileNotFoundError:
        performance_report = "Aucun rapport disponible"
    
    # Statistiques de la base de données
    feedback_stats = db.get_feedback_stats()
    
    # Calculer la prochaine date d'entraînement (demain à 2h du matin)
    now = datetime.now()
    if now.hour < 2:
        next_training = now.replace(hour=2, minute=0, second=0, microsecond=0)
    else:
        next_training = (now + timedelta(days=1)).replace(hour=2, minute=0, second=0, microsecond=0)
    
    model_info = {
        'training_date': model_data.get('training_date', ''),
        'data_size': model_data.get('data_size', 0),
        'features': model_data.get('features', []),
        'feature_importance': model_data.get('feature_importance', [])
    }
    
    return render_template('admin_dashboard.html', 
                           model_data=model_info,
                           performance_report=performance_report,
                           feedback_stats=feedback_stats,
                           next_training=next_training)

@app.route('/logout')
def logout():
    session.pop('admin_logged_in', None)
    return redirect(url_for('admin_login'))
@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')
    
# Fonctions utilitaires
def preprocess_name(full_name):
    full_name = full_name.upper().strip()
    parts = full_name.split()
    surname = parts[0] if parts else ""
    first_names = parts[1:] if len(parts) > 1 else []
    main_first_name = first_names[-1] if first_names else ""
    return surname, first_names, main_first_name

if __name__ == '__main__':
    # Créer un compte admin par défaut
    user_db.create_user('ericjohny8@gmail.com', 'admin123')
    app.run(host='0.0.0.0', port=5000, debug=False)