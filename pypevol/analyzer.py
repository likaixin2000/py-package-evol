"""Main package analyzer for PyPevol."""

import logging
from pathlib import Path
from typing import List, Optional, Dict, Set, Tuple
from datetime import datetime
import tempfile
import shutil

from .models import APIElement, VersionInfo, AnalysisResult, APIChange, ChangeType
from .fetcher import PyPIFetcher
from .parser import SourceParser

logger = logging.getLogger(__name__)


class PackageAnalyzer:
    """Main analyzer for package API evolution."""

    def __init__(
        self,
        cache_dir: Optional[Path] = None,
        include_private: bool = False,
        include_deprecated: bool = True,
        prefer_wheels: bool = True,
        include_yanked: bool = False,
    ):
        """Initialize the package analyzer.

        Args:
            cache_dir: Directory to cache downloaded files
            include_private: Whether to include private APIs
            include_deprecated: Whether to include deprecated APIs
            prefer_wheels: Whether to prefer wheel files over source distributions
            include_yanked: Whether to include yanked versions in analysis
        """
        self.fetcher = PyPIFetcher(cache_dir)
        self.parser = SourceParser(include_private, include_deprecated)
        self.prefer_wheels = prefer_wheels
        self.include_yanked = include_yanked
        self.temp_dirs = []  # Track temp directories for cleanup

    def get_package_versions(
        self, package_name: str, include_yanked: bool = False
    ) -> List[VersionInfo]:
        """Get all available version information for a package.

        Args:
            package_name: Name of the package
            include_yanked: Whether to include yanked versions

        Returns:
            List of VersionInfo objects for all available versions
        """
        logger.info(f"Fetching version information for package: {package_name}")

        try:
            version_infos = self.fetcher.get_version_range(
                package_name,
                from_version=None,
                to_version=None,
                max_versions=None,
                include_yanked=include_yanked,
            )

            logger.info(f"Found {len(version_infos)} versions for {package_name}")
            return version_infos

        except Exception as e:
            logger.error(f"Failed to fetch version information for {package_name}: {e}")
            raise

    def analyze_package(
        self,
        package_name: str,
        from_version: Optional[str] = None,
        to_version: Optional[str] = None,
        max_versions: Optional[int] = None,
        versions: Optional[List[str]] = None,
        from_date: Optional[datetime] = None,
        to_date: Optional[datetime] = None,
    ) -> AnalysisResult:
        """Analyze the API evolution of a package.

        Args:
            package_name: Name of the package to analyze
            from_version: Starting version (inclusive). Mutually exclusive with versions.
            to_version: Ending version (inclusive). Mutually exclusive with versions.
            max_versions: Maximum number of versions to analyze. Mutually exclusive with versions.
            versions: Specific list of version names to analyze. Mutually exclusive with from_version/to_version/max_versions.
            from_date: Starting date (inclusive). Filters versions released on or after this date.
            to_date: Ending date (inclusive). Filters versions released on or before this date.

        Returns:
            AnalysisResult containing the evolution data

        Raises:
            ValueError: If both versions and from_version/to_version/max_versions are specified
        """
        logger.info(f"Starting analysis of package: {package_name}")

        # Validate parameter combinations
        if versions is not None and (
            from_version is not None
            or to_version is not None
            or max_versions is not None
        ):
            raise ValueError(
                "Cannot specify 'versions' parameter together with 'from_version', 'to_version', or 'max_versions'"
            )

        try:
            # Get version information
            if versions is not None:
                # Use specific versions
                version_infos = self.fetcher.get_specific_versions(
                    package_name, versions, include_yanked=self.include_yanked
                )
            else:
                # Use version range or all versions
                version_infos = self.fetcher.get_version_range(
                    package_name,
                    from_version,
                    to_version,
                    max_versions,
                    include_yanked=self.include_yanked,
                )

            # Apply date filtering
            if from_date is not None or to_date is not None:
                version_infos = self._filter_versions_by_date(
                    version_infos, from_date, to_date
                )

            if not version_infos:
                logger.error(f"No versions found for package {package_name}")
                return AnalysisResult(
                    package_name=package_name, versions=[], api_elements={}, changes=[]
                )

            logger.info(f"Found {len(version_infos)} versions to analyze")

            # Analyze each version
            api_elements = {}
            successful_versions = []

            for version_info in version_infos:
                logger.info(f"Analyzing version {version_info.version}")

                try:
                    elements = self._analyze_version(package_name, version_info)
                    if elements is not None:
                        api_elements[version_info.version] = elements
                        successful_versions.append(version_info)
                        logger.info(
                            f"Found {len(elements)} API elements in version {version_info.version}"
                        )
                    else:
                        logger.warning(
                            f"Failed to analyze version {version_info.version}"
                        )

                except Exception as e:
                    logger.error(f"Error analyzing version {version_info.version}: {e}")
                    continue

            if not successful_versions:
                logger.error(
                    f"No versions could be successfully analyzed for {package_name}"
                )
                return AnalysisResult(
                    package_name=package_name,
                    versions=version_infos,
                    api_elements={},
                    changes=[],
                )

            # Calculate API changes
            logger.info("Calculating API changes...")
            changes = self._calculate_changes(successful_versions, api_elements)

            logger.info(f"Analysis complete. Found {len(changes)} API changes.")

            return AnalysisResult(
                package_name=package_name,
                versions=successful_versions,
                api_elements=api_elements,
                changes=changes,
                metadata={
                    "total_versions_attempted": len(version_infos),
                    "successful_versions": len(successful_versions),
                    "analysis_settings": {
                        "include_private": self.parser.include_private,
                        "include_deprecated": self.parser.include_deprecated,
                        "prefer_wheels": self.prefer_wheels,
                        "include_yanked": self.include_yanked,
                    },
                },
            )

        except Exception as e:
            logger.error(f"Analysis failed for {package_name}: {e}")
            raise

        finally:
            self._cleanup()

    def _filter_versions_by_date(
        self,
        version_infos: List[VersionInfo],
        from_date: Optional[datetime],
        to_date: Optional[datetime],
    ) -> List[VersionInfo]:
        """Filter version information by release date.

        Args:
            version_infos: List of version information to filter
            from_date: Starting date (inclusive). None means no lower bound.
            to_date: Ending date (inclusive). None means no upper bound.

        Returns:
            Filtered list of version information
        """
        if from_date is None and to_date is None:
            return version_infos

        filtered_versions = []

        for version_info in version_infos:
            # Skip versions without release date if date filtering is requested
            if version_info.release_date is None:
                logger.warning(
                    f"Version {version_info.version} has no release date, skipping in date filter"
                )
                continue

            # Check date bounds
            if from_date is not None and version_info.release_date < from_date:
                continue
            if to_date is not None and version_info.release_date > to_date:
                continue

            filtered_versions.append(version_info)

        logger.info(
            f"Date filtering reduced versions from {len(version_infos)} to {len(filtered_versions)}"
        )
        return filtered_versions

    def _analyze_version(
        self, package_name: str, version_info: VersionInfo
    ) -> Optional[List[APIElement]]:
        """Analyze a specific version of a package.

        Args:
            package_name: Name of the package
            version_info: Version information

        Returns:
            List of API elements or None if analysis failed
        """
        try:
            # Download and extract the package
            result = self.fetcher.download_and_extract_version(
                package_name, version_info.version, self.prefer_wheels
            )

            if not result:
                return None

            extracted_path, _ = result
            self.temp_dirs.append(extracted_path)

            # Find the actual package directory
            package_dir = self._find_package_directory(extracted_path, package_name)
            if not package_dir:
                logger.warning(
                    f"Could not find package directory for {package_name} {version_info.version}"
                )
                return []

            # Parse the package
            api_elements = self.parser.parse_package(package_dir, package_name)

            return api_elements

        except Exception as e:
            logger.error(f"Failed to analyze version {version_info.version}: {e}")
            return None

    def _find_package_directory(
        self, extracted_path: Path, package_name: str
    ) -> Optional[Path]:
        """Find the actual package directory within an extracted archive.

        Args:
            extracted_path: Path to the extracted archive
            package_name: Name of the package

        Returns:
            Path to the package directory or None if not found
        """
        # Common patterns for package directories
        candidates = [
            extracted_path / package_name,
            extracted_path / package_name.replace("-", "_"),
            extracted_path / package_name.replace("_", "-"),
        ]

        # Look for existing candidates
        for candidate in candidates:
            if candidate.exists() and candidate.is_dir():
                # Check if it contains Python files or __init__.py
                if self._is_python_package(candidate):
                    return candidate

        # Search recursively
        for item in extracted_path.rglob("*"):
            if item.is_dir() and item.name in [
                package_name,
                package_name.replace("-", "_"),
                package_name.replace("_", "-"),
            ]:
                if self._is_python_package(item):
                    return item

        # Look for any directory with Python files
        for item in extracted_path.iterdir():
            if item.is_dir() and not item.name.startswith("."):
                if self._is_python_package(item):
                    return item

        # Fallback: return the extracted path itself if it contains Python files
        if self._is_python_package(extracted_path):
            return extracted_path

        return None

    def _is_python_package(self, path: Path) -> bool:
        """Check if a directory contains Python code.

        Args:
            path: Path to check

        Returns:
            True if the directory contains Python files
        """
        if not path.is_dir():
            return False

        # Check for __init__.py
        if (path / "__init__.py").exists():
            return True

        # Check for any .py files
        for item in path.iterdir():
            if item.suffix == ".py":
                return True

        # Check recursively (but not too deep)
        for item in path.iterdir():
            if item.is_dir() and not item.name.startswith("."):
                if (item / "__init__.py").exists():
                    return True

        return False

    def _calculate_changes(
        self, versions: List[VersionInfo], api_elements: Dict[str, List[APIElement]]
    ) -> List[APIChange]:
        """Calculate API changes between versions.

        Args:
            versions: List of version information
            api_elements: Dictionary mapping version to API elements

        Returns:
            List of API changes
        """
        changes = []

        # Sort versions chronologically
        sorted_versions = sorted(versions, key=lambda v: v.release_date or datetime.min)

        for i in range(len(sorted_versions)):
            current_version = sorted_versions[i].version
            current_apis = {
                self._get_api_key(api): api
                for api in api_elements.get(current_version, [])
            }

            if i == 0:
                # First version - all APIs are new
                for api in current_apis.values():
                    changes.append(
                        APIChange(
                            element=api,
                            change_type=ChangeType.ADDED,
                            to_version=current_version,
                            description=f"API introduced in version {current_version}",
                        )
                    )
            else:
                # Compare with previous version
                previous_version = sorted_versions[i - 1].version
                previous_apis = {
                    self._get_api_key(api): api
                    for api in api_elements.get(previous_version, [])
                }

                # Find added APIs
                for api_key, api in current_apis.items():
                    if api_key not in previous_apis:
                        changes.append(
                            APIChange(
                                element=api,
                                change_type=ChangeType.ADDED,
                                from_version=previous_version,
                                to_version=current_version,
                                description=f"API added in version {current_version}",
                            )
                        )

                # Find removed APIs
                for api_key, api in previous_apis.items():
                    if api_key not in current_apis:
                        changes.append(
                            APIChange(
                                element=api,
                                change_type=ChangeType.REMOVED,
                                from_version=previous_version,
                                to_version=current_version,
                                description=f"API removed in version {current_version}",
                            )
                        )

                # Find modified APIs
                for api_key, current_api in current_apis.items():
                    if api_key in previous_apis:
                        previous_api = previous_apis[api_key]

                        # Compare signatures
                        if current_api.signature != previous_api.signature:
                            changes.append(
                                APIChange(
                                    element=current_api,
                                    change_type=ChangeType.MODIFIED,
                                    from_version=previous_version,
                                    to_version=current_version,
                                    old_signature=previous_api.signature,
                                    new_signature=current_api.signature,
                                    description=f"API signature changed in version {current_version}",
                                )
                            )

                        # Check for deprecation changes
                        if not previous_api.is_deprecated and current_api.is_deprecated:
                            changes.append(
                                APIChange(
                                    element=current_api,
                                    change_type=ChangeType.DEPRECATED,
                                    from_version=previous_version,
                                    to_version=current_version,
                                    description=f"API deprecated in version {current_version}",
                                )
                            )

        return changes

    def _get_api_key(self, api: APIElement) -> str:
        """Get a unique key for an API element.

        Args:
            api: API element

        Returns:
            Unique key string
        """
        return f"{api.module_path}.{api.name}.{api.type.value}"

    def _cleanup(self):
        """Clean up temporary directories."""
        for temp_dir in self.temp_dirs:
            try:
                if temp_dir.exists():
                    shutil.rmtree(temp_dir)
                    logger.debug(f"Cleaned up temporary directory: {temp_dir}")
            except Exception as e:
                logger.warning(f"Failed to clean up {temp_dir}: {e}")

        self.temp_dirs.clear()
        self.fetcher.cleanup_temp_files()

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self._cleanup()
