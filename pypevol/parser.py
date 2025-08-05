"""Python source code parser for API extraction."""

import ast
import os
import re
from pathlib import Path
from typing import List, Dict, Set, Optional, Any, Union
import logging
from dataclasses import dataclass

from .models import APIElement, APIType

logger = logging.getLogger(__name__)


@dataclass
class ParseContext:
    """Context information for parsing."""

    module_path: str
    file_path: Path
    source_code: str
    tree: ast.AST


class SourceParser:
    """Parses Python source code to extract API elements."""

    def __init__(self, include_private: bool = False, include_deprecated: bool = True):
        """Initialize the source parser.

        Args:
            include_private: Whether to include private APIs (starting with _)
            include_deprecated: Whether to include deprecated APIs
        """
        self.include_private = include_private
        self.include_deprecated = include_deprecated
        self.deprecation_patterns = [
            r"@deprecated",
            r".. deprecated::",
            r"DEPRECATED",
            r"This.*deprecated",
            r"deprecated.*use",
        ]

    def parse_package(self, package_path: Path, package_name: str) -> List[APIElement]:
        """Parse an entire package directory.

        Args:
            package_path: Path to the package directory
            package_name: Name of the package

        Returns:
            List of API elements found in the package
        """
        api_elements = []

        # Find all Python files
        python_files = []
        if package_path.is_file() and package_path.suffix == ".py":
            python_files = [package_path]
        else:
            python_files = list(package_path.rglob("*.py"))

        for file_path in python_files:
            try:
                # Skip __pycache__ and other non-source directories
                if "__pycache__" in str(file_path):
                    continue

                # Determine module path
                module_path = self._get_module_path(
                    file_path, package_path, package_name
                )

                # Parse the file
                file_elements = self.parse_file(file_path, module_path)
                api_elements.extend(file_elements)

            except Exception as e:
                logger.warning(f"Failed to parse {file_path}: {e}")
                continue

        return api_elements

    def parse_file(self, file_path: Path, module_path: str) -> List[APIElement]:
        """Parse a single Python file.

        Args:
            file_path: Path to the Python file
            module_path: Module path (e.g., 'package.module')

        Returns:
            List of API elements found in the file
        """
        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                source_code = f.read()

            # Parse the AST
            tree = ast.parse(source_code, filename=str(file_path))

            # Create parse context
            context = ParseContext(
                module_path=module_path,
                file_path=file_path,
                source_code=source_code,
                tree=tree,
            )

            # Extract API elements
            visitor = APIVisitor(self, context)
            visitor.visit(tree)

            return visitor.api_elements

        except Exception as e:
            logger.error(f"Failed to parse {file_path}: {e}")
            return []

    def _get_module_path(
        self, file_path: Path, package_path: Path, package_name: str
    ) -> str:
        """Get the module path for a file.

        Args:
            file_path: Path to the Python file
            package_path: Path to the package root
            package_name: Name of the package

        Returns:
            Module path string
        """
        try:
            # Get relative path from package root
            if package_path.is_file():
                # Single file package
                return package_name

            rel_path = file_path.relative_to(package_path)

            # Convert path to module notation
            parts = list(rel_path.parts[:-1])  # Remove filename
            if rel_path.stem != "__init__":
                parts.append(rel_path.stem)

            if not parts:
                return package_name

            return f"{package_name}.{'.'.join(parts)}"

        except Exception:
            # Fallback to filename-based module path
            return f"{package_name}.{file_path.stem}"

    def _is_deprecated(self, node: ast.AST, docstring: Optional[str] = None) -> bool:
        """Check if an AST node represents a deprecated API.

        Args:
            node: AST node to check
            docstring: Docstring of the node

        Returns:
            True if the API is deprecated
        """
        # Check decorators
        if hasattr(node, "decorator_list"):
            for decorator in node.decorator_list:
                decorator_name = self._get_decorator_name(decorator)
                if "deprecated" in decorator_name.lower():
                    return True

        # Check docstring
        if docstring:
            for pattern in self.deprecation_patterns:
                if re.search(pattern, docstring, re.IGNORECASE):
                    return True

        return False

    def _get_decorator_name(self, decorator: ast.AST) -> str:
        """Get the name of a decorator.

        Args:
            decorator: Decorator AST node

        Returns:
            Decorator name as string
        """
        if isinstance(decorator, ast.Name):
            return decorator.id
        elif isinstance(decorator, ast.Attribute):
            return ast.unparse(decorator)
        elif isinstance(decorator, ast.Call):
            if isinstance(decorator.func, ast.Name):
                return decorator.func.id
            elif isinstance(decorator.func, ast.Attribute):
                return ast.unparse(decorator.func)

        return str(decorator)

    def _extract_type_hints(
        self, node: Union[ast.FunctionDef, ast.AsyncFunctionDef]
    ) -> Dict[str, str]:
        """Extract type hints from a function.

        Args:
            node: Function AST node

        Returns:
            Dictionary of parameter/return type hints
        """
        type_hints = {}

        # Extract parameter type hints
        for arg in node.args.args:
            if arg.annotation:
                try:
                    type_hints[arg.arg] = ast.unparse(arg.annotation)
                except Exception:
                    type_hints[arg.arg] = str(arg.annotation)

        # Extract return type hint
        if node.returns:
            try:
                type_hints["return"] = ast.unparse(node.returns)
            except Exception:
                type_hints["return"] = str(node.returns)

        return type_hints

    def _get_signature(self, node: Union[ast.FunctionDef, ast.AsyncFunctionDef]) -> str:
        """Get the function signature.

        Args:
            node: Function AST node

        Returns:
            Function signature as string
        """
        try:
            # Build signature manually
            parts = []

            # Regular arguments
            for arg in node.args.args:
                arg_str = arg.arg
                if arg.annotation:
                    try:
                        arg_str += f": {ast.unparse(arg.annotation)}"
                    except Exception:
                        pass
                parts.append(arg_str)

            # Default arguments
            defaults = node.args.defaults
            if defaults:
                num_defaults = len(defaults)
                for i, default in enumerate(defaults):
                    idx = len(parts) - num_defaults + i
                    if idx >= 0 and idx < len(parts):
                        try:
                            parts[idx] += f" = {ast.unparse(default)}"
                        except Exception:
                            parts[idx] += " = ..."

            # *args
            if node.args.vararg:
                arg_str = f"*{node.args.vararg.arg}"
                if node.args.vararg.annotation:
                    try:
                        arg_str += f": {ast.unparse(node.args.vararg.annotation)}"
                    except Exception:
                        pass
                parts.append(arg_str)

            # **kwargs
            if node.args.kwarg:
                arg_str = f"**{node.args.kwarg.arg}"
                if node.args.kwarg.annotation:
                    try:
                        arg_str += f": {ast.unparse(node.args.kwarg.annotation)}"
                    except Exception:
                        pass
                parts.append(arg_str)

            signature = f"{node.name}({', '.join(parts)})"

            # Add return type
            if node.returns:
                try:
                    signature += f" -> {ast.unparse(node.returns)}"
                except Exception:
                    pass

            return signature

        except Exception:
            return node.name + "(...)"


class APIVisitor(ast.NodeVisitor):
    """AST visitor for extracting API elements."""

    def __init__(self, parser: SourceParser, context: ParseContext):
        """Initialize the visitor.

        Args:
            parser: Source parser instance
            context: Parse context
        """
        self.parser = parser
        self.context = context
        self.api_elements = []
        self.current_class = None
        self.class_stack = []

    def visit_FunctionDef(self, node: ast.FunctionDef):
        """Visit function definition."""
        self._visit_function(node)
        self.generic_visit(node)

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef):
        """Visit async function definition."""
        self._visit_function(node)
        self.generic_visit(node)

    def _visit_function(self, node: Union[ast.FunctionDef, ast.AsyncFunctionDef]):
        """Handle function/method definitions."""
        # Skip private functions if not included
        if not self.parser.include_private and node.name.startswith("_"):
            return

        # Get docstring
        docstring = ast.get_docstring(node)

        # Check if deprecated
        is_deprecated = self.parser._is_deprecated(node, docstring)
        if not self.parser.include_deprecated and is_deprecated:
            return

        # Determine API type
        if self.current_class:
            api_type = APIType.METHOD
        else:
            api_type = APIType.FUNCTION

        # Get decorators
        decorators = [self.parser._get_decorator_name(d) for d in node.decorator_list]

        # Create API element
        api_element = APIElement(
            name=node.name,
            type=api_type,
            module_path=self.context.module_path,
            signature=self.parser._get_signature(node),
            docstring=docstring,
            line_number=node.lineno,
            is_deprecated=is_deprecated,
            type_hints=self.parser._extract_type_hints(node),
            decorators=decorators,
            metadata={
                "is_async": isinstance(node, ast.AsyncFunctionDef),
                "class_name": self.current_class,
            },
        )

        self.api_elements.append(api_element)

    def visit_ClassDef(self, node: ast.ClassDef):
        """Visit class definition."""
        # Skip private classes if not included
        if not self.parser.include_private and node.name.startswith("_"):
            return

        # Get docstring
        docstring = ast.get_docstring(node)

        # Check if deprecated
        is_deprecated = self.parser._is_deprecated(node, docstring)
        if not self.parser.include_deprecated and is_deprecated:
            return

        # Get base classes
        bases = []
        for base in node.bases:
            try:
                bases.append(ast.unparse(base))
            except Exception:
                bases.append(str(base))

        # Get decorators
        decorators = [self.parser._get_decorator_name(d) for d in node.decorator_list]

        # Create API element
        api_element = APIElement(
            name=node.name,
            type=APIType.CLASS,
            module_path=self.context.module_path,
            docstring=docstring,
            line_number=node.lineno,
            is_deprecated=is_deprecated,
            decorators=decorators,
            metadata={
                "bases": bases,
                "is_exception": any("Exception" in base for base in bases),
            },
        )

        self.api_elements.append(api_element)

        # Visit class contents with class context
        old_class = self.current_class
        self.current_class = node.name
        self.class_stack.append(node.name)

        self.generic_visit(node)

        self.current_class = old_class
        if self.class_stack:
            self.class_stack.pop()

    def visit_Assign(self, node: ast.Assign):
        """Visit assignment (for constants and properties)."""
        # Look for module-level constants
        if not self.current_class:
            for target in node.targets:
                if isinstance(target, ast.Name):
                    name = target.id

                    # Skip private constants if not included
                    if not self.parser.include_private and name.startswith("_"):
                        continue

                    # Only consider UPPERCASE names as constants
                    if name.isupper():
                        try:
                            value = ast.unparse(node.value)
                        except Exception:
                            value = str(node.value)

                        api_element = APIElement(
                            name=name,
                            type=APIType.CONSTANT,
                            module_path=self.context.module_path,
                            line_number=node.lineno,
                            metadata={"value": value},
                        )

                        self.api_elements.append(api_element)

        self.generic_visit(node)

    def visit_AnnAssign(self, node: ast.AnnAssign):
        """Visit annotated assignment."""
        # Handle type-annotated constants
        if isinstance(node.target, ast.Name) and not self.current_class:
            name = node.target.id

            # Skip private constants if not included
            if not self.parser.include_private and name.startswith("_"):
                return

            try:
                type_hint = ast.unparse(node.annotation)
            except Exception:
                type_hint = str(node.annotation)

            value = None
            if node.value:
                try:
                    value = ast.unparse(node.value)
                except Exception:
                    value = str(node.value)

            api_element = APIElement(
                name=name,
                type=APIType.CONSTANT,
                module_path=self.context.module_path,
                line_number=node.lineno,
                type_hints={"type": type_hint},
                metadata={"value": value},
            )

            self.api_elements.append(api_element)

        self.generic_visit(node)
