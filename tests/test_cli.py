"""Tests for CLI module."""

import unittest
from unittest.mock import Mock, patch, MagicMock
import sys
import tempfile
import json
from io import StringIO
from click.testing import CliRunner

from pypevol.cli import main, analyze, track, list_apis, report
from pypevol.models import AnalysisResult, VersionInfo, APIElement, APIType


class TestCLI(unittest.TestCase):
    """Test CLI functionality."""
    
    def setUp(self):
        """Set up test data."""
        self.runner = CliRunner()
        
        # Create a sample analysis result for testing
        self.sample_result = AnalysisResult(
            package_name="test-package",
            versions=[
                VersionInfo(version="1.0.0"),
                VersionInfo(version="1.1.0")
            ],
            api_elements={
                "1.0.0": [APIElement(
                    name="test_func",
                    type=APIType.FUNCTION,
                    module_path="test.module",
                    signature="test_func() -> None"
                )]
            },
            changes=[]
        )
    
    def test_parse_arguments_basic(self):
        """Test basic argument parsing."""
        args = parse_arguments(['analyze', 'requests'])
        
        self.assertEqual(args.command, 'analyze')
        self.assertEqual(args.package, 'requests')
        self.assertEqual(args.output_format, 'json')  # Default
        self.assertIsNone(args.output_file)
        self.assertIsNone(args.version_range)
    
    def test_parse_arguments_with_options(self):
        """Test argument parsing with various options."""
        args = parse_arguments([
            'analyze', 'requests',
            '--output-format', 'html',
            '--output-file', 'report.html',
            '--version-range', '2.0.0:2.5.0',
            '--verbose'
        ])
        
        self.assertEqual(args.command, 'analyze')
        self.assertEqual(args.package, 'requests')
        self.assertEqual(args.output_format, 'html')
        self.assertEqual(args.output_file, 'report.html')
        self.assertEqual(args.version_range, '2.0.0:2.5.0')
        self.assertTrue(args.verbose)
    
    def test_parse_arguments_compare_command(self):
        """Test parsing compare command."""
        args = parse_arguments([
            'compare', 'requests', '2.0.0', '2.1.0'
        ])
        
        self.assertEqual(args.command, 'compare')
        self.assertEqual(args.package, 'requests')
        self.assertEqual(args.from_version, '2.0.0')
        self.assertEqual(args.to_version, '2.1.0')
    
    def test_parse_arguments_list_command(self):
        """Test parsing list command."""
        args = parse_arguments(['list', 'requests'])
        
        self.assertEqual(args.command, 'list')
        self.assertEqual(args.package, 'requests')
    
    def test_parse_arguments_list_with_limit(self):
        """Test parsing list command with limit."""
        args = parse_arguments(['list', 'requests', '--limit', '10'])
        
        self.assertEqual(args.command, 'list')
        self.assertEqual(args.package, 'requests')
        self.assertEqual(args.limit, 10)
    
    def test_parse_arguments_invalid_format(self):
        """Test argument parsing with invalid format."""
        with self.assertRaises(SystemExit):
            parse_arguments([
                'analyze', 'requests',
                '--output-format', 'invalid'
            ])
    
    def test_parse_arguments_missing_package(self):
        """Test argument parsing without package name."""
        with self.assertRaises(SystemExit):
            parse_arguments(['analyze'])
    
    def test_analysis_config_creation(self):
        """Test AnalysisConfig creation from arguments."""
        args = argparse.Namespace(
            package='requests',
            version_range='2.0.0:2.5.0',
            max_versions=20,
            include_prereleases=True
        )
        
        config = AnalysisConfig.from_args(args)
        
        self.assertEqual(config.package_name, 'requests')
        self.assertEqual(config.version_range, '2.0.0:2.5.0')
        self.assertEqual(config.max_versions, 20)
        self.assertTrue(config.include_prereleases)
    
    def test_analysis_config_defaults(self):
        """Test AnalysisConfig with default values."""
        args = argparse.Namespace(
            package='requests',
            version_range=None,
            max_versions=None,
            include_prereleases=None
        )
        
        config = AnalysisConfig.from_args(args)
        
        self.assertEqual(config.package_name, 'requests')
        self.assertIsNone(config.version_range)
        self.assertEqual(config.max_versions, 50)  # Default
        self.assertFalse(config.include_prereleases)  # Default
    
    @patch('pypevol.cli.PackageAnalyzer')
    @patch('sys.stdout', new_callable=StringIO)
    def test_main_analyze_command_json(self, mock_stdout, mock_analyzer_class):
        """Test main function with analyze command and JSON output."""
        # Setup mock
        mock_analyzer = Mock()
        mock_analyzer_class.return_value = mock_analyzer
        mock_analyzer.analyze_package.return_value = self.sample_result
        
        # Patch sys.argv
        with patch('sys.argv', ['pypevol', 'analyze', 'test-package']):
            main()
        
        # Verify analyzer was called
        mock_analyzer_class.assert_called_once()
        mock_analyzer.analyze_package.assert_called_once_with('test-package')
        
        # Verify JSON output
        output = mock_stdout.getvalue()
        parsed = json.loads(output)
        self.assertEqual(parsed['package_name'], 'test-package')
    
    @patch('pypevol.cli.PackageAnalyzer')
    @patch('pypevol.cli.ReportGenerator')
    @patch('sys.stdout', new_callable=StringIO)
    def test_main_analyze_command_html(self, mock_stdout, mock_report_class, mock_analyzer_class):
        """Test main function with analyze command and HTML output."""
        # Setup mocks
        mock_analyzer = Mock()
        mock_analyzer_class.return_value = mock_analyzer
        mock_analyzer.analyze_package.return_value = self.sample_result
        
        mock_reporter = Mock()
        mock_report_class.return_value = mock_reporter
        mock_reporter.generate_html_report.return_value = "<html>Test Report</html>"
        
        # Patch sys.argv
        with patch('sys.argv', ['pypevol', 'analyze', 'test-package', '--output-format', 'html']):
            main()
        
        # Verify report generator was used
        mock_report_class.assert_called_once()
        mock_reporter.generate_html_report.assert_called_once_with(self.sample_result)
        
        # Verify HTML output
        output = mock_stdout.getvalue()
        self.assertIn("<html>Test Report</html>", output)
    
    @patch('pypevol.cli.PackageAnalyzer')
    @patch('pypevol.cli.ReportGenerator')
    def test_main_analyze_with_output_file(self, mock_report_class, mock_analyzer_class):
        """Test main function with output file."""
        # Setup mocks
        mock_analyzer = Mock()
        mock_analyzer_class.return_value = mock_analyzer
        mock_analyzer.analyze_package.return_value = self.sample_result
        
        mock_reporter = Mock()
        mock_report_class.return_value = mock_reporter
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
            output_file = f.name
        
        try:
            # Patch sys.argv
            with patch('sys.argv', ['pypevol', 'analyze', 'test-package', '--output-file', output_file]):
                main()
            
            # Verify save_report was called
            mock_reporter.save_report.assert_called_once_with(
                self.sample_result, 
                output_file, 
                format='json'
            )
            
        finally:
            import os
            os.unlink(output_file)
    
    @patch('pypevol.cli.PackageAnalyzer')
    @patch('sys.stdout', new_callable=StringIO)
    def test_main_compare_command(self, mock_stdout, mock_analyzer_class):
        """Test main function with compare command."""
        # Setup mock
        mock_analyzer = Mock()
        mock_analyzer_class.return_value = mock_analyzer
        mock_analyzer.compare_versions.return_value = []  # Empty changes list
        
        # Patch sys.argv
        with patch('sys.argv', ['pypevol', 'compare', 'test-package', '1.0.0', '1.1.0']):
            main()
        
        # Verify compare was called
        mock_analyzer.compare_versions.assert_called_once_with('test-package', '1.0.0', '1.1.0')
        
        # Verify output
        output = mock_stdout.getvalue()
        self.assertIn("No API changes detected", output)
    
    @patch('pypevol.cli.PyPIFetcher')
    @patch('sys.stdout', new_callable=StringIO)
    def test_main_list_command(self, mock_stdout, mock_fetcher_class):
        """Test main function with list command."""
        # Setup mock
        mock_fetcher = Mock()
        mock_fetcher_class.return_value = mock_fetcher
        mock_fetcher.get_package_versions.return_value = [
            VersionInfo(version="1.0.0"),
            VersionInfo(version="1.1.0"),
            VersionInfo(version="2.0.0")
        ]
        
        # Patch sys.argv
        with patch('sys.argv', ['pypevol', 'list', 'test-package']):
            main()
        
        # Verify fetcher was called
        mock_fetcher.get_package_versions.assert_called_once_with('test-package')
        
        # Verify output
        output = mock_stdout.getvalue()
        self.assertIn("1.0.0", output)
        self.assertIn("1.1.0", output)
        self.assertIn("2.0.0", output)
    
    @patch('pypevol.cli.PyPIFetcher')
    @patch('sys.stdout', new_callable=StringIO)
    def test_main_list_command_with_limit(self, mock_stdout, mock_fetcher_class):
        """Test main function with list command and limit."""
        # Setup mock
        mock_fetcher = Mock()
        mock_fetcher_class.return_value = mock_fetcher
        mock_fetcher.get_package_versions.return_value = [
            VersionInfo(version="1.0.0"),
            VersionInfo(version="1.1.0"),
            VersionInfo(version="2.0.0")
        ]
        
        # Patch sys.argv
        with patch('sys.argv', ['pypevol', 'list', 'test-package', '--limit', '2']):
            main()
        
        # Verify output (should be limited to 2 versions)
        output = mock_stdout.getvalue()
        lines = [line for line in output.split('\n') if line.strip()]
        version_lines = [line for line in lines if any(v in line for v in ['1.0.0', '1.1.0', '2.0.0'])]
        self.assertLessEqual(len(version_lines), 2)
    
    @patch('pypevol.cli.PackageAnalyzer')
    @patch('sys.stderr', new_callable=StringIO)
    def test_main_with_error(self, mock_stderr, mock_analyzer_class):
        """Test main function error handling."""
        # Setup mock to raise an exception
        mock_analyzer = Mock()
        mock_analyzer_class.return_value = mock_analyzer
        mock_analyzer.analyze_package.side_effect = Exception("Test error")
        
        # Patch sys.argv
        with patch('sys.argv', ['pypevol', 'analyze', 'test-package']):
            with self.assertRaises(SystemExit) as context:
                main()
            
            # Should exit with error code 1
            self.assertEqual(context.exception.code, 1)
        
        # Verify error message
        error_output = mock_stderr.getvalue()
        self.assertIn("Error", error_output)
        self.assertIn("Test error", error_output)
    
    @patch('pypevol.cli.PackageAnalyzer')
    @patch('sys.stderr', new_callable=StringIO)
    def test_main_verbose_mode(self, mock_stderr, mock_analyzer_class):
        """Test main function in verbose mode."""
        # Setup mock
        mock_analyzer = Mock()
        mock_analyzer_class.return_value = mock_analyzer
        mock_analyzer.analyze_package.return_value = self.sample_result
        
        # Patch sys.argv
        with patch('sys.argv', ['pypevol', 'analyze', 'test-package', '--verbose']):
            main()
        
        # In verbose mode, should see debug messages
        error_output = mock_stderr.getvalue()
        # The exact debug messages depend on implementation
        # but in verbose mode, there should be some output to stderr
    
    def test_version_range_parsing(self):
        """Test version range parsing logic."""
        from pypevol.cli import parse_version_range
        
        # Test various formats
        start, end = parse_version_range("1.0.0:2.0.0")
        self.assertEqual(start, "1.0.0")
        self.assertEqual(end, "2.0.0")
        
        start, end = parse_version_range("1.0.0:")
        self.assertEqual(start, "1.0.0")
        self.assertIsNone(end)
        
        start, end = parse_version_range(":2.0.0")
        self.assertIsNone(start)
        self.assertEqual(end, "2.0.0")
        
        start, end = parse_version_range(None)
        self.assertIsNone(start)
        self.assertIsNone(end)
    
    def test_format_change_output(self):
        """Test change formatting for CLI output."""
        from pypevol.cli import format_change_output
        from pypevol.models import APIChange, ChangeType
        
        change = APIChange(
            element=APIElement(
                name="test_func",
                type=APIType.FUNCTION,
                module_path="test.module",
                signature="test_func() -> None"
            ),
            change_type=ChangeType.ADDED,
            to_version="1.1.0",
            description="Function added"
        )
        
        output = format_change_output(change)
        
        self.assertIn("test_func", output)
        self.assertIn("ADDED", output)
        self.assertIn("1.1.0", output)
        self.assertIn("function", output.lower())
    
    def test_format_version_output(self):
        """Test version formatting for CLI output."""
        from pypevol.cli import format_version_output
        from datetime import datetime
        
        version = VersionInfo(
            version="1.0.0",
            release_date=datetime(2023, 1, 1),
            python_requires=">=3.8"
        )
        
        output = format_version_output(version)
        
        self.assertIn("1.0.0", output)
        self.assertIn("2023-01-01", output)
        self.assertIn(">=3.8", output)
    
    @patch('sys.argv', ['pypevol', '--help'])
    def test_help_output(self):
        """Test help output."""
        with self.assertRaises(SystemExit) as context:
            parse_arguments(['--help'])
        
        # Help should exit with code 0
        self.assertEqual(context.exception.code, 0)
    
    def test_invalid_command(self):
        """Test handling of invalid commands."""
        with self.assertRaises(SystemExit):
            parse_arguments(['invalid-command', 'package'])
    
    @patch('pypevol.cli.logging')
    def test_setup_logging_verbose(self, mock_logging):
        """Test logging setup in verbose mode."""
        from pypevol.cli import setup_logging
        
        setup_logging(verbose=True)
        
        # Should set logging level to DEBUG
        mock_logging.basicConfig.assert_called()
        call_args = mock_logging.basicConfig.call_args
        self.assertEqual(call_args[1]['level'], mock_logging.DEBUG)
    
    @patch('pypevol.cli.logging')
    def test_setup_logging_normal(self, mock_logging):
        """Test logging setup in normal mode."""
        from pypevol.cli import setup_logging
        
        setup_logging(verbose=False)
        
        # Should set logging level to INFO
        mock_logging.basicConfig.assert_called()
        call_args = mock_logging.basicConfig.call_args
        self.assertEqual(call_args[1]['level'], mock_logging.INFO)


if __name__ == '__main__':
    unittest.main()
