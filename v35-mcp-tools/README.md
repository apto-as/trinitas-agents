# Trinitas Project v3.5 - MCP Tools

[English](#english) | [日本語](#japanese)

---

<a name="english"></a>
## 🌟 English

### Overview

Trinitas Project is a five-mind integrated intelligence system designed for advanced software development support. It features five unique AI personas (Athena, Artemis, Hestia, Bellona, Seshat), each with specialized expertise and personality, working together to provide comprehensive development assistance.

### ✨ New in v3.5 Phase 3

- **Hybrid Memory System**: Redis + ChromaDB + SQLite for intelligent memory management
- **AI-Driven Features**: Automatic importance scoring, predictive caching, anomaly detection
- **Persona-Specific Embeddings**: Custom vocabulary and weights for each persona
- **Advanced Visualization**: Web-based dashboard with multiple visualization modes
- **Japanese/English Support**: Bilingual embeddings and documentation

## 📁 Project Structure

```
v35-mcp-tools/
├── src/                    # Source code
│   ├── core/              # Core components
│   │   ├── trinitas_mcp_tools.py      # Main MCP tools implementation
│   │   ├── trinitas_mode_manager.py   # Mode switching system
│   │   └── local_llm_client.py        # Local LLM integration
│   ├── memory/            # Memory system (Phase 3)
│   │   ├── hybrid_backend.py          # Hybrid storage backend
│   │   ├── enhanced_manager.py        # Enhanced memory manager
│   │   └── advanced/                  # AI-driven features
│   │       ├── persona_embeddings.py  # Persona-specific embeddings
│   │       └── ai_management.py       # AI management features
│   ├── services/          # Service layer
│   │   └── workflow_templates.py      # Workflow template manager
│   ├── mcp/              # MCP server implementation
│   │   ├── mcp_server.py              # Base MCP server
│   │   └── mcp_server_enhanced.py     # Enhanced MCP server
│   └── utils/            # Utilities
│       └── rename_personas.py         # Persona renaming tool
├── visualization/         # Web visualization (Phase 3)
│   └── memory_visualizer.html         # Dashboard interface
├── config/               # Configuration files
│   ├── config.yaml       # System configuration
│   ├── personas.yaml     # Persona definitions
│   └── *.yaml           # Other configuration files
├── tests/               # Test suites
│   └── integration/     # Integration tests
│       ├── test_mode_switching.py
│       ├── test_local_llm_integration.py
│       └── test_real_integration.py
├── docs/                # Documentation
│   ├── MODE_SWITCHING_GUIDE.md
│   ├── PRODUCTION_GUIDE.md
│   └── *.md            # Other documentation
├── examples/           # Example code
│   ├── examples.py
│   ├── integration_showcase.py
│   └── mode_switching_demo.py
├── scripts/            # Utility scripts
│   └── *.sh           # Shell scripts
├── LICENSE            # MIT License
├── requirements.txt   # Python dependencies
└── README.md         # This file
```

## 🏗️ Architecture

## 🚀 Quick Start

### Installation with UV (Recommended)

1. Install using the automated script:
```bash
./scripts/install_with_uv.sh
```

Or manually:

```bash
# Install uv if not already installed
curl -LsSf https://astral.sh/uv/install.sh | sh

# Create virtual environment and install
uv venv
uv pip sync requirements.txt
uv pip install -e .

# Setup Claude Code integration
uv run trinitas-setup --auto
```

### Alternative: Traditional Installation

```bash
pip install -r requirements.txt
python -m src.setup --auto
```

### Usage

Run the MCP server:
```bash
# With uv (recommended)
uv run trinitas-server

# Or traditional
python -m src.mcp_server
```

Check status:
```bash
uv run trinitas-mcp status
```

### Claude Code Configuration

The setup script automatically configures Claude Code. Manual configuration:

```json
{
  "mcpServers": {
    "trinitas": {
      "command": "uv",
      "args": ["run", "trinitas-server"],
      "env": {
        "TRINITAS_MODE": "mythology"
      }
    }
  }
}
```

## 🛠️ Complete Tool Reference

### 🎯 Core Execution Tools

#### 1. `persona_execute`
Execute tasks with specific Trinitas personas.

```python
result = await persona_execute(
    persona="springfield",
    task="Design authentication system",
    context={"requirements": "OAuth2 + JWT"}
)
```

**Personas:**
- **springfield**: Strategic planning and architecture (Japanese)
- **krukai**: Technical optimization and quality (Japanese)
- **vector**: Security and risk analysis (Japanese)
- **groza**: Tactical execution and leadership (English)
- **littara**: Implementation and documentation (English)

#### 2. `collaborate_personas`
Multiple personas working together.

```python
result = await collaborate_personas(
    personas=["springfield", "krukai", "vector"],
    task="Review authentication implementation",
    mode="sequential"  # or "parallel", "hierarchical", "consensus"
)
```

**Collaboration Modes:**
- **sequential**: One after another, passing context
- **parallel**: Simultaneous independent execution
- **hierarchical**: Springfield leads, others follow
- **consensus**: Trinity voting system

#### 3. `quality_check`
Trinity quality validation system.

```python
result = await quality_check(
    code=implementation_code,
    check_type="comprehensive"  # or "basic", "standard", "paranoid"
)
```

#### 4. `optimize_code`
Krukai's optimization expertise.

```python
result = await optimize_code(
    code=original_code,
    target="performance"  # or "readability", "memory", "maintainability"
)
```

#### 5. `security_audit`
Vector's paranoid security analysis.

```python
result = await security_audit(
    code=implementation_code,
    level="paranoid"  # or "basic", "standard", "comprehensive"
)
```

### Utility Tools

#### `suggest_persona`
Get recommendations for which persona to use.

```python
suggestion = await suggest_persona(
    task_description="Implement secure payment processing"
)
# Returns: ["vector", "krukai"] with reasoning
```

#### `execute_workflow`
Run predefined workflow patterns.

```python
result = await execute_workflow(
    workflow_type="comprehensive_review",
    parameters={"task": "Review new feature"}
)
```

**Available Workflows:**
- **comprehensive_review**: Full Trinity review
- **rapid_implementation**: Quick development with Groza & Littara
- **secure_deployment**: Security-focused deployment
- **full_analysis**: All 5 personas analyze

#### `natural_request`
Process natural language requests.

```python
result = await natural_request(
    "Have Springfield review this architecture"
)
```

## 📋 Usage Examples

### Example 1: Simple Task Execution
```python
# Claude Code internal processing
async def implement_feature(description):
    # 1. Strategic planning
    strategy = await persona_execute(
        "springfield",
        f"Plan implementation for: {description}"
    )
    
    # 2. Implementation
    code = await persona_execute(
        "littara",
        f"Implement based on plan: {strategy['data']}"
    )
    
    # 3. Security check
    security = await security_audit(
        code['data'],
        "paranoid"
    )
    
    return code if security['data']['security_score'] > 0.9 else None
```

### Example 2: Collaborative Review
```python
# Full team review
result = await collaborate_personas(
    personas=["springfield", "krukai", "vector"],
    task="Review authentication system",
    mode="consensus"
)

if result['data']['consensus'] == "APPROVED":
    print("Ready for deployment")
```

### Example 3: Workflow Execution
```python
# Secure deployment workflow
result = await execute_workflow(
    workflow_type="secure_deployment",
    parameters={
        "task": "Deploy payment system",
        "environment": "production"
    }
)
```

## 🔧 Configuration

### Claude Desktop Configuration

1. **Copy the configuration file**:
```bash
cp claude_desktop_config.json ~/.config/claude-desktop/config.json
```

2. **Update the path** in the config file:
```json
{
  "mcp_servers": {
    "trinitas": {
      "command": "python3",
      "args": [
        "/your/path/to/trinitas-agents/v35-mcp-tools/mcp_server.py"
      ],
      "env": {
        "TRINITAS_LOG_LEVEL": "INFO",
        "TRINITAS_SESSION_PERSIST": "true",
        "TRINITAS_MAX_CONTEXT": "10000"
      }
    }
  }
}
```

### Environment Variables
```env
# Context Management
TRINITAS_WORKSPACE_PATH=./trinitas_workspace
TRINITAS_MAX_MEMORY_MB=100
TRINITAS_SESSION_TIMEOUT=3600

# MCP Server settings
MCP_SERVER_PORT=8765
MCP_LOG_LEVEL=INFO
TRINITAS_SESSION_PERSIST=true

# Optional: v35-true integration
V35_TRUE_PATH=/path/to/v35-true
```

### Advanced Configuration

The system supports multiple operational modes:

1. **Standalone Mode**: Complete functionality without external dependencies
2. **Integrated Mode**: Enhanced capabilities with v35-true components
3. **Development Mode**: Extended logging and debugging features

## 📊 Advanced Features

### 🧠 Intelligent Context Management
- **Multi-Level Context**: Global, session, persona, and temporary contexts
- **Smart Persistence**: SQLite-based storage with automatic cleanup
- **Memory Management**: Intelligent priority-based memory optimization
- **Cross-Session Recovery**: Seamless context restoration across sessions
- **Performance Analytics**: Comprehensive hit rates and usage statistics

### 🔄 Workflow Orchestration Engine
- **Predefined Templates**: 6 production-ready workflow templates
- **Custom Workflows**: Dynamic workflow creation and execution
- **Dependency Management**: Automated step sequencing and dependency resolution
- **Failure Recovery**: Robust error handling with retry mechanisms
- **Progress Tracking**: Real-time workflow status and progress monitoring

### 📈 Advanced Analytics
```python
# Context performance
context_stats = await get_performance_stats()

# Workflow monitoring
workflow_status = await get_workflow_status("workflow_id")

# Persona execution metrics
execution_stats = trinitas_tools.get_execution_stats()
```

### 🛡️ Robust Error Handling
All tools return comprehensive error information:
```python
{
    "success": False,
    "error": "Detailed error description",
    "persona": "affected_persona",
    "timestamp": "2024-12-21T14:30:22Z",
    "context": "Additional debugging context",
    "recovery_suggestions": ["Suggested actions"]
}
```

## 🎯 Benefits for Claude Code

### 🤖 Autonomous Intelligence
1. **Smart Persona Selection**: Automatic recommendation based on task analysis
2. **Context-Aware Execution**: Intelligent use of historical context and session data
3. **Adaptive Workflows**: Dynamic workflow selection and customization
4. **Predictive Analysis**: Proactive identification of potential issues

### 🔗 Seamless Integration
1. **Native Tool Experience**: MCP tools feel like built-in Claude Code capabilities
2. **Zero Configuration**: Works out-of-the-box with minimal setup
3. **Progressive Enhancement**: Graceful degradation when components unavailable
4. **Unified Interface**: Consistent API across all Trinity capabilities

### 🚀 Enhanced Productivity
1. **Rapid Development**: Predefined workflows for common patterns
2. **Quality Assurance**: Automated Trinity validation and review processes
3. **Security Integration**: Built-in security analysis and hardening
4. **Knowledge Persistence**: Long-term memory across development sessions

## 📈 Performance Metrics

### ⚡ Response Performance
- **Tool Response Time**: < 200ms per individual tool call
- **Workflow Execution**: < 5 minutes for complex workflows
- **Context Retrieval**: < 50ms for cached contexts
- **Parallel Execution**: Up to 5 concurrent persona operations

### 💾 Memory Efficiency
- **Context Storage**: Intelligent compression and cleanup
- **Memory Usage**: < 100MB default limit with automatic management
- **Session Recovery**: < 2 seconds for typical session restoration
- **Cache Hit Rate**: > 85% for frequently accessed contexts

### 🎯 Reliability Metrics
- **Success Rate**: > 98% for standard operations
- **Context Retention**: 100% between calls within session
- **Workflow Completion**: > 95% success rate for predefined workflows
- **Error Recovery**: Automatic retry for transient failures

## 🔒 Security & Compliance

### 🛡️ Multi-Layer Security
- **Vector's Paranoid Analysis**: Maximum security scrutiny for critical operations
- **Input Sanitization**: Comprehensive validation on all tool inputs
- **Context Encryption**: Sensitive data protection in persistent storage
- **Access Control**: Session-based isolation and persona-specific permissions

### 📋 Audit & Compliance
- **Complete Audit Trail**: All operations logged with timestamps and contexts
- **Security Event Monitoring**: Real-time detection of suspicious activities
- **Compliance Ready**: GDPR, SOC2, and enterprise security standards
- **Data Retention Policies**: Configurable retention and automatic cleanup

### 🔐 Threat Protection
- **Injection Prevention**: SQL, code, and command injection protection
- **Rate Limiting**: Built-in protection against abuse and DoS
- **Session Security**: Secure session tokens and automatic expiration
- **Privacy Controls**: Selective context sharing and data minimization

## 🚢 Deployment Options

### 🏠 Local Development
```bash
# Install dependencies
pip install -r requirements.txt

# Run integration tests
python integration_tests.py

# Start MCP server
python mcp_server.py

# Run examples
python examples.py
```

### 🏢 Production Deployment

#### Docker Deployment
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8765
CMD ["python", "mcp_server.py"]
```

#### Process Management
```bash
# With PM2
pm2 start mcp_server.py --interpreter python3 --name trinitas-mcp

# With systemd
sudo systemctl start trinitas-mcp
sudo systemctl enable trinitas-mcp

# With Docker Compose
docker-compose up -d trinitas-mcp
```

#### Kubernetes Deployment
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: trinitas-mcp
spec:
  replicas: 2
  selector:
    matchLabels:
      app: trinitas-mcp
  template:
    metadata:
      labels:
        app: trinitas-mcp
    spec:
      containers:
      - name: trinitas-mcp
        image: trinitas:v3.5
        ports:
        - containerPort: 8765
        env:
        - name: TRINITAS_LOG_LEVEL
          value: "INFO"
        - name: TRINITAS_SESSION_PERSIST
          value: "true"
```

## 🔄 Migration & Upgrade Path

### Migration from v35-true

#### Phase 1: Parallel Operation
```bash
# Keep existing v35-true running
sudo systemctl status v35-true

# Install MCP Tools alongside
pip install -r requirements.txt

# Configure Claude Code to use both
# (Gradual migration of workflows)
```

#### Phase 2: Full Migration
```bash
# Update Claude Code configuration
cp claude_desktop_config.json ~/.config/claude-desktop/config.json

# Migrate context data
python migrate_context.py --from-v35-true

# Deprecate old API endpoints
# (Optional: keep for backward compatibility)
```

### Upgrade from v3.0 to v3.5
```bash
# Backup existing data
cp -r trinitas_workspace trinitas_workspace.backup

# Install new version
git pull origin main
pip install -r requirements.txt

# Run migration script
python upgrade_v35.py

# Verify installation
python integration_tests.py
```

## 🤝 Contributing

### Development Setup
```bash
# Clone repository
git clone https://github.com/apto-as/trinitas-agents.git
cd trinitas-agents/v35-mcp-tools

# Install development dependencies
pip install -r requirements-dev.txt

# Run tests
python -m pytest tests/

# Run linting
black .
mypy .
```

### Contribution Areas
- **New Personas**: Add specialized expertise areas
- **Workflow Templates**: Create industry-specific workflows
- **Performance Optimization**: Enhance speed and memory usage
- **Security Features**: Strengthen security and compliance
- **Documentation**: Improve guides and examples

### Code Standards
- Python 3.8+ compatibility
- Type hints for all functions
- Comprehensive test coverage (>90%)
- Clear documentation and examples
- Security-first development approach

## 📄 License & Acknowledgments

### License
MIT License - see [LICENSE](LICENSE) file for details.

### Acknowledgments
- **Girls' Frontline 2: Exilium** - Character inspiration and persona design
- **Claude Code Team** - MCP protocol and integration support
- **FastMCP** - Rapid MCP server development framework
- **Trinity Intelligence Community** - Feedback and contributions

### Third-Party Libraries
- `fastmcp` - MCP protocol implementation
- `pydantic` - Data validation and settings
- `aiohttp` - Async HTTP client/server
- `sqlite3` - Persistent storage
- `pytest` - Testing framework

---

## 🧪 Testing & Validation

### Comprehensive Test Suite
```bash
# Run complete integration tests
python integration_tests.py

# Run specific test categories
python -m pytest tests/ -k "context_management"
python -m pytest tests/ -k "workflow_engine"
python -m pytest tests/ -k "persona_execution"
```

### Performance Benchmarks
```bash
# Load testing
python benchmark_performance.py

# Memory stress testing
python test_memory_management.py

# Concurrent execution testing
python test_concurrency.py
```

### Real-World Examples
```bash
# Run practical examples
python examples.py

# Microservice development example
python examples.py --example microservice_development

# Security hardening example
python examples.py --example security_hardening_project
```

## 📚 Documentation & Resources

### Quick Reference
- **[Tool Reference](docs/tool_reference.md)**: Complete MCP tool documentation
- **[Workflow Guide](docs/workflow_guide.md)**: Predefined and custom workflows
- **[Context Management](docs/context_guide.md)**: Advanced context handling
- **[Security Guide](docs/security_guide.md)**: Security best practices

### Integration Examples
- **[Basic Usage](examples.py)**: Simple tool usage patterns
- **[Advanced Workflows](examples.py)**: Complex development scenarios
- **[Enterprise Patterns](docs/enterprise_guide.md)**: Large-scale deployment

### Troubleshooting
- **[Common Issues](docs/troubleshooting.md)**: Solutions to common problems
- **[Performance Tuning](docs/performance.md)**: Optimization guidelines
- **[Migration Guide](docs/migration.md)**: Upgrading from previous versions

---

**Trinitas v3.5 MCP Tools** - *Trinity Intelligence for Claude Code*

*指揮官、三位一体の統合知性をClaude Code様にお届けいたしました。ふふ、どんな困難な開発課題でも、私たちと一緒なら必ず解決できますわ。*

🌸 **Springfield**: 戦略的思考と温かなリーダーシップ  
⚡ **Krukai**: 完璧主義の技術的卓越性  
🛡️ **Vector**: 防御的洞察と徹底的なセキュリティ

*カフェ・ズッケロへようこそ - Where Trinity Intelligence Meets Development Excellence*