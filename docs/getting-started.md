# Getting Started

Get up and running with PyPevol quickly.

## Installation

**From PyPI (Recommended)**
```bash
pip install pypevol
```

**Development Installation**
```bash
git clone https://github.com/your-username/py-package-evol.git
cd py-package-evol
pip install -e ".[dev]"
```

## Basic Usage

### First Analysis
```python
from pypevol import PackageAnalyzer

# Create analyzer and run analysis
analyzer = PackageAnalyzer()
result = analyzer.analyze_package('requests')

# Print summary
summary = result.generate_summary()
print(f"Package: {summary['package_name']}")
print(f"Versions analyzed: {summary['total_versions']}")
print(f"Total API changes: {summary['total_changes']}")
```

### Understanding Results

The `AnalysisResult` object contains:
- **`package_name`**: Name of the analyzed package
- **`versions`**: List of analyzed versions with metadata
- **`api_elements`**: APIs found in each version
- **`changes`**: List of all API changes between versions

### Track API Lifecycle
```python
# Find when an API was introduced
lifecycle = result.get_api_lifecycle('Session')

print(f"Introduced in: {lifecycle['introduced_in']}")
print(f"Present in versions: {lifecycle['versions_present']}")
if lifecycle['removed_in']:
    print(f"Removed in: {lifecycle['removed_in']}")
```

### Filter Changes
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


## Controling Your Analysis
### API Filtering Options
```python
analyzer = PackageAnalyzer(
    include_private=True,  # Include private APIs (starting with _)
    include_deprecated=True,  # Exclude deprecated APIs
    include_yanked=False. # Include yanked versions
)
```

### Version Selection Strategies
```python
# Analyze all versions (use with caution for large packages)
result = analyzer.analyze_package('requests')

# Limit number of versions (sample evenly throughout the package hisstory)
result = analyzer.analyze_package('requests', max_versions=10)

# Specific version range
result = analyzer.analyze_package(
    'requests',
    from_version='2.20.0',
    to_version='2.28.0'
)

# Date-based filtering
from datetime import datetime, timezone
result = analyzer.analyze_package(
    'requests',
    from_date=datetime(2022, 1, 1, tzinfo=timezone.utc),
    to_date=datetime(2023, 1, 1, tzinfo=timezone.utc)
)

# Specific versions only
result = analyzer.analyze_package(
    'requests',
    versions=['2.25.0', '2.26.0', '2.27.0']
)
```


### Result Filtering
```python
from pypevol.models import ChangeType, APIType

# Filter by change type
breaking_changes = result.get_api_changes(
    change_types=[ChangeType.REMOVED, ChangeType.MODIFIED]
)

# Filter by API type
function_changes = result.get_api_changes(
    api_types=[APIType.FUNCTION]
)

# Combined filtering
new_classes = result.get_api_changes(
    change_types=[ChangeType.ADDED],
    api_types=[APIType.CLASS]
)
```