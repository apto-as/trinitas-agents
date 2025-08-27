#!/bin/bash

# Trinitas v3.5 Production Deployment Script
# Complete deployment automation for production environment

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
DEPLOYMENT_DIR="/opt/trinitas-v35"
LOG_DIR="/var/log/trinitas"
CONFIG_DIR="/etc/trinitas"
SERVICE_NAME="trinitas-mcp"
PYTHON_VERSION="3.9"

# Functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# Check prerequisites
check_prerequisites() {
    log_info "Checking prerequisites..."
    
    # Check Python version
    if ! python3 --version | grep -q "$PYTHON_VERSION"; then
        log_error "Python $PYTHON_VERSION is required"
        exit 1
    fi
    
    # Check Docker
    if ! command -v docker &> /dev/null; then
        log_error "Docker is not installed"
        exit 1
    fi
    
    # Check Redis (optional)
    if command -v redis-cli &> /dev/null; then
        log_info "Redis detected - will enable distributed caching"
        REDIS_ENABLED=true
    else
        log_warning "Redis not found - distributed caching disabled"
        REDIS_ENABLED=false
    fi
    
    log_success "Prerequisites check passed"
}

# Create directory structure
setup_directories() {
    log_info "Setting up directory structure..."
    
    sudo mkdir -p $DEPLOYMENT_DIR
    sudo mkdir -p $LOG_DIR
    sudo mkdir -p $CONFIG_DIR
    sudo mkdir -p $DEPLOYMENT_DIR/cache
    sudo mkdir -p $DEPLOYMENT_DIR/sessions
    sudo mkdir -p $DEPLOYMENT_DIR/backups
    
    # Set permissions
    sudo chown -R $USER:$USER $DEPLOYMENT_DIR
    sudo chown -R $USER:$USER $LOG_DIR
    
    log_success "Directories created"
}

# Copy application files
deploy_application() {
    log_info "Deploying application files..."
    
    # Copy core files
    cp -r *.py $DEPLOYMENT_DIR/
    cp -r examples/ $DEPLOYMENT_DIR/
    cp -r tests/ $DEPLOYMENT_DIR/
    
    # Copy configuration
    if [ -f "config/production.env" ]; then
        cp config/production.env $CONFIG_DIR/trinitas.env
    fi
    
    log_success "Application deployed to $DEPLOYMENT_DIR"
}

# Install dependencies
install_dependencies() {
    log_info "Installing Python dependencies..."
    
    cd $DEPLOYMENT_DIR
    
    # Create virtual environment
    python3 -m venv venv
    source venv/bin/activate
    
    # Upgrade pip
    pip install --upgrade pip
    
    # Install dependencies
    cat > requirements.txt << EOF
fastmcp>=0.1.0
asyncio>=3.4.3
redis>=4.5.0
psutil>=5.9.0
aiofiles>=23.0.0
pyyaml>=6.0
pytest>=7.0.0
pytest-asyncio>=0.21.0
EOF
    
    pip install -r requirements.txt
    
    log_success "Dependencies installed"
}

# Configure environment
configure_environment() {
    log_info "Configuring environment..."
    
    # Create production environment file if not exists
    if [ ! -f "$CONFIG_DIR/trinitas.env" ]; then
        cat > $CONFIG_DIR/trinitas.env << EOF
# Trinitas v3.5 Production Configuration
TRINITAS_MODE=production
LOG_LEVEL=INFO
MAX_WORKERS=10
CACHE_TTL=3600
MEMORY_LIMIT_MB=512
DISK_CACHE_DIR=$DEPLOYMENT_DIR/cache
SESSION_DIR=$DEPLOYMENT_DIR/sessions

# Redis Configuration
REDIS_ENABLED=$REDIS_ENABLED
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0

# Performance Settings
BATCH_SIZE=50
BATCH_TIMEOUT=0.1
DEDUP_WINDOW=60

# Security Settings
API_KEY_REQUIRED=true
RATE_LIMIT=1000
SSL_ENABLED=true
EOF
    fi
    
    log_success "Environment configured"
}

# Setup systemd service
setup_service() {
    log_info "Setting up systemd service..."
    
    sudo cat > /etc/systemd/system/$SERVICE_NAME.service << EOF
[Unit]
Description=Trinitas v3.5 MCP Server
After=network.target redis.service
Wants=redis.service

[Service]
Type=simple
User=$USER
WorkingDirectory=$DEPLOYMENT_DIR
Environment="PATH=$DEPLOYMENT_DIR/venv/bin"
EnvironmentFile=$CONFIG_DIR/trinitas.env
ExecStart=$DEPLOYMENT_DIR/venv/bin/python $DEPLOYMENT_DIR/mcp_server_enhanced.py
Restart=always
RestartSec=10
StandardOutput=append:$LOG_DIR/trinitas.log
StandardError=append:$LOG_DIR/trinitas-error.log

[Install]
WantedBy=multi-user.target
EOF
    
    # Reload systemd and enable service
    sudo systemctl daemon-reload
    sudo systemctl enable $SERVICE_NAME
    
    log_success "Service configured"
}

# Setup Docker containers (optional)
setup_docker() {
    log_info "Setting up Docker containers..."
    
    if [ -f "docker-compose.production.yml" ]; then
        docker-compose -f docker-compose.production.yml up -d
        log_success "Docker containers started"
    else
        log_warning "docker-compose.production.yml not found - skipping Docker setup"
    fi
}

# Setup monitoring
setup_monitoring() {
    log_info "Setting up monitoring..."
    
    # Create monitoring script
    cat > $DEPLOYMENT_DIR/monitor.sh << 'EOF'
#!/bin/bash
# Simple monitoring script

while true; do
    # Check service status
    if systemctl is-active --quiet trinitas-mcp; then
        echo "$(date): Service running"
    else
        echo "$(date): Service down - attempting restart"
        systemctl restart trinitas-mcp
    fi
    
    # Check memory usage
    MEM_USAGE=$(ps aux | grep mcp_server | awk '{sum+=$6} END {print sum/1024}')
    echo "$(date): Memory usage: ${MEM_USAGE}MB"
    
    # Check cache hit rate
    CACHE_STATS=$(curl -s http://localhost:8080/metrics | grep cache_hit_rate)
    echo "$(date): $CACHE_STATS"
    
    sleep 60
done
EOF
    
    chmod +x $DEPLOYMENT_DIR/monitor.sh
    
    log_success "Monitoring configured"
}

# Run health checks
run_health_checks() {
    log_info "Running health checks..."
    
    cd $DEPLOYMENT_DIR
    source venv/bin/activate
    
    # Test import
    python3 -c "import trinitas_mcp_tools; print('Import test: OK')"
    
    # Test basic functionality
    python3 quick_test.py
    
    log_success "Health checks passed"
}

# Start service
start_service() {
    log_info "Starting Trinitas service..."
    
    sudo systemctl start $SERVICE_NAME
    
    # Wait for service to start
    sleep 5
    
    # Check status
    if systemctl is-active --quiet $SERVICE_NAME; then
        log_success "Service started successfully"
        sudo systemctl status $SERVICE_NAME --no-pager
    else
        log_error "Service failed to start"
        sudo journalctl -u $SERVICE_NAME -n 50 --no-pager
        exit 1
    fi
}

# Main deployment flow
main() {
    echo "=================================================="
    echo "   Trinitas v3.5 Production Deployment"
    echo "=================================================="
    echo
    
    check_prerequisites
    setup_directories
    deploy_application
    install_dependencies
    configure_environment
    setup_service
    setup_docker
    setup_monitoring
    run_health_checks
    start_service
    
    echo
    echo "=================================================="
    log_success "Deployment completed successfully!"
    echo
    echo "Service: $SERVICE_NAME"
    echo "Status: $(systemctl is-active $SERVICE_NAME)"
    echo "Logs: $LOG_DIR/trinitas.log"
    echo "Config: $CONFIG_DIR/trinitas.env"
    echo
    echo "Management commands:"
    echo "  Start:   systemctl start $SERVICE_NAME"
    echo "  Stop:    systemctl stop $SERVICE_NAME"
    echo "  Restart: systemctl restart $SERVICE_NAME"
    echo "  Status:  systemctl status $SERVICE_NAME"
    echo "  Logs:    journalctl -u $SERVICE_NAME -f"
    echo "=================================================="
}

# Run main if not sourced
if [ "${BASH_SOURCE[0]}" == "${0}" ]; then
    main "$@"
fi