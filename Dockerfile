FROM python:3.13-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements-prod.txt .
RUN pip install --no-cache-dir -r requirements-prod.txt

# Copy application code
COPY src/ ./src/
COPY templates/ ./templates/
COPY static/ ./static/
COPY setup.py .
COPY pyproject.toml .
COPY README.md .

# Install the package
RUN pip install -e .

# Create necessary directories for runtime-generated content
RUN mkdir -p data models logs

# Copy only the dataset (CSV file)
COPY data/noms_prenoms_togo.csv ./data/

# Note: The following are generated at runtime and should NOT be copied:
# - models/ directory (trained model)
# - *.db.sqlite3 files (databases)
# - training_report.txt (generated report)
# - feature_importance.csv (generated metrics)
# - logs/ directory (application logs)

# Expose port
EXPOSE 8000

# Set environment variables
ENV PYTHONPATH=/app/src
ENV FLASK_APP=gender_detection.app

# Run with gunicorn
# Note: Extended timeout (300s) to allow model training on first deployment
CMD ["gunicorn", "--workers", "2", "--bind", "0.0.0.0:8000", "--timeout", "300", "--chdir", "src", "gender_detection.app:app"]
