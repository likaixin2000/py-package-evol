#!/usr/bin/env python3
"""
Example script demonstrating how to compare two arbitrary versions of a package.
"""

import sys
from pathlib import Path

# Add the pypevol package to the path
sys.path.insert(0, str(Path(__file__).parent))

from pypevol.analyzer import PackageAnalyzer
from pypevol.models import ChangeType


def main():
    """Demonstrate comparing two arbitrary versions."""
    
    # Example 1: Direct version comparison
    print("=== Example 1: Direct Version Comparison ===")
    print("Comparing requests v2.25.1 vs v2.28.0")
    
    with PackageAnalyzer() as analyzer:
        try:
            # Compare two specific versions directly
            result = analyzer.compare_versions(
                package_name="requests",
                version1="2.25.1",  # older version
                version2="2.28.0"   # newer version
            )
            
            print(f"\nPackage: {result.package_name}")
            print(f"Versions compared: {result.versions[0].version} -> {result.versions[1].version}")
            print(f"Total API changes found: {len(result.changes)}")
            
            # Group changes by type
            changes_by_type = {}
            for change in result.changes:
                change_type = change.change_type
                if change_type not in changes_by_type:
                    changes_by_type[change_type] = []
                changes_by_type[change_type].append(change)
            
            # Display summary
            for change_type, changes in changes_by_type.items():
                print(f"\n{change_type.value.upper()} ({len(changes)} changes):")
                for change in changes[:5]:  # Show first 5 changes
                    print(f"  - {change.element.full_name}")
                    if change.old_signature and change.new_signature:
                        print(f"    Old: {change.old_signature}")
                        print(f"    New: {change.new_signature}")
                if len(changes) > 5:
                    print(f"  ... and {len(changes) - 5} more")
                    
        except Exception as e:
            print(f"Error during comparison: {e}")
    
    # Example 2: Using analyze_package with compare_only flag
    print("\n\n=== Example 2: Using analyze_package with compare_only flag ===")
    print("Comparing numpy v1.20.0 vs v1.21.0")
    
    with PackageAnalyzer() as analyzer:
        try:
            # Use the main analyze_package method with compare_only=True
            result = analyzer.analyze_package(
                package_name="numpy",
                from_version="1.20.0",
                to_version="1.21.0",
                compare_only=True
            )
            
            print(f"\nPackage: {result.package_name}")
            print(f"Comparison type: {result.metadata.get('comparison_type', 'sequential')}")
            print(f"Total API changes found: {len(result.changes)}")
            
            # Show breakdown by change type
            added = sum(1 for c in result.changes if c.change_type == ChangeType.ADDED)
            removed = sum(1 for c in result.changes if c.change_type == ChangeType.REMOVED)
            modified = sum(1 for c in result.changes if c.change_type == ChangeType.MODIFIED)
            deprecated = sum(1 for c in result.changes if c.change_type == ChangeType.DEPRECATED)
            
            print(f"  - Added: {added}")
            print(f"  - Removed: {removed}")
            print(f"  - Modified: {modified}")
            print(f"  - Deprecated: {deprecated}")
            
        except Exception as e:
            print(f"Error during comparison: {e}")


if __name__ == "__main__":
    main()
