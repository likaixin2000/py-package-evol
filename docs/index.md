# PyPevol Documentation

Welcome to PyPevol - a comprehensive tool for analyzing PyPI package API evolution and lifecycle.

## Overview

PyPevol helps you understand how Python packages evolve over time by tracking API changes across versions. Whether you're maintaining dependencies, researching package evolution, or planning migrations, PyPevol provides the tools you need.

## 🚀 Quick Start

```bash
# Install PyPevol
pip install pypevol

# Analyze a package
pypevol analyze requests --max-versions 5
```

```python
# Python API
from pypevol import PackageAnalyzer

analyzer = PackageAnalyzer()
result = analyzer.analyze_package('requests', max_versions=5)

# Find when an API was introduced
lifecycle = result.get_api_lifecycle('Session')
print(f"Session class introduced in: {lifecycle['introduced_in']}")
```

## 📚 Documentation

### [Getting Started](getting-started.md)
Learn how to install and use PyPevol with basic examples.

**Topics covered:**
- Installation options
- Command line usage  
- Basic Python API
- Understanding results
- Configuration basics

### [Examples](examples.md)
Practical examples for common analysis scenarios.

**Topics covered:**
- Version range analysis
- API lifecycle tracking
- Change type filtering
- Advanced analysis patterns
- Error handling
- Performance tips

### [API Reference](api-reference.md)
Complete documentation of PyPevol's Python API.

**Topics covered:**
- `PackageAnalyzer` class
- `AnalysisResult` object
- Data models (`APIElement`, `VersionInfo`, `APIChange`)
- Enums and constants
- Utility functions

### [Configuration](configuration.md)
Advanced configuration options and customization.

**Topics covered:**
- Configuration files
- Environment variables
- Performance tuning
- Troubleshooting
- Batch processing

## 🎯 Use Cases

### Library Maintainers
- Track API changes in dependencies
- Identify breaking changes before upgrading
- Generate migration guides

### Researchers
- Study API evolution patterns
- Analyze deprecation timelines  
- Compare evolution strategies

### DevOps Teams
- Automate dependency analysis
- Generate compliance reports
- Monitor breaking changes

## 🔧 Key Features

| Feature | Description |
|---------|-------------|
| **Multi-version Analysis** | Compare APIs across package versions |
| **Change Detection** | Identify additions, removals, modifications |
| **Lifecycle Tracking** | See when APIs were introduced/deprecated |
| **Flexible Filtering** | Filter by API type, change type, dates |
| **Rich Output** | JSON, HTML reports, programmatic access |
| **Collision Detection** | Handle APIs with identical names |
| **Fuzzy Matching** | Find APIs even with partial names |

## 📊 Analysis Types

### API Elements Tracked
- Functions and methods
- Classes and inheritance
- Properties and descriptors  
- Constants and variables
- Type hints and annotations
- Decorators

### Change Types Detected
- **Added**: New APIs introduced
- **Removed**: APIs no longer available
- **Modified**: Signature or behavior changes
- **Deprecated**: APIs marked for removal

## 🏃‍♂️ Quick Examples

### Find Breaking Changes
```python
from pypevol.models import ChangeType

# Get potentially breaking changes
breaking = result.get_api_changes(
    change_types=[ChangeType.REMOVED, ChangeType.MODIFIED]
)

for change in breaking:
    print(f"{change.element.name} {change.change_type.value} in {change.to_version}")
```

### Track New Features  
```python
# Find new APIs in recent versions
new_apis = result.get_api_changes(change_types=[ChangeType.ADDED])
recent_additions = [c for c in new_apis if c.to_version >= '2.25.0']

print(f"New APIs since 2.25.0: {len(recent_additions)}")
```

### Generate Summary Report
```python
summary = result.generate_summary()
print(f"""
Package: {summary['package_name']}
Versions: {summary['total_versions']} 
Changes: {summary['total_changes']}
Added: {summary['change_types']['added']}
Removed: {summary['change_types']['removed']}
""")
```

## 🔗 Links

- [GitHub Repository](https://github.com/likaixin2000/py-package-evol)
- [PyPI Package](https://pypi.org/project/pypevol)
- [Issue Tracker](https://github.com/likaixin2000/py-package-evol/issues)

## 📄 License

MIT License - see the [LICENSE file](https://github.com/likaixin2000/py-package-evol/blob/main/LICENSE) for details.
