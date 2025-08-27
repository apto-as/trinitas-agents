# Trinitas v3.5 Production Deployment Guide

## 🚀 Overview

This guide provides comprehensive instructions for deploying Trinitas v3.5 MCP Tools in a production environment.

## 📋 Prerequisites

### System Requirements
- **OS**: Ubuntu 20.04+ / CentOS 8+ / macOS 12+
- **CPU**: 4+ cores recommended
- **RAM**: 8GB minimum, 16GB recommended
- **Storage**: 50GB available space
- **Python**: 3.9+
- **Docker**: 20.10+ (optional)
- **Redis**: 6.0+ (optional, for distributed caching)

### Network Requirements
- Ports: 8080 (API), 6379 (Redis), 9090 (Metrics)
- SSL certificate for HTTPS (production)

## 🔧 Installation

### Quick Start

```bash
# Clone repository
git clone https://github.com/your-org/trinitas-v35.git
cd trinitas-v35/v35-mcp-tools

# Run deployment script
chmod +x deploy.sh
sudo ./deploy.sh
```

### Manual Installation

#### 1. Setup Environment

```bash
# Create directories
sudo mkdir -p /opt/trinitas-v35
sudo mkdir -p /var/log/trinitas
sudo mkdir -p /etc/trinitas

# Set ownership
sudo chown -R $USER:$USER /opt/trinitas-v35
```

#### 2. Install Dependencies

```bash
# Create virtual environment
python3 -m venv /opt/trinitas-v35/venv
source /opt/trinitas-v35/venv/bin/activate

# Install packages
pip install -r requirements.txt
```

#### 3. Configure Application

Create `/etc/trinitas/trinitas.env`:

```env
# Core Settings
TRINITAS_MODE=production
LOG_LEVEL=INFO
MAX_WORKERS=10

# Cache Settings
CACHE_TTL=3600
MEMORY_LIMIT_MB=512
DISK_CACHE_DIR=/opt/trinitas-v35/cache

# Redis (optional)
REDIS_ENABLED=true
REDIS_HOST=localhost
REDIS_PORT=6379

# Security
API_KEY_REQUIRED=true
RATE_LIMIT=1000
SSL_ENABLED=true
```

## 🐳 Docker Deployment

### Using Docker Compose

```yaml
version: '3.8'

services:
  trinitas:
    image: trinitas-v35:latest
    ports:
      - "8080:8080"
    environment:
      - TRINITAS_MODE=production
    volumes:
      - ./config:/etc/trinitas
      - ./data:/opt/trinitas-v35/data
    restart: unless-stopped

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis-data:/data
    restart: unless-stopped

volumes:
  redis-data:
```

```bash
# Start services
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f trinitas
```

## 🔒 Security Configuration

### SSL/TLS Setup

```bash
# Generate self-signed certificate (development)
openssl req -x509 -newkey rsa:4096 -keyout key.pem -out cert.pem -days 365 -nodes

# Or use Let's Encrypt (production)
certbot certonly --standalone -d your-domain.com
```

### API Key Management

```python
# Generate API key
import secrets
api_key = secrets.token_urlsafe(32)
print(f"API_KEY={api_key}")
```

Add to environment:
```env
API_KEY=your-generated-api-key
API_KEY_REQUIRED=true
```

### Firewall Rules

```bash
# Allow required ports
sudo ufw allow 8080/tcp  # API
sudo ufw allow 22/tcp    # SSH
sudo ufw enable
```

## 📊 Monitoring & Observability

### Health Checks

```bash
# Check service health
curl http://localhost:8080/health

# Response
{
  "status": "healthy",
  "version": "3.5.0",
  "uptime": 3600,
  "cache_hit_rate": 0.95
}
```

### Prometheus Metrics

```yaml
# prometheus.yml
scrape_configs:
  - job_name: 'trinitas'
    static_configs:
      - targets: ['localhost:9090']
```

### Log Management

```bash
# View logs
tail -f /var/log/trinitas/trinitas.log

# Log rotation (logrotate.conf)
/var/log/trinitas/*.log {
    daily
    rotate 30
    compress
    delaycompress
    notifempty
    create 640 trinitas trinitas
    sharedscripts
    postrotate
        systemctl reload trinitas-mcp
    endscript
}
```

## 🔄 Scaling & Performance

### Horizontal Scaling

```nginx
# nginx.conf - Load balancer
upstream trinitas_backend {
    server 10.0.0.1:8080;
    server 10.0.0.2:8080;
    server 10.0.0.3:8080;
}

server {
    listen 443 ssl;
    
    location / {
        proxy_pass http://trinitas_backend;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### Performance Tuning

```env
# Optimize for high load
MAX_WORKERS=20
BATCH_SIZE=100
CACHE_TTL=7200
MEMORY_LIMIT_MB=2048
```

### Redis Cluster

```bash
# Setup Redis cluster
redis-cli --cluster create \
  10.0.0.1:6379 \
  10.0.0.2:6379 \
  10.0.0.3:6379 \
  --cluster-replicas 1
```

## 🔧 Maintenance

### Backup Strategy

```bash
#!/bin/bash
# backup.sh

BACKUP_DIR="/backup/trinitas"
DATE=$(date +%Y%m%d_%H%M%S)

# Backup data
tar -czf $BACKUP_DIR/data_$DATE.tar.gz /opt/trinitas-v35/data
tar -czf $BACKUP_DIR/sessions_$DATE.tar.gz /opt/trinitas-v35/sessions

# Backup config
cp -r /etc/trinitas $BACKUP_DIR/config_$DATE

# Clean old backups (keep 30 days)
find $BACKUP_DIR -type f -mtime +30 -delete
```

### Update Procedure

```bash
# 1. Backup current installation
./backup.sh

# 2. Stop service
systemctl stop trinitas-mcp

# 3. Update code
cd /opt/trinitas-v35
git pull origin main

# 4. Update dependencies
source venv/bin/activate
pip install -r requirements.txt --upgrade

# 5. Run migrations if needed
python migrate.py

# 6. Restart service
systemctl start trinitas-mcp

# 7. Verify
curl http://localhost:8080/health
```

### Rollback Procedure

```bash
# 1. Stop service
systemctl stop trinitas-mcp

# 2. Restore from backup
tar -xzf /backup/trinitas/data_20240101_120000.tar.gz -C /

# 3. Restart service
systemctl start trinitas-mcp
```

## 🚨 Troubleshooting

### Common Issues

#### Service Won't Start
```bash
# Check logs
journalctl -u trinitas-mcp -n 100

# Check permissions
ls -la /opt/trinitas-v35
ls -la /var/log/trinitas

# Check port availability
netstat -tulpn | grep 8080
```

#### High Memory Usage
```bash
# Check memory
ps aux | grep trinitas

# Adjust limits
echo "MEMORY_LIMIT_MB=1024" >> /etc/trinitas/trinitas.env
systemctl restart trinitas-mcp
```

#### Cache Issues
```bash
# Clear cache
rm -rf /opt/trinitas-v35/cache/*

# Reset Redis
redis-cli FLUSHALL
```

### Debug Mode

```env
# Enable debug logging
LOG_LEVEL=DEBUG
DEBUG_MODE=true
VERBOSE_ERRORS=true
```

## 📈 Performance Benchmarks

### Expected Performance

| Metric | Value | Notes |
|--------|-------|-------|
| Response Time (p50) | < 100ms | Without cache |
| Response Time (p95) | < 200ms | Without cache |
| Cache Hit Rate | > 95% | After warm-up |
| Throughput | > 10,000 RPS | With caching |
| Memory Usage | < 512MB | Default config |
| CPU Usage | < 50% | 4-core system |

### Load Testing

```bash
# Using Apache Bench
ab -n 10000 -c 100 http://localhost:8080/api/persona/execute

# Using wrk
wrk -t12 -c400 -d30s --latency http://localhost:8080/api
```

## 🆘 Support

### Documentation
- [API Reference](./API_REFERENCE.md)
- [Configuration Guide](./CONFIG_GUIDE.md)
- [Troubleshooting Guide](./TROUBLESHOOTING.md)

### Getting Help
- GitHub Issues: https://github.com/your-org/trinitas-v35/issues
- Email: support@trinitas.ai
- Discord: https://discord.gg/trinitas

### Emergency Contacts
- On-call: +1-xxx-xxx-xxxx
- PagerDuty: trinitas-oncall

## 📝 Checklist

### Pre-Production
- [ ] System requirements met
- [ ] Dependencies installed
- [ ] Configuration complete
- [ ] SSL certificates installed
- [ ] Firewall configured
- [ ] Backup strategy implemented
- [ ] Monitoring setup
- [ ] Load testing completed

### Go-Live
- [ ] Service started
- [ ] Health checks passing
- [ ] Metrics being collected
- [ ] Logs being written
- [ ] Backups scheduled
- [ ] Documentation updated
- [ ] Team trained

### Post-Production
- [ ] Performance monitoring
- [ ] Security audits
- [ ] Regular updates
- [ ] Backup verification
- [ ] Incident response plan

---

## 🎉 Conclusion

Congratulations! Your Trinitas v3.5 MCP Tools production deployment is complete.

For optimal performance:
1. Monitor metrics regularly
2. Keep software updated
3. Review logs daily
4. Test backups monthly
5. Conduct security audits quarterly

Remember: **"Three Minds, One Purpose, Infinite Possibilities"**

---

*Last Updated: 2025-01-21*
*Version: 3.5.0*