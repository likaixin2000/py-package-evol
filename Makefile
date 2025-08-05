# Makefile for PyPevol

.PHONY: help install install-dev test lint format clean build upload docs docs-serve docs-build check-format check-lint ci-check

help:  ## Show this help message
	@echo "PyPevol - Makefile Help"
	@echo "======================="
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

format:  ## Format code with black and isort
	black pypevol tests examples
	isort pypevol tests examples

check-format:  ## Check code formatting without making changes
	black --check pypevol tests examples
	isort --check-only pypevol tests examples

check-lint:  ## Check linting without fixing
	flake8 pypevol tests examples
	mypy pypevol

ci-check:  ## Run all CI checks locally
	@echo "Running CI checks..."
	$(MAKE) check-format
	$(MAKE) check-lint
	$(MAKE) test
	$(MAKE) docs-build

clean:  ## Clean build artifacts
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf .pytest_cache/
	rm -rf htmlcov/
	rm -rf site/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

build:  ## Build distribution packages
	python -m build

upload:  ## Upload to PyPI (requires twine)
	twine upload dist/*

docs:  ## Alias for docs-serve
	$(MAKE) docs-serve

docs-serve:  ## Serve documentation locally
	mkdocs serve

docs-build:  ## Build documentation
	mkdocs build --strict

docs-deploy:  ## Deploy documentation to GitHub Pages
	mkdocs gh-deploy

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
