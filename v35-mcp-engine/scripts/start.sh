#!/bin/bash

# Trinitas v3.5 TRUE - Start Script
# Start the complete MCP orchestration system

set -e

echo "═══════════════════════════════════════════════════════════"
echo "    Trinitas v3.5 TRUE - Hybrid MCP Intelligence Platform"
echo "═══════════════════════════════════════════════════════════"
echo ""

# Check Docker
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed"
    exit 1
fi

echo "✅ Docker environment ready"
echo ""

# Check for .env file
if [ ! -f .env ]; then
    echo "⚠️  .env file not found. Creating from .env.example..."
    cp .env.example .env
    echo "Please configure .env file with your settings"
fi

# Load environment variables from .env
if [ -f .env ]; then
    export $(cat .env | grep -v '^#' | xargs)
    echo "✅ Environment variables loaded from .env"
fi

# Check critical environment variables
if [ -z "$CLAUDE_API_KEY" ]; then
    echo "⚠️  CLAUDE_API_KEY not set (Claude MCP will run in simulation mode)"
fi

if [ -z "$LOCAL_LLM_ENDPOINT" ]; then
    echo "ℹ️  Using default Local LLM endpoint from .env"
fi

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p monitoring
mkdir -p shared
mkdir -p logs

# Build and start containers
echo "🔨 Building Docker images..."
docker-compose build

echo ""
echo "🚀 Starting services..."
docker-compose up -d

# Wait for services to be ready
echo ""
echo "⏳ Waiting for services to initialize..."
sleep 10

# Check service health
echo ""
echo "🔍 Checking service health..."

check_service() {
    local service=$1
    local port=$2
    local name=$3
    
    if curl -f -s "http://localhost:$port/health" > /dev/null 2>&1; then
        echo "✅ $name is healthy"
        return 0
    else
        echo "❌ $name is not responding"
        return 1
    fi
}

# Check each service
services_healthy=true

if ! check_service "mcp-orchestrator" 8000 "MCP Orchestrator"; then
    services_healthy=false
fi

if ! check_service "claude-mcp" 8001 "Claude MCP Server"; then
    services_healthy=false
fi

if ! check_service "local-mcp" 8002 "Local MCP Server"; then
    services_healthy=false
fi

echo ""
if [ "$services_healthy" = true ]; then
    echo "✅ All services are running!"
    echo ""
    echo "📊 Service URLs:"
    echo "  - MCP Orchestrator: http://localhost:8000"
    echo "  - Claude MCP:       http://localhost:8001"
    echo "  - Local MCP:        http://localhost:8002"
    echo "  - Grafana:          http://localhost:3000 (admin/admin)"
    echo "  - Prometheus:       http://localhost:9090"
    echo ""
    echo "🧪 Run tests with: python test_mcp_system.py"
    echo "📝 View logs with: docker-compose logs -f"
    echo "🛑 Stop with:     ./stop.sh"
else
    echo "⚠️  Some services failed to start"
    echo "Check logs with: docker-compose logs"
    exit 1
fi

echo ""
echo "═══════════════════════════════════════════════════════════"
echo "    Trinitas v3.5 TRUE is ready for operation!"
echo "═══════════════════════════════════════════════════════════"