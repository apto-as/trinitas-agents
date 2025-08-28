#!/bin/bash

echo "======================================"
echo "Trinitas v4.0 Installation"
echo "Memory-focused MCP Implementation"
echo "======================================"

# Check Python version
PYTHON_VERSION=$(python3 --version 2>&1 | grep -oP '\d+\.\d+')
REQUIRED_VERSION="3.10"

if [ "$(printf '%s\n' "$REQUIRED_VERSION" "$PYTHON_VERSION" | sort -V | head -n1)" != "$REQUIRED_VERSION" ]; then
    echo "❌ Python $REQUIRED_VERSION+ required, but $PYTHON_VERSION found"
    exit 1
fi

echo "✅ Python version check passed ($PYTHON_VERSION)"

# Create virtual environment
echo "Creating virtual environment..."
if [ -d ".venv" ]; then
    echo "  Removing existing .venv..."
    rm -rf .venv
fi

python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install --quiet --upgrade pip
pip install --quiet fastmcp==2.11.3
pip install --quiet redis chromadb sqlite-utils
pip install --quiet python-dotenv numpy

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
echo "  python3 src/mcp_server_v4.py"
echo ""
echo "Configuration file: config/.env"
echo "Test suite: python3 test_v4.py"
echo ""