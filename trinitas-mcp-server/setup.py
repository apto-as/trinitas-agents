#!/usr/bin/env python3
"""
Trinity Hybrid MCP Server
Optimized for Claude, Compatible with All
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read the README
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

setup(
    name="trinitas-mcp-server",
    version="1.0.0",
    author="Trinitas-Core",
    author_email="trinitas@cafe-zuccaro.local",
    description="Trinity Hybrid MCP Server - Three-persona thinking framework for any LLM",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/apto-as/trinitas-agents",
    packages=find_packages(where="hybrid-mcp"),
    package_dir={"": "hybrid-mcp"},
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Application Frameworks",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.10",
    install_requires=[
        "fastmcp>=2.9.0",
    ],
    extras_require={
        "dev": [
            "pytest>=8.0.0",
            "pytest-asyncio>=1.0.0",
            "black>=23.0.0",
            "ruff>=0.1.0",
            "mypy>=1.0.0",
        ],
        "llm": [
            "openai",  # For LMStudio integration
        ],
    },
    entry_points={
        "console_scripts": [
            "trinity-mcp=hybrid_mcp.core.hybrid_server:main",
        ],
    },
    include_package_data=True,
    package_data={
        "": ["*.md", "personas/*.md"],
    },
)