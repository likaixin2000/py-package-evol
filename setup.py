#!/usr/bin/env python3
"""Setup script for pypevol package."""

from setuptools import setup, find_packages
import os


# Read README file
def read_readme():
    readme_path = os.path.join(os.path.dirname(__file__), "README.md")
    if os.path.exists(readme_path):
        with open(readme_path, "r", encoding="utf-8") as f:
            return f.read()
    return ""


setup(
    name="pypevol",
    use_scm_version=True,
    setup_requires=["setuptools_scm"],
    author="pypevol Team",
    author_email="likaixin@u.nus.edu",
    description="A package to analyze PyPI package API evolution and lifecycle",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/likaixin2000/py-package-evol",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.8",
    install_requires=[
        "requests>=2.25.0",
        "beautifulsoup4>=4.9.0",
        "lxml>=4.6.0",
        "packaging>=21.0",
        "ast_tools>=0.1.0",
        "jinja2>=3.0.0",
        "click>=8.0.0",
        "plotly>=5.0.0",
        "pandas>=1.3.0",
        "colorama>=0.4.0",
        "tqdm>=4.60.0",
    ],
    extras_require={
        "dev": [
            "pytest>=6.0.0",
            "pytest-cov>=2.12.0",
            "black>=21.0.0",
            "flake8>=3.9.0",
            "mypy>=0.910",
            "isort>=5.0.0",
            "mkdocs>=1.5.0",
            "mkdocs-material>=9.0.0",
            "mkdocs-mermaid2-plugin>=0.6.0",
            "build>=0.8.0",
            "twine>=4.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "pypevol=pypevol.cli:main",
        ],
    },
    include_package_data=True,
    package_data={
        "pypevol": ["templates/*.html", "templates/*.css", "templates/*.js"],
    },
)
