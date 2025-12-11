"""Flask web application for gender detection."""

import logging
import threading
import time
import re
from datetime import datetime, timedelta
from pathlib import Path

from flask import (
    Flask, request, jsonify, render_template,
    redirect, url_for, session, send_from_directory
)
import pandas as pd

from gender_detection.model import GenderClassifier
from gender_detection.database import db, user_db
from gender_detection.config import (
    SECRET_KEY, DEBUG, DEFAULT_ADMIN_EMAIL,
    DEFAULT_ADMIN_PASSWORD, DATASET_PATH
)


# Configure logging
logging.basicConfig(
    level=logging.DEBUG if DEBUG else logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__, 
            template_folder='../../templates',  # Adjusted path to root/templates
            static_folder='../../static')        # Adjusted path to root/static
app.secret_key = SECRET_KEY

# Initialize model
classifier = GenderClassifier()


@app.template_filter('datetimeformat')
def datetimeformat(value, fmt='%d/%m/%Y %H:%M'):
    """Format datetime for templates."""
    if value is None:
        return ''
    if isinstance(value, str):
        try:
            value = datetime.fromisoformat(value)
        except (ValueError, AttributeError):
            return value
    return value.strftime(fmt)


@app.route('/')
def index():
    """Render main prediction page."""
    return render_template('index.html')


@app.route('/predict', methods=['POST'])
def predict():
    """Handle gender prediction request."""
    if classifier.model_data is None:
        return jsonify({'error': 'Model not available'}), 500

    try:
        data = request.get_json()
        full_name = data.get('full_name', '').strip()

        if not full_name:
            return jsonify({'error': 'Full name is required'}), 400

        # Make prediction
        result = classifier.predict(full_name)

        # Convert first_names to list if string
        first_names = result['first_names']
        if isinstance(first_names, str):
            first_names = [first_names] if first_names else []

        # Save prediction for future feedback
        feedback_id = db.save_prediction(
            full_name,
            result['surname'],
            str(first_names),
            result['main_first_name'],
            result['predicted_value']
        )

        return jsonify({
            'surname': result['surname'],
            'first_names': first_names,
            'main_first_name': result['main_first_name'],
            'gender': result['gender'],
            'predicted_value': result['predicted_value'],
            'feedback_id': feedback_id
        })

    except Exception as e:
        logger.error(f"Error during prediction: {str(e)}", exc_info=True)
        return jsonify({'error': 'Internal server error'}), 500


@app.route('/feedback', methods=['POST'])
def receive_feedback():
    """Handle user feedback on predictions."""
    try:
        data = request.json
        feedback_id = data.get('feedback_id')
        actual_gender = data.get('actual_gender')  # "Homme" or "Femme"
        predicted_value = data.get('predicted_value')  # 0 or 1

        if actual_gender not in ['Homme', 'Femme']:
            return jsonify({'error': 'Invalid gender value'}), 400

        # Convert to numeric
        gender_value = 1 if actual_gender == 'Homme' else 0
        is_correct = 1 if gender_value == predicted_value else 0

        # Update database
        db.update_feedback(feedback_id, gender_value, is_correct)

        # Add to CSV for future retraining
        full_name = db.get_full_name(feedback_id)
        if full_name:
            _add_to_csv(full_name, gender_value)

        return jsonify({'status': 'success'})

    except Exception as e:
        logger.error(f"Error processing feedback: {str(e)}", exc_info=True)
        return jsonify({'error': 'Internal server error'}), 500


@app.route('/admin', methods=['GET', 'POST'])
def admin_login():
    """Handle admin login."""
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        if user_db.authenticate(email, password):
            session['admin_logged_in'] = True
            return redirect(url_for('admin_dashboard'))
        else:
            return render_template('admin_login.html', error="Invalid credentials")

    return render_template('admin_login.html')


@app.route('/dashboard')
def admin_dashboard():
    """Display admin dashboard."""
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))

    if classifier.model_data is None:
        return "Model not available", 500

    # Read performance report
    try:
        report_path = Path(__file__).parent.parent.parent / 'training_report.txt'
        with open(report_path, 'r') as f:
            performance_report = f.read()
    except FileNotFoundError:
        performance_report = "No report available"

    # Extract model accuracy from performance report
    model_accuracy = 93  # Default from training
    try:
        # Extract accuracy from classification report
        match = re.search(r'accuracy\s+([0-9.]+)', performance_report)
        if match:
            model_accuracy = round(float(match.group(1)) * 100, 2)
    except Exception as e:
        logger.warning(f"Could not parse accuracy: {e}")

    # Get feedback statistics
    feedback_stats = db.get_feedback_stats()
    # Override with model accuracy instead of feedback accuracy
    feedback_stats['model_accuracy'] = model_accuracy

    # Get recent feedbacks for display
    recent_feedbacks = db.get_recent_feedbacks(limit=20)

    # Calculate next training time (tomorrow at 2 AM)
    now = datetime.now()
    if now.hour < 2:
        next_training = now.replace(hour=2, minute=0, second=0, microsecond=0)
    else:
        next_training = (now + timedelta(days=1)).replace(
            hour=2, minute=0, second=0, microsecond=0
        )

    # Model information
    model_info = {
        'training_date': classifier.model_data.get('training_date', ''),
        'data_size': classifier.model_data.get('data_size', 0),
        'features': classifier.model_data.get('features', []),
        'feature_importance': classifier.model_data.get('feature_importance', [])
    }

    return render_template(
        'admin_dashboard.html',
        model_data=model_info,
        performance_report=performance_report,
        feedback_stats=feedback_stats,
        feedbacks=recent_feedbacks,
        next_training=next_training
    )


@app.route('/retrain', methods=['POST'])
def retrain_model():
    """Manually trigger model retraining."""
    if not session.get('admin_logged_in'):
        return jsonify({'error': 'Unauthorized'}), 401

    try:
        logger.info("Manual retraining started")
        
        # Check for new feedback
        feedback_data = db.get_new_feedback()
        
        if feedback_data.empty:
            return jsonify({
                'success': True,
                'message': 'Pas de nouveaux feedbacks. Modèle déjà à jour.',
                'feedback_count': 0
            })
        
        # Update model with feedback
        success = classifier.update_with_feedback()
        
        if success:
            return jsonify({
                'success': True,
                'message': f'Modèle réentraîné avec succès avec {len(feedback_data)} nouveaux exemples!',
                'feedback_count': len(feedback_data)
            })
        else:
            return jsonify({
                'success': False,
                'message': 'Échec du réentraînement',
                'feedback_count': 0
            })
            
    except Exception as e:
        logger.error(f"Retraining error: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'Erreur: {str(e)}',
            'feedback_count': 0
        }), 500


@app.route('/logout')
def logout():
    """Handle admin logout."""
    session.pop('admin_logged_in', None)
    return redirect(url_for('admin_login'))


@app.route('/favicon.ico')
def favicon():
    """Serve favicon."""
    static_dir = Path(__file__).parent.parent / 'static'
    return send_from_directory(
        static_dir,
        'favicon.ico',
        mimetype='image/vnd.microsoft.icon'
    )


def _add_to_csv(full_name: str, gender: int) -> None:
    """
    Add feedback entry to CSV dataset.

    Args:
        full_name: Complete name
        gender: Gender value (0=Female, 1=Male)
    """
    try:
        new_entry = pd.DataFrame({
            'full_name': [full_name],
            'gender': [gender]
        })

        # Append without overwriting
        new_entry.to_csv(str(DATASET_PATH), mode='a', header=False, index=False)
    except Exception as e:
        logger.error(f"Error adding to CSV: {str(e)}")


def automatic_training_scheduler():
    """Background thread for automatic training at 2 AM."""
    while True:
        now = datetime.now()
        # Calculate seconds until next 2 AM
        if now.hour < 2:
            next_run = now.replace(hour=2, minute=0, second=0, microsecond=0)
        else:
            next_run = (now + timedelta(days=1)).replace(
                hour=2, minute=0, second=0, microsecond=0
            )
        
        sleep_seconds = (next_run - now).total_seconds()
        logger.info(f"Next automatic training scheduled at {next_run} (in {sleep_seconds/3600:.1f} hours)")
        
        # Sleep until 2 AM
        time.sleep(sleep_seconds)
        
        # Run automatic training
        try:
            logger.info("Starting automatic training at 2 AM")
            classifier.update_with_feedback()
        except Exception as e:
            logger.error(f"Automatic training failed: {str(e)}")
        
        # Sleep 1 minute to avoid running twice
        time.sleep(60)


def create_app():
    """Application factory."""
    # Create default admin user
    user_db.create_user(DEFAULT_ADMIN_EMAIL, DEFAULT_ADMIN_PASSWORD)
    
    # Train model if it doesn't exist (first deployment)
    if classifier.model_data is None:
        logger.info("Model not found - training model on first deployment...")
        try:
            classifier.train()
            logger.info("✅ Initial model training completed successfully")
        except Exception as e:
            logger.error(f"❌ Failed to train model on startup: {e}", exc_info=True)
    
    # Start automatic training scheduler in background
    scheduler_thread = threading.Thread(
        target=automatic_training_scheduler,
        daemon=True  # Thread will stop when main program stops
    )
    scheduler_thread.start()
    logger.info("Automatic training scheduler started (runs daily at 2 AM)")
    
    return app


if __name__ == '__main__':
    # Create default admin user
    user_db.create_user(DEFAULT_ADMIN_EMAIL, DEFAULT_ADMIN_PASSWORD)
    
    # Train model if it doesn't exist (first deployment)
    if classifier.model_data is None:
        logger.info("Model not found - training model on first startup...")
        try:
            classifier.train()
            logger.info("✅ Initial model training completed successfully")
        except Exception as e:
            logger.error(f"❌ Failed to train model on startup: {e}", exc_info=True)
    
    # Start automatic training scheduler in background
    scheduler_thread = threading.Thread(
        target=automatic_training_scheduler,
        daemon=True
    )
    scheduler_thread.start()
    logger.info("Automatic training scheduler started (runs daily at 2 AM)")

    # Run development server
    app.run(debug=DEBUG, host='0.0.0.0', port=5000)
