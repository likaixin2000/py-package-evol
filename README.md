# PyPevol

A comprehensive tool for analyzing PyPI package API evolution and lifecycle. This package fetches information from PyPI, analyzes wheels and sources, and provides detailed reports about when APIs were introduced and removed across different versions.

## Features

- **PyPI Integration**: Fetch package metadata and releases from PyPI
- **Wheel Analysis**: Download and analyze wheel files to extract API information
- **Source Code Analysis**: Parse Python source code to identify APIs
- **Evolution Tracking**: Track API changes across package versions
- **Visualization**: Generate interactive reports and visualizations
- **CLI Interface**: Easy-to-use command-line interface
- **Web Dashboard**: Interactive web interface for exploring results

## Installation

```bash
pip install pypevol
```

For development:
```bash
pip install -e ".[dev]"
```

## Quick Start

### Command Line Usage

```bash
# Analyze a single package
pypevol analyze requests

# Analyze with specific version range
pypevol analyze requests --from-version 2.20.0 --to-version 2.28.0

# Generate HTML report
pypevol analyze requests --output report.html --format html

# Analyze multiple packages
pypevol analyze requests flask django --output results/

# Analyze specific versions
pypevol analyze requests --versions="2.32.0,2.32.1,2.32.2"
```

### Python API Usage

```python
from pypevol import PackageAnalyzer, PyPIFetcher

# Create analyzer
analyzer = PackageAnalyzer()

# Option 1: Analyze all versions (limited)
result = analyzer.analyze_package('requests', max_versions=10)

# Option 2: Analyze version range
result = analyzer.analyze_package('requests', 
                                 from_version='2.30.0', 
                                 to_version='2.32.0')

# Option 3: Analyze specific versions (NEW!)
result = analyzer.analyze_package('requests', 
                                 versions=['2.32.0', '2.32.1', '2.32.2'])

# Get available versions first
fetcher = PyPIFetcher()
available_versions = fetcher.get_package_versions('requests')
print(f"Available versions: {available_versions[-5:]}")  # Last 5 versions

# Get API changes
api_changes = result.get_api_changes()

# Generate report
report = result.generate_report(format='html')
```

## API Evolution Analysis

PyPevol tracks the following API elements:

- **Functions**: Top-level and module functions
- **Classes**: Class definitions and inheritance
- **Methods**: Instance and class methods
- **Properties**: Class properties and descriptors
- **Constants**: Module-level constants
- **Type Hints**: Type annotations and their evolution

## Output Formats

- **JSON**: Machine-readable format for further processing
- **HTML**: Interactive web report with visualizations
- **CSV**: Tabular format for spreadsheet analysis
- **Markdown**: Human-readable documentation format

## Configuration

Create a `.pypevol.yaml` configuration file:

```yaml
# Package analysis settings
analysis:
  include_private: false
  include_deprecated: true
  max_versions: 50

# Output settings
output:
  default_format: html
  include_source_links: true
  show_usage_examples: true

# Caching settings
cache:
  enabled: true
  directory: ~/.pypevol/cache
  max_size: 1GB
```

## Examples

See the `examples/` directory for detailed usage examples and tutorials.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Run the test suite: `pytest`
6. Submit a pull request

## License

MIT License - see LICENSE file for details.
