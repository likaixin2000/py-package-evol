"""Report generation for PyPevol."""

import json
from typing import Dict, Any, List
from datetime import datetime
from pathlib import Path
import os

from .models import ChangeType, APIType


class ReportGenerator:
    """Generates various types of reports from analysis results."""

    def __init__(self):
        """Initialize the report generator."""
        self.template_dir = Path(__file__).parent / "templates"

    def generate_single_package_report(
        self, result_data: Dict[str, Any], format_type: str
    ) -> str:
        """Generate a report for a single package.

        Args:
            result_data: Analysis result data
            format_type: Output format ('html', 'markdown', 'csv')

        Returns:
            Report content as string
        """
        if format_type == "html":
            return self._generate_html_report(result_data)
        elif format_type == "markdown":
            return self._generate_markdown_report(result_data)
        elif format_type == "csv":
            return self._generate_csv_report(result_data)
        else:
            raise ValueError(f"Unsupported format: {format_type}")

    def generate_multi_package_report(
        self, results_data: Dict[str, Dict[str, Any]], format_type: str
    ) -> str:
        """Generate a report for multiple packages.

        Args:
            results_data: Dictionary of package name to analysis result data
            format_type: Output format ('html', 'markdown')

        Returns:
            Report content as string
        """
        if format_type == "html":
            return self._generate_multi_html_report(results_data)
        elif format_type == "markdown":
            return self._generate_multi_markdown_report(results_data)
        else:
            raise ValueError(f"Unsupported format for multi-package: {format_type}")

    def _generate_html_report(self, result_data: Dict[str, Any]) -> str:
        """Generate HTML report for a single package."""
        package_name = result_data["package_name"]
        summary = result_data["summary"]
        versions = result_data["versions"]
        changes = result_data["changes"]

        # Generate charts data
        version_timeline = self._generate_version_timeline_data(versions, changes)
        change_distribution = self._generate_change_distribution_data(changes)
        api_evolution = self._generate_api_evolution_data(result_data)

        html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>API Evolution Report - {package_name}</title>
    <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            padding: 30px;
        }}
        .header {{
            text-align: center;
            margin-bottom: 30px;
            padding-bottom: 20px;
            border-bottom: 2px solid #e0e0e0;
        }}
        .header h1 {{
            color: #2c3e50;
            margin: 0;
        }}
        .header .subtitle {{
            color: #7f8c8d;
            margin-top: 10px;
        }}
        .summary {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}
        .summary-card {{
            background: #f8f9fa;
            padding: 20px;
            border-radius: 8px;
            text-align: center;
            border-left: 4px solid #3498db;
        }}
        .summary-card .number {{
            font-size: 2em;
            font-weight: bold;
            color: #2c3e50;
        }}
        .summary-card .label {{
            color: #7f8c8d;
            margin-top: 5px;
        }}
        .chart-container {{
            margin: 30px 0;
            padding: 20px;
            background: #fafafa;
            border-radius: 8px;
        }}
        .chart-title {{
            font-size: 1.2em;
            font-weight: bold;
            color: #2c3e50;
            margin-bottom: 15px;
        }}
        .changes-table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 20px;
        }}
        .changes-table th, .changes-table td {{
            padding: 10px;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }}
        .changes-table th {{
            background-color: #f5f5f5;
            font-weight: bold;
        }}
        .change-added {{ color: #27ae60; font-weight: bold; }}
        .change-removed {{ color: #e74c3c; font-weight: bold; }}
        .change-modified {{ color: #f39c12; font-weight: bold; }}
        .change-deprecated {{ color: #8e44ad; font-weight: bold; }}
        .signature {{
            font-family: 'Monaco', 'Consolas', monospace;
            font-size: 0.9em;
            background: #f4f4f4;
            padding: 2px 4px;
            border-radius: 3px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>API Evolution Report</h1>
            <div class="subtitle">Package: <strong>{package_name}</strong></div>
            <div class="subtitle">Generated on {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</div>
        </div>
        
        <div class="summary">
            <div class="summary-card">
                <div class="number">{summary['total_versions']}</div>
                <div class="label">Versions Analyzed</div>
            </div>
            <div class="summary-card">
                <div class="number">{summary['total_changes']}</div>
                <div class="label">API Changes</div>
            </div>
            <div class="summary-card">
                <div class="number">{summary['changes_by_type'].get('added', 0)}</div>
                <div class="label">APIs Added</div>
            </div>
            <div class="summary-card">
                <div class="number">{summary['changes_by_type'].get('removed', 0)}</div>
                <div class="label">APIs Removed</div>
            </div>
        </div>
        
        <div class="chart-container">
            <div class="chart-title">API Changes Over Time</div>
            <div id="timeline-chart" style="height: 400px;"></div>
        </div>
        
        <div class="chart-container">
            <div class="chart-title">Change Type Distribution</div>
            <div id="distribution-chart" style="height: 400px;"></div>
        </div>
        
        <div class="chart-container">
            <div class="chart-title">API Evolution Heatmap</div>
            <div id="evolution-chart" style="height: 500px;"></div>
        </div>
        
        <div class="chart-container">
            <div class="chart-title">Recent API Changes</div>
            <table class="changes-table">
                <thead>
                    <tr>
                        <th>Version</th>
                        <th>Change Type</th>
                        <th>API</th>
                        <th>Description</th>
                    </tr>
                </thead>
                <tbody>
"""

        # Add recent changes to table
        for change in sorted(
            changes, key=lambda x: x.get("to_version", ""), reverse=True
        )[:20]:
            change_type = change["change_type"]
            change_class = f"change-{change_type}"
            api_name = change["element"]["full_name"]
            description = change.get("description", "")
            version = change.get("to_version", "")

            html_content += f"""
                    <tr>
                        <td>{version}</td>
                        <td class="{change_class}">{change_type.upper()}</td>
                        <td class="signature">{api_name}</td>
                        <td>{description}</td>
                    </tr>
"""

        html_content += f"""
                </tbody>
            </table>
        </div>
    </div>
    
    <script>
        // Timeline chart
        var timelineData = {json.dumps(version_timeline)};
        Plotly.newPlot('timeline-chart', timelineData.data, timelineData.layout, {{responsive: true}});
        
        // Distribution chart
        var distributionData = {json.dumps(change_distribution)};
        Plotly.newPlot('distribution-chart', distributionData.data, distributionData.layout, {{responsive: true}});
        
        // Evolution heatmap
        var evolutionData = {json.dumps(api_evolution)};
        Plotly.newPlot('evolution-chart', evolutionData.data, evolutionData.layout, {{responsive: true}});
    </script>
</body>
</html>"""

        return html_content

    def _generate_markdown_report(self, result_data: Dict[str, Any]) -> str:
        """Generate Markdown report for a single package."""
        package_name = result_data["package_name"]
        summary = result_data["summary"]
        versions = result_data["versions"]
        changes = result_data["changes"]

        markdown_content = f"""# API Evolution Report: {package_name}

Generated on {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

## Summary

- **Versions Analyzed**: {summary['total_versions']}
- **Total API Changes**: {summary['total_changes']}
- **APIs Added**: {summary['changes_by_type'].get('added', 0)}
- **APIs Removed**: {summary['changes_by_type'].get('removed', 0)}
- **APIs Modified**: {summary['changes_by_type'].get('modified', 0)}
- **APIs Deprecated**: {summary['changes_by_type'].get('deprecated', 0)}

## Change Distribution by Type

"""

        for change_type, count in summary["changes_by_type"].items():
            if count > 0:
                markdown_content += f"- **{change_type.title()}**: {count} changes\\n"

        markdown_content += f"""

## API Type Distribution

"""

        for api_type, count in summary["apis_by_type"].items():
            if count > 0:
                markdown_content += f"- **{api_type.title()}**: {count} APIs\\n"

        # Recent changes
        markdown_content += """

## Recent API Changes

| Version | Change Type | API | Description |
|---------|-------------|-----|-------------|
"""

        for change in sorted(
            changes, key=lambda x: x.get("to_version", ""), reverse=True
        )[:20]:
            change_type = change["change_type"].upper()
            api_name = change["element"]["full_name"]
            description = change.get("description", "")
            version = change.get("to_version", "")

            markdown_content += (
                f"| {version} | {change_type} | `{api_name}` | {description} |\\n"
            )

        # Version history
        markdown_content += """

## Version History

"""

        for version in sorted(
            versions, key=lambda x: x.get("release_date", ""), reverse=True
        ):
            version_num = version["version"]
            release_date = version.get("release_date", "Unknown")
            if release_date != "Unknown":
                release_date = release_date.split("T")[0]  # Just the date part

            markdown_content += f"- **{version_num}** ({release_date})\\n"

        return markdown_content

    def _generate_csv_report(self, result_data: Dict[str, Any]) -> str:
        """Generate CSV report for a single package."""
        changes = result_data["changes"]

        csv_content = "Version,Change Type,API Type,API Name,Module Path,Description,Old Signature,New Signature\\n"

        for change in changes:
            version = change.get("to_version", "")
            change_type = change["change_type"]
            api_type = change["element"]["type"]
            api_name = change["element"]["name"]
            module_path = change["element"]["module_path"]
            description = change.get("description", "").replace(",", ";")
            old_sig = (
                change.get("old_signature", "").replace(",", ";")
                if change.get("old_signature")
                else ""
            )
            new_sig = (
                change.get("new_signature", "").replace(",", ";")
                if change.get("new_signature")
                else ""
            )

            csv_content += f'"{version}","{change_type}","{api_type}","{api_name}","{module_path}","{description}","{old_sig}","{new_sig}"\\n'

        return csv_content

    def _generate_multi_markdown_report(
        self, results_data: Dict[str, Dict[str, Any]]
    ) -> str:
        """Generate Markdown report for multiple packages."""
        markdown_content = f"""# Multi-Package API Evolution Report

Generated on {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

## Overview

This report analyzes the API evolution of {len(results_data)} packages.

"""

        # Summary table
        markdown_content += """| Package | Versions | Total Changes | Added | Removed | Modified | Deprecated |
|---------|----------|---------------|-------|---------|----------|------------|
"""

        for package_name, result_data in results_data.items():
            summary = result_data["summary"]
            changes_by_type = summary["changes_by_type"]

            markdown_content += f"""| {package_name} | {summary['total_versions']} | {summary['total_changes']} | {changes_by_type.get('added', 0)} | {changes_by_type.get('removed', 0)} | {changes_by_type.get('modified', 0)} | {changes_by_type.get('deprecated', 0)} |
"""

        # Individual package reports
        for package_name, result_data in results_data.items():
            markdown_content += f"\\n## {package_name}\\n\\n"
            package_report = self._generate_markdown_report(result_data)
            # Remove the main title and add content
            lines = package_report.split("\\n")[3:]  # Skip first 3 lines
            markdown_content += "\\n".join(lines)
            markdown_content += "\\n---\\n"

        return markdown_content

    def _generate_multi_html_report(
        self, results_data: Dict[str, Dict[str, Any]]
    ) -> str:
        """Generate HTML report for multiple packages."""
        # For simplicity, generate individual reports and combine them
        html_content = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Multi-Package API Evolution Report</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        .package-section { margin: 40px 0; border-top: 2px solid #ccc; padding-top: 20px; }
        h1 { color: #2c3e50; }
        h2 { color: #34495e; }
    </style>
</head>
<body>
    <h1>Multi-Package API Evolution Report</h1>
"""

        for package_name, result_data in results_data.items():
            html_content += f'<div class="package-section">'
            package_report = self._generate_html_report(result_data)
            # Extract body content
            body_start = package_report.find("<body>") + 6
            body_end = package_report.find("</body>")
            body_content = package_report[body_start:body_end]
            html_content += body_content
            html_content += "</div>"

        html_content += "</body></html>"
        return html_content

    def _generate_version_timeline_data(
        self, versions: List[Dict], changes: List[Dict]
    ) -> Dict:
        """Generate data for version timeline chart."""
        # Group changes by version
        changes_by_version = {}
        for change in changes:
            version = change.get("to_version", "")
            if version not in changes_by_version:
                changes_by_version[version] = {
                    "added": 0,
                    "removed": 0,
                    "modified": 0,
                    "deprecated": 0,
                }
            changes_by_version[version][change["change_type"]] += 1

        versions_list = [
            v["version"]
            for v in sorted(versions, key=lambda x: x.get("release_date", ""))
        ]

        traces = []
        for change_type in ["added", "removed", "modified", "deprecated"]:
            y_values = [
                changes_by_version.get(v, {}).get(change_type, 0) for v in versions_list
            ]
            traces.append(
                {
                    "x": versions_list,
                    "y": y_values,
                    "name": change_type.title(),
                    "type": "scatter",
                    "mode": "lines+markers",
                }
            )

        return {
            "data": traces,
            "layout": {
                "title": "API Changes Over Versions",
                "xaxis": {"title": "Version"},
                "yaxis": {"title": "Number of Changes"},
                "hovermode": "x unified",
            },
        }

    def _generate_change_distribution_data(self, changes: List[Dict]) -> Dict:
        """Generate data for change distribution pie chart."""
        distribution = {}
        for change in changes:
            change_type = change["change_type"]
            distribution[change_type] = distribution.get(change_type, 0) + 1

        return {
            "data": [
                {
                    "labels": list(distribution.keys()),
                    "values": list(distribution.values()),
                    "type": "pie",
                    "textinfo": "label+percent+value",
                }
            ],
            "layout": {"title": "Distribution of Change Types"},
        }

    def _generate_api_evolution_data(self, result_data: Dict) -> Dict:
        """Generate data for API evolution heatmap."""
        # This is a simplified version - could be enhanced with more sophisticated analysis
        api_elements = result_data["api_elements"]

        # Create a matrix of API presence across versions
        all_apis = set()
        for elements in api_elements.values():
            for element in elements:
                all_apis.add(element["full_name"])

        versions = sorted(api_elements.keys())
        api_list = sorted(list(all_apis))[:50]  # Limit to top 50 APIs

        z_data = []
        for api in api_list:
            row = []
            for version in versions:
                present = any(
                    e["full_name"] == api for e in api_elements.get(version, [])
                )
                row.append(1 if present else 0)
            z_data.append(row)

        return {
            "data": [
                {
                    "z": z_data,
                    "x": versions,
                    "y": api_list,
                    "type": "heatmap",
                    "colorscale": "Viridis",
                    "showscale": False,
                }
            ],
            "layout": {
                "title": "API Presence Across Versions",
                "xaxis": {"title": "Version"},
                "yaxis": {"title": "API"},
                "height": 500,
            },
        }
