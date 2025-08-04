"""Tests for ReportGenerator."""

import unittest
from unittest.mock import Mock, patch, mock_open
import tempfile
import json
from pathlib import Path
from datetime import datetime

from pypevol.reports import ReportGenerator  
from pypevol.models import APIElement, APIType, VersionInfo, AnalysisResult, APIChange, ChangeType


class TestReportGenerator(unittest.TestCase):
    """Test ReportGenerator class."""
    
    def setUp(self):
        """Set up test data."""
        self.generator = ReportGenerator()
        
        # Create test analysis result
        self.version1 = VersionInfo(
            version="1.0.0",
            release_date=datetime(2023, 1, 1)
        )
        self.version2 = VersionInfo(
            version="1.1.0", 
            release_date=datetime(2023, 2, 1)
        )
        
        self.api1 = APIElement(
            name="function1",
            type=APIType.FUNCTION,
            module_path="test.module",
            signature="function1() -> None",
            docstring="Test function 1"
        )
        self.api2 = APIElement(
            name="TestClass",
            type=APIType.CLASS,
            module_path="test.module",
            signature="class TestClass",
            docstring="Test class"
        )
        
        self.change1 = APIChange(
            element=self.api1,
            change_type=ChangeType.ADDED,
            to_version="1.0.0",
            description="Function added in 1.0.0"
        )
        self.change2 = APIChange(
            element=self.api2,
            change_type=ChangeType.ADDED,
            to_version="1.1.0",
            description="Class added in 1.1.0"
        )
        
        self.analysis_result = AnalysisResult(
            package_name="test-package",
            versions=[self.version1, self.version2],
            api_elements={
                "1.0.0": [self.api1],
                "1.1.0": [self.api1, self.api2]
            },
            changes=[self.change1, self.change2],
            metadata={"test_key": "test_value"}
        )
    
    def test_init(self):
        """Test ReportGenerator initialization."""
        generator = ReportGenerator()
        self.assertIsNotNone(generator)
    
    def test_generate_json_report(self):
        """Test JSON report generation."""
        report = self.generator.generate_json_report(self.analysis_result)
        
        # Verify it's valid JSON
        parsed = json.loads(report)
        
        # Verify structure
        self.assertEqual(parsed['package_name'], "test-package")
        self.assertEqual(len(parsed['versions']), 2)
        self.assertEqual(len(parsed['changes']), 2)
        self.assertIn('summary', parsed)
        self.assertIn('analysis_date', parsed)
    
    def test_generate_json_report_with_indent(self):
        """Test JSON report generation with custom indentation."""
        report = self.generator.generate_json_report(self.analysis_result, indent=4)
        
        # Verify it's properly indented (should have 4-space indents)
        lines = report.split('\n')
        indented_lines = [line for line in lines if line.startswith('    ')]
        self.assertGreater(len(indented_lines), 0)
    
    def test_generate_html_report(self):
        """Test HTML report generation."""
        report = self.generator.generate_html_report(self.analysis_result)
        
        # Verify basic HTML structure
        self.assertIn('<html>', report)
        self.assertIn('<head>', report)
        self.assertIn('<body>', report)
        self.assertIn('</html>', report)
        
        # Verify content
        self.assertIn("test-package", report)
        self.assertIn("function1", report)
        self.assertIn("TestClass", report)
        
        # Verify CSS and JavaScript are included
        self.assertIn('<style>', report)
        self.assertIn('<script>', report)
    
    def test_generate_html_report_with_custom_template(self):
        """Test HTML report generation with custom template."""
        custom_template = """
        <html>
        <head><title>{{package_name}} Report</title></head>
        <body>
            <h1>{{package_name}}</h1>
            <p>Total versions: {{total_versions}}</p>
        </body>
        </html>
        """
        
        report = self.generator.generate_html_report(
            self.analysis_result, 
            template=custom_template
        )
        
        self.assertIn("test-package Report", report)
        self.assertIn("Total versions: 2", report)
    
    def test_generate_csv_report(self):
        """Test CSV report generation."""
        report = self.generator.generate_csv_report(self.analysis_result)
        
        # Verify CSV structure
        lines = report.strip().split('\n')
        self.assertGreater(len(lines), 1)  # Header + data rows
        
        # Verify header
        header = lines[0]
        expected_columns = ['Element Name', 'Type', 'Module', 'Change Type', 'Version', 'Description']
        for column in expected_columns:
            self.assertIn(column, header)
        
        # Verify data rows
        self.assertEqual(len(lines), 3)  # Header + 2 changes
        self.assertIn("function1", report)
        self.assertIn("TestClass", report)
    
    def test_generate_markdown_report(self):
        """Test Markdown report generation."""
        report = self.generator.generate_markdown_report(self.analysis_result)
        
        # Verify Markdown structure
        self.assertIn('# API Evolution Report', report)
        self.assertIn('## Package: test-package', report)
        self.assertIn('## Summary', report)
        self.assertIn('## API Changes', report)
        
        # Verify content
        self.assertIn("function1", report)
        self.assertIn("TestClass", report)
        
        # Verify Markdown formatting
        self.assertIn('|', report)  # Table formatting
        self.assertIn('###', report)  # Subheadings
    
    def test_generate_report_unknown_format(self):
        """Test error handling for unknown format."""
        with self.assertRaises(ValueError) as context:
            self.generator.generate_report(self.analysis_result, format='unknown')
        
        self.assertIn("Unsupported format", str(context.exception))
    
    def test_generate_report_json_format(self):
        """Test generate_report with JSON format."""
        report = self.generator.generate_report(self.analysis_result, format='json')
        
        # Should be same as generate_json_report
        expected = self.generator.generate_json_report(self.analysis_result)
        self.assertEqual(report, expected)
    
    def test_generate_report_html_format(self):
        """Test generate_report with HTML format."""
        report = self.generator.generate_report(self.analysis_result, format='html')
        
        # Should be same as generate_html_report  
        expected = self.generator.generate_html_report(self.analysis_result)
        self.assertEqual(report, expected)
    
    def test_save_report_to_file(self):
        """Test saving report to file."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
            filepath = f.name
        
        try:
            # Generate and save report
            self.generator.save_report(
                self.analysis_result, 
                filepath, 
                format='json'
            )
            
            # Verify file was created and contains expected content
            with open(filepath, 'r') as f:
                content = f.read()
            
            # Should be valid JSON
            parsed = json.loads(content)
            self.assertEqual(parsed['package_name'], "test-package")
            
        finally:
            # Cleanup
            Path(filepath).unlink(missing_ok=True)
    
    def test_save_report_auto_format_detection(self):
        """Test automatic format detection from filename."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.html') as f:
            filepath = f.name
        
        try:
            # Save without specifying format - should detect HTML from extension
            self.generator.save_report(self.analysis_result, filepath)
            
            # Verify file contains HTML
            with open(filepath, 'r') as f:
                content = f.read()
            
            self.assertIn('<html>', content)
            
        finally:
            Path(filepath).unlink(missing_ok=True)
    
    def test_get_format_from_filename(self):
        """Test format detection from filename."""
        self.assertEqual(self.generator._get_format_from_filename("report.json"), "json")
        self.assertEqual(self.generator._get_format_from_filename("report.html"), "html")
        self.assertEqual(self.generator._get_format_from_filename("report.htm"), "html")
        self.assertEqual(self.generator._get_format_from_filename("report.csv"), "csv")
        self.assertEqual(self.generator._get_format_from_filename("report.md"), "markdown")
        self.assertEqual(self.generator._get_format_from_filename("report.txt"), "json")  # Default
        self.assertEqual(self.generator._get_format_from_filename("report"), "json")  # No extension
    
    def test_format_api_element(self):
        """Test API element formatting for reports."""
        formatted = self.generator._format_api_element(self.api1)
        
        expected_keys = ['name', 'type', 'module', 'signature', 'docstring', 'full_name']
        for key in expected_keys:
            self.assertIn(key, formatted)
        
        self.assertEqual(formatted['name'], "function1")
        self.assertEqual(formatted['type'], "function")
        self.assertEqual(formatted['module'], "test.module")
    
    def test_format_version_info(self):
        """Test version info formatting for reports."""
        formatted = self.generator._format_version_info(self.version1)
        
        expected_keys = ['version', 'release_date', 'python_requires']
        for key in expected_keys:
            self.assertIn(key, formatted)
        
        self.assertEqual(formatted['version'], "1.0.0")
        self.assertEqual(formatted['release_date'], "2023-01-01")
    
    def test_format_api_change(self):
        """Test API change formatting for reports."""
        formatted = self.generator._format_api_change(self.change1)
        
        expected_keys = ['element', 'change_type', 'to_version', 'description']
        for key in expected_keys:
            self.assertIn(key, formatted)
        
        self.assertEqual(formatted['change_type'], "added")
        self.assertEqual(formatted['to_version'], "1.0.0")
    
    def test_create_summary_data(self):
        """Test summary data creation for templates."""
        summary = self.generator._create_summary_data(self.analysis_result)
        
        expected_keys = [
            'package_name', 'total_versions', 'total_changes', 
            'version_range', 'changes_by_type', 'apis_by_type'
        ]
        
        for key in expected_keys:
            self.assertIn(key, summary)
        
        self.assertEqual(summary['package_name'], "test-package")
        self.assertEqual(summary['total_versions'], 2)
        self.assertEqual(summary['total_changes'], 2)
    
    def test_html_template_rendering(self):
        """Test HTML template rendering with variables."""
        template = "<h1>{{title}}</h1><p>{{content}}</p>"
        variables = {"title": "Test Title", "content": "Test Content"}
        
        result = self.generator._render_template(template, variables)
        
        self.assertEqual(result, "<h1>Test Title</h1><p>Test Content</p>")
    
    def test_html_template_missing_variable(self):
        """Test HTML template rendering with missing variables."""
        template = "<h1>{{title}}</h1><p>{{missing}}</p>"
        variables = {"title": "Test Title"}
        
        result = self.generator._render_template(template, variables)
        
        # Missing variables should be left as-is or replaced with empty string
        self.assertIn("Test Title", result)
        # The exact behavior depends on implementation
    
    def test_escape_html_content(self):
        """Test HTML content escaping."""
        content_with_html = "<script>alert('xss')</script>"
        escaped = self.generator._escape_html(content_with_html)
        
        self.assertNotIn("<script>", escaped)
        self.assertIn("&lt;script&gt;", escaped)
    
    def test_generate_change_timeline(self):
        """Test change timeline generation for HTML reports."""
        timeline = self.generator._generate_change_timeline(self.analysis_result)
        
        self.assertIsInstance(timeline, list)
        self.assertEqual(len(timeline), 2)  # Two versions
        
        # Check structure
        for entry in timeline:
            self.assertIn('version', entry)
            self.assertIn('date', entry)
            self.assertIn('changes', entry)
    
    def test_generate_api_overview(self):
        """Test API overview generation."""
        overview = self.generator._generate_api_overview(self.analysis_result)
        
        self.assertIsInstance(overview, dict)
        self.assertIn('total_apis', overview)
        self.assertIn('by_type', overview)
        self.assertIn('by_version', overview)
    
    @patch('builtins.open', new_callable=mock_open)
    def test_save_report_file_error(self, mock_file):
        """Test error handling when saving report to file."""
        mock_file.side_effect = IOError("Permission denied")
        
        with self.assertRaises(IOError):
            self.generator.save_report(
                self.analysis_result, 
                "/invalid/path/report.json",
                format='json'
            )
    
    def test_empty_analysis_result(self):
        """Test report generation with empty analysis result."""
        empty_result = AnalysisResult(
            package_name="empty-package",
            versions=[],
            api_elements={},
            changes=[]
        )
        
        # Should not raise errors
        json_report = self.generator.generate_json_report(empty_result)
        html_report = self.generator.generate_html_report(empty_result)
        csv_report = self.generator.generate_csv_report(empty_result)
        md_report = self.generator.generate_markdown_report(empty_result)
        
        # Verify basic structure is still present
        self.assertIn("empty-package", json_report)
        self.assertIn("empty-package", html_report)
        self.assertIn("Element Name", csv_report)  # CSV header
        self.assertIn("empty-package", md_report)


if __name__ == '__main__':
    unittest.main()
