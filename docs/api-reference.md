# API Reference

Complete reference for PyPevol's Python API.

## Core Classes

### PackageAnalyzer

The main class for analyzing PyPI packages.

```python
class PackageAnalyzer:
    def __init__(self, 
                 cache_dir: Optional[Path] = None,
                 include_private: bool = False,
                 include_deprecated: bool = True,
                 prefer_wheels: bool = True,
                 include_yanked: bool = False)
```

**Parameters:**
- `cache_dir`: Directory to cache downloaded files
- `include_private`: Include private APIs (starting with `_`)
- `include_deprecated`: Include deprecated APIs  
- `prefer_wheels`: Prefer wheel files over source distributions
- `include_yanked`: Include yanked versions in analysis

#### Methods

##### `analyze_package()`

Analyze the API evolution of a package.

```python
def analyze_package(self, 
                   package_name: str,
                   from_version: Optional[str] = None,
                   to_version: Optional[str] = None,
                   max_versions: Optional[int] = None,
                   versions: Optional[List[str]] = None,
                   from_date: Optional[datetime] = None,
                   to_date: Optional[datetime] = None) -> AnalysisResult
```

**Parameters:**
- `package_name`: Name of the package to analyze
- `from_version`: Starting version (inclusive)
- `to_version`: Ending version (inclusive)  
- `max_versions`: Maximum number of versions to analyze
- `versions`: Specific list of versions to analyze
- `from_date`: Filter versions released after this date
- `to_date`: Filter versions released before this date

**Returns:** `AnalysisResult` object containing the analysis data

##### `get_package_versions()`

Get all available version information for a package.

```python
def get_package_versions(self, 
                        package_name: str,
                        include_yanked: bool = False) -> List[VersionInfo]
```

## Data Models

### AnalysisResult

Contains the results of package API evolution analysis.

#### Properties

- `package_name`: Name of the analyzed package
- `versions`: List of `VersionInfo` objects
- `api_elements`: Dictionary mapping version to list of `APIElement`
- `changes`: List of `APIChange` objects
- `analysis_date`: When the analysis was performed
- `metadata`: Additional analysis metadata

#### Methods

##### `get_api_changes()`

Get filtered API changes.

```python
def get_api_changes(self, 
                   change_types: Optional[List[ChangeType]] = None,
                   api_types: Optional[List[APIType]] = None) -> List[APIChange]
```

##### `get_api_lifecycle()`

Get lifecycle information for a specific API.

```python
def get_api_lifecycle(self, api_name: str) -> Dict[str, Any]
```

**Returns dictionary with:**
- `name`: API name searched for
- `introduced_in`: Version where API was first introduced
- `removed_in`: Version where API was removed (if applicable)
- `versions_present`: List of versions containing the API
- `matched_api`: Full name if fuzzy matching was used
- `collision_detected`: True if multiple APIs found with same name
- `available_apis`: List of colliding APIs if collision detected

##### `generate_summary()`

Generate a summary of the analysis results.

```python
def generate_summary(self) -> Dict[str, Any]
```

##### `to_dict()` / `to_json()`

Export analysis results.

```python
def to_dict(self) -> Dict[str, Any]
def to_json(self, indent: int = 2) -> str
```

### APIElement

Represents an API element (function, class, method, etc.).

#### Properties

- `name`: Name of the API element
- `type`: `APIType` enum value
- `module_path`: Full module path
- `signature`: Function/method signature (if available)
- `docstring`: Documentation string
- `line_number`: Line number in source file
- `is_private`: True if API is private (starts with `_`)
- `is_deprecated`: True if API is marked as deprecated
- `type_hints`: Dictionary of type annotations
- `decorators`: List of decorator names
- `metadata`: Additional metadata

#### Methods

##### `full_name`

Get the fully qualified name.

```python
@property
def full_name(self) -> str
```

##### `get_signature()`

Get a unique signature for comparison.

```python
def get_signature(self) -> str
```

### VersionInfo

Information about a specific package version.

#### Properties

- `version`: Version string
- `release_date`: Release date as datetime
- `python_requires`: Python version requirement
- `dependencies`: List of dependencies
- `wheel_url`: URL to wheel file
- `source_url`: URL to source distribution
- `yanked`: True if version is yanked
- `yanked_reason`: Reason for yanking (if applicable)
- `metadata`: Additional version metadata

### APIChange

Represents a change to an API element between versions.

#### Properties

- `element`: The `APIElement` that changed
- `change_type`: `ChangeType` enum value
- `from_version`: Previous version
- `to_version`: Version where change occurred
- `old_signature`: Previous signature (for modifications)
- `new_signature`: New signature (for modifications)
- `description`: Human-readable description
- `is_backwards_compatible`: Whether change is backwards compatible

## Enums

### APIType

Types of API elements that can be tracked.

```python
class APIType(Enum):
    FUNCTION = "function"
    CLASS = "class"
    METHOD = "method"
    PROPERTY = "property"
    CONSTANT = "constant"
    MODULE = "module"
```

### ChangeType

Types of changes that can occur to API elements.

```python
class ChangeType(Enum):
    ADDED = "added"
    REMOVED = "removed"
    MODIFIED = "modified"
    DEPRECATED = "deprecated"
```

## Utility Functions

### Context Manager Usage

PackageAnalyzer supports context manager protocol for automatic cleanup:

```python
with PackageAnalyzer() as analyzer:
    result = analyzer.analyze_package('requests')
    # Temporary files cleaned up automatically
```

### Error Handling

Common exceptions that may be raised:

- `ValueError`: Invalid parameter combinations
- `requests.exceptions.RequestException`: Network/PyPI access errors
- `FileNotFoundError`: Package files not found
- `ImportError`: Failed to import parsing dependencies

### Performance Considerations

- **Wheel vs Source**: Wheels are faster to process than source distributions
- **Version Limits**: Use `max_versions` to limit analysis scope
- **Caching**: Downloaded files are cached to speed up repeated analysis
- **Cleanup**: Use context managers or call cleanup manually to free disk space

## Configuration

### Environment Variables

- `PYPEVOL_CACHE_DIR`: Default cache directory
- `PYPEVOL_USER_AGENT`: Custom user agent for PyPI requests

### Settings

```python
# Customize analysis behavior
analyzer = PackageAnalyzer(
    include_private=True,       # Include _private APIs
    include_deprecated=False,   # Exclude deprecated APIs
    prefer_wheels=False,        # Prefer source over wheels
    include_yanked=True         # Include yanked versions
)
```
