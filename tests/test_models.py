"""Tests for PyPevol models."""

import unittest
from datetime import datetime
from pypevol.models import (
    APIElement,
    APIType,
    VersionInfo,
    AnalysisResult,
    APIChange,
    ChangeType,
)


class TestAPIElement(unittest.TestCase):
    """Test APIElement class."""

    def test_create_api_element(self):
        """Test creating an API element."""
        element = APIElement(
            name="test_function",
            type=APIType.FUNCTION,
            module_path="test.module",
            signature="test_function(arg1: str, arg2: int = 5) -> bool",
        )

        self.assertEqual(element.name, "test_function")
        self.assertEqual(element.type, APIType.FUNCTION)
        self.assertEqual(element.module_path, "test.module")
        self.assertEqual(element.full_name, "test.module.test_function")
        self.assertFalse(element.is_private)

    def test_private_api_detection(self):
        """Test private API detection."""
        private_element = APIElement(
            name="_private_function", type=APIType.FUNCTION, module_path="test.module"
        )

        self.assertTrue(private_element.is_private)

        magic_element = APIElement(
            name="__magic_method__", type=APIType.METHOD, module_path="test.module"
        )

        self.assertFalse(
            magic_element.is_private
        )  # Magic methods are not considered private

    def test_to_dict(self):
        """Test converting API element to dictionary."""
        element = APIElement(
            name="test_function",
            type=APIType.FUNCTION,
            module_path="test.module",
            docstring="Test function docstring",
        )

        data = element.to_dict()

        self.assertEqual(data["name"], "test_function")
        self.assertEqual(data["type"], "function")
        self.assertEqual(data["module_path"], "test.module")
        self.assertEqual(data["docstring"], "Test function docstring")
        self.assertEqual(data["full_name"], "test.module.test_function")


class TestVersionInfo(unittest.TestCase):
    """Test VersionInfo class."""

    def test_create_version_info(self):
        """Test creating version info."""
        release_date = datetime(2023, 1, 15)
        version = VersionInfo(
            version="1.2.3",
            release_date=release_date,
            python_requires=">=3.8",
            dependencies=["requests>=2.0", "click>=8.0"],
        )

        self.assertEqual(version.version, "1.2.3")
        self.assertEqual(version.release_date, release_date)
        self.assertEqual(version.python_requires, ">=3.8")
        self.assertEqual(len(version.dependencies), 2)

    def test_to_dict(self):
        """Test converting version info to dictionary."""
        release_date = datetime(2023, 1, 15)
        version = VersionInfo(version="1.2.3", release_date=release_date)

        data = version.to_dict()

        self.assertEqual(data["version"], "1.2.3")
        self.assertEqual(data["release_date"], "2023-01-15T00:00:00")


class TestAnalysisResult(unittest.TestCase):
    """Test AnalysisResult class."""

    def setUp(self):
        """Set up test data."""
        self.version1 = VersionInfo(version="1.0.0", release_date=datetime(2023, 1, 1))
        self.version2 = VersionInfo(version="1.1.0", release_date=datetime(2023, 2, 1))

        self.api1 = APIElement(name="func1", type=APIType.FUNCTION, module_path="test")
        self.api2 = APIElement(name="func2", type=APIType.FUNCTION, module_path="test")

        self.change1 = APIChange(
            element=self.api1, change_type=ChangeType.ADDED, to_version="1.0.0"
        )
        self.change2 = APIChange(
            element=self.api2, change_type=ChangeType.ADDED, to_version="1.1.0"
        )

        self.result = AnalysisResult(
            package_name="test-package",
            versions=[self.version1, self.version2],
            api_elements={"1.0.0": [self.api1], "1.1.0": [self.api1, self.api2]},
            changes=[self.change1, self.change2],
        )

    def test_get_api_changes_filter_by_type(self):
        """Test filtering API changes by change type."""
        added_changes = self.result.get_api_changes(change_types=[ChangeType.ADDED])

        self.assertEqual(len(added_changes), 2)
        self.assertTrue(all(c.change_type == ChangeType.ADDED for c in added_changes))

    def test_get_api_changes_filter_by_api_type(self):
        """Test filtering API changes by API type."""
        function_changes = self.result.get_api_changes(api_types=[APIType.FUNCTION])

        self.assertEqual(len(function_changes), 2)
        self.assertTrue(
            all(c.element.type == APIType.FUNCTION for c in function_changes)
        )

    def test_get_version_apis(self):
        """Test getting APIs for a specific version."""
        v1_apis = self.result.get_version_apis("1.0.0")
        v2_apis = self.result.get_version_apis("1.1.0")

        self.assertEqual(len(v1_apis), 1)
        self.assertEqual(len(v2_apis), 2)
        self.assertEqual(v1_apis[0].name, "func1")

    def test_get_api_lifecycle(self):
        """Test getting API lifecycle information."""
        lifecycle = self.result.get_api_lifecycle("func1")

        self.assertEqual(lifecycle["name"], "func1")
        self.assertEqual(lifecycle["introduced_in"], "1.0.0")
        self.assertIsNone(lifecycle["removed_in"])
        self.assertEqual(
            len(lifecycle["versions_present"]), 2
        )  # Present in both versions

    def test_generate_summary(self):
        """Test generating analysis summary."""
        summary = self.result.generate_summary()

        self.assertEqual(summary["package_name"], "test-package")
        self.assertEqual(summary["total_versions"], 2)
        self.assertEqual(summary["total_changes"], 2)
        self.assertEqual(summary["change_types"]["added"], 2)
        # func1 appears in 2 versions + func2 appears in 1 version = 3 total API occurrences
        self.assertEqual(summary["api_types"]["function"], 3)

    def test_to_dict(self):
        """Test converting analysis result to dictionary."""
        data = self.result.to_dict()

        self.assertEqual(data["package_name"], "test-package")
        self.assertEqual(len(data["versions"]), 2)
        self.assertEqual(len(data["changes"]), 2)
        self.assertIn("summary", data)

    def test_to_json(self):
        """Test converting analysis result to JSON."""
        json_str = self.result.to_json()

        self.assertIsInstance(json_str, str)
        self.assertIn('"package_name": "test-package"', json_str)


if __name__ == "__main__":
    unittest.main()
