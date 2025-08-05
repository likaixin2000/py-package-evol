# Contributing to PyPevol

Thank you for your interest in contributing to PyPevol! This document provides guidelines and information for contributors.

## Table of Contents

- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Making Changes](#making-changes)
- [Testing](#testing)
- [Documentation](#documentation)
- [Submitting Changes](#submitting-changes)
- [Code Style](#code-style)
- [Release Process](#release-process)

## Getting Started

### Prerequisites

- Python 3.8 or higher
- Git
- A GitHub account

### Fork and Clone

1. Fork the repository on GitHub
2. Clone your fork locally:
   ```bash
   git clone https://github.com/YOUR-USERNAME/py-package-evol.git
   cd py-package-evol
   ```

## Development Setup

1. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. Install development dependencies:
   ```bash
   make install-dev
   # or
   pip install -e ".[dev]"
   ```

3. Install pre-commit hooks (optional but recommended):
   ```bash
   pre-commit install
   ```

4. Verify the setup:
   ```bash
   make ci-check
   ```

## Making Changes

### Branch Strategy

- Create feature branches from `main`
- Use descriptive branch names: `feature/add-api-filtering`, `fix/version-parsing`, `docs/update-examples`

### Development Workflow

1. Create a new branch:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. Make your changes
3. Run tests and linting:
   ```bash
   make ci-check
   ```

4. Commit your changes:
   ```bash
   git add .
   git commit -m "Add feature: description of your changes"
   ```

5. Push to your fork:
   ```bash
   git push origin feature/your-feature-name
   ```

## Testing

### Running Tests

```bash
# Run all tests
make test

# Run specific test file
pytest tests/test_analyzer.py -v

# Run with coverage
pytest tests/ --cov=pypevol --cov-report=html
```

### Writing Tests

- Place tests in the `tests/` directory
- Follow the naming convention: `test_*.py`
- Use descriptive test names
- Include both unit tests and integration tests
- Mock external dependencies (PyPI API calls, file downloads)

Example test structure:
```python
def test_analyze_package_basic():
    """Test basic package analysis functionality."""
    analyzer = PackageAnalyzer()
    # Mock external dependencies
    with patch.object(analyzer.fetcher, 'get_version_range'):
        result = analyzer.analyze_package('test-package')
        assert result is not None
```

## Documentation

### Building Documentation

```bash
# Serve documentation locally
make docs-serve

# Build documentation
make docs-build
```

### Writing Documentation

- Documentation is written in Markdown and located in `docs/`
- Use clear, concise language
- Include code examples
- Update relevant documentation when making changes

## Submitting Changes

### Pull Request Process

1. Ensure your code passes all CI checks
2. Update documentation if needed
3. Create a pull request with:
   - Clear description of changes
   - Reference to related issues
   - Screenshots if UI changes

### Pull Request Template

Use the provided PR template and fill out all relevant sections.

## Code Style

### Formatting

We use automated code formatting:

- **Black** for Python code formatting
- **isort** for import sorting
- **flake8** for linting
- **mypy** for type checking

### Running Code Style Checks

```bash
# Format code
make format

# Check formatting without changes
make check-format

# Run linting
make check-lint
```

### Code Guidelines

- Follow PEP 8 style guide
- Use type hints where appropriate
- Write docstrings for public functions and classes
- Keep functions focused and small
- Use meaningful variable and function names

### Example Code Style

```python
from typing import List, Optional
from pathlib import Path

def analyze_package(
    package_name: str,
    max_versions: Optional[int] = None
) -> AnalysisResult:
    """Analyze the API evolution of a package.
    
    Args:
        package_name: Name of the package to analyze
        max_versions: Maximum number of versions to analyze
        
    Returns:
        AnalysisResult containing the evolution data
    """
    # Implementation here
    pass
```

## Project Structure

```
py-package-evol/
├── pypevol/           # Main package code
│   ├── __init__.py
│   ├── analyzer.py    # Main analyzer class
│   ├── models.py      # Data models
│   ├── fetcher.py     # PyPI data fetching
│   ├── parser.py      # Source code parsing
│   └── cli.py         # Command line interface
├── tests/             # Test files
├── docs/              # Documentation
├── examples/          # Usage examples
└── .github/           # GitHub workflows and templates
```

## Types of Contributions

### Bug Reports

- Use the bug report template
- Include minimal reproduction case
- Provide environment details

### Feature Requests

- Use the feature request template
- Explain the use case
- Consider backward compatibility

### Code Contributions

- Bug fixes
- New features
- Performance improvements
- Documentation improvements

### Documentation Contributions

- Fix typos or improve clarity
- Add examples
- Improve API documentation
- Write tutorials

## Release Process

Releases are automated through GitHub Actions:

1. Create a new tag: `git tag v0.2.0`
2. Push the tag: `git push origin v0.2.0`
3. GitHub Actions will:
   - Run tests
   - Build the package
   - Publish to PyPI
   - Create a GitHub release
   - Deploy updated documentation

## Getting Help

- Open an issue for questions
- Check existing issues and documentation
- Join discussions in pull requests

## Code of Conduct

- Be respectful and inclusive
- Focus on constructive feedback
- Help others learn and grow
- Follow the project's code of conduct

## Recognition

Contributors will be recognized in:
- Release notes
- README contributors section
- Package metadata

Thank you for contributing to PyPevol!
