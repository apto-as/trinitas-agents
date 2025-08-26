#!/bin/bash

# Trinitas v3.5 MCP Engine Startup Script

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}  Trinitas v3.5 MCP Engine Launcher${NC}"
echo -e "${GREEN}========================================${NC}"

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to check if port is available
check_port() {
    local port=$1
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
        echo -e "${YELLOW}Warning: Port $port is already in use${NC}"
        return 1
    fi
    return 0
}

# Parse command line arguments
MODE="standalone"
USE_DOCKER=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --docker)
            USE_DOCKER=true
            shift
            ;;
        --mode)
            MODE="$2"
            shift 2
            ;;
        --help)
            echo "Usage: $0 [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  --docker       Use Docker Compose to run all services"
            echo "  --mode MODE    Set engine mode (standalone|integrated|distributed)"
            echo "  --help         Show this help message"
            exit 0
            ;;
        *)
            echo -e "${RED}Unknown option: $1${NC}"
            exit 1
            ;;
    esac
done

if [ "$USE_DOCKER" = true ]; then
    echo -e "${YELLOW}Starting MCP Engine with Docker Compose...${NC}"
    
    # Check if Docker is installed
    if ! command_exists docker; then
        echo -e "${RED}Error: Docker is not installed${NC}"
        exit 1
    fi
    
    if ! command_exists docker-compose; then
        echo -e "${RED}Error: Docker Compose is not installed${NC}"
        exit 1
    fi
    
    # Build and start services
    echo -e "${GREEN}Building Docker images...${NC}"
    docker-compose build
    
    echo -e "${GREEN}Starting services...${NC}"
    docker-compose up -d
    
    # Wait for services to be healthy
    echo -e "${YELLOW}Waiting for services to be ready...${NC}"
    sleep 5
    
    # Check health
    if curl -s http://localhost:8000/health | grep -q '"healthy":true'; then
        echo -e "${GREEN}✓ MCP Engine is running and healthy!${NC}"
        echo -e "${GREEN}  API: http://localhost:8000${NC}"
        echo -e "${GREEN}  Metrics: http://localhost:9090${NC}"
        echo -e "${GREEN}  Grafana: http://localhost:3000 (admin/admin)${NC}"
    else
        echo -e "${RED}✗ MCP Engine health check failed${NC}"
        echo -e "${YELLOW}Check logs: docker-compose logs mcp-engine${NC}"
    fi
    
else
    echo -e "${YELLOW}Starting MCP Engine in standalone mode...${NC}"
    
    # Check Python version
    if ! command_exists python3; then
        echo -e "${RED}Error: Python 3 is not installed${NC}"
        exit 1
    fi
    
    PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
    echo -e "${GREEN}Python version: $PYTHON_VERSION${NC}"
    
    # Check if virtual environment exists
    if [ ! -d "venv" ]; then
        echo -e "${YELLOW}Creating virtual environment...${NC}"
        python3 -m venv venv
    fi
    
    # Activate virtual environment
    source venv/bin/activate
    
    # Install dependencies
    echo -e "${YELLOW}Installing dependencies...${NC}"
    pip install -q --upgrade pip
    pip install -q -r requirements.txt
    
    # Check required ports
    echo -e "${YELLOW}Checking ports...${NC}"
    check_port 8000 || exit 1
    check_port 9090 || true  # Metrics port is optional
    
    # Set environment variables
    export ENGINE_MODE=$MODE
    export ENGINE_HOST=0.0.0.0
    export ENGINE_PORT=8000
    export ENABLE_AUTH=false
    export LOG_LEVEL=INFO
    
    # Check for Redis (optional but recommended)
    if command_exists redis-cli; then
        if redis-cli ping >/dev/null 2>&1; then
            echo -e "${GREEN}✓ Redis is available${NC}"
            export REDIS_URL=redis://localhost:6379
        else
            echo -e "${YELLOW}⚠ Redis is not running (coordination features disabled)${NC}"
        fi
    else
        echo -e "${YELLOW}⚠ Redis not installed (coordination features disabled)${NC}"
    fi
    
    # Check for Local LLM endpoint
    if [ -n "$LOCAL_LLM_ENDPOINT" ]; then
        echo -e "${GREEN}✓ Local LLM endpoint configured: $LOCAL_LLM_ENDPOINT${NC}"
    else
        echo -e "${YELLOW}⚠ Local LLM endpoint not configured${NC}"
        echo -e "${YELLOW}  Set LOCAL_LLM_ENDPOINT to connect to LM Studio or other local LLM${NC}"
    fi
    
    # Start the engine
    echo -e "${GREEN}Starting MCP Engine...${NC}"
    echo -e "${GREEN}========================================${NC}"
    
    # Run with uvicorn for better performance
    uvicorn src.api.main:app \
        --host $ENGINE_HOST \
        --port $ENGINE_PORT \
        --log-level ${LOG_LEVEL,,} \
        --reload
fi