#!/usr/bin/env python3
"""
Demonstration of the new versions parameter feature in pypevol.

This example shows how to:
1. Get available package versions
2. Select specific versions for analysis
3. Compare different approaches (range vs specific versions)
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '.'))

from pypevol import PackageAnalyzer, PyPIFetcher

def demonstrate_version_selection():
    """Demonstrate how to select versions for analysis."""
    print("🔍 Demonstrating Version Selection")
    print("=" * 40)
    
    # Step 1: Get all available versions
    fetcher = PyPIFetcher()
    all_versions = fetcher.get_package_versions("click")
    
    print(f"📦 Package 'click' has {len(all_versions)} versions")
    print(f"   First version: {all_versions[0]}")
    print(f"   Latest version: {all_versions[-1]}")
    print(f"   Last 5 versions: {all_versions[-5:]}")
    
    return all_versions

def compare_analysis_approaches(package_name="click"):
    """Compare different approaches to version analysis."""
    print(f"\n🔬 Comparing Analysis Approaches for '{package_name}'")
    print("=" * 50)
    
    analyzer = PackageAnalyzer()
    
    # Approach 1: Using from/to version range
    print("\n1️⃣ Using version range (from/to):")
    try:
        result1 = analyzer.analyze_package(
            package_name=package_name,
            from_version="8.0.0",
            to_version="8.1.0",
            max_versions=3
        )
        print(f"   ✅ Analyzed {len(result1.versions)} versions using range")
        analyzed_versions1 = [v.version for v in result1.versions]
        print(f"   📋 Versions: {analyzed_versions1}")
        print(f"   📊 Found {len(result1.changes)} API changes")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Approach 2: Using specific versions list
    print("\n2️⃣ Using specific versions list:")
    specific_versions = ["8.0.0", "8.0.1", "8.1.0"]
    try:
        result2 = analyzer.analyze_package(
            package_name=package_name,
            versions=specific_versions
        )
        print(f"   ✅ Analyzed {len(result2.versions)} versions using specific list")
        analyzed_versions2 = [v.version for v in result2.versions]
        print(f"   📋 Versions: {analyzed_versions2}")
        print(f"   📊 Found {len(result2.changes)} API changes")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Approach 3: All versions (limited)
    print("\n3️⃣ Using all versions (limited to 5):")
    try:
        result3 = analyzer.analyze_package(
            package_name=package_name,
            max_versions=5
        )
        print(f"   ✅ Analyzed {len(result3.versions)} versions (all/limited)")
        analyzed_versions3 = [v.version for v in result3.versions]
        print(f"   📋 Versions: {analyzed_versions3}")
        print(f"   📊 Found {len(result3.changes)} API changes")
    except Exception as e:
        print(f"   ❌ Error: {e}")

def demonstrate_cli_usage():
    """Show CLI usage examples."""
    print(f"\n💻 CLI Usage Examples")
    print("=" * 25)
    
    print("\n# Analyze specific versions:")
    print("python -m pypevol analyze requests --versions='2.32.0,2.32.1,2.32.2'")
    
    print("\n# Analyze version range (traditional way):")
    print("python -m pypevol analyze requests --from-version=2.32.0 --to-version=2.32.2")
    
    print("\n# Analyze all versions (limited):")
    print("python -m pypevol analyze requests --max-versions=5")
    
    print("\n# Parameter validation - this will error:")
    print("python -m pypevol analyze requests --versions='2.32.0' --from-version=2.32.0")
    print("# ❌ Error: Cannot specify --versions together with --from-version")

def main():
    print("🚀 PyPevol Plus - New Versions Parameter Feature")
    print("=" * 50)
    
    try:
        # Demonstrate version selection
        versions = demonstrate_version_selection()
        
        # Compare analysis approaches
        compare_analysis_approaches()
        
        # Show CLI usage
        demonstrate_cli_usage()
        
        print(f"\n✅ Demo completed successfully!")
        print(f"🎯 Key Benefits:")
        print(f"   • Precise version control for analysis")
        print(f"   • Better performance by avoiding unwanted versions")
        print(f"   • Flexibility in choosing analysis strategy")
        print(f"   • Maintained backward compatibility")
        
    except Exception as e:
        print(f"❌ Demo failed: {e}")

if __name__ == "__main__":
    main()
