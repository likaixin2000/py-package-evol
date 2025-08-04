#!/usr/bin/env python3
"""
Comparison of sequential vs direct version analysis approaches.
"""

import sys
from pathlib import Path
import time

# Add the pypevol package to the path
sys.path.insert(0, str(Path(__file__).parent))

from pypevol.analyzer import PackageAnalyzer
from pypevol.models import ChangeType


def analyze_sequential_vs_direct():
    """Compare sequential analysis vs direct comparison."""
    
    package_name = "requests"
    version1 = "2.20.0"
    version2 = "2.25.0"
    
    print(f"Analyzing {package_name}: {version1} -> {version2}")
    print("="*60)
    
    with PackageAnalyzer() as analyzer:
        
        # Method 1: Sequential analysis (analyzes all versions in between)
        print("\n1. SEQUENTIAL ANALYSIS (analyzes all intermediate versions)")
        start_time = time.time()
        
        try:
            sequential_result = analyzer.analyze_package(
                package_name=package_name,
                from_version=version1,
                to_version=version2,
                max_versions=10  # Limit to avoid too many versions
            )
            
            sequential_time = time.time() - start_time
            print(f"   Time taken: {sequential_time:.2f} seconds")
            print(f"   Versions analyzed: {len(sequential_result.versions)}")
            print(f"   Total changes found: {len(sequential_result.changes)}")
            
            # Show version progression
            versions = [v.version for v in sequential_result.versions]
            print(f"   Version progression: {' -> '.join(versions)}")
            
        except Exception as e:
            print(f"   Error: {e}")
            sequential_result = None
        
        # Method 2: Direct comparison (only compares the two specific versions)
        print(f"\n2. DIRECT COMPARISON (only compares {version1} vs {version2})")
        start_time = time.time()
        
        try:
            direct_result = analyzer.compare_versions(
                package_name=package_name,
                version1=version1,
                version2=version2
            )
            
            direct_time = time.time() - start_time
            print(f"   Time taken: {direct_time:.2f} seconds")
            print(f"   Versions analyzed: {len(direct_result.versions)}")
            print(f"   Total changes found: {len(direct_result.changes)}")
            
        except Exception as e:
            print(f"   Error: {e}")
            direct_result = None
        
        # Method 3: Using analyze_package with compare_only flag
        print(f"\n3. ANALYZE_PACKAGE WITH COMPARE_ONLY FLAG")
        start_time = time.time()
        
        try:
            compare_only_result = analyzer.analyze_package(
                package_name=package_name,
                from_version=version1,
                to_version=version2,
                compare_only=True
            )
            
            compare_only_time = time.time() - start_time
            print(f"   Time taken: {compare_only_time:.2f} seconds")
            print(f"   Versions analyzed: {len(compare_only_result.versions)}")
            print(f"   Total changes found: {len(compare_only_result.changes)}")
            
        except Exception as e:
            print(f"   Error: {e}")
            compare_only_result = None
        
        # Compare results
        print(f"\n4. COMPARISON OF RESULTS")
        print("-"*40)
        
        if direct_result and compare_only_result:
            print(f"   Direct vs Compare-only changes match: {len(direct_result.changes) == len(compare_only_result.changes)}")
        
        if sequential_result and direct_result:
            # Sequential analysis includes changes between all intermediate versions
            # Direct comparison only shows net changes between start and end versions
            print(f"   Sequential changes: {len(sequential_result.changes)}")
            print(f"   Direct changes: {len(direct_result.changes)}")
            print(f"   Difference: {len(sequential_result.changes) - len(direct_result.changes)}")
            print("   Note: Sequential analysis shows all intermediate changes,")
            print("         while direct comparison shows only net changes.")


def demonstrate_use_cases():
    """Show different use cases for the comparison methods."""
    
    print("\n" + "="*60)
    print("USE CASE RECOMMENDATIONS")
    print("="*60)
    
    print("""
1. DIRECT COMPARISON (compare_versions or compare_only=True)
   Use when you want to:
   - See the net API differences between two specific versions
   - Quickly assess breaking changes for migration planning
   - Compare distant versions without caring about intermediate changes
   - Get faster results with minimal resource usage
   
   Example: Migrating from v1.0 to v3.0 and want to see what changed
   
2. SEQUENTIAL ANALYSIS (default analyze_package behavior)
   Use when you want to:
   - Understand the evolution path of APIs over time
   - See when specific changes were introduced across versions
   - Track the history of deprecations and removals
   - Generate comprehensive changelogs
   
   Example: Creating documentation about API evolution history
   
3. PRACTICAL SCENARIOS:
   
   Migration Planning:     Use direct comparison
   Changelog Generation:   Use sequential analysis
   Breaking Change Audit:  Use direct comparison
   Historical Research:    Use sequential analysis
   CI/CD Compatibility:    Use direct comparison
   """)


if __name__ == "__main__":
    analyze_sequential_vs_direct()
    demonstrate_use_cases()
