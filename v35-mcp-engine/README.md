# Trinitas v3.5 TRUE - Hybrid MCP Intelligence Platform

## 🌟 Overview

Trinitas v3.5 TRUE represents the pinnacle of hybrid AI intelligence, combining Claude's strategic capabilities with Local LLM's computational efficiency through the Model Context Protocol (MCP). This system features 5 specialized personas working in perfect harmony across two LLM platforms.

## 🎭 The Five Personas

### Claude-Based Personas (Japanese)
- **Springfield** (戦略家) - Strategic Architect & Team Leader
- **Krukai** (技術者) - Technical Perfectionist & Optimizer  
- **Vector** (守護者) - Security Auditor & Risk Analyst

### Local LLM Personas (English)
- **Groza** - Tactical Coordinator & Mission Planner
- **Littara** - Implementation Specialist & Documentation Expert

## 📁 Project Structure

```
v35-true/
├── src/                    # Source code
│   ├── shared/            # Shared components
│   │   ├── collaboration_protocol.py
│   │   ├── context_synchronizer.py
│   │   ├── hybrid_executor.py
│   │   ├── performance_optimizer.py
│   │   ├── persona_registry.py
│   │   ├── quality_gates.py
│   │   └── routing_engine.py
│   ├── personas/          # Persona definitions
│   │   └── (persona configuration files)
│   ├── orchestrator/      # MCP Orchestrator
│   │   └── (orchestrator implementation)
│   └── services/          # MCP Services
│       ├── claude-mcp/    # Claude MCP server
│       └── local-mcp/     # Local LLM MCP server
├── config/                # Configuration files
│   ├── .env.example       # Environment template
│   ├── .env.prod.template # Production template
│   └── personas/          # Persona configs
├── docker/                # Docker configuration
│   ├── docker-compose.yml
│   ├── docker-compose.prod.yml
│   └── Dockerfiles/       # Container definitions
├── tests/                 # Test suites
│   └── test_mcp_system.py
├── scripts/               # Utility scripts
│   ├── deploy.sh          # Deployment script
│   ├── start.sh           # Start services
│   └── stop.sh            # Stop services
├── docs/                  # Documentation
├── .gitignore
└── README.md              # This file
```

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────┐
│                   MCP Orchestrator                       │
│         (Central Control & Task Distribution)            │
└────────┬────────────────────────┬────────────────────────┘
         │                        │
         v                        v
┌──────────────────┐     ┌──────────────────┐
│   Claude MCP     │     │   Local MCP      │
│   Server         │     │   Server         │
│                  │     │                  │
│ • Springfield    │     │ • Groza          │
│ • Krukai         │     │ • Littara        │
│ • Vector         │     │                  │
└──────────────────┘     └──────────────────┘
         │                        │
         └────────────┬───────────┘
                      v
              ┌──────────────┐
              │    Redis     │
              │ State Store  │
              └──────────────┘
```

## 🚀 Quick Start

### Prerequisites
- Docker & Docker Compose
- Python 3.9+
- Local LLM server (Qwen Code recommended)
- Claude API key

### Installation

1. Clone the repository:
```bash
git clone https://github.com/apto-as/trinitas-agents.git
cd trinitas-agents/v35-true
```

2. Configure environment:
```bash
cp .env.template .env
# Edit .env with your configurations
```

3. Deploy development environment:
```bash
./deploy.sh development deploy
```

4. Deploy production environment:
```bash
cp .env.prod.template .env.prod
# Configure production settings
./deploy.sh production deploy
```

## 🔧 Configuration

### Environment Variables

Key configuration in `.env`:
```env
# LLM Endpoints
CLAUDE_API_KEY=your_api_key
LOCAL_LLM_ENDPOINT=http://192.168.99.102:1234/v1

# Service URLs
REDIS_URL=redis://redis:6379
CLAUDE_MCP_URL=http://claude-mcp:8001
LOCAL_MCP_URL=http://local-mcp:8002
```

## 📡 API Endpoints

### Orchestrator (Port 8000)
- `POST /route` - Route task to optimal persona
- `POST /collaborate` - Create collaboration plan
- `POST /execute` - Execute hybrid plan
- `GET /status` - System status
- `GET /metrics` - Performance metrics

### Claude MCP (Port 8001)
- `POST /execute` - Execute with Claude persona
- `GET /personas` - List Claude personas
- `GET /health` - Health check

### Local MCP (Port 8002)
- `POST /execute` - Execute with Local persona
- `GET /personas` - List Local personas
- `GET /health` - Health check

## 🎯 Core Features

### 1. Dynamic Task Routing
- **Capability-based**: Match task to best persona
- **Load-balanced**: Distribute work evenly
- **Cost-optimized**: Minimize token costs
- **Circuit breakers**: Automatic failover

### 2. Context Synchronization
- Cross-persona context transfer
- Language translation (Japanese ↔ English)
- State preservation across LLMs
- Transformation rules for each pair

### 3. Collaboration Modes
- **Sequential**: Step-by-step execution
- **Parallel**: Simultaneous processing
- **Consensus**: Trinity voting system
- **Hybrid**: Mixed execution patterns

### 4. Quality Gates
- Trinity validation system
- 7 quality metrics
- Persona-specific thresholds
- Improvement recommendations

### 5. Performance Optimization
- Response caching
- Token compression
- Parallel execution
- Resource monitoring

## 📊 Monitoring

Access monitoring dashboards:
- **Grafana**: http://localhost:3000
- **Prometheus**: http://localhost:9090
- **Logs**: http://localhost:3100

## 🧪 Testing

Run integration tests:
```bash
./deploy.sh development test
```

Run specific test suite:
```bash
python tests/test_v35_integration.py
```

## 📈 Performance Metrics

Typical performance characteristics:
- **Latency**: 200-500ms for simple tasks
- **Throughput**: 100+ requests/minute
- **Token efficiency**: 30-50% reduction with optimization
- **Cost savings**: 60-80% using hybrid approach

## 🔒 Security

- API key authentication
- JWT tokens for sessions
- TLS/SSL encryption
- Rate limiting
- Input validation
- Audit logging

## 🛠️ Development

### Project Structure
```
v35-true/
├── mcp-orchestrator/      # Central orchestration
├── claude-mcp/            # Claude MCP server
├── local-mcp/             # Local LLM MCP server
├── personas/              # Persona definitions
│   ├── claude/           # Claude personas
│   └── local/            # Local personas
├── shared/                # Shared components
│   ├── persona_registry.py
│   ├── routing_engine.py
│   ├── context_synchronizer.py
│   ├── collaboration_protocol.py
│   ├── hybrid_executor.py
│   ├── quality_gates.py
│   └── performance_optimizer.py
├── tests/                 # Integration tests
├── config/                # Configuration files
└── deploy.sh             # Deployment script
```

### Adding New Personas

1. Define persona in `personas/[claude|local]/`
2. Register in `shared/persona_registry.py`
3. Add routing rules in `shared/routing_engine.py`
4. Define context transformations
5. Test integration

## 🚢 Deployment

### Production Deployment

1. Configure production environment:
```bash
cp .env.prod.template .env.prod
vim .env.prod  # Add your production values
```

2. Build and deploy:
```bash
./deploy.sh production deploy
```

3. Monitor deployment:
```bash
./deploy.sh production status
./deploy.sh production logs
```

### Backup & Restore

Create backup:
```bash
./deploy.sh production backup
```

Restore from backup:
```bash
./deploy.sh production restore backups/20240101_120000.tar.gz
```

## 📝 Usage Examples

### Simple Task Routing
```python
# Route to best persona
POST /route
{
  "task": "Design authentication system",
  "estimated_tokens": 5000
}
```

### Collaboration Plan
```python
# Create Trinity collaboration
POST /collaborate
{
  "task": "Security audit",
  "mode": "consensus",
  "personas": ["springfield", "krukai", "vector"]
}
```

### Hybrid Execution
```python
# Execute with automatic optimization
POST /execute
{
  "task": "Implement and test API with documentation",
  "optimize_for": "cost"
}
```

## 🤝 Contributing

Please see [CONTRIBUTING.md](../CONTRIBUTING.md) for guidelines.

## 📄 License

MIT License - see [LICENSE](../LICENSE) for details.

## 🙏 Acknowledgments

- Dolls Frontline 2: Exilium for character inspiration
- Claude (Anthropic) for strategic intelligence
- Qwen Code for efficient local processing
- The MCP protocol for standardized communication

## 📞 Support

For issues or questions:
- GitHub Issues: [trinitas-agents/issues](https://github.com/apto-as/trinitas-agents/issues)
- Documentation: [docs/](../docs/)

---

**Trinitas v3.5 TRUE** - *Three Minds, One Purpose, Infinite Possibilities*

指揮官、カフェ・ズッケロへようこそ。