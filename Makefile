.PHONY: help install install-dev test test-cov lint format clean run migrate build

help:  ## Show this help message
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Available targets:'
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

install:  ## Install production dependencies
	pip install -r requirements.txt
	pnpm install

install-dev:  ## Install development dependencies
	pip install -r requirements-dev.txt
	pnpm install
	pre-commit install

test:  ## Run tests
	pytest

test-cov:  ## Run tests with coverage
	pytest --cov=app --cov-report=html --cov-report=term-missing

lint:  ## Run linting checks
	flake8 app tests
	black --check app tests
	isort --check-only app tests

format:  ## Format code with black and isort
	black app tests
	isort app tests

clean:  ## Clean up generated files
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name '*.pyc' -delete
	find . -type f -name '*.pyo' -delete
	find . -type d -name '*.egg-info' -exec rm -rf {} + 2>/dev/null || true
	rm -rf .pytest_cache .coverage htmlcov coverage.xml
	rm -rf dist build

run:  ## Run development server
	python wsgi.py

migrate:  ## Run database migrations
	flask db upgrade

build:  ## Build CSS assets
	pnpm run build

db-init:  ## Initialize database
	flask db init

db-migrate:  ## Create new migration
	flask db migrate

db-upgrade:  ## Apply migrations
	flask db upgrade

db-downgrade:  ## Rollback migration
	flask db downgrade
