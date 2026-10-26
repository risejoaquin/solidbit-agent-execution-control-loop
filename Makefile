.PHONY: help install dev test test-cov lint format build-frontend run-ui clean

help:
	@echo "SACL (SolidBit Agent Execution Control Loop) Command Palette"
	@echo "------------------------------------------------------------"
	@echo "install         : Install package in editable mode"
	@echo "dev             : Install development dependencies"
	@echo "test            : Run backend Pytest suite"
	@echo "test-cov        : Run Pytest suite with code coverage"
	@echo "lint            : Run static code analysis (ruff)"
	@echo "build-frontend  : Build production web console bundle (Vite)"
	@echo "run-ui          : Launch SACL Executive Web Console (port 8765)"
	@echo "clean           : Remove temporary caches, build artifacts"

install:
	pip install -e .

dev:
	pip install -e ".[dev,ui]"

test:
	pytest tests/ui/ -v

test-cov:
	pytest tests/ui/ -v --cov=src --cov-report=term-missing

lint:
	ruff check src/ tests/

build-frontend:
	cd apps/web && npm ci && npm run build

run-ui:
	python -m sacl.cli ui --port 8765

clean:
	rm -rf .pytest_cache build dist *.egg-info coverage.xml
	find . -type d -name "__pycache__" -exec rm -rf {} +
