"""Command-line interface for PyPevol."""

import click
import json
import logging
from pathlib import Path
from typing import Optional

from .analyzer import PackageAnalyzer
from .reports import ReportGenerator

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)


@click.group()
@click.option("--verbose", "-v", is_flag=True, help="Enable verbose logging")
@click.option(
    "--cache-dir", type=click.Path(), help="Directory to cache downloaded files"
)
@click.pass_context
def main(ctx, verbose, cache_dir):
    """PyPevol - Analyze PyPI package API evolution."""
    if verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    ctx.ensure_object(dict)
    ctx.obj["cache_dir"] = Path(cache_dir) if cache_dir else None


@main.command()
@click.argument("packages", nargs=-1, required=True)
@click.option(
    "--from-version",
    help="Starting version (inclusive). Mutually exclusive with --versions.",
)
@click.option(
    "--to-version",
    help="Ending version (inclusive). Mutually exclusive with --versions.",
)
@click.option(
    "--max-versions",
    type=int,
    help="Maximum number of versions to analyze. Mutually exclusive with --versions.",
)
@click.option(
    "--versions",
    help="Comma-separated list of specific versions to analyze. Mutually exclusive with --from-version, --to-version, --max-versions.",
)
@click.option("--output", "-o", type=click.Path(), help="Output file or directory")
@click.option(
    "--format",
    "-f",
    "output_format",
    type=click.Choice(["json", "html", "csv", "markdown"]),
    default="json",
    help="Output format",
)
@click.option(
    "--include-private", is_flag=True, help="Include private APIs (starting with _)"
)
@click.option(
    "--include-deprecated", is_flag=True, default=True, help="Include deprecated APIs"
)
@click.option(
    "--include-yanked", is_flag=True, help="Include yanked versions in analysis"
)
@click.option(
    "--prefer-source", is_flag=True, help="Prefer source distributions over wheels"
)
@click.pass_context
def analyze(
    ctx,
    packages,
    from_version,
    to_version,
    max_versions,
    versions,
    output,
    output_format,
    include_private,
    include_deprecated,
    include_yanked,
    prefer_source,
):
    """Analyze one or more packages for API evolution."""

    cache_dir = ctx.obj.get("cache_dir")

    # Validate parameter combinations
    if versions is not None and (
        from_version is not None or to_version is not None or max_versions is not None
    ):
        click.echo(
            "Error: Cannot specify --versions together with --from-version, --to-version, or --max-versions",
            err=True,
        )
        return

    # Parse versions list if provided
    versions_list = None
    if versions:
        versions_list = [v.strip() for v in versions.split(",") if v.strip()]
        if not versions_list:
            click.echo("Error: --versions parameter cannot be empty", err=True)
            return

    # Create analyzer
    analyzer = PackageAnalyzer(
        cache_dir=cache_dir,
        include_private=include_private,
        include_deprecated=include_deprecated,
        prefer_wheels=not prefer_source,
        include_yanked=include_yanked,
    )

    results = {}

    try:
        for package_name in packages:
            click.echo(f"Analyzing package: {package_name}")

            try:
                result = analyzer.analyze_package(
                    package_name=package_name,
                    from_version=from_version,
                    to_version=to_version,
                    max_versions=max_versions,
                    versions=versions_list,
                )

                results[package_name] = result

                # Print summary
                summary = result.generate_summary()
                click.echo(f"  ✓ Found {summary['total_versions']} versions")
                click.echo(f"  ✓ Detected {summary['total_changes']} API changes")

            except Exception as e:
                click.echo(f"  ✗ Failed to analyze {package_name}: {e}", err=True)
                continue

        if not results:
            click.echo("No packages were successfully analyzed.", err=True)
            return

        # Generate output
        if output:
            _save_results(results, output, output_format)
        else:
            _print_results(results, output_format)

    finally:
        analyzer._cleanup()


@main.command()
@click.argument("package")
@click.argument("api_name")
@click.option("--from-version", help="Starting version (inclusive)")
@click.option("--to-version", help="Ending version (inclusive)")
@click.option("--max-versions", type=int, help="Maximum number of versions to analyze")
@click.pass_context
def track(ctx, package, api_name, from_version, to_version, max_versions):
    """Track the lifecycle of a specific API."""

    cache_dir = ctx.obj.get("cache_dir")

    analyzer = PackageAnalyzer(cache_dir=cache_dir)

    try:
        click.echo(f"Tracking API '{api_name}' in package '{package}'")

        result = analyzer.analyze_package(
            package_name=package,
            from_version=from_version,
            to_version=to_version,
            max_versions=max_versions,
        )

        lifecycle = result.get_api_lifecycle(api_name)

        if not lifecycle["versions_present"]:
            click.echo(f"API '{api_name}' not found in any analyzed versions.")
            return

        click.echo(f"\nAPI Lifecycle for '{api_name}':")
        click.echo(f"  Introduced in: {lifecycle['introduced_in'] or 'Unknown'}")
        click.echo(f"  Removed in: {lifecycle['removed_in'] or 'Still present'}")
        click.echo(f"  Present in {len(lifecycle['versions_present'])} versions")

        if lifecycle["modifications"]:
            click.echo(f"  Modified {len(lifecycle['modifications'])} times:")
            for mod in lifecycle["modifications"]:
                click.echo(
                    f"    - Version {mod['version']}: {mod['description'] or 'Signature changed'}"
                )

    except Exception as e:
        click.echo(f"Failed to track API: {e}", err=True)
    finally:
        analyzer._cleanup()


@main.command()
@click.argument("package")
@click.option("--version", help="Specific version to list APIs for")
@click.option(
    "--type",
    "api_type",
    type=click.Choice(["function", "class", "method", "property", "constant"]),
    help="Filter by API type",
)
@click.option("--private", is_flag=True, help="Include private APIs")
@click.pass_context
def list_apis(ctx, package, version, api_type, private):
    """List all APIs in a package version."""

    cache_dir = ctx.obj.get("cache_dir")

    analyzer = PackageAnalyzer(cache_dir=cache_dir, include_private=private)

    try:
        if version:
            # Analyze specific version
            from .fetcher import PyPIFetcher

            fetcher = PyPIFetcher(cache_dir)
            version_info = fetcher.get_version_info(package, version)

            if not version_info:
                click.echo(
                    f"Version {version} not found for package {package}", err=True
                )
                return

            elements = analyzer._analyze_version(package, version_info)
            if elements is None:
                click.echo(f"Failed to analyze version {version}", err=True)
                return
        else:
            # Analyze latest version
            result = analyzer.analyze_package(package, max_versions=1)
            if not result.versions:
                click.echo(f"No versions found for package {package}", err=True)
                return

            latest_version = result.versions[-1].version
            elements = result.get_version_apis(latest_version)
            version = latest_version

        # Filter by type if specified
        if api_type:
            from .models import APIType

            target_type = APIType(api_type)
            elements = [e for e in elements if e.type == target_type]

        click.echo(f"\nAPIs in {package} v{version}:")
        click.echo(f"Found {len(elements)} APIs")

        # Group by type
        by_type = {}
        for element in elements:
            if element.type.value not in by_type:
                by_type[element.type.value] = []
            by_type[element.type.value].append(element)

        for api_type_name, apis in sorted(by_type.items()):
            click.echo(f"\n{api_type_name.title()}s ({len(apis)}):")
            for api in sorted(apis, key=lambda x: x.name):
                marker = "🔒" if api.is_private else "📦"
                deprecated = " [DEPRECATED]" if api.is_deprecated else ""
                click.echo(f"  {marker} {api.full_name}{deprecated}")
                if api.signature:
                    click.echo(f"      {api.signature}")

    except Exception as e:
        click.echo(f"Failed to list APIs: {e}", err=True)
    finally:
        analyzer._cleanup()


@main.command()
@click.argument("input_file", type=click.Path(exists=True))
@click.option("--output", "-o", type=click.Path(), help="Output file")
@click.option(
    "--format",
    "-f",
    "output_format",
    type=click.Choice(["html", "markdown"]),
    default="html",
    help="Report format",
)
def report(input_file, output, output_format):
    """Generate a report from analysis results."""

    try:
        # Load results
        with open(input_file, "r") as f:
            data = json.load(f)

        # Generate report
        generator = ReportGenerator()

        if len(data) == 1:
            # Single package
            package_name, result_data = next(iter(data.items()))
            report_content = generator.generate_single_package_report(
                result_data, output_format
            )
        else:
            # Multiple packages
            report_content = generator.generate_multi_package_report(
                data, output_format
            )

        # Save or print report
        if output:
            with open(output, "w") as f:
                f.write(report_content)
            click.echo(f"Report saved to: {output}")
        else:
            click.echo(report_content)

    except Exception as e:
        click.echo(f"Failed to generate report: {e}", err=True)


def _save_results(results, output_path, format_type):
    """Save results to file."""
    output_path = Path(output_path)

    if len(results) == 1:
        # Single package
        package_name, result = next(iter(results.items()))

        if format_type == "json":
            content = result.to_json()
            if not output_path.suffix:
                output_path = output_path.with_suffix(".json")
        else:
            generator = ReportGenerator()
            content = generator.generate_single_package_report(
                result.to_dict(), format_type
            )
            if not output_path.suffix:
                output_path = output_path.with_suffix(f".{format_type}")

        with open(output_path, "w") as f:
            f.write(content)

        click.echo(f"Results saved to: {output_path}")

    else:
        # Multiple packages
        if output_path.is_file():
            output_path = output_path.parent

        output_path.mkdir(parents=True, exist_ok=True)

        for package_name, result in results.items():
            filename = f"{package_name}.{format_type}"
            file_path = output_path / filename

            if format_type == "json":
                content = result.to_json()
            else:
                generator = ReportGenerator()
                content = generator.generate_single_package_report(
                    result.to_dict(), format_type
                )

            with open(file_path, "w") as f:
                f.write(content)

        click.echo(f"Results saved to directory: {output_path}")


def _print_results(results, format_type):
    """Print results to stdout."""
    if format_type == "json":
        if len(results) == 1:
            package_name, result = next(iter(results.items()))
            click.echo(result.to_json())
        else:
            combined = {name: result.to_dict() for name, result in results.items()}
            click.echo(json.dumps(combined, indent=2, default=str))
    else:
        generator = ReportGenerator()
        for package_name, result in results.items():
            click.echo(f"\n{'='*60}")
            click.echo(f"Report for {package_name}")
            click.echo("=" * 60)
            content = generator.generate_single_package_report(
                result.to_dict(), format_type
            )
            click.echo(content)


if __name__ == "__main__":
    main()
