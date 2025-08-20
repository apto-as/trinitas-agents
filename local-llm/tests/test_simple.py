#!/usr/bin/env python3
"""
Simple test to diagnose the test hanging issue
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_import():
    """Test that imports work"""
    from connector.llm_connector import CognitiveComplexity
    assert CognitiveComplexity.MECHANICAL.value == 1
    print("Import test passed")

def test_simple_math():
    """Simple test that should always pass"""
    assert 2 + 2 == 4
    print("Math test passed")

if __name__ == "__main__":
    test_import()
    test_simple_math()
    print("All simple tests passed!")