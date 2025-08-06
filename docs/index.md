# PyPevol Documentation

PyPevol analyzes PyPI package API evolution and tracks changes across versions.

## Core Functions

PyPevol can:

- Analyze API evolution across versions
- Track when APIs were introduced/removed
- Create analysis summaries

**API Elements Tracked**

- Functions and methods
- Classes and inheritance
- Properties and constants
- Type hints and decorators

**Change Detection** - Identify API modifications

- Added
- Removed
- Modified: Signature changes
- Deprecated: APIs marked for future removal


## 🚀 Quick Start

```python
from pypevol import PackageAnalyzer

analyzer = PackageAnalyzer()
result = analyzer.analyze_package('requests')

# Find when an API was introduced
lifecycle = result.get_api_lifecycle('Session')
print(f"Session class introduced in: {lifecycle['introduced_in']}")
```


## 📚 Documentation

- **[Getting Started](getting-started.md)** - Installation and basic usage
- **[Examples](examples.md)** - Practical code examples and use cases  
- **[API Reference](api-reference.md)** - Complete function and class documentation
- **[Configuration](configuration.md)** - Advanced settings and customization

## 🔗 Resources

- [GitHub Repository](https://github.com/likaixin2000/py-package-evol)
- [PyPI Package](https://pypi.org/project/pypevol)
- [Issue Tracker](https://github.com/likaixin2000/py-package-evol/issues)

MIT License - see [LICENSE](https://github.com/likaixin2000/py-package-evol/blob/main/LICENSE) for details.
