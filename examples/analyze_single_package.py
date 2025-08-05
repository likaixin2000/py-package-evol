"""
Example: Analyzing a single package (requests)
"""

from pypevol import PackageAnalyzer


def main():
    # Create analyzer with custom settings
    analyzer = PackageAnalyzer(
        include_private=False, include_deprecated=True, prefer_wheels=True
    )

    try:
        # Analyze the requests package
        print("Analyzing requests package...")
        result = analyzer.analyze_package(
            package_name="requests", max_versions=10  # Analyze last 10 versions
        )

        # Print summary
        summary = result.generate_summary()
        print(f"\\nAnalysis Summary:")
        print(f"- Package: {result.package_name}")
        print(f"- Versions analyzed: {summary['total_versions']}")
        print(f"- Total API changes: {summary['total_changes']}")

        # Show change breakdown
        print(f"\\nChange breakdown:")
        for change_type, count in summary["changes_by_type"].items():
            print(f"- {change_type.title()}: {count}")

        # Show API type breakdown
        print(f"\\nAPI type breakdown:")
        for api_type, count in summary["apis_by_type"].items():
            print(f"- {api_type.title()}: {count}")

        # Show recent changes
        recent_changes = result.get_api_changes()[-5:]  # Last 5 changes
        print(f"\\nRecent changes:")
        for change in recent_changes:
            print(
                f"- {change.change_type.value.upper()}: {change.element.full_name} "
                f"in version {change.to_version}"
            )

        # Generate HTML report
        print("\\nGenerating HTML report...")
        html_report = result.to_json()

        with open("requests_analysis.json", "w") as f:
            f.write(html_report)

        print("Report saved to: requests_analysis.json")

    except Exception as e:
        print(f"Error: {e}")

    finally:
        # Clean up temporary files
        analyzer._cleanup()


if __name__ == "__main__":
    main()
