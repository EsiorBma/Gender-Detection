# 🎯 Gender Detection for Togolese Names

[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Code Style](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

A machine learning system for predicting gender from Togolese names, optimized for Ewe, Kabyé, and Arabic naming conventions.

## 📋 Table of Contents

- [Features](#-features)
- [Demo](#-demo)
- [Installation](#-installation)
- [Quick Start](#-quick-start)
- [Usage](#-usage)
- [Project Structure](#-project-structure)
- [Development](#-development)
- [Testing](#-testing)
- [Deployment](#-deployment)
- [Performance](#-performance)
- [Contributing](#-contributing)
- [License](#-license)

## ✨ Features

- **🎯 High Accuracy**: 93% overall accuracy on Togolese names
- **🌍 Multi-Ethnic Support**: Recognizes Ewe, Kabyé, and Arabic naming patterns
- **🔄 Continuous Learning**: Improves from user feedback
- **🚀 Production Ready**: Flask web app with admin dashboard
- **📊 Detailed Analytics**: Performance metrics and feature importance tracking
- **🔐 Secure Authentication**: Admin panel with user management
- **📱 Responsive UI**: Modern, mobile-friendly interface

## 🎥 Demo

```bash
# Try a prediction
curl -X POST http://localhost:5000/predict \
  -H "Content-Type: application/json" \
  -d '{"full_name": "AMEGANVI Koffi Ama"}'

# Response
{
  "gender": "Femme",
  "predicted_value": 0,
  "surname": "AMEGANVI",
  "first_names": ["KOFFI", "AMA"],
  "main_first_name": "AMA"
}
```

## 📦 Installation

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- Virtual environment (recommended)

### Option 1: Using Make (Recommended)

```bash
# Clone the repository
git clone https://github.com/yourusername/gender-detection.git
cd gender-detection

# Initialize project (installs dependencies, creates .env)
make init

# Train the model
make train

# Run the application
make run
```

### Option 2: Manual Installation

```bash
# Create virtual environment
python3 -m venv env
source env/bin/activate  # On Windows: env\Scripts\activate

# Install dependencies
pip install -r requirements.txt
pip install -e .

# Setup environment
cp .env.example .env

# Train the model
python -c "from gender_detection.model import train_model; train_model()"

# Run the application
cd src && python -m gender_detection.app
```

## 🚀 Quick Start

### 1. Train the Model

```bash
make train
```

This will:
- Load the dataset (`data/noms_prenoms_togo.csv`)
- Extract linguistic features
- Train an ensemble model (XGBoost + Random Forest)
- Save the model to `models/gender_classifier.joblib`
- Generate performance report

### 2. Run the Web Application

```bash
make run
```

Access the application at: **http://localhost:5000**

### 3. Access Admin Dashboard

Navigate to: **http://localhost:5000/admin**

**Default credentials:**
- Email: `ambroisekouwadan52@gmail.com`
- Password: `admin123`

⚠️ **Important**: Change these credentials in production!

## 📖 Usage

### Python API

```python
from gender_detection import GenderClassifier

# Initialize classifier
classifier = GenderClassifier()

# Make prediction
result = classifier.predict("AMEGANVI Koffi Ama")

print(result['gender'])  # "Femme"
print(result['main_first_name'])  # "AMA"
```

### REST API

#### Predict Gender

```bash
POST /predict
Content-Type: application/json

{
  "full_name": "KOKOU Mensah"
}
```

**Response:**
```json
{
  "gender": "Homme",
  "predicted_value": 1,
  "surname": "KOKOU",
  "first_names": ["MENSAH"],
  "main_first_name": "MENSAH",
  "feedback_id": 123
}
```

#### Submit Feedback

```bash
POST /feedback
Content-Type: application/json

{
  "feedback_id": 123,
  "actual_gender": "Homme",
  "predicted_value": 1
}
```

### Command Line

```bash
# Train model
make train

# Update model with feedback
make update-model

# Run tests
make test

# Format code
make format

# Run linting
make lint
```

## 📁 Project Structure

```
gender-detection/
├── src/
│   └── gender_detection/
│       ├── __init__.py          # Package initialization
│       ├── config.py            # Configuration settings
│       ├── features.py          # Feature extraction
│       ├── model.py             # ML model training/prediction
│       ├── database.py          # Database management
│       └── app.py               # Flask web application
├── tests/
│   ├── test_features.py         # Feature tests
│   ├── test_model.py            # Model tests
│   └── test_database.py         # Database tests
├── data/
│   └── noms_prenoms_togo.csv    # Training dataset
├── models/
│   └── gender_classifier.joblib # Trained model
├── templates/
│   ├── index.html               # Main page
│   ├── admin_login.html         # Admin login
│   └── admin_dashboard.html     # Dashboard
├── static/
│   └── styles.css               # Stylesheets
├── scripts/                     # Deployment scripts
├── docs/                        # Documentation
├── setup.py                     # Package setup
├── pyproject.toml               # Project metadata
├── Makefile                     # Automation commands
├── requirements.txt             # Dependencies
├── .env.example                 # Environment template
├── .gitignore                   # Git ignore rules
└── README.md                    # This file
```

## 🛠️ Development

### Setup Development Environment

```bash
make install-dev
```

This installs additional development tools:
- pytest (testing)
- black (code formatting)
- flake8 (linting)
- mypy (type checking)

### Run Tests

```bash
# Run all tests with coverage
make test

# Quick tests without coverage
make test-quick

# Run specific test file
pytest tests/test_features.py -v
```

### Code Quality

```bash
# Format code
make format

# Run linting
make lint

# Type checking
make type-check

# Run all checks
make check-all
```

### Adding New Features

1. Create feature branch: `git checkout -b feature/my-feature`
2. Write code following PEP 8
3. Add tests in `tests/`
4. Format code: `make format`
5. Run tests: `make test`
6. Submit pull request

## 🧪 Testing

The project includes comprehensive unit tests:

```bash
# Run all tests
make test

# Test specific module
pytest tests/test_model.py -v

# Test with coverage report
pytest --cov=gender_detection --cov-report=html
```

**Test Coverage:**
- Feature extraction: ✅ 95%
- Model training/prediction: ✅ 90%
- Database operations: ✅ 92%

## 🚀 Deployment

### Using Gunicorn (Production)

```bash
make run-gunicorn
```

### Using Docker

```bash
# Build image
make docker-build

# Run container
make docker-run
```

### Environment Variables

Create `.env` file (see `.env.example`):

```bash
FLASK_ENV=production
SECRET_KEY=your-secret-key-here
ADMIN_EMAIL=your-email@example.com
ADMIN_PASSWORD=secure-password
WORKERS=4
```

### Systemd Service (Linux)

Create `/etc/systemd/system/gender-detection.service`:

```ini
[Unit]
Description=Gender Detection Service
After=network.target

[Service]
Type=notify
User=www-data
WorkingDirectory=/path/to/gender-detection
Environment="PATH=/path/to/gender-detection/env/bin"
ExecStart=/path/to/gender-detection/env/bin/gunicorn \
    --workers 4 \
    --bind 0.0.0.0:8000 \
    gender_detection.app:app

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl enable gender-detection
sudo systemctl start gender-detection
```

## 📊 Performance

### Model Metrics (Test Set)

| Metric | Female | Male | Overall |
|--------|--------|------|---------|
| Precision | 92% | 95% | 93% |
| Recall | 94% | 93% | 93% |
| F1-Score | 93% | 94% | 93% |

### Feature Importance

Top 5 most important features:
1. `gender_score` (composite ethnic patterns)
2. `ends_ewe_fem` (Ewe female endings)
3. `vowel_ratio` (phonetic feature)
4. `first_name_length`
5. `exception_value` (known exceptions)

### Dataset

- **Training samples**: 7,840 Togolese names
- **Classes**: 0 (Female), 1 (Male)
- **Languages**: Ewe, Kabyé, Arabic
- **Update frequency**: Daily at 2:00 AM (with feedback)

## 🤝 Contributing

Contributions are welcome! Please follow these guidelines:

1. Fork the repository
2. Create a feature branch
3. Follow PEP 8 style guide
4. Add tests for new features
5. Ensure all tests pass
6. Submit a pull request

### Code Style

This project uses:
- **Black** for code formatting
- **Flake8** for linting
- **Type hints** where appropriate

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👨‍💻 Author

**Ambroise KOUWADAN**
- Email: ambroisekouwadan52@gmail.com
- Project: Gender Detection for Togolese Names

## 🙏 Acknowledgments

- Google Machine Learning Engineering Program
- Togolese linguistic resources
- scikit-learn and XGBoost communities

## 📞 Support

For issues, questions, or contributions:
- Open an issue on GitHub
- Email: ambroisekouwadan52@gmail.com

## 🔮 Future Improvements

- [ ] Add more West African languages (Yoruba, Hausa)
- [ ] REST API authentication (JWT)
- [ ] GraphQL API support
- [ ] Real-time model retraining
- [ ] Mobile application (React Native)
- [ ] Batch prediction API
- [ ] Model explainability dashboard

---

**Made with ❤️ for Togo**
