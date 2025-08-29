#!/bin/bash

echo "======================================"
echo "Trinitas v4.0 Installation"
echo "Memory-focused MCP Implementation"
echo "======================================"

# Check Python version
PYTHON_VERSION=$(python3 --version 2>&1 | grep -o '[0-9]\+\.[0-9]\+')
REQUIRED_VERSION="3.10"

if [ "$(printf '%s\n' "$REQUIRED_VERSION" "$PYTHON_VERSION" | sort -V | head -n1)" != "$REQUIRED_VERSION" ]; then
    echo "❌ Python $REQUIRED_VERSION+ required, but $PYTHON_VERSION found"
    exit 1
fi

echo "✅ Python version check passed ($PYTHON_VERSION)"

# Check if uv is installed
if ! command -v uv &> /dev/null; then
    echo "Installing UV package manager..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    source $HOME/.cargo/env
fi

echo "✅ UV is installed"

# Clean up any broken venv if it exists
if [ -d ".venv" ]; then
    echo "Removing existing virtual environment..."
    rm -rf .venv
fi

# Create fresh virtual environment with uv
echo "Creating fresh Python virtual environment..."
uv venv

# Install dependencies with uv
echo "Installing dependencies with UV..."
uv pip install --quiet fastmcp==2.11.3
uv pip install --quiet redis chromadb sqlite-utils
uv pip install --quiet python-dotenv numpy

# Create necessary directories
echo "Creating directory structure..."
mkdir -p learning_data/{patterns,models,metrics,insights}
mkdir -p chromadb_data
mkdir -p logs

# Initialize SQLite database
echo "Initializing SQLite database..."
python3 -c "
import sqlite3
from pathlib import Path

db_path = Path('./sqlite_data.db')
conn = sqlite3.connect(str(db_path))
cursor = conn.cursor()

# Create memory_store table
cursor.execute('''
    CREATE TABLE IF NOT EXISTS memory_store (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        key TEXT UNIQUE NOT NULL,
        value TEXT NOT NULL,
        metadata TEXT,
        section TEXT,
        persona TEXT,
        importance REAL DEFAULT 0.5,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        accessed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        access_count INTEGER DEFAULT 0
    )
''')

# Create indices
cursor.execute('CREATE INDEX IF NOT EXISTS idx_key ON memory_store(key);')
cursor.execute('CREATE INDEX IF NOT EXISTS idx_persona ON memory_store(persona);')
cursor.execute('CREATE INDEX IF NOT EXISTS idx_importance ON memory_store(importance);')

conn.commit()
conn.close()
print('✅ SQLite database initialized')
"

# Check Redis (optional)
echo "Checking Redis connection..."
python3 -c "
import redis
import sys
try:
    r = redis.from_url('redis://localhost:6379')
    r.ping()
    print('✅ Redis connection successful')
except:
    print('⚠️  Redis not available - will use SQLite fallback')
" 2>/dev/null || echo "⚠️  Redis not available - will use SQLite fallback"

# Run tests
echo ""
echo "Running v4.0 tests..."
python3 test_v4.py 2>/dev/null | grep -A 10 "Test Summary"

echo ""
echo "======================================"
echo "✅ Trinitas v4.0 installation complete"
echo "======================================"
echo ""
echo "To start the MCP server:"
echo "  uv run python src/mcp_server_v4.py"
echo ""
echo "Configuration file: config/.env"
echo "Test suite: uv run python test_v4.py"
echo ""