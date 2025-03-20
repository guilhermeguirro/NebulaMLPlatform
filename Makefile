.PHONY: setup build run test lint format clean help

# Default target
.DEFAULT_GOAL := help

# Variables
PYTHON = python3
PIP = $(PYTHON) -m pip
PYTEST = $(PYTHON) -m pytest
BLACK = $(PYTHON) -m black
ISORT = $(PYTHON) -m isort
FLAKE8 = $(PYTHON) -m flake8
MYPY = $(PYTHON) -m mypy
DOCKER_COMPOSE = docker-compose
DOCKER = docker

# Help target
help:
	@echo "Available commands:"
	@echo "  setup       - Install dependencies and set up development environment"
	@echo "  build       - Build Docker containers"
	@echo "  run         - Run the application locally"
	@echo "  test        - Run tests"
	@echo "  lint        - Run linting tools"
	@echo "  format      - Format code with Black and isort"
	@echo "  clean       - Remove build artifacts and caches"
	@echo "  docker-up   - Start all services with Docker Compose"
	@echo "  docker-down - Stop all services"
	@echo "  docker-logs - View logs from all services"

# Setup development environment
setup:
	$(PIP) install -e ".[dev]"
	pre-commit install

# Build Docker containers
build:
	$(DOCKER_COMPOSE) build

# Run locally
run:
	$(PYTHON) -m app

# Run tests
test:
	$(PYTEST) --cov=SecureFinStack --cov-report=term-missing

# Run linting
lint:
	$(FLAKE8) SecureFinStack
	$(MYPY) SecureFinStack
	$(ISORT) --check SecureFinStack
	$(BLACK) --check SecureFinStack

# Format code
format:
	$(ISORT) SecureFinStack
	$(BLACK) SecureFinStack

# Clean up
clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info
	rm -rf .pytest_cache
	rm -rf .coverage
	rm -rf htmlcov/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type d -name "*.pyc" -delete

# Docker commands
docker-up:
	$(DOCKER_COMPOSE) up -d

docker-down:
	$(DOCKER_COMPOSE) down

docker-logs:
	$(DOCKER_COMPOSE) logs -f 