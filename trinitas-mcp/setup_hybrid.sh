#!/bin/bash

# Trinitas v3.5 Hybrid Memory System Setup Script
# ハイブリッドバックエンドの自動セットアップ

set -e

echo "=========================================="
echo "Trinitas v3.5 Hybrid Memory Setup"
echo "=========================================="

# Check current directory
if [ ! -f "docker-compose.yml" ]; then
    echo "❌ Error: docker-compose.yml not found"
    echo "Please run this script from v35-mcp-tools directory"
    exit 1
fi

# Step 1: Check Docker
echo ""
echo "🐳 Step 1: Checking Docker..."
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed"
    echo "Please install Docker Desktop from: https://www.docker.com/products/docker-desktop"
    exit 1
fi

if ! docker info &> /dev/null; then
    echo "❌ Docker daemon is not running"
    echo "Please start Docker Desktop"
    exit 1
fi

echo "✅ Docker is ready"

# Step 2: Start Redis
echo ""
echo "🔴 Step 2: Starting Redis..."
docker-compose up -d redis
sleep 3

# Check Redis health
if docker-compose exec redis redis-cli ping | grep -q PONG; then
    echo "✅ Redis is running and healthy"
else
    echo "❌ Redis failed to start"
    exit 1
fi

# Step 3: Install Python dependencies
echo ""
echo "📦 Step 3: Installing Python dependencies..."

# Check if in virtual environment
if [[ "$VIRTUAL_ENV" != "" ]]; then
    echo "✅ Virtual environment detected: $VIRTUAL_ENV"
else
    echo "⚠️  No virtual environment detected"
    echo "Recommended: Create and activate a virtual environment first"
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Install dependencies
pip install redis aioredis chromadb sentence-transformers python-dotenv aiofiles

echo "✅ Python dependencies installed"

# Step 4: Setup environment file
echo ""
echo "⚙️  Step 4: Setting up environment..."

if [ ! -f .env ]; then
    cp .env.example .env
    echo "✅ Created .env file from template"
else
    echo "✅ .env file already exists"
fi

# Step 5: Initialize ChromaDB
echo ""
echo "🎨 Step 5: Initializing ChromaDB..."

python -c "
import chromadb
import os
path = os.getenv('CHROMADB_PATH', '/tmp/trinitas_chromadb')
client = chromadb.PersistentClient(path=path)
print(f'✅ ChromaDB initialized at {path}')
"

# Step 6: Test hybrid backend
echo ""
echo "🧪 Step 6: Testing hybrid backend..."

python -c "
import asyncio
import sys
sys.path.insert(0, '.')

async def test():
    from src.memory.hybrid_backend import create_hybrid_backend
    
    backend = create_hybrid_backend()
    success = await backend.initialize()
    
    if success:
        stats = await backend.get_stats()
        print('✅ Hybrid backend test successful')
        print(f'   Redis: {backend.redis_available}')
        print(f'   ChromaDB: {backend.chromadb_available}')
        print(f'   SQLite: {backend.sqlite_available}')
        return True
    else:
        print('❌ Hybrid backend test failed')
        return False

result = asyncio.run(test())
sys.exit(0 if result else 1)
"

if [ $? -eq 0 ]; then
    echo ""
    echo "=========================================="
    echo "✅ Setup Complete!"
    echo "=========================================="
    echo ""
    echo "📝 Next steps:"
    echo ""
    echo "1. Run memory system demo:"
    echo "   python v35-mcp-tools/examples/memory_system_demo.py"
    echo ""
    echo "2. Run semantic search demo:"
    echo "   python v35-mcp-tools/examples/semantic_search_demo.py"
    echo ""
    echo "3. Migrate existing memories (optional):"
    echo "   python v35-mcp-tools/scripts/migrate_to_hybrid.py"
    echo ""
    echo "4. Check Redis status:"
    echo "   docker-compose ps"
    echo ""
    echo "5. View Redis data (debug mode):"
    echo "   docker-compose --profile debug up -d redis-commander"
    echo "   Open http://localhost:8081"
    echo ""
    echo "6. Stop services:"
    echo "   docker-compose down"
    echo ""
    echo "=========================================="
else
    echo ""
    echo "❌ Setup failed. Please check the errors above."
    exit 1
fi