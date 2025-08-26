#!/bin/bash

# Trinitas v3.5 TRUE - Production Deployment Script
# Complete deployment automation for hybrid MCP intelligence platform

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
DEPLOYMENT_ENV="${1:-production}"
ACTION="${2:-deploy}"

echo -e "${BLUE}╔════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║     Trinitas v3.5 TRUE Deployment         ║${NC}"
echo -e "${BLUE}║     Hybrid MCP Intelligence Platform      ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════╝${NC}"
echo

# Function to check prerequisites
check_prerequisites() {
    echo -e "${YELLOW}Checking prerequisites...${NC}"
    
    # Check Docker
    if ! command -v docker &> /dev/null; then
        echo -e "${RED}Error: Docker is not installed${NC}"
        exit 1
    fi
    
    # Check Docker Compose
    if ! command -v docker-compose &> /dev/null; then
        echo -e "${RED}Error: Docker Compose is not installed${NC}"
        exit 1
    fi
    
    # Check environment file
    if [ "$DEPLOYMENT_ENV" = "production" ]; then
        if [ ! -f ".env.prod" ]; then
            echo -e "${RED}Error: .env.prod not found. Copy .env.prod.template and configure it.${NC}"
            exit 1
        fi
    else
        if [ ! -f ".env" ]; then
            echo -e "${RED}Error: .env not found${NC}"
            exit 1
        fi
    fi
    
    echo -e "${GREEN}✓ Prerequisites checked${NC}"
}

# Function to build images
build_images() {
    echo -e "${YELLOW}Building Docker images...${NC}"
    
    if [ "$DEPLOYMENT_ENV" = "production" ]; then
        docker-compose -f docker-compose.prod.yml build --parallel
    else
        docker-compose build --parallel
    fi
    
    echo -e "${GREEN}✓ Images built successfully${NC}"
}

# Function to run tests
run_tests() {
    echo -e "${YELLOW}Running integration tests...${NC}"
    
    # Start test environment
    docker-compose -f docker-compose.yml up -d redis
    sleep 5
    
    # Run tests
    docker run --rm \
        --network v35-true_default \
        -v $(pwd):/app \
        -w /app \
        python:3.9 \
        bash -c "pip install pytest pytest-asyncio && python tests/test_v35_integration.py"
    
    # Cleanup test environment
    docker-compose down
    
    echo -e "${GREEN}✓ All tests passed${NC}"
}

# Function to deploy services
deploy_services() {
    echo -e "${YELLOW}Deploying services...${NC}"
    
    if [ "$DEPLOYMENT_ENV" = "production" ]; then
        # Production deployment with health checks
        docker-compose -f docker-compose.prod.yml up -d
        
        # Wait for services to be healthy
        echo -e "${YELLOW}Waiting for services to be healthy...${NC}"
        sleep 10
        
        # Check health status
        for service in mcp-orchestrator claude-mcp local-mcp redis; do
            if docker-compose -f docker-compose.prod.yml ps | grep $service | grep -q "healthy"; then
                echo -e "${GREEN}✓ $service is healthy${NC}"
            else
                echo -e "${YELLOW}⚠ $service is starting...${NC}"
            fi
        done
    else
        # Development deployment
        docker-compose up -d
    fi
    
    echo -e "${GREEN}✓ Services deployed${NC}"
}

# Function to setup monitoring
setup_monitoring() {
    echo -e "${YELLOW}Setting up monitoring...${NC}"
    
    if [ "$DEPLOYMENT_ENV" = "production" ]; then
        # Wait for Grafana to be ready
        echo "Waiting for Grafana..."
        until curl -s http://localhost:3000/api/health > /dev/null; do
            sleep 2
        done
        
        echo -e "${GREEN}✓ Monitoring is available at:${NC}"
        echo "  - Grafana: http://localhost:3000"
        echo "  - Prometheus: http://localhost:9090"
        echo "  - Loki: http://localhost:3100"
    fi
}

# Function to show status
show_status() {
    echo -e "${YELLOW}Service Status:${NC}"
    
    if [ "$DEPLOYMENT_ENV" = "production" ]; then
        docker-compose -f docker-compose.prod.yml ps
    else
        docker-compose ps
    fi
    
    echo
    echo -e "${YELLOW}Resource Usage:${NC}"
    docker stats --no-stream
}

# Function to show logs
show_logs() {
    echo -e "${YELLOW}Recent logs:${NC}"
    
    if [ "$DEPLOYMENT_ENV" = "production" ]; then
        docker-compose -f docker-compose.prod.yml logs --tail=50
    else
        docker-compose logs --tail=50
    fi
}

# Function to stop services
stop_services() {
    echo -e "${YELLOW}Stopping services...${NC}"
    
    if [ "$DEPLOYMENT_ENV" = "production" ]; then
        docker-compose -f docker-compose.prod.yml down
    else
        docker-compose down
    fi
    
    echo -e "${GREEN}✓ Services stopped${NC}"
}

# Function to clean up
cleanup() {
    echo -e "${YELLOW}Cleaning up...${NC}"
    
    if [ "$DEPLOYMENT_ENV" = "production" ]; then
        docker-compose -f docker-compose.prod.yml down -v
    else
        docker-compose down -v
    fi
    
    # Remove unused images
    docker image prune -f
    
    echo -e "${GREEN}✓ Cleanup complete${NC}"
}

# Function to backup data
backup_data() {
    echo -e "${YELLOW}Creating backup...${NC}"
    
    BACKUP_DIR="backups/$(date +%Y%m%d_%H%M%S)"
    mkdir -p $BACKUP_DIR
    
    # Backup Redis data
    docker exec trinitas-redis redis-cli BGSAVE
    sleep 2
    docker cp trinitas-redis:/data/dump.rdb $BACKUP_DIR/redis_dump.rdb
    
    # Backup configurations
    cp -r config $BACKUP_DIR/
    cp .env* $BACKUP_DIR/
    
    # Create tarball
    tar -czf $BACKUP_DIR.tar.gz $BACKUP_DIR
    rm -rf $BACKUP_DIR
    
    echo -e "${GREEN}✓ Backup created: $BACKUP_DIR.tar.gz${NC}"
}

# Function to restore from backup
restore_backup() {
    BACKUP_FILE="$1"
    
    if [ -z "$BACKUP_FILE" ]; then
        echo -e "${RED}Error: Backup file not specified${NC}"
        exit 1
    fi
    
    echo -e "${YELLOW}Restoring from backup: $BACKUP_FILE${NC}"
    
    # Extract backup
    tar -xzf $BACKUP_FILE
    BACKUP_DIR="${BACKUP_FILE%.tar.gz}"
    
    # Restore Redis data
    docker cp $BACKUP_DIR/redis_dump.rdb trinitas-redis:/data/dump.rdb
    docker exec trinitas-redis redis-cli SHUTDOWN
    docker-compose -f docker-compose.prod.yml restart redis
    
    # Restore configurations
    cp -r $BACKUP_DIR/config/* config/
    
    # Cleanup
    rm -rf $BACKUP_DIR
    
    echo -e "${GREEN}✓ Restore complete${NC}"
}

# Main execution
case "$ACTION" in
    deploy)
        check_prerequisites
        build_images
        if [ "$DEPLOYMENT_ENV" = "production" ]; then
            run_tests
        fi
        deploy_services
        setup_monitoring
        show_status
        
        echo
        echo -e "${GREEN}════════════════════════════════════════════${NC}"
        echo -e "${GREEN}Deployment complete!${NC}"
        echo
        echo -e "${BLUE}Access points:${NC}"
        echo "  - Orchestrator: http://localhost:8000"
        echo "  - Claude MCP: http://localhost:8001"
        echo "  - Local MCP: http://localhost:8002"
        if [ "$DEPLOYMENT_ENV" = "production" ]; then
            echo "  - Grafana: http://localhost:3000"
            echo "  - Prometheus: http://localhost:9090"
        fi
        echo -e "${GREEN}════════════════════════════════════════════${NC}"
        ;;
        
    test)
        check_prerequisites
        run_tests
        ;;
        
    status)
        show_status
        ;;
        
    logs)
        show_logs
        ;;
        
    stop)
        stop_services
        ;;
        
    restart)
        stop_services
        deploy_services
        ;;
        
    clean)
        cleanup
        ;;
        
    backup)
        backup_data
        ;;
        
    restore)
        restore_backup "$3"
        ;;
        
    *)
        echo "Usage: $0 [production|development] [deploy|test|status|logs|stop|restart|clean|backup|restore]"
        echo
        echo "Commands:"
        echo "  deploy   - Build and deploy all services"
        echo "  test     - Run integration tests"
        echo "  status   - Show service status"
        echo "  logs     - Show recent logs"
        echo "  stop     - Stop all services"
        echo "  restart  - Restart all services"
        echo "  clean    - Stop services and remove volumes"
        echo "  backup   - Create backup of data and configs"
        echo "  restore  - Restore from backup (specify file)"
        echo
        echo "Examples:"
        echo "  $0 production deploy    # Deploy to production"
        echo "  $0 development test      # Run tests in development"
        echo "  $0 production backup     # Create production backup"
        exit 1
        ;;
esac