#!/usr/bin/env python3
"""
Examples demonstrating the new analyze_versions functionality.
"""

import sys
from pathlib import Path

# Add the pypevol package to the path
sys.path.insert(0, str(Path(__file__).parent))

from pypevol.analyzer import PackageAnalyzer
from pypevol.models import ChangeType


def example_analyze_specific_versions():
    """Demonstrate analyzing specific versions of a package."""
    
    print("=== Example 1: Analyzing Specific Versions ===")
    print("Analyzing specific versions of 'click': 7.0, 7.1, 8.0.0")
    
    with PackageAnalyzer() as analyzer:
        try:
            # Analyze specific versions with changes calculated
            result = analyzer.analyze_versions(
                package_name="click",
                versions=["7.0", "7.1", "8.0.0"],
                calculate_changes=True
            )
            
            print(f"\nPackage: {result.package_name}")
            print(f"Analysis type: {result.metadata['analysis_type']}")
            print(f"Versions requested: 3")
            print(f"Versions successfully analyzed: {result.metadata['successful_versions']}")
            print(f"Failed versions: {result.metadata['failed_versions']}")
            print(f"Total API changes found: {len(result.changes)}")
            
            # Show versions analyzed
            analyzed_versions = [v.version for v in result.versions]
            print(f"Analyzed versions: {analyzed_versions}")
            
            # Show API elements count per version
            for version in analyzed_versions:
                count = len(result.api_elements.get(version, []))
                print(f"  {version}: {count} API elements")
            
            # Group changes by type
            changes_by_type = {}
            for change in result.changes:
                change_type = change.change_type
                if change_type not in changes_by_type:
                    changes_by_type[change_type] = []
                changes_by_type[change_type].append(change)
            
            # Display summary of changes
            for change_type, changes in changes_by_type.items():
                print(f"\n{change_type.value.upper()} ({len(changes)} changes):")
                for change in changes[:3]:  # Show first 3 changes
                    print(f"  - {change.element.full_name}")
                    if hasattr(change, 'from_version') and change.from_version:
                        print(f"    {change.from_version} -> {change.to_version}")
                if len(changes) > 3:
                    print(f"  ... and {len(changes) - 3} more")
                    
        except Exception as e:
            print(f"Error during analysis: {e}")


def example_analyze_without_changes():
    """Demonstrate analyzing versions without calculating changes."""
    
    print("\n\n=== Example 2: Analyzing Versions Without Changes ===")
    print("Analyzing versions without calculating changes (faster)")
    
    with PackageAnalyzer() as analyzer:
        try:
            # Analyze specific versions without changes
            result = analyzer.analyze_versions(
                package_name="requests",
                versions=["2.25.0", "2.26.0", "2.27.0", "2.28.0"],
                calculate_changes=False
            )
            
            print(f"\nPackage: {result.package_name}")
            print(f"Changes calculated: {result.metadata.get('calculate_changes', True)}")
            print(f"Versions analyzed: {len(result.versions)}")
            print(f"Changes found: {len(result.changes)} (expected 0)")
            
            # Show API snapshot for each version
            for version_info in result.versions:
                version = version_info.version
                api_count = len(result.api_elements.get(version, []))
                print(f"  {version}: {api_count} APIs")
                
                # Show a few API examples
                apis = result.api_elements.get(version, [])
                if apis:
                    print("    Sample APIs:")
                    for api in apis[:3]:
                        print(f"      - {api.type.value}: {api.full_name}")
                    if len(apis) > 3:
                        print(f"      ... and {len(apis) - 3} more")
                    
        except Exception as e:
            print(f"Error during analysis: {e}")


def example_compare_all_methods():
    """Compare all analysis methods with the same versions."""
    
    print("\n\n=== Example 3: Comparing All Analysis Methods ===")
    print("Using the same versions with different methods")
    
    package_name = "click"
    versions = ["7.0", "8.0.0"]
    
    with PackageAnalyzer() as analyzer:
        
        print(f"\nAnalyzing {package_name} versions: {versions}")
        print("-" * 50)
        
        # Method 1: analyze_versions
        print("1. Using analyze_versions():")
        try:
            result1 = analyzer.analyze_versions(
                package_name=package_name,
                versions=versions,
                calculate_changes=True
            )
            print(f"   Versions analyzed: {len(result1.versions)}")
            print(f"   Changes found: {len(result1.changes)}")
            print(f"   Analysis type: {result1.metadata['analysis_type']}")
        except Exception as e:
            print(f"   Error: {e}")
        
        # Method 2: compare_versions
        print("\n2. Using compare_versions():")
        try:
            result2 = analyzer.compare_versions(
                package_name=package_name,
                version1=versions[0],
                version2=versions[1]
            )
            print(f"   Versions analyzed: {len(result2.versions)}")
            print(f"   Changes found: {len(result2.changes)}")
            print(f"   Analysis type: {result2.metadata.get('analysis_type', result2.metadata.get('comparison_type'))}")
        except Exception as e:
            print(f"   Error: {e}")
        
        # Method 3: analyze_package with compare_only
        print("\n3. Using analyze_package(compare_only=True):")
        try:
            result3 = analyzer.analyze_package(
                package_name=package_name,
                from_version=versions[0],
                to_version=versions[1],
                compare_only=True
            )
            print(f"   Versions analyzed: {len(result3.versions)}")
            print(f"   Changes found: {len(result3.changes)}")
            print(f"   Analysis type: {result3.metadata.get('analysis_type', result3.metadata.get('comparison_type'))}")
        except Exception as e:
            print(f"   Error: {e}")
        
        # Compare results
        if 'result1' in locals() and 'result2' in locals() and 'result3' in locals():
            print(f"\n4. Results comparison:")
            print(f"   analyze_versions vs compare_versions: {len(result1.changes)} vs {len(result2.changes)} changes")
            print(f"   compare_versions vs analyze_package: {len(result2.changes)} vs {len(result3.changes)} changes")
            print(f"   All methods consistent: {len(result1.changes) == len(result2.changes) == len(result3.changes)}")


def example_non_sequential_versions():
    """Demonstrate analyzing non-sequential versions."""
    
    print("\n\n=== Example 4: Non-Sequential Version Analysis ===")
    print("Analyzing non-sequential versions to see evolution patterns")
    
    with PackageAnalyzer() as analyzer:
        try:
            # Analyze major versions with gaps
            result = analyzer.analyze_versions(
                package_name="numpy",
                versions=["1.18.0", "1.20.0", "1.22.0", "1.24.0"],
                calculate_changes=True
            )
            
            print(f"\nPackage: {result.package_name}")
            print(f"Versions analyzed: {[v.version for v in result.versions]}")
            print(f"Total changes: {len(result.changes)}")
            
            # Show evolution between major versions
            print("\nMajor version evolution:")
            for i, version_info in enumerate(result.versions[:-1]):
                next_version = result.versions[i+1]
                version_changes = [c for c in result.changes 
                                 if c.from_version == version_info.version and c.to_version == next_version.version]
                print(f"  {version_info.version} -> {next_version.version}: {len(version_changes)} changes")
                
                # Show breakdown by change type
                added = sum(1 for c in version_changes if c.change_type == ChangeType.ADDED)
                removed = sum(1 for c in version_changes if c.change_type == ChangeType.REMOVED)
                modified = sum(1 for c in version_changes if c.change_type == ChangeType.MODIFIED)
                deprecated = sum(1 for c in version_changes if c.change_type == ChangeType.DEPRECATED)
                
                print(f"    Added: {added}, Removed: {removed}, Modified: {modified}, Deprecated: {deprecated}")
                    
        except Exception as e:
            print(f"Error during analysis: {e}")


if __name__ == "__main__":
    example_analyze_specific_versions()
    example_analyze_without_changes()
    example_compare_all_methods()
    example_non_sequential_versions()
