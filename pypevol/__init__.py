"""PyPevol - PyPI Package API Evolution Analyzer."""

__version__ = "0.1.0"
__author__ = "PyPevol Team"
__email__ = "pypevol@example.com"

from .analyzer import PackageAnalyzer
from .models import APIElement, VersionInfo, AnalysisResult
from .fetcher import PyPIFetcher
from .parser import SourceParser

__all__ = [
    "PackageAnalyzer",
    "APIElement",
    "VersionInfo",
    "AnalysisResult",
    "PyPIFetcher",
    "SourceParser",
]
