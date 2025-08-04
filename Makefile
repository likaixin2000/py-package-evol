# Makefile for PyPevol Plus

.PHONY: help install install-dev test lint format clean build upload docs

help:  ## Show this help message
	@echo "PyPevol Plus - Makefile Help"
	@echo "============================"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\\033[36m%-20s\\033[0m %s\\n", $$1, $$2}'

install:  ## Install the package
	pip install -e .

install-dev:  ## Install development dependencies
	pip install -e ".[dev]"
	pip install -r requirements-dev.txt

test:  ## Run tests
	pytest tests/ -v --cov=pypevol --cov-report=html --cov-report=term

lint:  ## Run linting checks
	flake8 pypevol tests examples
	mypy pypevol

format:  ## Format code with black
	black pypevol tests examples

clean:  ## Clean build artifacts
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf .pytest_cache/
	rm -rf htmlcov/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

build:  ## Build distribution packages
	python setup.py sdist bdist_wheel

upload:  ## Upload to PyPI (requires twine)
	twine upload dist/*

docs:  ## Generate documentation
	@echo "Documentation generation not implemented yet"

example-single:  ## Run single package analysis example
	python examples/analyze_single_package.py

example-compare:  ## Run package comparison example
	python examples/compare_packages.py

example-track:  ## Run API tracking example
	python examples/track_api_lifecycle.py

demo:  ## Run a quick demo
	python -m pypevol analyze requests --max-versions 5 --output demo_output.json

check-config:  ## Check configuration file
	python -c "from pypevol.utils import load_config; print('Config loaded successfully:', bool(load_config()))"
