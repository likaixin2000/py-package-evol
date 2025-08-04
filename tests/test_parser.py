"""Tests for PyMevol Plus source parser."""

import unittest
import tempfile
import textwrap
from pathlib import Path

from pymevol.parser import SourceParser
from pymevol.models import APIType


class TestSourceParser(unittest.TestCase):
    """Test SourceParser class."""
    
    def setUp(self):
        """Set up test parser."""
        self.parser = SourceParser(include_private=True, include_deprecated=True)
    
    def test_parse_function(self):
        """Test parsing function definitions."""
        code = textwrap.dedent('''
        def simple_function():
            """A simple function."""
            pass
        
        def function_with_params(arg1: str, arg2: int = 5) -> bool:
            """Function with parameters and type hints."""
            return True
        ''')
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(code)
            f.flush()
            
            elements = self.parser.parse_file(Path(f.name), "test.module")
        
        # Clean up
        Path(f.name).unlink()
        
        self.assertEqual(len(elements), 2)
        
        simple_func = next(e for e in elements if e.name == "simple_function")
        self.assertEqual(simple_func.type, APIType.FUNCTION)
        self.assertEqual(simple_func.docstring, "A simple function.")
        
        param_func = next(e for e in elements if e.name == "function_with_params")
        self.assertEqual(param_func.type, APIType.FUNCTION)
        self.assertIn("arg1", param_func.type_hints)
        self.assertIn("return", param_func.type_hints)
    
    def test_parse_class(self):
        """Test parsing class definitions."""
        code = textwrap.dedent('''
        class SimpleClass:
            """A simple class."""
            pass
        
        class InheritedClass(SimpleClass):
            """A class with inheritance."""
            
            def method(self):
                """A method."""
                pass
            
            @property
            def prop(self):
                """A property."""
                return 42
        ''')
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(code)
            f.flush()
            
            elements = self.parser.parse_file(Path(f.name), "test.module")
        
        Path(f.name).unlink()
        
        classes = [e for e in elements if e.type == APIType.CLASS]
        methods = [e for e in elements if e.type == APIType.METHOD]
        
        self.assertEqual(len(classes), 2)
        self.assertEqual(len(methods), 2)  # method and property getter
        
        simple_class = next(e for e in classes if e.name == "SimpleClass")
        self.assertEqual(simple_class.docstring, "A simple class.")
        
        inherited_class = next(e for e in classes if e.name == "InheritedClass")
        self.assertIn("SimpleClass", inherited_class.metadata.get('bases', []))
    
    def test_parse_constants(self):
        """Test parsing module constants."""
        code = textwrap.dedent('''
        # Module constants
        VERSION = "1.0.0"
        DEBUG_MODE = True
        MAX_CONNECTIONS = 100
        
        # Type annotated constant
        API_URL: str = "https://api.example.com"
        
        # Not a constant (lowercase)
        config = {}
        ''')
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(code)
            f.flush()
            
            elements = self.parser.parse_file(Path(f.name), "test.module")
        
        Path(f.name).unlink()
        
        constants = [e for e in elements if e.type == APIType.CONSTANT]
        
        # Should find VERSION, DEBUG_MODE, MAX_CONNECTIONS, and API_URL
        self.assertEqual(len(constants), 4)
        
        version_const = next(e for e in constants if e.name == "VERSION")
        self.assertEqual(version_const.metadata.get('value'), '"1.0.0"')
        
        api_url_const = next(e for e in constants if e.name == "API_URL")
        self.assertEqual(api_url_const.type_hints.get('type'), 'str')
    
    def test_private_api_filtering(self):
        """Test filtering of private APIs."""
        code = textwrap.dedent('''
        def public_function():
            pass
        
        def _private_function():
            pass
        
        def __dunder_function__():
            pass
        
        class PublicClass:
            def public_method(self):
                pass
            
            def _private_method(self):
                pass
        ''')
        
        # Test with private APIs included
        parser_with_private = SourceParser(include_private=True)
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(code)
            f.flush()
            
            elements_with_private = parser_with_private.parse_file(Path(f.name), "test.module")
        
        # Test with private APIs excluded
        parser_without_private = SourceParser(include_private=False)
        elements_without_private = parser_without_private.parse_file(Path(f.name), "test.module")
        
        Path(f.name).unlink()
        
        # With private APIs, should find all functions and methods
        public_funcs_with = [e for e in elements_with_private if e.type == APIType.FUNCTION and not e.name.startswith('_')]
        private_funcs_with = [e for e in elements_with_private if e.type == APIType.FUNCTION and e.name.startswith('_')]
        
        self.assertEqual(len(public_funcs_with), 1)  # public_function
        self.assertEqual(len(private_funcs_with), 2)  # _private_function, __dunder_function__
        
        # Without private APIs, should only find public ones
        public_funcs_without = [e for e in elements_without_private if e.type == APIType.FUNCTION]
        
        self.assertEqual(len(public_funcs_without), 1)  # Only public_function
    
    def test_deprecated_api_detection(self):
        """Test detection of deprecated APIs."""
        code = textwrap.dedent('''
        @deprecated
        def old_function():
            pass
        
        def new_function():
            """
            This is a new function.
            
            .. deprecated:: 1.5
                Use new_better_function instead.
            """
            pass
        
        def another_function():
            """DEPRECATED: This function is deprecated."""
            pass
        ''')
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(code)
            f.flush()
            
            elements = self.parser.parse_file(Path(f.name), "test.module")
        
        Path(f.name).unlink()
        
        deprecated_funcs = [e for e in elements if e.is_deprecated]
        
        # Should detect deprecation in decorator, docstring, and function name
        self.assertEqual(len(deprecated_funcs), 3)
        
        old_func = next(e for e in deprecated_funcs if e.name == "old_function")
        self.assertIn("deprecated", old_func.decorators)


if __name__ == '__main__':
    unittest.main()
