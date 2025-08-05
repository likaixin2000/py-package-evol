# Getting Started

This guide will help you get up and running with PyPevol quickly.

## Installation

### From PyPI (Recommended)
```bash
pip install pypevol
```

### Development Installation
```bash
git clone https://github.com/your-username/py-package-evol.git
cd py-package-evol
pip install -e ".[dev]"
```

## Basic Usage

### Command Line Interface

The simplest way to analyze a package:

```bash
# Analyze the requests package
pypevol analyze requests

# Analyze specific version range
pypevol analyze requests --from-version 2.20.0 --to-version 2.28.0

# Limit number of versions
pypevol analyze requests --max-versions 5

# Generate HTML report
pypevol analyze requests --output report.html --format html
```

### Python API

For programmatic access and more control:

```python
from pypevol import PackageAnalyzer

# Create analyzer instance
analyzer = PackageAnalyzer()

# Basic analysis
result = analyzer.analyze_package('requests')

# Print summary
summary = result.generate_summary()
print(f"Package: {summary['package_name']}")
print(f"Versions analyzed: {summary['total_versions']}")
print(f"Total API changes: {summary['total_changes']}")
```

## Understanding Results

### AnalysisResult Object

The main result object contains:

- **`package_name`**: Name of the analyzed package
- **`versions`**: List of analyzed versions with metadata
- **`api_elements`**: APIs found in each version
- **`changes`**: List of all API changes between versions

### API Lifecycle Tracking

Find out when an API was introduced:

```python
# Get lifecycle information for a specific API
lifecycle = result.get_api_lifecycle('Session')

print(f"Introduced in: {lifecycle['introduced_in']}")
print(f"Present in versions: {lifecycle['versions_present']}")
if lifecycle['removed_in']:
    print(f"Removed in: {lifecycle['removed_in']}")
```

### Filtering Changes

Filter changes by type or API type:

```python
from pypevol.models import ChangeType, APIType

# Get only added functions
added_functions = result.get_api_changes(
    change_types=[ChangeType.ADDED],
    api_types=[APIType.FUNCTION]
)

# Get all removed APIs
removed_apis = result.get_api_changes(
    change_types=[ChangeType.REMOVED]
)
```

## Configuration Options

### Analyzer Settings

```python
analyzer = PackageAnalyzer(
    include_private=False,      # Include private APIs (starting with _)
    include_deprecated=True,    # Include deprecated APIs
    prefer_wheels=True,         # Prefer wheel files over source
    include_yanked=False        # Include yanked versions
)
```

### Analysis Options

```python
# Analyze specific versions
result = analyzer.analyze_package(
    'requests', 
    versions=['2.25.0', '2.26.0', '2.27.0']
)

# Date-based filtering
from datetime import datetime
result = analyzer.analyze_package(
    'requests',
    from_date=datetime(2021, 1, 1),
    to_date=datetime(2022, 1, 1)
)
```

## Output Formats

### JSON Export

```python
# Export to JSON string
json_data = result.to_json(indent=2)

# Save to file
with open('analysis.json', 'w') as f:
    f.write(json_data)
```

### Dictionary Format

```python
# Convert to dictionary for custom processing
data = result.to_dict()

# Access specific data
for version_data in data['versions']:
    print(f"Version {version_data['version']}: {len(version_data)} APIs")
```

## Next Steps

- Explore [Examples](examples.md) for common analysis patterns
- Check the [API Reference](api-reference.md) for detailed method documentation
- Learn about [Configuration](configuration.md) options for advanced usage
