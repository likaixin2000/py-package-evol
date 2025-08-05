#!/usr/bin/env python3
"""
Simple focused analysis of requests.post API evolution from 2023-01-01 to present.

This script provides a streamlined analysis focusing specifically on:
1. requests.post function signature changes
2. Parameter additions/removals/modifications
3. Documentation changes
4. Breaking changes in the POST API
"""

import sys
from datetime import datetime, timezone
from pathlib import Path
import json

# Add the project root to Python path
sys.path.insert(0, str(Path(__file__).parent))

from pypevol import PackageAnalyzer


def analyze_requests_post():
    """Analyze the requests.post API evolution from 2023 to now."""

    print("🔍 Analyzing requests.post API Evolution")
    print("=" * 50)

    # Set up date range
    start_date = datetime(2023, 1, 1, tzinfo=timezone.utc)
    end_date = datetime.now(timezone.utc)

    print(
        f"📅 Date Range: {start_date.strftime('%Y-%m-%d')} → {end_date.strftime('%Y-%m-%d')}"
    )

    # Initialize analyzer
    analyzer = PackageAnalyzer(
        include_private=False, include_deprecated=True, prefer_wheels=True
    )

    try:
        print("\n🔍 Step 1: Fetching requests package versions...")

        # Get all versions in date range
        all_versions = analyzer.get_package_versions("requests")
        target_versions = [
            v
            for v in all_versions
            if v.release_date and start_date <= v.release_date <= end_date
        ]

        print(f"   Found {len(target_versions)} versions in target period")

        # Show versions we'll analyze
        print("   Versions to analyze:")
        for v in sorted(target_versions, key=lambda x: x.release_date):
            print(f"     • {v.version} ({v.release_date.strftime('%Y-%m-%d')})")

        if not target_versions:
            print("❌ No versions found in the specified date range")
            return

        print(f"\n🔬 Step 2: Analyzing requests package...")

        # Analyze the package
        result = analyzer.analyze_package(
            package_name="requests", from_date=start_date, to_date=end_date
        )

        print(f"   ✅ Analysis complete!")
        print(f"   📊 Analyzed {len(result.versions)} versions")
        print(f"   📈 Found {len(result.changes)} total API changes")

        print(f"\n🎯 Step 3: Focusing on requests.post API...")

        # Find requests.post across versions
        post_instances = []
        post_related = []

        for version, apis in result.api_elements.items():
            for api in apis:
                # Exact match for post function
                if api.name == "post" and (
                    "requests" in api.module_path or api.module_path == "requests"
                ):
                    post_instances.append((version, api))
                # Related POST functionality
                elif "post" in api.name.lower() and "requests" in api.module_path:
                    post_related.append((version, api))

        print(f"   Found {len(post_instances)} instances of requests.post")
        print(f"   Found {len(post_related)} related POST APIs")

        # Initialize variables
        signatures = {}
        docstrings = {}

        # Analyze post function details
        if post_instances:
            print(f"\n📋 requests.post Function Analysis:")
            print("   " + "-" * 40)

            for version, api in post_instances:
                print(f"   📦 Version {version}:")
                print(f"      Module: {api.module_path}")
                print(f"      Full name: {api.full_name}")

                if api.signature:
                    signatures[version] = api.signature
                    print(f"      Signature: {api.signature}")
                else:
                    print(f"      Signature: Not available")

                if api.docstring:
                    # Show first line of docstring
                    first_line = api.docstring.split("\n")[0]
                    docstrings[version] = api.docstring
                    print(f"      Docstring: {first_line}...")

                print()

            # Compare signatures across versions
            print(f"🔄 Signature Evolution:")
            print("   " + "-" * 30)

            if len(signatures) > 1:
                versions_with_sigs = sorted(signatures.keys())
                for i, version in enumerate(versions_with_sigs):
                    print(f"   {version}: {signatures[version]}")

                    if i > 0:
                        prev_version = versions_with_sigs[i - 1]
                        if signatures[version] != signatures[prev_version]:
                            print("      ⚠️  SIGNATURE CHANGED!")
            else:
                print("   No signature changes detected (or limited signature data)")

        # Check for POST-related changes
        print(f"\n🔄 POST-Related API Changes:")
        print("   " + "-" * 35)

        post_changes = [
            change
            for change in result.changes
            if "post" in change.element.name.lower()
            or "post" in change.element.full_name.lower()
        ]

        if post_changes:
            change_stats = {}
            for change in post_changes:
                change_type = change.change_type.value
                change_stats[change_type] = change_stats.get(change_type, 0) + 1

            for change_type, count in change_stats.items():
                print(f"   {change_type.title()}: {count}")

            print(f"\n   Detailed changes:")
            for change in post_changes[:5]:  # Show first 5
                print(f"   • {change.change_type.value}: {change.element.full_name}")
                print(f"     Version: {change.from_version} → {change.to_version}")
                if change.description:
                    print(f"     Description: {change.description}")
                print()
        else:
            print("   No POST-specific changes detected")

        # Get lifecycle information
        print(f"\n🔬 requests.post Lifecycle Analysis:")
        print("   " + "-" * 40)

        lifecycle = result.get_api_lifecycle("post")
        print(f"   API Name: {lifecycle['name']}")
        print(f"   Introduced: {lifecycle.get('introduced_in', 'Not determined')}")
        print(f"   Removed: {lifecycle.get('removed_in', 'Still present')}")
        print(f"   Present in versions: {lifecycle.get('versions_present', [])}")
        print(f"   Number of changes: {len(lifecycle.get('changes', []))}")

        # Stability assessment
        print(f"\n📊 Stability Assessment:")
        print("   " + "-" * 25)

        if len(lifecycle.get("changes", [])) == 0:
            stability = "🟢 STABLE"
            recommendation = "API appears stable with no detected changes"
        elif len(lifecycle.get("changes", [])) <= 2:
            stability = "🟡 MOSTLY STABLE"
            recommendation = "Minor changes detected, monitor for breaking changes"
        else:
            stability = "🔴 EVOLVING"
            recommendation = "Multiple changes detected, review for compatibility"

        print(f"   Status: {stability}")
        print(f"   Recommendation: {recommendation}")

        # Save detailed report
        report = {
            "analysis_date": datetime.now().isoformat(),
            "package": "requests",
            "api_focus": "post",
            "date_range": {
                "start": start_date.isoformat(),
                "end": end_date.isoformat(),
            },
            "versions_analyzed": [v.version for v in result.versions],
            "post_instances": len(post_instances),
            "post_changes": len(post_changes),
            "lifecycle": lifecycle,
            "stability": stability,
            "recommendation": recommendation,
            "signatures": signatures,
            "changes_detail": [
                {
                    "type": change.change_type.value,
                    "element": change.element.full_name,
                    "from_version": change.from_version,
                    "to_version": change.to_version,
                    "description": change.description,
                }
                for change in post_changes
            ],
        }

        report_file = Path(__file__).parent / "requests_post_focused_report.json"
        with open(report_file, "w") as f:
            json.dump(report, f, indent=2, default=str)

        print(f"\n💾 Report saved to: {report_file}")
        print(f"\n✅ Analysis completed successfully!")

    except Exception as e:
        print(f"❌ Analysis failed: {e}")
        import traceback

        traceback.print_exc()
        return False

    finally:
        # Cleanup
        analyzer._cleanup()

    return True


if __name__ == "__main__":
    success = analyze_requests_post()
    if success:
        print("\n🎉 requests.post analysis completed successfully!")
        print("📁 Check the generated JSON report for detailed findings.")
    else:
        print("\n💥 Analysis failed. Check the error messages above.")

    sys.exit(0 if success else 1)
