#!/usr/bin/env python3
"""
Simple test to verify the compare_versions functionality works.
"""

import sys
from pathlib import Path

# Add the pypevol package to the path
sys.path.insert(0, str(Path(__file__).parent))

from pypevol.analyzer import PackageAnalyzer


def test_compare_versions():
    """Test the new compare_versions functionality."""
    
    print("Testing compare_versions functionality...")
    
    # Test with a simple, lightweight package
    package_name = "click"  # Popular CLI library with stable API
    version1 = "7.0"
    version2 = "8.0.0"
    
    try:
        with PackageAnalyzer() as analyzer:
            print(f"Comparing {package_name} versions {version1} and {version2}...")
            
            result = analyzer.compare_versions(
                package_name=package_name,
                version1=version1,
                version2=version2
            )
            
            print(f"✓ Successfully compared versions")
            print(f"  Package: {result.package_name}")
            print(f"  Versions: {len(result.versions)}")
            print(f"  API elements in {version1}: {len(result.api_elements.get(version1, []))}")
            print(f"  API elements in {version2}: {len(result.api_elements.get(version2, []))}")
            print(f"  Changes found: {len(result.changes)}")
            print(f"  Metadata: {result.metadata}")
            
            # Test the compare_only flag as well
            print(f"\nTesting analyze_package with compare_only=True...")
            
            result2 = analyzer.analyze_package(
                package_name=package_name,
                from_version=version1,
                to_version=version2,
                compare_only=True
            )
            
            print(f"✓ Successfully used compare_only flag")
            print(f"  Changes found: {len(result2.changes)}")
            print(f"  Results match: {len(result.changes) == len(result2.changes)}")
            
        print("\n✓ All tests passed!")
        return True
        
    except Exception as e:
        print(f"✗ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_compare_versions()
    sys.exit(0 if success else 1)
