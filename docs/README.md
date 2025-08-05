# PyPevol Documentation

Welcome to PyPevol - a comprehensive tool for analyzing PyPI package API evolution and lifecycle.

## Table of Contents

- [Getting Started](getting-started.md)
- [API Reference](api-reference.md)
- [Examples](examples.md)
- [Configuration](configuration.md)

## What is PyPevol?

PyPevol is a Python package that helps you understand how PyPI packages evolve over time by:

- **Tracking API Changes**: Monitor when functions, classes, and methods are added, removed, or modified
- **Version Analysis**: Compare different versions of a package to understand evolution patterns  
- **Interactive Reports**: Generate detailed HTML reports with visualizations
- **Lifecycle Information**: Discover when specific APIs were introduced or deprecated

## Quick Example

```python
from pypevol import PackageAnalyzer

# Analyze the evolution of the requests package
analyzer = PackageAnalyzer()
result = analyzer.analyze_package('requests', max_versions=10)

# Get API lifecycle information
lifecycle = result.get_api_lifecycle('Session')
print(f"Session class introduced in: {lifecycle['introduced_in']}")

# Generate an HTML report
report = result.to_json()
```

## Key Features

### 🔍 **Deep Package Analysis**
- Analyzes both wheel files and source distributions
- Extracts functions, classes, methods, properties, and constants
- Tracks type hints and decorators

### 📊 **Evolution Tracking** 
- Identifies API additions, removals, and modifications
- Detects signature changes and deprecations
- Provides version-by-version change history

### 📈 **Rich Reporting**
- JSON output for programmatic access
- HTML reports with interactive visualizations
- CSV exports for spreadsheet analysis

### 🎯 **Flexible Analysis**
- Analyze specific version ranges
- Filter by date ranges
- Include or exclude private/deprecated APIs
- Support for yanked versions

## Use Cases

- **Library Migration**: Understand breaking changes when upgrading dependencies
- **API Research**: Study how popular packages evolve their APIs
- **Deprecation Planning**: Track when APIs were deprecated across versions
- **Version Compatibility**: Identify safe version ranges for your dependencies

## Installation

```bash
pip install pypevol
```

For development:
```bash
pip install -e ".[dev]"
```

## Next Steps

- Check out the [Getting Started Guide](getting-started.md) for installation and basic usage
- Browse [Examples](examples.md) for common use cases
- See the [API Reference](api-reference.md) for detailed documentation
