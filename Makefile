.PHONY: help install install-dev clean test lint format run train update-model docker-build docker-run

# Variables
PYTHON := python3
PIP := $(PYTHON) -m pip
PYTEST := $(PYTHON) -m pytest
BLACK := $(PYTHON) -m black
FLAKE8 := $(PYTHON) -m flake8
MYPY := $(PYTHON) -m mypy

help:  ## Show this help message
	@echo "Gender Detection - Makefile Commands"
	@echo "====================================="
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install:  ## Install production dependencies
	$(PIP) install --upgrade pip
	$(PIP) install -r requirements.txt
	$(PIP) install -e .

install-dev:  ## Install development dependencies
	$(PIP) install --upgrade pip
	$(PIP) install -r requirements.txt
	$(PIP) install -e ".[dev]"
	@echo "✓ Development environment ready!"

clean:  ## Clean up generated files
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	rm -rf build/ dist/ .pytest_cache/ .coverage htmlcov/ .mypy_cache/
	@echo "✓ Cleaned up!"

test:  ## Run tests with coverage
	$(PYTEST) tests/ -v --cov=src/gender_detection --cov-report=html --cov-report=term
	@echo "✓ Tests completed! Open htmlcov/index.html to view coverage report"

test-quick:  ## Run tests without coverage
	$(PYTEST) tests/ -v
	@echo "✓ Quick tests completed!"

lint:  ## Run linting checks
	$(FLAKE8) src/gender_detection tests --max-line-length=88 --extend-ignore=E203,W503
	@echo "✓ Linting passed!"

format:  ## Format code with black
	$(BLACK) src/gender_detection tests
	@echo "✓ Code formatted!"

type-check:  ## Run type checking with mypy
	$(MYPY) src/gender_detection
	@echo "✓ Type checking passed!"

check-all: format lint type-check test  ## Run all quality checks

run:  ## Run Flask development server
	cd src && PYTHONPATH=. $(PYTHON) -m gender_detection.app

run-gunicorn:  ## Run with Gunicorn (production)
	cd src && gunicorn --workers 4 --bind 0.0.0.0:8000 --timeout 120 gender_detection.app:app

train:  ## Train the model
	cd src && PYTHONPATH=. $(PYTHON) -c "from gender_detection.model import train_model; train_model()"

update-model:  ## Update model with feedback
	cd src && PYTHONPATH=. $(PYTHON) -c "from gender_detection.model import update_model_with_feedback; update_model_with_feedback()"

move-data:  ## Move data files to data directory
	@mkdir -p data models
	@[ -f noms_prenoms_togo.csv ] && mv noms_prenoms_togo.csv data/ || true
	@[ -f gender_classifier.joblib ] && mv gender_classifier.joblib models/ || true
	@echo "✓ Data files moved!"

setup-env:  ## Create .env file from example
	@if [ ! -f .env ]; then \
		cp .env.example .env; \
		echo "✓ .env file created! Please update with your settings."; \
	else \
		echo "⚠ .env already exists"; \
	fi

docker-build:  ## Build Docker image
	docker build -t gender-detection:latest .

docker-run:  ## Run Docker container
	docker run -p 8000:8000 -v $(PWD)/data:/app/data -v $(PWD)/models:/app/models gender-detection:latest

init: install-dev setup-env  ## Initialize project (first time setup)
	@echo "✓ Project initialized! Run 'make train' to train the model, then 'make run' to start the server."

dev: install-dev  ## Setup development environment
	@echo "✓ Development environment ready!"
	@echo "  Run 'make train' to train the model"
	@echo "  Run 'make run' to start development server"
	@echo "  Run 'make test' to run tests"
