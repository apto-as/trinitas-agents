#!/usr/bin/env python3
"""
Trinitas MCP Server Entry Point
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from mcp_server import main

if __name__ == "__main__":
    main()