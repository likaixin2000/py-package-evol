# Configuration

This page covers advanced configuration options for PyPevol.

## Configuration File

Create a `.pypevol.yaml` configuration file in your project root or home directory:

```yaml
# Package analysis settings
analysis:
  include_private: false
  include_deprecated: true
  max_versions: 50
  prefer_wheels: true
  include_yanked: false

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
  
# Network settings
network:
  timeout: 30
  retries: 3
  user_agent: "pypevol/1.0.0"
```

## Environment Variables

PyPevol respects several environment variables:

### Cache Configuration

```bash
# Set custom cache directory
export PYPEVOL_CACHE_DIR="/path/to/cache"

# Disable caching entirely
export PYPEVOL_CACHE_DISABLED=true

# Set cache size limit (in bytes)
export PYPEVOL_CACHE_MAX_SIZE=1073741824  # 1GB
```

### Network Configuration

```bash
# Set request timeout
export PYPEVOL_TIMEOUT=60

# Set custom user agent
export PYPEVOL_USER_AGENT="MyApp/1.0 pypevol/1.0.0"

# Set PyPI index URL
export PYPEVOL_INDEX_URL="https://pypi.org/simple"
```

### Logging Configuration

```bash
# Set log level
export PYPEVOL_LOG_LEVEL=DEBUG  # DEBUG, INFO, WARNING, ERROR

# Set log format
export PYPEVOL_LOG_FORMAT="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
```

## Programmatic Configuration

### Analyzer Settings

```python
from pypevol import PackageAnalyzer
from pathlib import Path

# Configure analyzer instance
analyzer = PackageAnalyzer(
    cache_dir=Path("./my-cache"),
    include_private=True,
    include_deprecated=False,
    prefer_wheels=True,
    include_yanked=False
)
```

### Logging Configuration

```python
import logging

# Configure logging for pypevol
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('pypevol')
logger.setLevel(logging.DEBUG)

# Add custom handler
handler = logging.FileHandler('pypevol.log')
handler.setFormatter(logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
))
logger.addHandler(handler)
```

## Analysis Options

### Version Selection Strategies

```python
# Analyze all versions (use with caution for large packages)
result = analyzer.analyze_package('requests')

# Limit to recent versions
result = analyzer.analyze_package('requests', max_versions=10)

# Specific version range
result = analyzer.analyze_package(
    'requests',
    from_version='2.20.0',
    to_version='2.28.0'
)

# Date-based filtering
from datetime import datetime
result = analyzer.analyze_package(
    'requests',
    from_date=datetime(2022, 1, 1),
    to_date=datetime(2023, 1, 1)
)

# Specific versions only
result = analyzer.analyze_package(
    'requests',
    versions=['2.25.0', '2.26.0', '2.27.0']
)
```

### API Filtering Options

```python
# Include private APIs (starting with _)
analyzer = PackageAnalyzer(include_private=True)

# Exclude deprecated APIs
analyzer = PackageAnalyzer(include_deprecated=False)

# Include yanked versions
analyzer = PackageAnalyzer(include_yanked=True)
```

## Output Configuration

### Export Formats

```python
# JSON with custom formatting
json_output = result.to_json(indent=4)

# Dictionary for custom processing
data = result.to_dict()

# Custom summary
summary = result.generate_summary()
```

### Filtering Results

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

## Performance Tuning

### Cache Management

```python
# Use custom cache directory
analyzer = PackageAnalyzer(cache_dir=Path("/fast-ssd/cache"))

# Manual cache cleanup
analyzer.fetcher.cleanup_temp_files()
```

### Memory Optimization

```python
# Process packages one at a time to reduce memory usage
packages = ['requests', 'flask', 'django']

for package_name in packages:
    with PackageAnalyzer() as analyzer:
        result = analyzer.analyze_package(package_name, max_versions=5)
        
        # Process result immediately
        summary = result.generate_summary()
        print(f"{package_name}: {summary['total_changes']} changes")
        
        # Save to file
        with open(f"{package_name}_analysis.json", "w") as f:
            f.write(result.to_json())
    
    # Analyzer is cleaned up automatically here
```

### Network Optimization

```python
# Prefer wheels for faster downloading
analyzer = PackageAnalyzer(prefer_wheels=True)

# Reduce network timeout for faster failures
import os
os.environ['PYPEVOL_TIMEOUT'] = '10'
```

## Troubleshooting

### Common Issues

#### Package Not Found
```python
try:
    result = analyzer.analyze_package('nonexistent-package')
except Exception as e:
    print(f"Package not found: {e}")
```

#### Network Issues
```python
# Increase timeout for slow connections
os.environ['PYPEVOL_TIMEOUT'] = '120'

# Enable debug logging to see network requests
logging.getLogger('pypevol').setLevel(logging.DEBUG)
```

#### Memory Issues
```python
# Limit analysis scope
result = analyzer.analyze_package(
    'large-package',
    max_versions=3,  # Reduce version count
    include_private=False  # Reduce API count
)
```

### Debug Mode

Enable verbose logging to troubleshoot issues:

```python
import logging

# Enable debug logging for all pypevol components
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Run analysis with debug output
result = analyzer.analyze_package('requests', max_versions=2)
```

### Cache Issues

```python
# Clear cache if corrupted
import shutil
from pathlib import Path

cache_dir = Path.home() / '.pypevol' / 'cache'
if cache_dir.exists():
    shutil.rmtree(cache_dir)
    print("Cache cleared")
```

## Advanced Usage

### Custom PyPI Index

```python
# Use private PyPI index
os.environ['PYPEVOL_INDEX_URL'] = 'https://my-private-pypi.com/simple'

# Analyze package from private index
result = analyzer.analyze_package('my-internal-package')
```

### Batch Processing

```python
# Analyze multiple packages efficiently
def batch_analyze(packages, max_versions=5):
    results = {}
    
    with PackageAnalyzer(
        include_private=False,
        prefer_wheels=True
    ) as analyzer:
        
        for package in packages:
            try:
                print(f"Analyzing {package}...")
                result = analyzer.analyze_package(
                    package, 
                    max_versions=max_versions
                )
                results[package] = result
                print(f"✓ {package}: {len(result.changes)} changes")
                
            except Exception as e:
                print(f"✗ {package}: {e}")
                results[package] = None
    
    return results

# Use it
popular_packages = ['requests', 'numpy', 'pandas', 'flask']
results = batch_analyze(popular_packages)
```
