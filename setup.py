"""
Setup configuration for Trinitas Agents Python package
=======================================================

This setup file enables proper Python package installation,
eliminating the need for sys.path manipulation.

Installation:
    pip install -e .  # Development installation
    pip install .     # Production installation
"""

from setuptools import setup, find_packages
import os

# Read README for long description
def read_long_description():
    """Read README.md for package long description."""
    readme_path = os.path.join(os.path.dirname(__file__), 'README.md')
    if os.path.exists(readme_path):
        with open(readme_path, 'r', encoding='utf-8') as f:
            return f.read()
    return "Trinitas Agents - Three Minds, One Purpose, Infinite Possibilities"

# Read requirements
def read_requirements():
    """Read requirements from requirements.txt."""
    req_path = os.path.join(os.path.dirname(__file__), 'requirements.txt')
    if os.path.exists(req_path):
        with open(req_path, 'r', encoding='utf-8') as f:
            return [line.strip() for line in f if line.strip() and not line.startswith('#')]
    return []

setup(
    name="trinitas-agents",
    version="3.0.0",
    author="Trinitas Core Team",
    author_email="trinitas@example.com",
    description="Advanced AI agent system for Claude Code with Trinity integration",
    long_description=read_long_description(),
    long_description_content_type="text/markdown",
    url="https://github.com/apto-as/trinitas-agents",
    packages=find_packages(where="hooks/python"),
    package_dir={"": "hooks/python"},
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
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
        "typing-extensions>=4.0.0",
        "dataclasses>=0.6; python_version<'3.7'",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-asyncio>=0.21.0",
            "pytest-cov>=4.0.0",
            "mypy>=1.0.0",
            "ruff>=0.1.0",
            "black>=23.0.0",
        ],
        "mcp": [
            # MCP dependencies when available
            # Currently using mock implementation
        ],
    },
    entry_points={
        "console_scripts": [
            "trinitas-hook=trinitas_hooks.cli:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
)