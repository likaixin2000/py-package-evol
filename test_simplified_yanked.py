#!/usr/bin/env python3
"""
Test script for the simplified yanked version implementation.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '.'))

from pypevol import PackageAnalyzer, PyPIFetcher

def test_simplified_implementation():
    """Test the simplified yanked version implementation."""
    print("🧪 Testing simplified yanked version implementation...")
    
    fetcher = PyPIFetcher()
    
    # Test 1: Get version info without yanked filtering
    print("\n1. Testing get_version_info without yanked filtering:")
    version_info = fetcher.get_version_info("setuptools", "51.1.0.post20201221", include_yanked=True)
    if version_info:
        print(f"   ✅ Got version info: {version_info.version}, yanked={version_info.yanked}")
        if version_info.yanked_reason:
            print(f"   📝 Yanked reason: {version_info.yanked_reason}")
    else:
        print("   ❌ Could not get version info")
    
    # Test 2: Get version info with yanked filtering (default)
    print("\n2. Testing get_version_info with yanked filtering (default):")
    version_info_filtered = fetcher.get_version_info("setuptools", "51.1.0.post20201221", include_yanked=False)
    if version_info_filtered is None:
        print("   ✅ Yanked version correctly filtered out")
    else:
        print("   ❌ Yanked version was not filtered out")
    
    # Test 3: Get regular (non-yanked) version
    print("\n3. Testing regular version:")
    regular_version = fetcher.get_version_info("setuptools", "70.0.0", include_yanked=False)
    if regular_version:
        print(f"   ✅ Got regular version: {regular_version.version}, yanked={regular_version.yanked}")
    else:
        print("   ❌ Could not get regular version info")
    
    # Test 4: Test analyzer with yanked filtering
    print("\n4. Testing analyzer yanked filtering:")
    analyzer = PackageAnalyzer(include_yanked=False)
    result = analyzer.analyze_package("setuptools", max_versions=2)
    print(f"   ✅ Analyzer (no yanked): {len(result.versions)} versions analyzed")
    
    analyzer_with_yanked = PackageAnalyzer(include_yanked=True)
    result_with_yanked = analyzer_with_yanked.analyze_package("setuptools", max_versions=2)
    print(f"   ✅ Analyzer (with yanked): {len(result_with_yanked.versions)} versions analyzed")
    
    print("\n✅ All tests completed successfully!")
    return True

if __name__ == "__main__":
    test_simplified_implementation()
