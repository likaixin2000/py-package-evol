# Examples

This page provides practical examples of using PyPevol for different analysis scenarios.

## Basic Package Analysis

### Analyze Recent Versions

```python
from pypevol import PackageAnalyzer

analyzer = PackageAnalyzer()

# Analyze the last 10 versions of requests
result = analyzer.analyze_package('requests', max_versions=10)

print(f"Analyzed {len(result.versions)} versions")
print(f"Found {len(result.changes)} API changes")
```

### Version Range Analysis

```python
# Analyze specific version range
result = analyzer.analyze_package(
    'flask',
    from_version='1.0.0',
    to_version='2.0.0'
)

# Show major changes
for change in result.changes:
    if change.change_type.value in ['added', 'removed']:
        print(f"{change.change_type.value.title()}: {change.element.name}")
```

## API Evolution Tracking

### Track Function Evolution

```python
# Find when a specific function was introduced
lifecycle = result.get_api_lifecycle('make_response')

if lifecycle['introduced_in']:
    print(f"make_response was introduced in version {lifecycle['introduced_in']}")
else:
    print("Function not found or collision detected")
    
# Handle name collisions
if lifecycle['collision_detected']:
    print("Multiple APIs found with this name:")
    for api in lifecycle['available_apis']:
        print(f"  - {api['full_name']} ({api['type']})")
```

### Monitor Deprecations

```python
from pypevol.models import ChangeType

# Find all deprecated APIs
deprecated_changes = result.get_api_changes(
    change_types=[ChangeType.DEPRECATED]
)

print(f"Found {len(deprecated_changes)} deprecations:")
for change in deprecated_changes:
    print(f"  {change.element.name} in version {change.to_version}")
```

## Advanced Analysis

### Compare Two Specific Versions

```python
# Analyze only two specific versions for comparison
result = analyzer.analyze_package(
    'django',
    versions=['3.2.0', '4.0.0']
)

# Find breaking changes
breaking_changes = [
    change for change in result.changes 
    if change.change_type.value in ['removed', 'modified']
]

print(f"Potential breaking changes: {len(breaking_changes)}")
```

### Date-Based Analysis

```python
from datetime import datetime

# Analyze changes in the last year
result = analyzer.analyze_package(
    'numpy',
    from_date=datetime(2023, 1, 1),
    max_versions=20
)

# Group changes by month
from collections import defaultdict
changes_by_month = defaultdict(list)

for change in result.changes:
    # Find the version info for this change
    version_info = next(
        (v for v in result.versions if v.version == change.to_version), 
        None
    )
    if version_info and version_info.release_date:
        month_key = version_info.release_date.strftime('%Y-%m')
        changes_by_month[month_key].append(change)

for month, changes in sorted(changes_by_month.items()):
    print(f"{month}: {len(changes)} changes")
```

## Analysis by API Type

### Focus on Classes

```python
from pypevol.models import APIType, ChangeType

# Find all new classes
new_classes = result.get_api_changes(
    change_types=[ChangeType.ADDED],
    api_types=[APIType.CLASS]
)

print("New classes added:")
for change in new_classes:
    print(f"  {change.element.name} in version {change.to_version}")
```

### Method Analysis

```python
# Find modified methods
modified_methods = result.get_api_changes(
    change_types=[ChangeType.MODIFIED],
    api_types=[APIType.METHOD]
)

for change in modified_methods:
    print(f"Method {change.element.name} changed in {change.to_version}")
    if change.old_signature and change.new_signature:
        print(f"  From: {change.old_signature}")
        print(f"  To:   {change.new_signature}")
```

## Working with Results

### Export Analysis Results

```python
# Save detailed analysis to JSON
with open('requests_analysis.json', 'w') as f:
    f.write(result.to_json(indent=2))

# Create summary report
summary = result.generate_summary()
print(f"""
Package Analysis Summary
========================
Package: {summary['package_name']}
Versions: {summary['total_versions']}
Total APIs: {summary['unique_apis']}
Changes: {summary['total_changes']}

Change Types:
  Added: {summary['change_types'].get('added', 0)}
  Removed: {summary['change_types'].get('removed', 0)}
  Modified: {summary['change_types'].get('modified', 0)}
  Deprecated: {summary['change_types'].get('deprecated', 0)}
""")
```

### Custom Analysis

```python
# Find APIs that were added and then removed
added_apis = {change.element.full_name for change in result.changes 
              if change.change_type == ChangeType.ADDED}
removed_apis = {change.element.full_name for change in result.changes 
                if change.change_type == ChangeType.REMOVED}

short_lived_apis = added_apis & removed_apis
print(f"APIs that were added and later removed: {len(short_lived_apis)}")
for api_name in short_lived_apis:
    print(f"  {api_name}")
```

## Error Handling

### Robust Analysis

```python
def analyze_package_safely(package_name, **kwargs):
    """Safely analyze a package with error handling."""
    try:
        analyzer = PackageAnalyzer()
        result = analyzer.analyze_package(package_name, **kwargs)
        
        if not result.versions:
            print(f"No versions found for {package_name}")
            return None
            
        return result
        
    except Exception as e:
        print(f"Failed to analyze {package_name}: {e}")
        return None

# Use it
result = analyze_package_safely('some-package', max_versions=5)
if result:
    print(f"Successfully analyzed {result.package_name}")
```

### Handle Missing APIs

```python
# Safely get API lifecycle
def get_api_info(result, api_name):
    lifecycle = result.get_api_lifecycle(api_name)
    
    if lifecycle['collision_detected']:
        return f"Multiple APIs found with name '{api_name}'"
    elif lifecycle['matched_api']:
        return f"Found as {lifecycle['matched_api']}"
    elif lifecycle['introduced_in']:
        return f"Introduced in {lifecycle['introduced_in']}"
    else:
        return f"API '{api_name}' not found"

print(get_api_info(result, 'Session'))
```

## Performance Tips

### Efficient Analysis

```python
# For large packages, limit versions
result = analyzer.analyze_package(
    'tensorflow',
    max_versions=5,  # Only analyze recent versions
    prefer_wheels=True  # Wheels are faster to process
)

# Use context manager for automatic cleanup
with PackageAnalyzer() as analyzer:
    result = analyzer.analyze_package('pandas')
    # Cleanup happens automatically
```

### Batch Analysis

```python
packages = ['requests', 'flask', 'django']
results = {}

with PackageAnalyzer() as analyzer:
    for package in packages:
        try:
            results[package] = analyzer.analyze_package(
                package, 
                max_versions=3
            )
            print(f"✓ Analyzed {package}")
        except Exception as e:
            print(f"✗ Failed to analyze {package}: {e}")

# Compare results
for package, result in results.items():
    if result:
        print(f"{package}: {len(result.changes)} changes")
```
