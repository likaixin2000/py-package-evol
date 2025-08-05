"""PyPI package fetcher and metadata extractor."""

import requests
import json
import tempfile
import zipfile
import tarfile
import os
import shutil
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime
from urllib.parse import urlparse
from pathlib import Path
import logging

from .models import VersionInfo

logger = logging.getLogger(__name__)


class PyPIFetcher:
    """Fetches package information and files from PyPI."""

    def __init__(self, cache_dir: Optional[Path] = None):
        """Initialize the PyPI fetcher.

        Args:
            cache_dir: Directory to cache downloaded files. If None, uses temp directory.
        """
        self.base_url = "https://pypi.org/pypi"
        self.session = requests.Session()
        self.session.headers.update(
            {"User-Agent": "pypevol-plus/0.1.0 (package-evolution-analyzer)"}
        )

        if cache_dir:
            self.cache_dir = Path(cache_dir)
            self.cache_dir.mkdir(parents=True, exist_ok=True)
        else:
            self.cache_dir = None

    def _is_version_yanked(self, version_data: List[Dict]) -> bool:
        """Check if a version is yanked by examining its files.

        Args:
            version_data: List of file information for a version

        Returns:
            True if any file in the version is yanked
        """
        if not version_data:
            return False

        for file_info in version_data:
            if file_info.get("yanked", False):
                return True

        return False

    def get_package_metadata(self, package_name: str) -> Dict[str, Any]:
        """Get package metadata from PyPI.

        Args:
            package_name: Name of the package

        Returns:
            Package metadata dictionary

        Raises:
            requests.RequestException: If the request fails
        """
        url = f"{self.base_url}/{package_name}/json"
        logger.info(f"Fetching metadata for package: {package_name}")

        try:
            response = self.session.get(url)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            logger.error(f"Failed to fetch metadata for {package_name}: {e}")
            raise

    def get_version_info(
        self, package_name: str, version: str, include_yanked: bool = False
    ) -> Optional[VersionInfo]:
        """Get information about a specific package version.

        Args:
            package_name: Name of the package
            version: Version string
            include_yanked: Whether to include yanked versions

        Returns:
            VersionInfo object or None if version not found or is yanked (when include_yanked=False)
        """
        try:
            metadata = self.get_package_metadata(package_name)
            releases = metadata.get("releases", {})

            if version not in releases:
                logger.warning(
                    f"Version {version} not found for package {package_name}"
                )
                return None

            version_data = releases[version]
            if not version_data:
                return None

            # Determine if version is yanked and get yanked reason
            is_yanked = self._is_version_yanked(version_data)
            yanked_reason = None
            if is_yanked:
                # Find the yanked reason from any of the files
                for file_info in version_data:
                    if file_info.get("yanked", False):
                        yanked_reason = file_info.get("yanked_reason")
                        if yanked_reason:
                            break

            # Filter out yanked versions if not requested
            if not include_yanked and is_yanked:
                logger.info(
                    f"Skipping yanked version {version} for package {package_name}"
                )
                return None

            # Parse release date from the first file
            release_date = None
            if version_data:
                # Try different timestamp formats used by PyPI
                upload_time = version_data[0].get(
                    "upload_time_iso_8601"
                ) or version_data[0].get("upload_time")
                if upload_time:
                    try:
                        if "T" in upload_time and upload_time.endswith("Z"):
                            # ISO format with Z suffix
                            release_date = datetime.fromisoformat(
                                upload_time.replace("Z", "+00:00")
                            )
                        elif "T" in upload_time:
                            # ISO format without Z suffix
                            release_date = datetime.fromisoformat(upload_time)
                        else:
                            # Try parsing as general datetime format
                            from dateutil.parser import parse as parse_date

                            release_date = parse_date(upload_time)
                    except (ValueError, ImportError) as e:
                        logger.warning(
                            f"Could not parse upload_time '{upload_time}' for {package_name} {version}: {e}"
                        )
                        release_date = None

            # Find wheel and source URLs
            wheel_url = None
            source_url = None

            for file_info in version_data:
                if file_info["packagetype"] == "bdist_wheel":
                    wheel_url = file_info["url"]
                elif file_info["packagetype"] == "sdist":
                    source_url = file_info["url"]

            # Get package info for this version
            package_info = metadata.get("info", {})

            return VersionInfo(
                version=version,
                release_date=release_date,
                python_requires=package_info.get("requires_python"),
                dependencies=package_info.get("requires_dist", []) or [],
                wheel_url=wheel_url,
                source_url=source_url,
                yanked=is_yanked,
                yanked_reason=yanked_reason,
                metadata={
                    "summary": package_info.get("summary"),
                    "description": package_info.get("description"),
                    "author": package_info.get("author"),
                    "license": package_info.get("license"),
                    "home_page": package_info.get("home_page"),
                    "keywords": package_info.get("keywords"),
                    "classifiers": package_info.get("classifiers", []),
                },
            )
        except Exception as e:
            logger.error(
                f"Failed to get version info for {package_name} {version}: {e}"
            )
            return None

    def get_all_versions(
        self, package_name: str, include_yanked: bool = False
    ) -> List[VersionInfo]:
        """Get information about all versions of a package.

        Args:
            package_name: Name of the package
            include_yanked: Whether to include yanked versions

        Returns:
            List of VersionInfo objects sorted by release date
        """
        try:
            metadata = self.get_package_metadata(package_name)
            releases = metadata.get("releases", {})

            versions = []
            for version in releases.keys():
                version_info = self.get_version_info(
                    package_name, version, include_yanked=include_yanked
                )
                if version_info:
                    versions.append(version_info)

            # Sort by release date (oldest first)
            versions.sort(key=lambda v: v.release_date or datetime.min)
            return versions

        except Exception as e:
            logger.error(f"Failed to get all versions for {package_name}: {e}")
            return []

    def download_file(self, url: str, filename: Optional[str] = None) -> Path:
        """Download a file from URL.

        Args:
            url: URL to download from
            filename: Optional filename to save as

        Returns:
            Path to the downloaded file

        Raises:
            requests.RequestException: If download fails
        """
        if not filename:
            filename = os.path.basename(urlparse(url).path)

        # Use cache if available
        if self.cache_dir:
            file_path = self.cache_dir / filename
            if file_path.exists():
                logger.info(f"Using cached file: {file_path}")
                return file_path
        else:
            temp_dir = Path(tempfile.mkdtemp())
            file_path = temp_dir / filename

        logger.info(f"Downloading {url} to {file_path}")

        try:
            response = self.session.get(url, stream=True)
            response.raise_for_status()

            file_path.parent.mkdir(parents=True, exist_ok=True)

            with open(file_path, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)

            logger.info(f"Downloaded {filename} ({file_path.stat().st_size} bytes)")
            return file_path

        except requests.RequestException as e:
            logger.error(f"Failed to download {url}: {e}")
            raise

    def extract_package(self, file_path: Path) -> Path:
        """Extract a package file (wheel or source distribution).

        Args:
            file_path: Path to the package file

        Returns:
            Path to the extracted directory

        Raises:
            ValueError: If file format is not supported
        """
        extract_dir = file_path.parent / f"{file_path.stem}_extracted"

        if extract_dir.exists():
            logger.info(f"Using existing extracted directory: {extract_dir}")
            return extract_dir

        extract_dir.mkdir(exist_ok=True)

        try:
            if file_path.suffix == ".whl" or file_path.name.endswith(".zip"):
                with zipfile.ZipFile(file_path, "r") as zip_file:
                    zip_file.extractall(extract_dir)
                    logger.info(f"Extracted wheel/zip to: {extract_dir}")

            elif file_path.suffix == ".gz" and ".tar" in file_path.name:
                with tarfile.open(file_path, "r:gz") as tar_file:
                    tar_file.extractall(extract_dir)
                    logger.info(f"Extracted tar.gz to: {extract_dir}")

            elif file_path.suffix == ".bz2" and ".tar" in file_path.name:
                with tarfile.open(file_path, "r:bz2") as tar_file:
                    tar_file.extractall(extract_dir)
                    logger.info(f"Extracted tar.bz2 to: {extract_dir}")

            else:
                raise ValueError(f"Unsupported file format: {file_path}")

            return extract_dir

        except Exception as e:
            logger.error(f"Failed to extract {file_path}: {e}")
            if extract_dir.exists():
                shutil.rmtree(extract_dir)
            raise

    def download_and_extract_version(
        self, package_name: str, version: str, prefer_wheel: bool = True
    ) -> Optional[Tuple[Path, VersionInfo]]:
        """Download and extract a specific version of a package.

        Args:
            package_name: Name of the package
            version: Version to download
            prefer_wheel: Whether to prefer wheel over source distribution

        Returns:
            Tuple of (extracted_path, version_info) or None if failed
        """
        version_info = self.get_version_info(package_name, version)
        if not version_info:
            return None

        # Choose which file to download
        download_url = None
        if prefer_wheel and version_info.wheel_url:
            download_url = version_info.wheel_url
        elif version_info.source_url:
            download_url = version_info.source_url
        elif version_info.wheel_url:
            download_url = version_info.wheel_url

        if not download_url:
            logger.warning(f"No downloadable files found for {package_name} {version}")
            return None

        try:
            # Download the file
            file_path = self.download_file(download_url)

            # Extract the file
            extracted_path = self.extract_package(file_path)

            return extracted_path, version_info

        except Exception as e:
            logger.error(
                f"Failed to download and extract {package_name} {version}: {e}"
            )
            return None

    def get_package_versions(
        self, package_name: str, include_yanked: bool = False
    ) -> List[str]:
        """Get a list of all version names for a package without parsing VersionInfo.

        Args:
            package_name: Name of the package
            include_yanked: Whether to include yanked versions

        Returns:
            List of version strings sorted chronologically (oldest first)
        """
        try:
            metadata = self.get_package_metadata(package_name)
            releases = metadata.get("releases", {})

            # Filter out versions without release data and optionally yanked versions
            valid_versions = []
            for version, version_data in releases.items():
                if version_data:  # Only include versions with actual release data
                    # Check if version is yanked
                    if not include_yanked and self._is_version_yanked(version_data):
                        logger.debug(
                            f"Skipping yanked version {version} for package {package_name}"
                        )
                        continue
                    valid_versions.append(version)

            # Sort versions chronologically by trying to parse release dates
            def get_sort_key(version):
                try:
                    version_data = releases[version]
                    if version_data:
                        upload_time = version_data[0].get(
                            "upload_time_iso_8601"
                        ) or version_data[0].get("upload_time")
                        if upload_time:
                            if "T" in upload_time and upload_time.endswith("Z"):
                                return datetime.fromisoformat(
                                    upload_time.replace("Z", "+00:00")
                                )
                            elif "T" in upload_time:
                                return datetime.fromisoformat(upload_time)
                            else:
                                from dateutil.parser import parse as parse_date

                                return parse_date(upload_time)
                except Exception:
                    pass
                return datetime.min

            valid_versions.sort(key=get_sort_key)
            return valid_versions

        except Exception as e:
            logger.error(f"Failed to get version list for {package_name}: {e}")
            return []

    def get_specific_versions(
        self, package_name: str, versions: List[str], include_yanked: bool = False
    ) -> List[VersionInfo]:
        """Get VersionInfo objects for specific version names.

        Args:
            package_name: Name of the package
            versions: List of version strings to get info for
            include_yanked: Whether to include yanked versions

        Returns:
            List of VersionInfo objects for the specified versions
        """
        version_infos = []
        for version in versions:
            version_info = self.get_version_info(
                package_name, version, include_yanked=include_yanked
            )
            if version_info:
                version_infos.append(version_info)
            else:
                logger.warning(
                    f"Could not get version info for {package_name} {version}"
                )

        # Sort by release date (oldest first)
        version_infos.sort(key=lambda v: v.release_date or datetime.min)
        return version_infos

    def cleanup_temp_files(self):
        """Clean up temporary files and directories."""
        # This method can be extended to clean up temporary files
        # Currently, we rely on the system's temp directory cleanup
        pass

    def get_version_range(
        self,
        package_name: str,
        from_version: Optional[str] = None,
        to_version: Optional[str] = None,
        max_versions: Optional[int] = None,
        include_yanked: bool = False,
    ) -> List[VersionInfo]:
        """Get a range of versions for analysis.

        Args:
            package_name: Name of the package
            from_version: Starting version (inclusive)
            to_version: Ending version (inclusive)
            max_versions: Maximum number of versions to return
            include_yanked: Whether to include yanked versions

        Returns:
            List of VersionInfo objects in the specified range
        """
        all_versions = self.get_all_versions(
            package_name, include_yanked=include_yanked
        )

        if not all_versions:
            return []

        # Filter by version range
        if from_version or to_version:
            from packaging.version import parse as parse_version

            filtered_versions = []
            for version_info in all_versions:
                try:
                    v = parse_version(version_info.version)

                    if from_version and v < parse_version(from_version):
                        continue
                    if to_version and v > parse_version(to_version):
                        continue

                    filtered_versions.append(version_info)
                except Exception:
                    # Skip versions that can't be parsed
                    continue

            all_versions = filtered_versions

        # Limit number of versions
        if max_versions and len(all_versions) > max_versions:
            # Take evenly distributed versions across the range
            step = len(all_versions) // max_versions
            all_versions = all_versions[::step][:max_versions]

        return all_versions
