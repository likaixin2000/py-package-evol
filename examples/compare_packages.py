"""
Example: Comparing multiple packages
"""

from pypevol import PackageAnalyzer
from pypevol.reports import ReportGenerator


def main():
    packages = ["requests", "urllib3", "httpx"]

    analyzer = PackageAnalyzer(max_versions=5)
    results = {}

    try:
        for package in packages:
            print(f"Analyzing {package}...")
            result = analyzer.analyze_package(package)
            results[package] = result

            summary = result.generate_summary()
            print(
                f"  - {summary['total_versions']} versions, "
                f"{summary['total_changes']} changes"
            )

        # Generate comparison report
        print("\\nGenerating comparison report...")

        # Convert to dict format for report generator
        results_data = {name: result.to_dict() for name, result in results.items()}

        generator = ReportGenerator()
        html_report = generator.generate_multi_package_report(results_data, "html")

        with open("http_libraries_comparison.html", "w") as f:
            f.write(html_report)

        print("Comparison report saved to: http_libraries_comparison.html")

        # Print summary comparison
        print("\\nSummary Comparison:")
        print(
            "Package".ljust(15)
            + "Versions".ljust(10)
            + "Changes".ljust(10)
            + "APIs Added".ljust(12)
            + "APIs Removed"
        )
        print("-" * 60)

        for package, result in results.items():
            summary = result.generate_summary()
            print(
                f"{package}".ljust(15)
                + f"{summary['total_versions']}".ljust(10)
                + f"{summary['total_changes']}".ljust(10)
                + f"{summary['changes_by_type'].get('added', 0)}".ljust(12)
                + f"{summary['changes_by_type'].get('removed', 0)}"
            )

    except Exception as e:
        print(f"Error: {e}")

    finally:
        analyzer._cleanup()


if __name__ == "__main__":
    main()
