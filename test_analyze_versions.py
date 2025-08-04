#!/usr/bin/env python3
"""
Comprehensive test for the new analyze_versions functionality.
"""

import sys
from pathlib import Path

# Add the pypevol package to the path
sys.path.insert(0, str(Path(__file__).parent))

from pypevol.analyzer import PackageAnalyzer


def test_analyze_versions_basic():
    """Test basic analyze_versions functionality."""
    
    print("Testing analyze_versions basic functionality...")
    
    package_name = "click"  # Popular, stable package
    versions = ["7.0", "7.1"]
    
    try:
        with PackageAnalyzer() as analyzer:
            result = analyzer.analyze_versions(
                package_name=package_name,
                versions=versions,
                calculate_changes=True
            )
            
            # Basic checks
            assert result.package_name == package_name
            assert len(result.versions) == len(versions)
            assert len(result.api_elements) == len(versions)
            assert result.metadata['analysis_type'] == 'specific_versions'
            assert result.metadata['successful_versions'] == len(versions)
            
            # Check that all requested versions were analyzed
            analyzed_versions = {v.version for v in result.versions}
            requested_versions = set(versions)
            assert analyzed_versions == requested_versions
            
            # Check API elements exist for each version
            for version in versions:
                assert version in result.api_elements
                assert isinstance(result.api_elements[version], list)
                assert len(result.api_elements[version]) > 0
            
            print("✓ Basic analyze_versions test passed")
            return True
            
    except Exception as e:
        print(f"✗ Basic analyze_versions test failed: {e}")
        return False


def test_analyze_versions_no_changes():
    """Test analyze_versions with calculate_changes=False."""
    
    print("Testing analyze_versions with calculate_changes=False...")
    
    try:
        with PackageAnalyzer() as analyzer:
            result = analyzer.analyze_versions(
                package_name="click",
                versions=["7.0", "7.1", "8.0.0"],
                calculate_changes=False
            )
            
            # Should have no changes calculated
            assert len(result.changes) == 0
            assert result.metadata.get('calculate_changes') == False
            assert len(result.versions) == 3
            assert len(result.api_elements) == 3
            
            print("✓ No changes calculation test passed")
            return True
            
    except Exception as e:
        print(f"✗ No changes calculation test failed: {e}")
        return False


def test_invalid_version():
    """Test behavior with invalid version."""
    
    print("Testing behavior with invalid version...")
    
    try:
        with PackageAnalyzer() as analyzer:
            try:
                result = analyzer.analyze_versions(
                    package_name="click",
                    versions=["7.0", "999.999.999"],  # Invalid version
                    calculate_changes=True
                )
                print("✗ Expected ValueError for invalid version")
                return False
                
            except ValueError as e:
                # This is expected
                assert "not found" in str(e)
                print("✓ Invalid version handling test passed")
                return True
                
    except Exception as e:
        print(f"✗ Invalid version test failed unexpectedly: {e}")
        return False


def test_empty_version_list():
    """Test behavior with empty version list."""
    
    print("Testing behavior with empty version list...")
    
    try:
        with PackageAnalyzer() as analyzer:
            try:
                result = analyzer.analyze_versions(
                    package_name="click",
                    versions=[],
                    calculate_changes=True
                )
                print("✗ Expected ValueError for empty version list")
                return False
                
            except ValueError as e:
                # This is expected
                assert "At least one version" in str(e)
                print("✓ Empty version list handling test passed")
                return True
                
    except Exception as e:
        print(f"✗ Empty version list test failed unexpectedly: {e}")
        return False


def test_single_version():
    """Test analyze_versions with single version."""
    
    print("Testing analyze_versions with single version...")
    
    try:
        with PackageAnalyzer() as analyzer:
            result = analyzer.analyze_versions(
                package_name="click",
                versions=["7.0"],
                calculate_changes=True
            )
            
            # Should have no changes (need at least 2 versions for changes)
            assert len(result.changes) == 0
            assert len(result.versions) == 1
            assert len(result.api_elements) == 1
            assert result.versions[0].version == "7.0"
            
            print("✓ Single version test passed")
            return True
            
    except Exception as e:
        print(f"✗ Single version test failed: {e}")
        return False


def test_method_consistency():
    """Test that different methods produce consistent results."""
    
    print("Testing consistency between different analysis methods...")
    
    package_name = "click"
    version1 = "7.0"
    version2 = "8.0.0"
    
    try:
        with PackageAnalyzer() as analyzer:
            
            # Method 1: analyze_versions
            result1 = analyzer.analyze_versions(
                package_name=package_name,
                versions=[version1, version2],
                calculate_changes=True
            )
            
            # Method 2: compare_versions
            result2 = analyzer.compare_versions(
                package_name=package_name,
                version1=version1,
                version2=version2
            )
            
            # Method 3: analyze_package with compare_only
            result3 = analyzer.analyze_package(
                package_name=package_name,
                from_version=version1,
                to_version=version2,
                compare_only=True
            )
            
            # All should have same number of changes
            changes1 = len(result1.changes)
            changes2 = len(result2.changes)
            changes3 = len(result3.changes)
            
            assert changes1 == changes2 == changes3, f"Inconsistent change counts: {changes1}, {changes2}, {changes3}"
            
            # All should analyze the same versions
            assert len(result1.versions) == len(result2.versions) == len(result3.versions) == 2
            
            # All should have API elements for both versions
            assert len(result1.api_elements) == len(result2.api_elements) == len(result3.api_elements) == 2
            
            print("✓ Method consistency test passed")
            print(f"  All methods found {changes1} changes")
            return True
            
    except Exception as e:
        print(f"✗ Method consistency test failed: {e}")
        return False


def test_refactoring_no_regression():
    """Test that refactoring didn't break existing functionality."""
    
    print("Testing that refactoring didn't break existing functionality...")
    
    try:
        with PackageAnalyzer() as analyzer:
            
            # Test original analyze_package method
            result = analyzer.analyze_package(
                package_name="click",
                from_version="7.0",
                to_version="7.1",
                max_versions=5
            )
            
            # Should work as before
            assert result.package_name == "click"
            assert len(result.versions) >= 1
            assert len(result.api_elements) >= 1
            assert 'analysis_settings' in result.metadata
            
            print("✓ No regression test passed")
            return True
            
    except Exception as e:
        print(f"✗ No regression test failed: {e}")
        return False


def run_all_tests():
    """Run all tests."""
    
    print("Running comprehensive tests for analyze_versions functionality...")
    print("=" * 60)
    
    tests = [
        test_analyze_versions_basic,
        test_analyze_versions_no_changes,
        test_invalid_version,
        test_empty_version_list,
        test_single_version,
        test_method_consistency,
        test_refactoring_no_regression,
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
            print()  # Add spacing between tests
        except Exception as e:
            print(f"✗ Test {test.__name__} failed with exception: {e}")
            print()
    
    print("=" * 60)
    print(f"Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed!")
        return True
    else:
        print(f"❌ {total - passed} tests failed")
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
