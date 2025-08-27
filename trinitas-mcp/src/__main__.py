#!/usr/bin/env python3
"""
Trinitas MCP Server Entry Point
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from mcp_server_fastmcp import mcp

if __name__ == "__main__":
    mcp.run()