# Makefile for Belvo Streamlit App Docker Management

# Variables
IMAGE_NAME = belvo-streamlit
CONTAINER_NAME = belvo-streamlit-container
PORT = 8501
OPENAI_API_KEY ?= $(shell echo $$OPENAI_API_KEY)

# Default target
.PHONY: help
help:
	@echo "Available commands:"
	@echo "  build       - Build the Docker image"
	@echo "  run         - Run the container in foreground"
	@echo "  run-bg      - Run the container in background"
	@echo "  stop        - Stop the running container"
	@echo "  logs        - Show container logs"
	@echo "  shell       - Open shell in running container"
	@echo "  clean       - Stop and remove container"
	@echo "  clean-all   - Stop container, remove container and image"
	@echo "  rebuild     - Clean and rebuild everything"
	@echo "  status      - Show container status"
	@echo ""
	@echo "Testing commands:"
	@echo "  test        - Run all tests"
	@echo "  test-unit   - Run unit tests only"
	@echo "  test-extractor - Run InvoicesExtractor tests"
	@echo "  test-anomaly   - Run AnomalyDetector tests"
	@echo "  test-coverage  - Run tests with coverage report"
	@echo ""
	@echo "Usage with OPENAI_API_KEY:"
	@echo "  make start OPENAI_API_KEY=your_key_here"
	@echo "  make run-bg OPENAI_API_KEY=your_key_here"
	@echo "  export OPENAI_API_KEY=your_key && make start"

# Build the Docker image
.PHONY: build
build:
	@echo "Building Docker image: $(IMAGE_NAME)"
	docker build -t $(IMAGE_NAME) .

# Run container in foreground
.PHONY: run
run:
	@echo "Running container: $(CONTAINER_NAME)"
	docker run --rm --name $(CONTAINER_NAME) -p $(PORT):$(PORT) -e OPENAI_API_KEY="$(OPENAI_API_KEY)" $(IMAGE_NAME)

# Run container in background
.PHONY: run-bg
run-bg:
	@echo "Running container in background: $(CONTAINER_NAME)"
	docker run -d --name $(CONTAINER_NAME) -p $(PORT):$(PORT) -e OPENAI_API_KEY="$(OPENAI_API_KEY)" $(IMAGE_NAME)
	@echo "Container started. Access the app at http://localhost:$(PORT)"

# Run with environment file (if exists)
.PHONY: run-env
run-env:
	@echo "Running container with environment file"
	docker run --rm --name $(CONTAINER_NAME) -p $(PORT):$(PORT) --env-file .env $(IMAGE_NAME)

# Run with data volume mounted
.PHONY: run-dev
run-dev:
	@echo "Running container with data volume mounted"
	docker run --rm --name $(CONTAINER_NAME) -p $(PORT):$(PORT) -e OPENAI_API_KEY="$(OPENAI_API_KEY)" -v $(PWD)/data:/app/data $(IMAGE_NAME)

# Stop the running container
.PHONY: stop
stop:
	@echo "Stopping container: $(CONTAINER_NAME)"
	-docker stop $(CONTAINER_NAME)

# Show container logs
.PHONY: logs
logs:
	@echo "Showing logs for container: $(CONTAINER_NAME)"
	docker logs -f $(CONTAINER_NAME)

# Open shell in running container
.PHONY: shell
shell:
	@echo "Opening shell in container: $(CONTAINER_NAME)"
	docker exec -it $(CONTAINER_NAME) /bin/bash

# Clean up container
.PHONY: clean
clean: stop
	@echo "Removing container: $(CONTAINER_NAME)"
	-docker rm $(CONTAINER_NAME)

# Clean up everything (container and image)
.PHONY: clean-all
clean-all: clean
	@echo "Removing image: $(IMAGE_NAME)"
	-docker rmi $(IMAGE_NAME)

# Rebuild everything from scratch
.PHONY: rebuild
rebuild: clean-all build

# Show container status
.PHONY: status
status:
	@echo "Container status:"
	-docker ps -a --filter name=$(CONTAINER_NAME)
	@echo ""
	@echo "Image status:"
	-docker images $(IMAGE_NAME)

# Quick start (build and run)
.PHONY: start
start: build run-bg

# Development workflow (build and run with volumes)
.PHONY: dev
dev: build run-dev

# Testing commands
.PHONY: test
test:
	@echo "Running all tests..."
	pytest tests/ -v


.PHONY: test-extractor
test-extractor:
	@echo "Running InvoicesExtractor tests..."
	pytest tests/test_invoices_extractor.py -v

.PHONY: test-anomaly
test-anomaly:
	@echo "Running AnomalyDetector tests..."
	pytest tests/test_anomaly_detector.py -v

.PHONY: test-coverage
test-coverage:
	@echo "Running tests with coverage..."
	pytest tests/ --cov=app --cov-report=html --cov-report=term

# Code quality commands
.PHONY: lint
lint:
	@echo "Running linting checks..."
	flake8 app/ tests/

.PHONY: format
format:
	@echo "Formatting code..."
	black app/ tests/
	isort app/ tests/

.PHONY: format-check
format-check:
	@echo "Checking code formatting..."
	black --check app/ tests/
	isort --check-only app/ tests/

.PHONY: pre-commit-install
pre-commit-install:
	@echo "Installing pre-commit hooks..."
	pre-commit install

.PHONY: pre-commit-run
pre-commit-run:
	@echo "Running pre-commit hooks on all files..."
	pre-commit run --all-files

.PHONY: quality-check
quality-check: format-check lint test
	@echo "All quality checks passed!"
