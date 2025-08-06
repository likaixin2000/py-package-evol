# Configuration

Advanced configuration options and customization for PyPevol.

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

### Cache Settings
```bash
# Set custom cache directory
export PYPEVOL_CACHE_DIR="/path/to/cache"

# Disable caching entirely
export PYPEVOL_CACHE_DISABLED=true

# Set cache size limit (in bytes)
export PYPEVOL_CACHE_MAX_SIZE=1073741824  # 1GB
```

### Network Settings
```bash
# Set request timeout
export PYPEVOL_TIMEOUT=60

# Set custom user agent
export PYPEVOL_USER_AGENT="MyApp/1.0 pypevol/1.0.0"

# Set PyPI index URL
export PYPEVOL_INDEX_URL="https://pypi.org/simple"
```

### Logging Settings
```bash
# Set log level
export PYPEVOL_LOG_LEVEL=DEBUG  # DEBUG, INFO, WARNING, ERROR

# Set log format
export PYPEVOL_LOG_FORMAT="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
```
