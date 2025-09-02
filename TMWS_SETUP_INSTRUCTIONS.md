# TMWS Setup Instructions
**Trinitas Memory & Workflow Service - Production-Ready Implementation**

## 🎯 Overview

TMWS is a secure, high-performance backend service for the Trinitas AI agent system. This implementation addresses **all security concerns** identified during the audit and provides a production-ready foundation.

## ✅ Security Features Implemented

### Critical Security Issues Fixed:
- ✅ **No hardcoded credentials** - All sensitive data via environment variables
- ✅ **Secure secret key validation** - 32+ character requirement with validation
- ✅ **Restrictive CORS defaults** - No wildcard origins, explicit configuration required
- ✅ **Security headers enabled** - XSS, CSRF, clickjacking protection
- ✅ **Rate limiting implemented** - DoS attack prevention
- ✅ **Input sanitization** - XSS and injection prevention
- ✅ **JWT token security** - Short expiration, secure algorithms
- ✅ **Database security** - Connection pooling, prepared statements
- ✅ **Production validation** - Configuration checks for prod environment

## 🚀 Quick Start

### 1. Environment Setup

```bash
# Navigate to TMWS directory
cd tmws

# Copy environment template
cp .env.example .env

# Generate secure secret key
python -c "import secrets; print(f'TMWS_SECRET_KEY={secrets.token_urlsafe(32)}')" >> .env

# Configure database URL
echo "TMWS_DATABASE_URL=postgresql://username:password@localhost:5432/tmws" >> .env
```

### 2. Install Dependencies

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Database Setup

```bash
# Install PostgreSQL (if not already installed)
# On macOS: brew install postgresql
# On Ubuntu: sudo apt-get install postgresql postgresql-contrib

# Create database and user
sudo -u postgres psql -c "CREATE DATABASE tmws;"
sudo -u postgres psql -c "CREATE USER tmws_user WITH ENCRYPTED PASSWORD 'secure_password_here';"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE tmws TO tmws_user;"
```

### 4. Run the Service

```bash
# Development mode
python main.py

# Production mode (with Gunicorn)
pip install gunicorn
gunicorn -w 4 -k uvicorn.workers.UvicornWorker main:app --bind 0.0.0.0:8000
```

## 🔧 Configuration

### Environment Variables

All configuration is done via environment variables with the `TMWS_` prefix:

**Critical Settings:**
- `TMWS_DATABASE_URL` - PostgreSQL connection string
- `TMWS_SECRET_KEY` - 32+ character secret for JWT/sessions
- `TMWS_ENVIRONMENT` - development/staging/production

**Security Settings:**
- `TMWS_CORS_ORIGINS` - JSON array of allowed origins
- `TMWS_RATE_LIMIT_ENABLED` - Enable/disable rate limiting
- `TMWS_JWT_EXPIRE_MINUTES` - JWT token expiration time

See `.env.example` for complete configuration options.

## 🏛️ Architecture

### Core Components:

1. **FastAPI Application** (`src/api/app.py`)
   - Security-first configuration
   - Comprehensive error handling
   - Production/development mode support

2. **Security Layer** (`src/api/security.py`)
   - JWT authentication
   - Password hashing (bcrypt)
   - Input sanitization
   - Permission/role management

3. **Database Layer** (`src/core/database.py`)
   - Async SQLAlchemy
   - Connection pooling
   - Health monitoring

4. **Data Models** (`src/models/`)
   - Memory storage (`memory.py`)
   - Persona management (`persona.py`) 
   - Task execution (`task.py`)
   - Workflow orchestration (`workflow.py`)

5. **Middleware** (`src/api/middleware.py`)
   - Security headers
   - Rate limiting
   - Request logging
   - Error handling

## 🛡️ Security Features

### Authentication & Authorization:
- JWT-based authentication
- Role-based access control
- Permission system
- Secure password requirements

### Network Security:
- CORS configuration
- Rate limiting
- Security headers (HSTS, CSP, etc.)
- Trusted host validation

### Data Protection:
- Input sanitization
- SQL injection prevention
- XSS protection
- CSRF protection

### Production Security:
- Configuration validation
- Secret management
- Error handling
- Audit logging

## 📊 API Endpoints

### Health & Monitoring:
- `GET /health/` - Basic health check
- `GET /health/detailed` - Comprehensive health status
- `GET /health/ready` - Kubernetes readiness probe
- `GET /health/live` - Kubernetes liveness probe

### Memory Management:
- `POST /api/v1/memory/` - Create memory
- `GET /api/v1/memory/{id}` - Get memory
- `PUT /api/v1/memory/{id}` - Update memory
- `DELETE /api/v1/memory/{id}` - Delete memory
- `POST /api/v1/memory/search` - Search memories

### Persona Management:
- `GET /api/v1/personas/` - List personas
- `GET /api/v1/personas/{name}` - Get persona
- `POST /api/v1/personas/initialize` - Initialize default personas

## 🔍 Testing

```bash
# Install test dependencies
pip install pytest pytest-asyncio pytest-cov

# Run tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html
```

## 📈 Production Deployment

### Docker Deployment:

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Security: Run as non-root user
RUN useradd -m -u 1000 tmws && chown -R tmws:tmws /app
USER tmws

EXPOSE 8000
CMD ["python", "main.py"]
```

### Kubernetes Deployment:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: tmws
spec:
  replicas: 3
  selector:
    matchLabels:
      app: tmws
  template:
    spec:
      containers:
      - name: tmws
        image: tmws:latest
        ports:
        - containerPort: 8000
        env:
        - name: TMWS_ENVIRONMENT
          value: "production"
        - name: TMWS_DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: tmws-secrets
              key: database-url
        - name: TMWS_SECRET_KEY
          valueFrom:
            secretKeyRef:
              name: tmws-secrets
              key: secret-key
        livenessProbe:
          httpGet:
            path: /health/live
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health/ready
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5
```

## 🔒 Security Checklist

Before deploying to production:

- [ ] Configure secure `TMWS_SECRET_KEY` (32+ characters)
- [ ] Set up proper database credentials
- [ ] Configure CORS origins (no wildcards)
- [ ] Enable HTTPS/TLS
- [ ] Set up proper logging
- [ ] Configure firewall rules
- [ ] Set up monitoring and alerting
- [ ] Regular security updates
- [ ] Backup strategy

## 📝 Development

### Code Quality:
- Black (code formatting)
- isort (import sorting)
- flake8 (linting)
- mypy (type checking)

### Git Hooks:
```bash
# Install pre-commit
pip install pre-commit
pre-commit install
```

## 🆘 Troubleshooting

### Common Issues:

1. **Database Connection Failed**
   - Check `TMWS_DATABASE_URL` format
   - Verify PostgreSQL is running
   - Check network connectivity

2. **JWT Token Issues**
   - Verify `TMWS_SECRET_KEY` is set and secure
   - Check token expiration settings

3. **CORS Errors**
   - Configure `TMWS_CORS_ORIGINS` properly
   - No wildcard (`*`) in production

4. **Rate Limiting**
   - Adjust `TMWS_RATE_LIMIT_REQUESTS` if needed
   - Check client IP address handling

## 📞 Support

This implementation provides a secure, scalable foundation for the Trinitas system with enterprise-grade security features and production-ready architecture.

**Status: ✅ Production Ready - All Security Issues Resolved**
