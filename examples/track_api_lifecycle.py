"""
Example: Track specific API lifecycle
"""

from pypevol import PackageAnalyzer


def track_api_lifecycle(package_name, api_name):
    """Track the lifecycle of a specific API across versions."""

    analyzer = PackageAnalyzer()

    try:
        print(f"Tracking '{api_name}' in package '{package_name}'...")

        # Analyze the package
        result = analyzer.analyze_package(package_name)

        # Get API lifecycle
        lifecycle = result.get_api_lifecycle(api_name)

        if not lifecycle["versions_present"]:
            print(f"API '{api_name}' not found in any analyzed versions.")
            return

        print(f"\\nAPI Lifecycle for '{api_name}':")
        print(
            f"  Introduced in: {lifecycle['introduced_in'] or 'Unknown (before first analyzed version)'}"
        )
        print(f"  Removed in: {lifecycle['removed_in'] or 'Still present'}")
        print(f"  Present in {len(lifecycle['versions_present'])} versions")

        if lifecycle["versions_present"]:
            print(f"  Versions: {', '.join(sorted(lifecycle['versions_present']))}")

        if lifecycle["modifications"]:
            print(f"\\n  Modifications ({len(lifecycle['modifications'])}):")
            for mod in lifecycle["modifications"]:
                print(f"    - Version {mod['version']}: {mod['description']}")
                if mod["old_signature"] and mod["new_signature"]:
                    print(f"      Old: {mod['old_signature']}")
                    print(f"      New: {mod['new_signature']}")

        # Find related changes
        related_changes = [
            change
            for change in result.changes
            if change.element.name == api_name or api_name in change.element.full_name
        ]

        if related_changes:
            print(f"\\n  All related changes:")
            for change in sorted(related_changes, key=lambda x: x.to_version or ""):
                print(
                    f"    - {change.to_version}: {change.change_type.value.upper()} - {change.description}"
                )

    except Exception as e:
        print(f"Error: {e}")

    finally:
        analyzer._cleanup()


def main():
    # Example usage
    examples = [
        ("requests", "Session"),
        ("requests", "get"),
        ("flask", "Flask"),
        ("django", "Model"),
    ]

    for package, api in examples:
        print("=" * 60)
        track_api_lifecycle(package, api)
        print()


if __name__ == "__main__":
    main()
