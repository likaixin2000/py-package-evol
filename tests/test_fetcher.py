"""Tests for PyPIFetcher."""

import unittest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime
import json
import requests

from pypevol.fetcher import PyPIFetcher
from pypevol.models import VersionInfo


class TestPyPIFetcher(unittest.TestCase):
    """Test PyPIFetcher class."""
    
    def setUp(self):
        """Set up test data."""
        self.fetcher = PyPIFetcher()
        
        # Mock PyPI response data
        self.mock_pypi_response = {
            "info": {
                "name": "test-package",
                "version": "1.2.0",
                "summary": "A test package",
                "author": "Test Author",
                "requires_python": ">=3.8"
            },
            "releases": {
                "1.0.0": [
                    {
                        "upload_time": "2023-01-01T00:00:00",
                        "python_version": "py3",
                        "packagetype": "bdist_wheel",
                        "url": "https://files.pythonhosted.org/test-1.0.0-py3-none-any.whl",
                        "yanked": False,
                        "requires_python": ">=3.8"
                    },
                    {
                        "upload_time": "2023-01-01T00:00:00",
                        "python_version": "source",
                        "packagetype": "sdist",
                        "url": "https://files.pythonhosted.org/test-1.0.0.tar.gz",
                        "yanked": False,
                        "requires_python": ">=3.8"
                    }
                ],
                "1.1.0": [
                    {
                        "upload_time": "2023-02-01T00:00:00",
                        "python_version": "py3",
                        "packagetype": "bdist_wheel",
                        "url": "https://files.pythonhosted.org/test-1.1.0-py3-none-any.whl",
                        "yanked": False,
                        "requires_python": ">=3.8"
                    }
                ],
                "1.2.0": [
                    {
                        "upload_time": "2023-03-01T00:00:00",
                        "python_version": "py3",
                        "packagetype": "bdist_wheel",
                        "url": "https://files.pythonhosted.org/test-1.2.0-py3-none-any.whl",
                        "yanked": True,
                        "yanked_reason": "Security issue",
                        "requires_python": ">=3.9"
                    }
                ]
            }
        }
    
    def test_init(self):
        """Test PyPIFetcher initialization."""
        fetcher = PyPIFetcher()
        self.assertIsNotNone(fetcher.session)
        self.assertEqual(fetcher.base_url, "https://pypi.org/pypi")
    
    def test_init_with_base_url(self):
        """Test PyPIFetcher initialization with custom base URL."""
        custom_url = "https://custom.pypi.org/pypi"
        fetcher = PyPIFetcher(base_url=custom_url)
        self.assertEqual(fetcher.base_url, custom_url)
    
    @patch('requests.Session.get')
    def test_get_package_info_success(self, mock_get):
        """Test successful package info retrieval."""
        # Mock successful response
        mock_response = Mock()
        mock_response.raise_for_status = Mock()
        mock_response.json.return_value = self.mock_pypi_response
        mock_get.return_value = mock_response
        
        # Execute
        result = self.fetcher.get_package_info("test-package")
        
        # Verify
        self.assertIsNotNone(result)
        self.assertEqual(result["info"]["name"], "test-package")
        mock_get.assert_called_once_with("https://pypi.org/pypi/test-package/json")
    
    @patch('requests.Session.get')
    def test_get_package_info_not_found(self, mock_get):
        """Test package info retrieval for non-existent package."""
        # Mock 404 response
        mock_response = Mock()
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError("404 Not Found")
        mock_get.return_value = mock_response
        
        # Execute
        result = self.fetcher.get_package_info("nonexistent-package")
        
        # Verify
        self.assertIsNone(result)
    
    @patch('requests.Session.get')
    def test_get_package_info_network_error(self, mock_get):
        """Test package info retrieval with network error."""
        # Mock network error
        mock_get.side_effect = requests.exceptions.RequestException("Network error")
        
        # Execute
        result = self.fetcher.get_package_info("test-package")
        
        # Verify
        self.assertIsNone(result)
    
    @patch.object(PyPIFetcher, 'get_package_info')
    def test_get_package_versions_success(self, mock_get_info):
        """Test successful package versions retrieval."""
        mock_get_info.return_value = self.mock_pypi_response
        
        # Execute without yanked versions
        versions = self.fetcher.get_package_versions("test-package", include_yanked=False)
        
        # Verify - should exclude yanked version 1.2.0
        self.assertEqual(len(versions), 2)
        version_numbers = [v.version for v in versions]
        self.assertIn("1.0.0", version_numbers)
        self.assertIn("1.1.0", version_numbers)
        self.assertNotIn("1.2.0", version_numbers)
    
    @patch.object(PyPIFetcher, 'get_package_info')
    def test_get_package_versions_include_yanked(self, mock_get_info):
        """Test package versions retrieval including yanked versions."""
        mock_get_info.return_value = self.mock_pypi_response
        
        # Execute with yanked versions
        versions = self.fetcher.get_package_versions("test-package", include_yanked=True)
        
        # Verify - should include yanked version 1.2.0
        self.assertEqual(len(versions), 3)
        version_numbers = [v.version for v in versions]
        self.assertIn("1.2.0", version_numbers)
        
        # Check yanked version properties
        yanked_version = next(v for v in versions if v.version == "1.2.0")
        self.assertTrue(yanked_version.yanked)
        self.assertEqual(yanked_version.yanked_reason, "Security issue")
    
    @patch.object(PyPIFetcher, 'get_package_info')
    def test_get_package_versions_no_package(self, mock_get_info):
        """Test package versions retrieval for non-existent package."""
        mock_get_info.return_value = None
        
        # Execute
        versions = self.fetcher.get_package_versions("nonexistent-package")
        
        # Verify
        self.assertEqual(versions, [])
    
    @patch.object(PyPIFetcher, 'get_package_versions')
    def test_get_version_range_all_versions(self, mock_get_versions):
        """Test getting version range without limits."""
        mock_versions = [
            VersionInfo(version="1.0.0", release_date=datetime(2023, 1, 1)),
            VersionInfo(version="1.1.0", release_date=datetime(2023, 2, 1)),
            VersionInfo(version="1.2.0", release_date=datetime(2023, 3, 1))
        ]
        mock_get_versions.return_value = mock_versions
        
        # Execute
        result = self.fetcher.get_version_range("test-package")
        
        # Verify
        self.assertEqual(len(result), 3)
        self.assertEqual(result, mock_versions)
    
    @patch.object(PyPIFetcher, 'get_package_versions')
    def test_get_version_range_with_limits(self, mock_get_versions):
        """Test getting version range with from/to version limits."""
        mock_versions = [
            VersionInfo(version="1.0.0", release_date=datetime(2023, 1, 1)),
            VersionInfo(version="1.1.0", release_date=datetime(2023, 2, 1)),
            VersionInfo(version="1.2.0", release_date=datetime(2023, 3, 1)),
            VersionInfo(version="2.0.0", release_date=datetime(2023, 4, 1))
        ]
        mock_get_versions.return_value = mock_versions
        
        # Execute
        result = self.fetcher.get_version_range(
            "test-package", 
            from_version="1.1.0", 
            to_version="1.2.0"
        )
        
        # Verify - should include 1.1.0 and 1.2.0, exclude 1.0.0 and 2.0.0
        self.assertEqual(len(result), 2)
        version_numbers = [v.version for v in result]
        self.assertIn("1.1.0", version_numbers)
        self.assertIn("1.2.0", version_numbers)
        self.assertNotIn("1.0.0", version_numbers)
        self.assertNotIn("2.0.0", version_numbers)
    
    @patch.object(PyPIFetcher, 'get_package_versions')
    def test_get_version_range_with_max_versions(self, mock_get_versions):
        """Test getting version range with max_versions limit."""
        mock_versions = [
            VersionInfo(version="1.0.0", release_date=datetime(2023, 1, 1)),
            VersionInfo(version="1.1.0", release_date=datetime(2023, 2, 1)),
            VersionInfo(version="1.2.0", release_date=datetime(2023, 3, 1)),
            VersionInfo(version="2.0.0", release_date=datetime(2023, 4, 1))
        ]
        mock_get_versions.return_value = mock_versions
        
        # Execute
        result = self.fetcher.get_version_range("test-package", max_versions=2)
        
        # Verify - should return latest 2 versions
        self.assertEqual(len(result), 2)
        version_numbers = [v.version for v in result]
        self.assertIn("1.2.0", version_numbers)
        self.assertIn("2.0.0", version_numbers)
    
    @patch.object(PyPIFetcher, 'get_package_versions')
    def test_get_version_info_success(self, mock_get_versions):
        """Test getting specific version info."""
        mock_versions = [
            VersionInfo(version="1.0.0", release_date=datetime(2023, 1, 1)),
            VersionInfo(version="1.1.0", release_date=datetime(2023, 2, 1))
        ]
        mock_get_versions.return_value = mock_versions
        
        # Execute
        result = self.fetcher.get_version_info("test-package", "1.1.0")
        
        # Verify
        self.assertIsNotNone(result)
        self.assertEqual(result.version, "1.1.0")
    
    @patch.object(PyPIFetcher, 'get_package_versions')
    def test_get_version_info_not_found(self, mock_get_versions):
        """Test getting non-existent version info."""
        mock_versions = [
            VersionInfo(version="1.0.0", release_date=datetime(2023, 1, 1))
        ]
        mock_get_versions.return_value = mock_versions
        
        # Execute
        result = self.fetcher.get_version_info("test-package", "2.0.0")
        
        # Verify
        self.assertIsNone(result)
    
    def test_parse_upload_time(self):
        """Test upload time parsing."""
        # Test valid ISO format
        date_str = "2023-01-01T12:00:00"
        result = self.fetcher._parse_upload_time(date_str)
        expected = datetime(2023, 1, 1, 12, 0, 0)
        self.assertEqual(result, expected)
        
        # Test invalid format
        invalid_date = "invalid-date"
        result = self.fetcher._parse_upload_time(invalid_date)
        self.assertIsNone(result)
        
        # Test None input
        result = self.fetcher._parse_upload_time(None)
        self.assertIsNone(result)
    
    def test_create_version_info(self):
        """Test VersionInfo creation from release data."""
        release_data = self.mock_pypi_response["releases"]["1.0.0"][0]  # wheel
        
        version_info = self.fetcher._create_version_info("1.0.0", [release_data])
        
        self.assertEqual(version_info.version, "1.0.0")
        self.assertEqual(version_info.release_date, datetime(2023, 1, 1))
        self.assertEqual(version_info.python_requires, ">=3.8")
        self.assertEqual(version_info.wheel_url, release_data["url"])
        self.assertFalse(version_info.yanked)
    
    def test_create_version_info_with_source(self):
        """Test VersionInfo creation with both wheel and source."""
        releases = self.mock_pypi_response["releases"]["1.0.0"]  # Both wheel and sdist
        
        version_info = self.fetcher._create_version_info("1.0.0", releases)
        
        # Should prefer wheel but also set source_url
        self.assertIsNotNone(version_info.wheel_url)
        self.assertIsNotNone(version_info.source_url)
        self.assertTrue(version_info.wheel_url.endswith(".whl"))
        self.assertTrue(version_info.source_url.endswith(".tar.gz"))
    
    def test_create_version_info_yanked(self):
        """Test VersionInfo creation for yanked version."""
        release_data = self.mock_pypi_response["releases"]["1.2.0"][0]  # yanked
        
        version_info = self.fetcher._create_version_info("1.2.0", [release_data])
        
        self.assertTrue(version_info.yanked)
        self.assertEqual(version_info.yanked_reason, "Security issue")
    
    def test_version_comparison(self):
        """Test version comparison logic."""
        from packaging import version
        
        # Test that we can compare versions correctly
        v1 = version.parse("1.0.0")
        v2 = version.parse("1.1.0")
        v3 = version.parse("2.0.0")
        
        self.assertTrue(v1 < v2 < v3)
        self.assertTrue(v2 >= v1)
        self.assertTrue(v3 > v2)
    
    def test_filter_versions_by_range(self):
        """Test version filtering by range."""
        versions = [
            VersionInfo(version="0.9.0", release_date=datetime(2022, 12, 1)),
            VersionInfo(version="1.0.0", release_date=datetime(2023, 1, 1)),
            VersionInfo(version="1.1.0", release_date=datetime(2023, 2, 1)),
            VersionInfo(version="1.2.0", release_date=datetime(2023, 3, 1)),
            VersionInfo(version="2.0.0", release_date=datetime(2023, 4, 1))
        ]
        
        # Filter by range
        filtered = self.fetcher._filter_versions_by_range(
            versions, 
            from_version="1.0.0", 
            to_version="1.2.0"
        )
        
        # Should include 1.0.0, 1.1.0, 1.2.0
        self.assertEqual(len(filtered), 3)
        version_numbers = [v.version for v in filtered]
        self.assertIn("1.0.0", version_numbers)
        self.assertIn("1.1.0", version_numbers)
        self.assertIn("1.2.0", version_numbers)
        self.assertNotIn("0.9.0", version_numbers)
        self.assertNotIn("2.0.0", version_numbers)
    
    def test_get_latest_versions(self):
        """Test getting latest N versions."""
        versions = [
            VersionInfo(version="1.0.0", release_date=datetime(2023, 1, 1)),
            VersionInfo(version="1.1.0", release_date=datetime(2023, 2, 1)),
            VersionInfo(version="1.2.0", release_date=datetime(2023, 3, 1)),
            VersionInfo(version="2.0.0", release_date=datetime(2023, 4, 1))
        ]
        
        # Get latest 2 versions
        latest = self.fetcher._get_latest_versions(versions, 2)
        
        self.assertEqual(len(latest), 2)
        version_numbers = [v.version for v in latest]
        self.assertIn("1.2.0", version_numbers)
        self.assertIn("2.0.0", version_numbers)


if __name__ == '__main__':
    unittest.main()
