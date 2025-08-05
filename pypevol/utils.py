"""Utility functions for PyPevol."""

import os
import sys
import yaml
import logging
from pathlib import Path
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


def load_config(config_path: Optional[Path] = None) -> Dict[str, Any]:
    """Load configuration from YAML file.

    Args:
        config_path: Path to config file. If None, searches for .pypevol.yaml

    Returns:
        Configuration dictionary
    """
    if config_path is None:
        # Search for config file in common locations
        search_paths = [
            Path.cwd() / ".pypevol.yaml",
            Path.cwd() / ".pypevol.yml",
            Path.home() / ".pypevol.yaml",
            Path.home() / ".pypevol.yml",
        ]

        for path in search_paths:
            if path.exists():
                config_path = path
                break

    if config_path is None or not config_path.exists():
        logger.info("No configuration file found, using defaults")
        return get_default_config()

    try:
        with open(config_path, "r") as f:
            config = yaml.safe_load(f)

        logger.info(f"Loaded configuration from {config_path}")
        return merge_with_defaults(config)

    except Exception as e:
        logger.warning(f"Failed to load config from {config_path}: {e}")
        return get_default_config()


def get_default_config() -> Dict[str, Any]:
    """Get default configuration."""
    return {
        "analysis": {
            "include_private": False,
            "include_deprecated": True,
            "max_versions": 50,
            "prefer_wheels": True,
        },
        "output": {
            "default_format": "html",
            "include_source_links": True,
            "show_usage_examples": True,
            "interactive_charts": True,
        },
        "cache": {
            "enabled": True,
            "directory": str(Path.home() / ".pypevol" / "cache"),
            "max_size": "1GB",
            "retention_days": 30,
        },
        "logging": {
            "level": "INFO",
            "file": None,
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        },
        "reports": {
            "custom_css": None,
            "custom_js": None,
            "template_dir": None,
            "max_changes_display": 100,
        },
        "filters": {
            "exclude_tests": True,
            "exclude_examples": True,
            "exclude_patterns": [
                "*/tests/*",
                "*/test_*.py",
                "*/examples/*",
                "*/docs/*",
                "*/__pycache__/*",
            ],
        },
        "categorization": {
            "auto_categorize": True,
            "rules": {
                "internal": ["_*", "*.internal.*"],
                "experimental": ["*.experimental.*", "*.beta.*"],
                "deprecated": ["*.deprecated.*"],
            },
        },
    }


def merge_with_defaults(config: Dict[str, Any]) -> Dict[str, Any]:
    """Merge user config with defaults.

    Args:
        config: User configuration

    Returns:
        Merged configuration
    """
    defaults = get_default_config()
    return deep_merge(defaults, config)


def deep_merge(base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
    """Deep merge two dictionaries.

    Args:
        base: Base dictionary
        override: Override dictionary

    Returns:
        Merged dictionary
    """
    result = base.copy()

    for key, value in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = deep_merge(result[key], value)
        else:
            result[key] = value

    return result


def setup_logging(config: Dict[str, Any]):
    """Set up logging based on configuration.

    Args:
        config: Configuration dictionary
    """
    logging_config = config.get("logging", {})

    level = getattr(logging, logging_config.get("level", "INFO").upper())
    format_str = logging_config.get(
        "format", "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    # Configure root logger
    logging.basicConfig(level=level, format=format_str, handlers=[])

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_handler.setFormatter(logging.Formatter(format_str))
    logging.getLogger().addHandler(console_handler)

    # File handler if specified
    log_file = logging_config.get("file")
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)

        file_handler = logging.FileHandler(log_path)
        file_handler.setLevel(level)
        file_handler.setFormatter(logging.Formatter(format_str))
        logging.getLogger().addHandler(file_handler)


def parse_size(size_str: str) -> int:
    """Parse size string (e.g., '1GB', '500MB') to bytes.

    Args:
        size_str: Size string

    Returns:
        Size in bytes
    """
    if not size_str:
        return 0

    size_str = size_str.upper().strip()

    # Extract number and unit
    import re

    match = re.match(r"^(\d+(?:\.\d+)?)\s*([KMGTPE]?B?)$", size_str)

    if not match:
        raise ValueError(f"Invalid size format: {size_str}")

    number = float(match.group(1))
    unit = match.group(2) or "B"

    # Convert to bytes
    units = {
        "B": 1,
        "KB": 1024,
        "MB": 1024**2,
        "GB": 1024**3,
        "TB": 1024**4,
        "PB": 1024**5,
        "EB": 1024**6,
    }

    if unit not in units:
        raise ValueError(f"Unknown unit: {unit}")

    return int(number * units[unit])


def format_size(size_bytes: int) -> str:
    """Format size in bytes to human-readable string.

    Args:
        size_bytes: Size in bytes

    Returns:
        Human-readable size string
    """
    if size_bytes == 0:
        return "0 B"

    units = ["B", "KB", "MB", "GB", "TB", "PB", "EB"]
    unit_index = 0

    size = float(size_bytes)
    while size >= 1024 and unit_index < len(units) - 1:
        size /= 1024
        unit_index += 1

    if size == int(size):
        return f"{int(size)} {units[unit_index]}"
    else:
        return f"{size:.1f} {units[unit_index]}"


def ensure_directory(path: Path) -> Path:
    """Ensure directory exists, creating it if necessary.

    Args:
        path: Directory path

    Returns:
        The directory path
    """
    path.mkdir(parents=True, exist_ok=True)
    return path


def cleanup_directory(path: Path, max_age_days: int = 30):
    """Clean up old files in a directory.

    Args:
        path: Directory to clean up
        max_age_days: Maximum age of files to keep
    """
    if not path.exists():
        return

    import time

    max_age_seconds = max_age_days * 24 * 60 * 60
    current_time = time.time()

    for item in path.iterdir():
        try:
            if item.is_file():
                age = current_time - item.stat().st_mtime
                if age > max_age_seconds:
                    item.unlink()
                    logger.debug(f"Deleted old file: {item}")
            elif item.is_dir():
                # Recursively clean subdirectories
                cleanup_directory(item, max_age_days)
                # Remove empty directories
                if not any(item.iterdir()):
                    item.rmdir()
                    logger.debug(f"Deleted empty directory: {item}")
        except Exception as e:
            logger.warning(f"Failed to clean up {item}: {e}")


def get_cache_size(cache_dir: Path) -> int:
    """Get total size of cache directory.

    Args:
        cache_dir: Cache directory path

    Returns:
        Total size in bytes
    """
    if not cache_dir.exists():
        return 0

    total_size = 0
    for item in cache_dir.rglob("*"):
        if item.is_file():
            try:
                total_size += item.stat().st_size
            except Exception:
                pass

    return total_size


def clean_cache_by_size(cache_dir: Path, max_size: int):
    """Clean cache by removing oldest files until under size limit.

    Args:
        cache_dir: Cache directory path
        max_size: Maximum size in bytes
    """
    if not cache_dir.exists():
        return

    current_size = get_cache_size(cache_dir)
    if current_size <= max_size:
        return

    # Get all files with their modification times
    files = []
    for item in cache_dir.rglob("*"):
        if item.is_file():
            try:
                files.append((item.stat().st_mtime, item.stat().st_size, item))
            except Exception:
                pass

    # Sort by modification time (oldest first)
    files.sort(key=lambda x: x[0])

    # Remove files until under size limit
    for mtime, size, file_path in files:
        if current_size <= max_size:
            break

        try:
            file_path.unlink()
            current_size -= size
            logger.debug(f"Removed cache file: {file_path}")
        except Exception as e:
            logger.warning(f"Failed to remove cache file {file_path}: {e}")


def validate_package_name(package_name: str) -> bool:
    """Validate PyPI package name.

    Args:
        package_name: Package name to validate

    Returns:
        True if valid package name
    """
    import re

    # PyPI package names must be valid Python module names
    # Allow letters, numbers, hyphens, underscores, and dots
    pattern = r"^[a-zA-Z][a-zA-Z0-9._-]*[a-zA-Z0-9]$|^[a-zA-Z]$"

    return bool(re.match(pattern, package_name)) and len(package_name) <= 214


def normalize_version(version: str) -> str:
    """Normalize version string for comparison.

    Args:
        version: Version string

    Returns:
        Normalized version string
    """
    try:
        from packaging.version import parse

        return str(parse(version))
    except Exception:
        return version
