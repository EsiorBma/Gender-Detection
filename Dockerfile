FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY src/ ./src/
COPY templates/ ./templates/
COPY static/ ./static/
COPY setup.py .
COPY pyproject.toml .

# Install the package
RUN pip install -e .

# Create necessary directories
RUN mkdir -p data models logs

# Copy data files
COPY data/ ./data/
COPY models/ ./models/

# Expose port
EXPOSE 8000

# Set environment variables
ENV PYTHONPATH=/app/src
ENV FLASK_APP=gender_detection.app

# Run with gunicorn
CMD ["gunicorn", "--workers", "4", "--bind", "0.0.0.0:8000", "--timeout", "120", "--chdir", "src", "gender_detection.app:app"]
