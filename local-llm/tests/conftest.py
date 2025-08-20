"""
Pytest configuration for Trinitas v3.5 tests
"""
import sys
import os
from pathlib import Path

# Add local-llm directory to Python path
test_dir = Path(__file__).parent
local_llm_dir = test_dir.parent
sys.path.insert(0, str(local_llm_dir))