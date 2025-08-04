#!/usr/bin/env python3
"""Test script for the new versions parameter functionality."""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '.'))

from pypevol import PackageAnalyzer, PyPIFetcher

def test_get_package_versions():
    """Test the new get_package_versions method."""
    print("Testing get_package_versions method...")
    
    fetcher = PyPIFetcher()
    versions = fetcher.get_package_versions("requests")
    
    print(f"Found {len(versions)} versions for requests")
    print(f"First few versions: {versions[:5]}")
    print(f"Last few versions: {versions[-5:]}")
    
    return versions

def test_analyze_with_specific_versions():
    """Test the analyze_package method with specific versions."""
    print("\nTesting analyze_package with specific versions...")
    
    # Get available versions first
    fetcher = PyPIFetcher()
    all_versions = fetcher.get_package_versions("requests")
    
    # Select a few recent versions for testing
    test_versions = all_versions[-3:]  # Last 3 versions
    print(f"Testing with versions: {test_versions}")
    
    # Create analyzer
    analyzer = PackageAnalyzer()
    
    try:
        # Test with specific versions
        result = analyzer.analyze_package(
            package_name="requests",
            versions=test_versions
        )
        
        print(f"Analysis successful!")
        print(f"Analyzed {len(result.versions)} versions")
        print(f"Found {len(result.changes)} API changes")
        
        return result
        
    except Exception as e:
        print(f"Error during analysis: {e}")
        return None

def test_parameter_validation():
    """Test parameter validation."""
    print("\nTesting parameter validation...")
    
    analyzer = PackageAnalyzer()
    
    try:
        # This should raise ValueError
        result = analyzer.analyze_package(
            package_name="requests",
            versions=["2.32.0", "2.32.1"],
            from_version="2.32.0"  # This should conflict
        )
        print("ERROR: Should have raised ValueError!")
        
    except ValueError as e:
        print(f"✅ Correctly caught validation error: {e}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

if __name__ == "__main__":
    print("🚀 Testing new versions parameter functionality")
    print("=" * 50)
    
    # Test 1: Get package versions
    versions = test_get_package_versions()
    
    if versions:
        # Test 2: Analyze with specific versions
        result = test_analyze_with_specific_versions()
        
        # Test 3: Parameter validation
        test_parameter_validation()
        
        print("\n✅ All tests completed!")
    else:
        print("❌ Failed to get package versions, skipping other tests")
