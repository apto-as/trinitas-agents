#!/bin/bash

# Trinitas v3.5 - Test Runner
# Runs all integration and unit tests

set -e

echo "🧪 Trinitas v3.5 - Running Tests"
echo "================================"

# Set Python path
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

# Check if pytest is installed
if ! command -v pytest &> /dev/null; then
    echo "⚠️  pytest not found. Installing..."
    pip install pytest pytest-asyncio pytest-cov
fi

# Run unit tests
echo ""
echo "📦 Running Unit Tests..."
echo "------------------------"
pytest local-llm/tests/test_connector.py -v
pytest local-llm/tests/test_delegation.py -v

# Run integration tests
echo ""
echo "🔄 Running Integration Tests..."
echo "-------------------------------"
pytest local-llm/tests/test_integration.py -v

# Run with coverage if requested
if [ "$1" == "--coverage" ]; then
    echo ""
    echo "📊 Running with Coverage..."
    echo "--------------------------"
    pytest local-llm/tests/ \
        --cov=local-llm \
        --cov-report=html \
        --cov-report=term-missing \
        -v
    echo "Coverage report generated in htmlcov/"
fi

# Performance tests (optional)
if [ "$1" == "--performance" ]; then
    echo ""
    echo "⚡ Running Performance Tests..."
    echo "------------------------------"
    pytest local-llm/tests/test_integration.py::TestPerformance -v
fi

echo ""
echo "✅ All tests completed!"
echo ""

# Show summary
echo "📈 Test Summary:"
echo "---------------"
pytest local-llm/tests/ --co -q | tail -n 5