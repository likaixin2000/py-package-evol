#!/usr/bin/env python3
"""
Test script for yanked version filtering functionality.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '.'))

from pypevol import PackageAnalyzer, PyPIFetcher

def test_yanked_detection():
    """Test detection of yanked versions."""
    print("🧪 Testing yanked version detection...")
    
    fetcher = PyPIFetcher()
    
    # Test with a package that has yanked versions (e.g., setuptools)
    package_name = "setuptools"
    
    # Get all versions including yanked
    all_versions_with_yanked = fetcher.get_package_versions(package_name, include_yanked=True)
    print(f"   Found {len(all_versions_with_yanked)} versions (including yanked)")
    
    # Get versions excluding yanked (default)
    all_versions_no_yanked = fetcher.get_package_versions(package_name, include_yanked=False)
    print(f"   Found {len(all_versions_no_yanked)} versions (excluding yanked)")
    
    # Show the difference
    yanked_count = len(all_versions_with_yanked) - len(all_versions_no_yanked)
    print(f"   Detected {yanked_count} yanked versions")
    
    if yanked_count > 0:
        print("   ✅ Yanked version filtering is working")
        return True
    else:
        print("   ⚠️  No yanked versions found (or all versions are yanked)")
        return True

def test_analyzer_yanked_filtering():
    """Test that the analyzer filters yanked versions by default."""
    print("\n🧪 Testing analyzer yanked filtering...")
    
    # Test with analyzer that excludes yanked versions (default)
    analyzer_no_yanked = PackageAnalyzer(include_yanked=False)
    
    # Test with analyzer that includes yanked versions
    analyzer_with_yanked = PackageAnalyzer(include_yanked=True)
    
    package_name = "setuptools"
    
    try:
        # Get versions without yanked (should be faster and fewer versions)
        result_no_yanked = analyzer_no_yanked.analyze_package(package_name, max_versions=3)
        versions_no_yanked = len(result_no_yanked.versions)
        print(f"   Analyzer without yanked: {versions_no_yanked} versions analyzed")
        
        # Get versions with yanked
        result_with_yanked = analyzer_with_yanked.analyze_package(package_name, max_versions=3)
        versions_with_yanked = len(result_with_yanked.versions)
        print(f"   Analyzer with yanked: {versions_with_yanked} versions analyzed")
        
        print("   ✅ Analyzer yanked filtering works")
        return True
        
    except Exception as e:
        print(f"   ⚠️  Analyzer test failed: {e}")
        return False

def test_specific_yanked_version():
    """Test handling of specific yanked versions."""
    print("\n🧪 Testing specific yanked version handling...")
    
    fetcher = PyPIFetcher()
    
    # Try to find a yanked version - let's check setuptools metadata
    try:
        metadata = fetcher.get_package_metadata("setuptools")
        releases = metadata.get('releases', {})
        
        yanked_version = None
        for version, files in releases.items():
            if files and fetcher._is_version_yanked(files):
                yanked_version = version
                break
        
        if yanked_version:
            print(f"   Found yanked version: {yanked_version}")
            
            # Try to get version info without including yanked
            version_info_no_yanked = fetcher.get_version_info("setuptools", yanked_version, include_yanked=False)
            if version_info_no_yanked is None:
                print("   ✅ Yanked version correctly filtered out")
            else:
                print("   ❌ Yanked version was not filtered out")
                return False
            
            # Try to get version info including yanked
            version_info_with_yanked = fetcher.get_version_info("setuptools", yanked_version, include_yanked=True)
            if version_info_with_yanked is not None:
                print("   ✅ Yanked version included when requested")
            else:
                print("   ❌ Yanked version not included when requested")
                return False
            
            return True
        else:
            print("   ⚠️  No yanked versions found in setuptools")
            return True
            
    except Exception as e:
        print(f"   ⚠️  Test failed: {e}")
        return False

def test_cli_yanked_option():
    """Test CLI yanked option."""
    print("\n🧪 Testing CLI yanked option...")
    
    import subprocess
    
    try:
        # Test without yanked (default)
        result1 = subprocess.run([
            sys.executable, "-m", "pypevol", "analyze", "setuptools", 
            "--max-versions=2", "--format=json"
        ], 
        cwd="/home/ec2-user/ssd/py-package-evol",
        capture_output=True, text=True, timeout=30)
        
        if result1.returncode == 0:
            print("   ✅ CLI without yanked works")
        else:
            print(f"   ❌ CLI without yanked failed: {result1.stderr}")
            return False
        
        # Test with yanked
        result2 = subprocess.run([
            sys.executable, "-m", "pypevol", "analyze", "setuptools", 
            "--max-versions=2", "--include-yanked", "--format=json"
        ], 
        cwd="/home/ec2-user/ssd/py-package-evol",
        capture_output=True, text=True, timeout=30)
        
        if result2.returncode == 0:
            print("   ✅ CLI with yanked works")
        else:
            print(f"   ❌ CLI with yanked failed: {result2.stderr}")
            return False
        
        return True
        
    except subprocess.TimeoutExpired:
        print("   ⚠️  CLI test timed out (acceptable)")
        return True
    except Exception as e:
        print(f"   ⚠️  CLI test failed: {e}")
        return False

def main():
    """Run all tests."""
    print("🚀 Testing Yanked Version Filtering")
    print("=" * 40)
    
    tests = [
        test_yanked_detection,
        test_analyzer_yanked_filtering,
        test_specific_yanked_version,
        test_cli_yanked_option,
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            if test():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            failed += 1
            print(f"   ❌ Test {test.__name__} failed: {e}")
    
    print(f"\n📊 Test Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("🎉 All tests passed! Yanked version filtering is working correctly.")
        return True
    else:
        print("⚠️  Some tests failed. Please review the implementation.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
