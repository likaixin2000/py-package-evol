"""Data models for PyPevol."""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set, Any, Union
from enum import Enum
from datetime import datetime
import json


class APIType(Enum):
    """Types of API elements that can be tracked."""

    FUNCTION = "function"
    CLASS = "class"
    METHOD = "method"
    PROPERTY = "property"
    CONSTANT = "constant"
    MODULE = "module"


class ChangeType(Enum):
    """Types of changes that can occur to API elements."""

    ADDED = "added"
    REMOVED = "removed"
    MODIFIED = "modified"
    DEPRECATED = "deprecated"


@dataclass
class APIElement:
    """Represents an API element (function, class, method, etc.)."""

    name: str
    type: APIType
    module_path: str
    signature: Optional[str] = None
    docstring: Optional[str] = None
    line_number: Optional[int] = None
    is_private: bool = False
    is_deprecated: bool = False
    type_hints: Dict[str, str] = field(default_factory=dict)
    decorators: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        """Post-initialization processing."""
        if self.name.startswith("_") and not self.name.startswith("__"):
            self.is_private = True

    @property
    def full_name(self) -> str:
        """Get the fully qualified name of the API element."""
        return f"{self.module_path}.{self.name}"

    @property
    def module(self) -> str:
        """Alias for module_path for backward compatibility."""
        return self.module_path

    def get_signature(self) -> str:
        """Get a unique signature for this API element.

        This creates a stable, unique identifier for the API element that can be used
        for comparison across versions. The signature includes the full name and either
        the method signature (if available) or the API type.

        Returns:
            str: A unique signature string for this API element
        """
        try:
            # Use the method signature if available for more precision
            if self.signature and self.signature.strip():
                return f"{self.full_name}:{self.signature}"
            else:
                # Fall back to a combination of full name and type
                return f"{self.full_name}:{self.type.value}"
        except Exception as e:
            # Robust fallback in case of any errors
            return f"{self.module_path}.{self.name}:{getattr(self.type, 'value', str(self.type))}"

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "name": self.name,
            "type": self.type.value,
            "module_path": self.module_path,
            "signature": self.signature,
            "docstring": self.docstring,
            "line_number": self.line_number,
            "is_private": self.is_private,
            "is_deprecated": self.is_deprecated,
            "type_hints": self.type_hints,
            "decorators": self.decorators,
            "metadata": self.metadata,
            "full_name": self.full_name,
        }


@dataclass
class VersionInfo:
    """Information about a specific package version."""

    version: str
    release_date: Optional[Union[datetime, str]]
    python_requires: Optional[str] = None
    dependencies: List[str] = field(default_factory=list)
    wheel_url: Optional[str] = None
    source_url: Optional[str] = None
    yanked: bool = False
    yanked_reason: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        """Post-initialization processing."""
        # Convert string dates to datetime objects
        if isinstance(self.release_date, str):
            try:
                # Try to parse ISO format first
                self.release_date = datetime.fromisoformat(self.release_date)
            except (ValueError, AttributeError):
                try:
                    # Try common date format
                    self.release_date = datetime.strptime(self.release_date, "%Y-%m-%d")
                except ValueError:
                    try:
                        # Try another common format
                        self.release_date = datetime.strptime(
                            self.release_date, "%Y-%m-%d %H:%M:%S"
                        )
                    except ValueError:
                        # If all parsing fails, set to None and warn
                        print(
                            f"Warning: Could not parse date '{self.release_date}', setting to None"
                        )
                        self.release_date = None

    @property
    def number(self) -> str:
        """Alias for version for backward compatibility."""
        return self.version

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        # Handle release_date conversion robustly
        release_date_str = None
        if self.release_date:
            if isinstance(self.release_date, datetime):
                release_date_str = self.release_date.isoformat()
            elif isinstance(self.release_date, str):
                release_date_str = self.release_date
            else:
                release_date_str = str(self.release_date)

        return {
            "version": self.version,
            "release_date": release_date_str,
            "python_requires": self.python_requires,
            "dependencies": self.dependencies,
            "wheel_url": self.wheel_url,
            "source_url": self.source_url,
            "yanked": self.yanked,
            "yanked_reason": self.yanked_reason,
            "metadata": self.metadata,
        }


@dataclass
class APIChange:
    """Represents a change to an API element between versions."""

    element: APIElement
    change_type: ChangeType
    from_version: Optional[str] = None
    to_version: Optional[str] = None
    old_signature: Optional[str] = None
    new_signature: Optional[str] = None
    description: Optional[str] = None
    is_backwards_compatible: bool = True

    @property
    def api_name(self) -> str:
        """Get the name of the API that changed."""
        return self.element.full_name

    @property
    def version(self) -> str:
        """Get the version where this change occurred (alias for to_version)."""
        return self.to_version or self.from_version or "unknown"

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "element": self.element.to_dict(),
            "change_type": self.change_type.value,
            "from_version": self.from_version,
            "to_version": self.to_version,
            "old_signature": self.old_signature,
            "new_signature": self.new_signature,
            "description": self.description,
            "is_backwards_compatible": self.is_backwards_compatible,
            "api_name": self.api_name,
            "version": self.version,
        }


@dataclass
class AnalysisResult:
    """Results of analyzing a package's API evolution."""

    package_name: str
    versions: List[VersionInfo]
    api_elements: Dict[str, List[APIElement]]  # version -> list of elements
    changes: List[APIChange]
    analysis_date: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def get_api_changes(
        self,
        change_types: Optional[List[ChangeType]] = None,
        api_types: Optional[List[APIType]] = None,
    ) -> List[APIChange]:
        """Get filtered API changes."""
        filtered_changes = self.changes

        if change_types:
            filtered_changes = [
                c for c in filtered_changes if c.change_type in change_types
            ]

        if api_types:
            filtered_changes = [
                c for c in filtered_changes if c.element.type in api_types
            ]

        return filtered_changes

    def get_version_apis(self, version: str) -> List[APIElement]:
        """Get all API elements for a specific version."""
        return self.api_elements.get(version, [])

    def _check_name_collisions(
        self, api_name: str, matches: Optional[List[APIChange]] = None
    ) -> Dict[str, Any]:
        """Check for name collisions and return collision information.

        This method checks for collisions in both API changes (if matches provided)
        and all API elements across versions.
        """
        unique_full_names = set()
        api_details = []

        # Check matches from API changes if provided
        if matches:
            for match in matches:
                full_name = match.element.full_name
                if full_name not in unique_full_names:
                    unique_full_names.add(full_name)
                    api_details.append(
                        {
                            "full_name": full_name,
                            "module_path": match.element.module_path,
                            "type": match.element.type.value,
                            "signature": match.element.signature,
                        }
                    )

        # Also check all API elements across versions to catch any we might have missed
        unique_elements = (
            {}
        )  # Use dict with full_name as key to avoid hashability issues
        for elements in self.api_elements.values():
            for element in elements:
                if element.name == api_name:
                    unique_elements[element.full_name] = element

        # Add any API elements not already found in changes
        for element in unique_elements.values():
            full_name = element.full_name
            if full_name not in unique_full_names:
                unique_full_names.add(full_name)
                api_details.append(
                    {
                        "full_name": full_name,
                        "module_path": element.module_path,
                        "type": element.type.value,
                        "signature": element.signature,
                    }
                )

        has_collision = len(unique_full_names) > 1

        return {
            "has_collision": has_collision,
            "unique_apis": api_details,
            "collision_count": len(unique_full_names),
        }

    def _find_exact_matches(self, api_name: str) -> List[APIChange]:
        """Find exact matches for the given API name."""
        exact_matches = []
        name_only_matches = []

        for change in self.changes:
            if change.element.full_name == api_name:
                # Exact full name match - highest priority
                exact_matches.append(change)
            elif change.element.name == api_name:
                # Name-only match - need to check for collisions
                name_only_matches.append(change)

        # If we have full name matches, return those (no ambiguity)
        if exact_matches:
            return exact_matches

        return name_only_matches

    def _calculate_element_similarity(
        self, api_name: str, element: APIElement
    ) -> float:
        """Calculate similarity score between api_name and an API element."""
        from difflib import SequenceMatcher

        scores = []

        # 1. Direct name similarity
        name_score = SequenceMatcher(
            None, api_name.lower(), element.name.lower()
        ).ratio()
        scores.append(name_score)

        # 2. Full name ending similarity (e.g., "connect_to_my_server" matches "mylib.remote.connections.connect_to_my_server")
        if "." in element.full_name:
            full_name_parts = element.full_name.split(".")
            if len(full_name_parts) > 1:
                ending_match_score = SequenceMatcher(
                    None, api_name.lower(), full_name_parts[-1].lower()
                ).ratio()
                scores.append(ending_match_score * 1.2)  # Boost ending matches

        # 3. Check if api_name is contained in the element name (substring match)
        if (
            api_name.lower() in element.name.lower()
            or element.name.lower() in api_name.lower()
        ):
            substring_score = max(len(api_name), len(element.name)) / (
                len(api_name) + len(element.name)
            )
            scores.append(substring_score * 1.1)  # Boost substring matches

        # Take the highest score for this element
        max_score = max(scores) if scores else 0.0

        # Prefer exact name matches over full name matches to avoid false positives
        if element.name.lower() == api_name.lower():
            max_score = 1.0

        return max_score

    def _find_fuzzy_match(self, api_name: str) -> Optional[APIElement]:
        """Find the best fuzzy match for the given API name."""
        # Collect all unique API elements for fuzzy matching using dict to avoid hashability issues
        unique_elements = {}

        # Add elements from changes
        for change in self.changes:
            unique_elements[change.element.full_name] = change.element

        # Add elements from all versions
        for elements in self.api_elements.values():
            for element in elements:
                unique_elements[element.full_name] = element

        # Find best fuzzy match
        best_match = None
        best_score = 0.0
        similarity_threshold = 0.6  # Minimum similarity threshold

        for element in unique_elements.values():
            score = self._calculate_element_similarity(api_name, element)
            if score > best_score and score >= similarity_threshold:
                best_score = score
                best_match = element

        return best_match

    def _process_lifecycle_changes(
        self, changes: List[APIChange], lifecycle: Dict[str, Any]
    ) -> None:
        """Process changes and update lifecycle information."""
        for change in changes:
            if change.change_type == ChangeType.ADDED:
                lifecycle["introduced_in"] = change.to_version
            elif change.change_type == ChangeType.REMOVED:
                lifecycle["removed_in"] = change.to_version
            elif change.change_type == ChangeType.MODIFIED:
                lifecycle["modifications"].append(
                    {
                        "version": change.to_version,
                        "old_signature": change.old_signature,
                        "new_signature": change.new_signature,
                        "description": change.description,
                    }
                )

    def _find_versions_present(
        self, api_name: str, matched_api: Optional[str]
    ) -> List[str]:
        """Find all versions where the API is present."""
        versions_present = []
        for version, elements in self.api_elements.items():
            for element in elements:
                # Check both exact matches and fuzzy matches
                # If we have a matched_api (from fuzzy matching), use that for comparison
                if matched_api:
                    is_match = element.full_name == matched_api
                else:
                    # For exact matches, check both name and full_name
                    is_match = element.name == api_name or element.full_name == api_name

                if is_match:
                    versions_present.append(version)
                    break
        return sorted(versions_present)

    def get_apis_by_name(self, api_name: str) -> List[Dict[str, Any]]:
        """Get all APIs that match a given name, including collision information.

        This is a helper method that provides detailed information about all APIs
        with the same name, useful when collision is detected.

        Args:
            api_name: The API name to search for

        Returns:
            List of dictionaries containing API information
        """
        # Check for all collisions using the consolidated method
        matches_from_changes = self._find_exact_matches(api_name)
        collision_info = self._check_name_collisions(api_name, matches_from_changes)

        # Add version information for each API
        result = []
        for api_info in collision_info["unique_apis"]:
            api_info = api_info.copy()
            api_info["versions_present"] = self._find_versions_present(
                api_info["full_name"], api_info["full_name"]
            )
            result.append(api_info)

        return sorted(result, key=lambda x: x["full_name"])

    def get_api_lifecycle(self, api_name: str) -> Dict[str, Any]:
        """Get the lifecycle information for a specific API with fuzzy matching support and collision detection."""
        lifecycle = {
            "name": api_name,
            "introduced_in": None,
            "removed_in": None,
            "modifications": [],
            "versions_present": [],
            "matched_api": None,  # Store the actual matched API name if fuzzy match was used
            "collision_detected": False,
            "available_apis": [],  # Store all colliding APIs if collision detected
        }

        # First, try exact matches in changes
        exact_matches = self._find_exact_matches(api_name)

        # Check for name collisions using the consolidated method
        collision_info = self._check_name_collisions(api_name, exact_matches)

        if collision_info["has_collision"]:
            # Handle collision case
            lifecycle["collision_detected"] = True
            lifecycle["available_apis"] = collision_info["unique_apis"]

            # Print collision information for user awareness
            print(f"\n⚠️  Multiple APIs found with name '{api_name}':")
            print(
                f"Found {collision_info['collision_count']} different APIs with the same name:"
            )
            for i, api_info in enumerate(collision_info["unique_apis"], 1):
                print(f"  {i}. {api_info['full_name']} ({api_info['type']})")
                if api_info["signature"]:
                    print(f"     Signature: {api_info['signature']}")

            print(
                f"\nTo get lifecycle information for a specific API, use the full name:"
            )
            for api_info in collision_info["unique_apis"]:
                print(f"  - get_api_lifecycle('{api_info['full_name']}')")
            print()

            # Return early with collision information
            return lifecycle

        if exact_matches:
            matched_changes = exact_matches
        else:
            # Try fuzzy matching
            best_match = self._find_fuzzy_match(api_name)

            if best_match:
                lifecycle["matched_api"] = best_match.full_name
                # Use the best match for finding changes
                matched_changes = [
                    c
                    for c in self.changes
                    if c.element.name == best_match.name
                    and c.element.full_name == best_match.full_name
                ]
            else:
                matched_changes = []

        # Process the matched changes
        self._process_lifecycle_changes(matched_changes, lifecycle)

        # Find all versions where API is present
        lifecycle["versions_present"] = self._find_versions_present(
            api_name, lifecycle["matched_api"]
        )

        return lifecycle

    def generate_summary(self) -> Dict[str, Any]:
        """Generate a summary of the analysis results."""
        summary = {
            "package_name": self.package_name,
            "total_versions": len(self.versions),
            "total_changes": len(self.changes),
            "analysis_date": self.analysis_date.isoformat(),
        }

        # Count changes by type
        change_counts = {}
        for change_type in ChangeType:
            change_counts[change_type.value] = len(
                [c for c in self.changes if c.change_type == change_type]
            )
        summary["change_types"] = change_counts

        # Count API elements by type
        api_counts = {}
        all_elements = []
        for elements in self.api_elements.values():
            all_elements.extend(elements)

        for api_type in APIType:
            api_counts[api_type.value] = len(
                [element for element in all_elements if element.type == api_type]
            )
        summary["api_types"] = api_counts

        # Add more detailed summary information
        if self.versions:
            sorted_versions = sorted(self.versions, key=lambda v: v.version)
            summary["version_range"] = {
                "first": sorted_versions[0].version,
                "last": sorted_versions[-1].version,
            }

        # Calculate unique APIs
        all_signatures = set()
        for elements in self.api_elements.values():
            for element in elements:
                all_signatures.add(element.get_signature())
        summary["unique_apis"] = len(all_signatures)

        # Add version details
        summary["versions"] = []
        for version in self.versions:
            version_changes = [
                c
                for c in self.changes
                if getattr(c, "to_version", None) == version.version
            ]
            version_apis = self.api_elements.get(version.version, [])

            summary["versions"].append(
                {
                    "version": version.version,
                    "release_date": (
                        version.release_date.strftime("%Y-%m-%d")
                        if version.release_date
                        else "Unknown"
                    ),
                    "api_count": len(version_apis),
                    "changes_count": len(version_changes),
                }
            )

        return summary

    def get_summary(self) -> Dict[str, Any]:
        """Alias for generate_summary() for backward compatibility."""
        return self.generate_summary()

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "package_name": self.package_name,
            "versions": [v.to_dict() for v in self.versions],
            "api_elements": {
                version: [element.to_dict() for element in elements]
                for version, elements in self.api_elements.items()
            },
            "changes": [change.to_dict() for change in self.changes],
            "analysis_date": self.analysis_date.isoformat(),
            "metadata": self.metadata,
            "summary": self.generate_summary(),
        }

    def to_json(self, indent: int = 2) -> str:
        """Convert to JSON string."""
        return json.dumps(self.to_dict(), indent=indent, default=str)

    @classmethod
    def from_json(cls, json_str: str) -> "AnalysisResult":
        """Create AnalysisResult from JSON string."""
        data = json.loads(json_str)
        return cls.from_dict(data)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AnalysisResult":
        """Create AnalysisResult from dictionary."""
        # Reconstruct versions
        versions = []
        for version_data in data.get("versions", []):
            release_date = None
            if version_data.get("release_date"):
                try:
                    release_date = datetime.fromisoformat(version_data["release_date"])
                except:
                    # Handle various date formats
                    try:
                        release_date = datetime.strptime(
                            version_data["release_date"], "%Y-%m-%d"
                        )
                    except:
                        release_date = None

            versions.append(
                VersionInfo(
                    version=version_data["version"],
                    release_date=release_date,
                    python_requires=version_data.get("python_requires"),
                    dependencies=version_data.get("dependencies", []),
                    wheel_url=version_data.get("wheel_url"),
                    source_url=version_data.get("source_url"),
                    yanked=version_data.get("yanked", False),
                    yanked_reason=version_data.get("yanked_reason"),
                    metadata=version_data.get("metadata", {}),
                )
            )

        # Reconstruct API elements
        api_elements = {}
        for version, elements_data in data.get("api_elements", {}).items():
            elements = []
            for element_data in elements_data:
                # Handle both string and enum values for type
                api_type = element_data["type"]
                if isinstance(api_type, str):
                    api_type = APIType(api_type)

                elements.append(
                    APIElement(
                        name=element_data["name"],
                        type=api_type,
                        module_path=element_data["module_path"],
                        signature=element_data.get("signature"),
                        docstring=element_data.get("docstring"),
                        line_number=element_data.get("line_number"),
                        is_private=element_data.get("is_private", False),
                        is_deprecated=element_data.get("is_deprecated", False),
                        type_hints=element_data.get("type_hints", {}),
                        decorators=element_data.get("decorators", []),
                        metadata=element_data.get("metadata", {}),
                    )
                )
            api_elements[version] = elements

        # Reconstruct changes
        changes = []
        for change_data in data.get("changes", []):
            element_data = change_data["element"]

            # Handle both string and enum values
            api_type = element_data["type"]
            if isinstance(api_type, str):
                api_type = APIType(api_type)

            change_type = change_data["change_type"]
            if isinstance(change_type, str):
                change_type = ChangeType(change_type)

            element = APIElement(
                name=element_data["name"],
                type=api_type,
                module_path=element_data["module_path"],
                signature=element_data.get("signature"),
                docstring=element_data.get("docstring"),
                line_number=element_data.get("line_number"),
                is_private=element_data.get("is_private", False),
                is_deprecated=element_data.get("is_deprecated", False),
                type_hints=element_data.get("type_hints", {}),
                decorators=element_data.get("decorators", []),
                metadata=element_data.get("metadata", {}),
            )

            changes.append(
                APIChange(
                    element=element,
                    change_type=change_type,
                    from_version=change_data.get("from_version"),
                    to_version=change_data.get("to_version"),
                    old_signature=change_data.get("old_signature"),
                    new_signature=change_data.get("new_signature"),
                    description=change_data.get("description"),
                    is_backwards_compatible=change_data.get(
                        "is_backwards_compatible", True
                    ),
                )
            )

        # Parse analysis date
        analysis_date = datetime.now()
        if data.get("analysis_date"):
            try:
                analysis_date = datetime.fromisoformat(data["analysis_date"])
            except:
                pass

        return cls(
            package_name=data["package_name"],
            versions=versions,
            api_elements=api_elements,
            changes=changes,
            analysis_date=analysis_date,
            metadata=data.get("metadata", {}),
        )
