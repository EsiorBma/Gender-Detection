"""Flask web application for gender detection."""

import logging
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

    # Get feedback statistics
    feedback_stats = db.get_feedback_stats()

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
        next_training=next_training
    )


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


def create_app():
    """Application factory."""
    # Create default admin user
    user_db.create_user(DEFAULT_ADMIN_EMAIL, DEFAULT_ADMIN_PASSWORD)
    return app


if __name__ == '__main__':
    # Create default admin user
    user_db.create_user(DEFAULT_ADMIN_EMAIL, DEFAULT_ADMIN_PASSWORD)

    # Run development server
    app.run(debug=DEBUG, host='0.0.0.0', port=5000)
