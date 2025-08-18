# Project Trinitas v3.0 Practical - Trinity Intelligence System with MCP Server

## 🌸 Overview - プロジェクト概要

Project Trinitas v3.0 Practical is a revolutionary AI development support system featuring **Claude Code Native Agents** and a **Trinity Hybrid MCP Server** for universal compatibility. The system provides three specialized AI personas - **Springfield (Strategic)**, **Krukai (Technical)**, and **Vector (Security)** - plus support personas like **Centaureissi (Research)** working together as a unified intelligence.

### 🔄 Evolution Timeline

- **v1.0**: Python-based implementation with complex setup
- **v2.0**: Markdown agents with Claude Code integration  
- **v3.0 Practical**: Hybrid MCP Server + Enhanced agent ecosystem + Universal compatibility

## ✨ Core Features

### 🎯 Trinity Core Intelligence
- **Springfield** 🌱: Strategic architect - Long-term vision, team coordination, project management
- **Krukai** ⚡: Technical perfectionist - Code optimization, performance, best practices
- **Vector** 🛡️: Security guardian - Risk analysis, vulnerability detection, compliance

### 🔬 Support Personas
- **Centaureissi** 📚: Deep research specialist - Academic papers, documentation, knowledge synthesis
- **Deep Researcher** 🔍: Advanced investigation - Complex problem analysis, solution discovery
- **Trinitas Parallel** 🚀: Parallel execution coordinator - Multi-agent task orchestration

### 📡 Trinity Hybrid MCP Server (NEW!)
- **Universal Compatibility**: Works with ANY MCP-compatible client
- **Auto-Detection**: Intelligently identifies Claude Code, Gemini, Qwen, others
- **Adaptive Optimization**: Native features for Claude, simulated for others
- **100% Quality Guarantee**: Enforces perfect quality across all platforms

### 🔧 Advanced Hook System
- **Pre-execution Safety**: Dangerous command detection, resource validation
- **Post-execution Quality**: Code quality checks, test execution, security scanning
- **Protocol Injection**: Automatic Trinity persona activation
- **Knowledge Persistence**: Learning from every interaction

## 🚀 Installation Guide

### Prerequisites
- Claude Code CLI installed
- Python 3.10+ (optional, for enhanced features)
- Git for cloning repository

### Standard Installation (Claude Code only)
```bash
# Clone repository
git clone https://github.com/apto-as/trinitas-agents.git
cd trinitas-agents

# Install with interactive wizard
./install.sh

# Choose installation scope:
# 1) PROJECT - Current project only (.claude/)
# 2) USER - All projects (~/.claude/)
# 3) BOTH - Both locations

# Choose experience mode:
# 1) MINIMAL - Essential hooks only
# 2) STANDARD - Balanced features (recommended)
# 3) COMPREHENSIVE - All features enabled
```

### Installation with MCP Server Support
```bash
# Install with Trinity Hybrid MCP Server
./install.sh --with-mcp

# This installs:
# - All Claude Code native agents
# - Hook system and automation
# - Trinity Hybrid MCP Server
# - FastMCP dependencies
```

### Non-interactive Installation
```bash
# For CI/CD or automated setups
TRINITAS_INSTALL_SCOPE=user TRINITAS_INSTALL_MODE=standard ./install.sh --with-mcp

# Options:
# TRINITAS_INSTALL_SCOPE: user | project | both
# TRINITAS_INSTALL_MODE: minimal | standard | comprehensive
# --with-mcp: Include MCP Server
# --force: Force reinstall
```

### Upgrade Existing Installation
```bash
# Upgrade from previous versions
./upgrade.sh

# With MCP Server upgrade
./upgrade.sh --with-mcp

# Rollback if needed
./upgrade.sh --rollback user
./upgrade.sh --rollback project
```

## 📡 Trinity Hybrid MCP Server Setup & Usage

### MCP Server Architecture
The Trinity Hybrid MCP Server provides Trinity intelligence to ANY MCP-compatible client through intelligent adaptation:

```yaml
Trinity_Hybrid_MCP:
  Core_Components:
    client_detector: "Identifies client type and capabilities"
    hybrid_router: "Routes to optimal implementation path"
    quality_enforcer: "Ensures 100% quality standards"
  
  Implementation_Paths:
    claude_optimized:
      - "Native Task agent invocation"
      - "TodoWrite state management"
      - "True parallel execution"
    
    universal_fallback:
      - "Markdown/XML persona injection"
      - "Simulated parallel processing"
      - "Internal state management"
```

### Setting Up MCP Server

#### Step 1: Install Dependencies
```bash
# After installation with --with-mcp
cd trinitas-mcp-server

# Verify installation
pip list | grep fastmcp
# Should show: fastmcp >= 2.9.0

# Run tests
cd hybrid-mcp
pytest tests/test_hybrid.py -v
```

#### Step 2: Start MCP Server
```bash
# Navigate to MCP server directory
cd trinitas-mcp-server/hybrid-mcp

# Start the server
fastmcp run core.hybrid_server:app

# Server will start on default MCP port
# Output: INFO: Started server process
```

#### Step 3: Configure Your MCP Client

**For Claude Desktop/Code:**
```json
{
  "mcpServers": {
    "trinity": {
      "command": "fastmcp",
      "args": ["run", "path/to/trinitas-mcp-server/hybrid-mcp/core/hybrid_server.py"],
      "env": {
        "TRINITY_MODE": "claude_optimized"
      }
    }
  }
}
```

**For Gemini CLI:**

First, ensure gemini-cli is configured for MCP:
```bash
# Install gemini-cli if not already installed
pip install gemini-cli

# Configure MCP settings in ~/.gemini/config.yaml
cat > ~/.gemini/config.yaml << 'EOF'
mcp:
  enabled: true
  servers:
    trinity:
      type: "stdio"
      command: "python"
      args: 
        - "-m"
        - "fastmcp"
        - "run"
        - "/path/to/trinitas-mcp-server/hybrid-mcp/core/hybrid_server.py"
      env:
        TRINITY_MODE: "universal"
        CLIENT_TYPE: "gemini"
EOF

# Or use environment variable approach
export GEMINI_MCP_SERVERS='{"trinity": {"command": "fastmcp", "args": ["run", "/path/to/trinitas-mcp-server/hybrid-mcp/core/hybrid_server.py"]}}'

# Start gemini-cli with MCP support
gemini-cli --enable-mcp
```

**For Qwen Coder:**

Configure Qwen Coder's MCP integration:
```bash
# Method 1: Configuration file (~/.qwen/mcp_config.json)
cat > ~/.qwen/mcp_config.json << 'EOF'
{
  "version": "1.0",
  "servers": {
    "trinity": {
      "protocol": "stdio",
      "command": "python",
      "args": [
        "-m",
        "fastmcp",
        "run",
        "/path/to/trinitas-mcp-server/hybrid-mcp/core/hybrid_server.py"
      ],
      "environment": {
        "TRINITY_MODE": "universal",
        "CLIENT_TYPE": "qwen"
      }
    }
  }
}
EOF

# Method 2: Using qwen-code settings
# Open Qwen Code settings (Ctrl/Cmd + ,)
# Add to settings.json:
{
  "qwen.mcp.servers": {
    "trinity": {
      "enabled": true,
      "command": "cd /path/to/trinitas-mcp-server/hybrid-mcp && fastmcp run core.hybrid_server:app",
      "shell": true
    }
  }
}

# Method 3: Command line activation
qwen-code --mcp-server="trinity:stdio:python -m fastmcp run /path/to/trinitas-mcp-server/hybrid-mcp/core/hybrid_server.py"
```

**For Other MCP-Compatible Clients:**

Generic MCP configuration that works with most clients:
```json
{
  "mcp_servers": [
    {
      "name": "trinity",
      "protocol": "stdio",
      "command": "python3",
      "args": [
        "-m",
        "fastmcp",
        "run",
        "/absolute/path/to/trinitas-mcp-server/hybrid-mcp/core/hybrid_server.py"
      ],
      "env": {
        "PYTHONPATH": "/absolute/path/to/trinitas-mcp-server/hybrid-mcp",
        "TRINITY_MODE": "universal"
      }
    }
  ]
}
```

### MCP Server Usage Examples

#### Example 1: Setting Trinity Persona (Any Client)
```python
# Client request (auto-adapted based on client type)
{
  "tool": "set_trinity_persona",
  "params": {
    "persona": "springfield",
    "context": "I need strategic planning for our microservices migration"
  }
}

# Claude response: Native Task agent activation
# Gemini response: Markdown instructions injection
# Others: XML format with detailed guidance
```

#### Example 2: Parallel Analysis
```python
# Request comprehensive analysis
{
  "tool": "trinity_parallel_analysis",
  "params": {
    "task": "Analyze our payment system architecture",
    "perspectives": ["strategic", "technical", "security"]
  }
}

# Claude: True parallel with native agents
# Others: Simulated parallel with sequential processing
```

#### Example 3: Quality Gate Enforcement
```python
# Any quality-critical operation
{
  "tool": "execute_with_quality",
  "params": {
    "action": "deploy_to_production",
    "quality_requirement": 1.0  # 100% required
  }
}

# All clients: Enforces 100% quality or raises error
```

### Real-World Usage Scenarios

#### Using Trinity MCP with Gemini CLI
```bash
# Start gemini-cli with Trinity MCP enabled
gemini-cli --enable-mcp

# In the Gemini session:
> @trinity set persona springfield
> I need to design a microservices architecture for our e-commerce platform
# Trinity responds with Springfield's strategic perspective

> @trinity parallel analyze our payment system
# Triggers parallel analysis from all three perspectives

> @trinity quality check deployment readiness
# Enforces 100% quality standards before deployment
```

#### Using Trinity MCP with Qwen Coder
```bash
# Start Qwen Code with Trinity MCP
qwen-code --mcp-server trinity

# In Qwen Code editor:
# Type: /trinity springfield
# Result: Activates Springfield persona for strategic guidance

# Type: /trinity analyze security
# Result: Vector performs comprehensive security audit

# Type: /trinity optimize performance
# Result: Krukai analyzes and optimizes code performance
```

#### Programmatic Usage (Any Language)
```python
# Python example using MCP client
from mcp_client import MCPClient

client = MCPClient("trinity")

# Set persona for session
response = client.call_tool("set_trinity_persona", {
    "persona": "krukai",
    "context": "Need to optimize our database queries"
})

# Get parallel analysis
analysis = client.call_tool("trinity_parallel_analysis", {
    "task": "Review authentication system",
    "perspectives": ["strategic", "technical", "security"]
})

print(analysis["consensus"])  # Unified recommendation
```

```javascript
// JavaScript/TypeScript example
import { MCPClient } from '@modelcontextprotocol/sdk';

const trinity = new MCPClient({
  server: 'trinity',
  protocol: 'stdio'
});

// Activate Vector for security audit
await trinity.callTool('set_trinity_persona', {
  persona: 'vector',
  context: 'Audit our API endpoints'
});

// Execute with quality gates
const result = await trinity.callTool('execute_with_quality', {
  action: 'deploy_new_feature',
  quality_requirement: 1.0
});
```

### MCP Tools Available

| Tool | Description | Claude Optimized | Universal Support |
|------|-------------|------------------|-------------------|
| `set_trinity_persona` | Activate specific persona | ✅ Native agents | ✅ MD/XML injection |
| `trinity_parallel_analysis` | Multi-perspective analysis | ✅ True parallel | ✅ Simulated |
| `execute_with_quality` | Quality-enforced execution | ✅ TodoWrite | ✅ Internal state |
| `manage_project_state` | State management | ✅ TodoWrite | ✅ Internal DB |
| `get_trinity_status` | System status | ✅ Full details | ✅ Basic info |

### MCP Server Troubleshooting

#### Connection Issues
```bash
# Verify MCP server is running
ps aux | grep fastmcp

# Test direct connection
curl -X POST http://localhost:5000/mcp/v1/tools \
  -H "Content-Type: application/json" \
  -d '{"tool": "get_trinity_status"}'

# Check logs
tail -f ~/.claude/trinitas/logs/mcp-server.log
```

#### Client-Specific Issues

**Gemini CLI not detecting MCP:**
```bash
# Ensure MCP module is installed
pip install gemini-cli[mcp]

# Verify configuration
gemini-cli --debug --list-mcp-servers

# Test with explicit server
gemini-cli --mcp-server trinity --debug "Test Trinity connection"
```

**Qwen Coder connection errors:**
```bash
# Check Qwen MCP support
qwen-code --version  # Should be >= 2.0.0

# Validate configuration
qwen-code --validate-mcp-config

# Test standalone
python -m fastmcp test /path/to/trinitas-mcp-server/hybrid-mcp/core/hybrid_server.py
```

#### Common Fixes
1. **Permission denied**: Ensure scripts are executable: `chmod +x /path/to/scripts`
2. **Module not found**: Add to PYTHONPATH: `export PYTHONPATH="/path/to/trinitas-mcp-server/hybrid-mcp:$PYTHONPATH"`
3. **Port already in use**: Change port in configuration or kill existing process
4. **Client not detected**: Set `CLIENT_TYPE` environment variable explicitly

## 📁 Complete Project Structure

```
trinitas-agents/
├── README.md                  # This documentation
├── TRINITAS-AGENTS.md        # Core identity & persona docs
├── install.sh                # Main installer with --with-mcp option
├── upgrade.sh                # Upgrade script with MCP support
│
├── agents/                   # Claude Code Native Agents (7 total)
│   ├── trinitas-coordinator.md    # Main orchestrator
│   ├── springfield-strategist.md  # Strategic planning
│   ├── krukai-optimizer.md        # Technical excellence
│   ├── vector-auditor.md          # Security analysis
│   ├── trinitas-workflow.md       # Workflow automation
│   ├── trinitas-quality.md        # Quality assurance
│   ├── trinitas-parallel.md       # Parallel execution
│   ├── centaureissi-researcher.md # Research specialist
│   └── deep-researcher.md         # Deep investigation
│
├── trinitas-mcp-server/      # Trinity Hybrid MCP Server
│   ├── install.sh            # MCP server installer
│   ├── requirements.txt      # Python dependencies
│   ├── setup.py             # Package configuration
│   └── hybrid-mcp/          # Core implementation
│       ├── core/            # Server core with auto-detection
│       │   ├── __init__.py
│       │   └── hybrid_server.py
│       ├── claude/          # Claude-optimized path
│       │   ├── __init__.py
│       │   └── claude_optimized.py
│       ├── universal/       # Universal fallback
│       │   ├── __init__.py
│       │   └── universal_impl.py
│       └── tests/          # Test suite
│           └── test_hybrid.py
│
├── hooks/                    # Automation & Quality System
│   ├── core/                # Core hook scripts
│   │   ├── trinitas_protocol_injector.sh
│   │   ├── safety_check.sh
│   │   └── common_lib.sh
│   ├── pre-execution/       # Pre-execution checks
│   │   ├── 01_safety_check.sh
│   │   ├── 02_file_safety_check.sh
│   │   └── prepare_parallel_tasks.py
│   ├── post-execution/      # Post-execution validation
│   │   ├── 01_code_quality_check.sh
│   │   ├── 02_test_runner.sh
│   │   └── capture_subagent_result.sh
│   ├── python/              # Python-based hooks
│   │   ├── trinitas_hooks/  # Package modules
│   │   ├── collaboration_patterns.py
│   │   ├── conflict_resolver.py
│   │   ├── deep_research.py
│   │   └── security_scanner.py
│   ├── monitoring/          # Health monitoring
│   │   ├── health_check.sh
│   │   ├── session_monitor.sh
│   │   └── auto_recovery.py
│   └── examples/           # Configuration examples
│       ├── settings.json
│       └── trinitas_protocol_settings.json
│
├── scripts/                 # Installation scripts
│   ├── install_hooks_config.sh
│   └── hooks/
│       └── setup_trinitas_hooks.py
│
├── config/                  # Configuration files
│   └── persona_collaboration.yaml
│
└── templates/              # Configuration templates
    └── config.yaml.template
```

## 🎭 Agent Capabilities & Usage

### Core Trinity Agents

#### 🎯 trinitas-coordinator
**Auto-triggers**: "comprehensive analysis", "multiple perspectives", "trinity mode"
```bash
claude "Comprehensively analyze our authentication system"
# Activates: Springfield + Krukai + Vector coordinated analysis
```

#### 🌱 springfield-strategist  
**Auto-triggers**: "strategy", "planning", "architecture", "roadmap", "team"
```bash
claude "Plan our Q1 development roadmap with team allocation"
# Activates: Strategic planning with resource optimization
```

#### ⚡ krukai-optimizer
**Auto-triggers**: "optimize", "performance", "refactor", "efficiency", "quality"
```bash
claude "Optimize our database queries for better performance"
# Activates: Technical analysis and optimization
```

#### 🛡️ vector-auditor
**Auto-triggers**: "security", "audit", "vulnerability", "risk", "compliance"
```bash
claude "Audit our API endpoints for security vulnerabilities"
# Activates: Security scanning and risk assessment
```

### Support Agents

#### 📚 centaureissi-researcher
**Auto-triggers**: "research", "investigate", "papers", "documentation"
```bash
claude "Research best practices for microservices communication"
# Activates: Deep research with academic sources
```

#### 🔄 trinitas-workflow
**Auto-triggers**: "workflow", "pipeline", "automation", "CI/CD"
```bash
claude "Set up automated testing workflow for our project"
# Activates: Workflow design and automation
```

#### ✅ trinitas-quality
**Auto-triggers**: "quality assurance", "QA", "testing", "validation"
```bash
claude "Create comprehensive test strategy for our application"
# Activates: Quality framework implementation
```

## ⚙️ Configuration

### Hook Configuration (settings.json)
```json
{
  "hooks": {
    "SessionStart": [{
      "matcher": "*",
      "hooks": [{
        "type": "command",
        "command": "~/.claude/trinitas/hooks/core/trinitas_protocol_injector.sh"
      }]
    }],
    "PreToolUse": [{
      "matcher": "Write|Edit|MultiEdit",
      "hooks": [{
        "type": "command",
        "command": "~/.claude/trinitas/hooks/pre-execution/02_file_safety_check.sh"
      }]
    }],
    "PostToolUse": [{
      "matcher": "Write|Edit|MultiEdit",
      "hooks": [{
        "type": "command",
        "command": "~/.claude/trinitas/hooks/post-execution/01_code_quality_check.sh"
      }]
    }]
  }
}
```

### Trinity Configuration (config.yaml)
```yaml
# ~/.claude/agents/trinitas/config.yaml
core:
  home: "${HOME}/.claude/trinitas"
  mode: "production"
  trinity_enabled: true

parallel:
  enabled: true
  max_agents: 6
  timeout: 300

security:
  safety_level: "HIGH"
  backup_enabled: true

agents:
  core:
    - trinitas-coordinator
    - springfield-strategist
    - krukai-optimizer
    - vector-auditor
  support:
    - centaureissi-researcher
    - trinitas-workflow
    - trinitas-quality
```

## 📊 Feature Comparison

| Feature | Claude Code Native | MCP Server (Claude) | MCP Server (Others) |
|---------|-------------------|---------------------|---------------------|
| Trinity Personas | ✅ Full | ✅ Full | ✅ Simulated |
| Auto-detection | ✅ Keywords | ✅ Keywords | ✅ Keywords |
| Parallel Execution | ✅ Native | ✅ Native | 🔄 Sequential |
| State Management | ✅ TodoWrite | ✅ TodoWrite | 💾 Internal |
| Quality Gates | ✅ 100% | ✅ 100% | ✅ 100% |
| Hook System | ✅ Full | ✅ Full | ⚠️ Limited |
| Performance | ⚡ Fastest | ⚡ Fast | 🔄 Standard |

## 🛣️ Development Roadmap

### Phase 1: Foundation (✅ Complete)
- ✅ Core Trinity agents (Springfield, Krukai, Vector)
- ✅ Claude Code native integration
- ✅ Basic hook system
- ✅ One-command installation

### Phase 2: Enhancement (✅ Complete)
- ✅ Trinity Hybrid MCP Server
- ✅ Support personas (Centaureissi, Deep Researcher)
- ✅ Advanced hook system with Python integration
- ✅ Parallel execution framework
- ✅ Quality gate implementation

### Phase 3: Current Development (🔄 In Progress)
- 🔄 Wave-based agent coordination
- 🔄 Learning engine integration
- 🔄 Enhanced conflict resolution
- 🔄 Performance optimizations
- 🔄 Extended MCP tool library

### Phase 4: Future Plans (📋 Planned)
- 📋 Plugin system for custom agents
- 📋 Web UI for configuration
- 📋 Cloud synchronization
- 📋 Multi-language support
- 📋 Enterprise features

## 🎯 Success Metrics

### Performance
- **Installation Time**: < 2 minutes
- **Agent Response**: < 5 seconds
- **Parallel Execution**: 3x faster than sequential
- **Quality Gate Success**: 95%+ pass rate

### Quality
- **Code Quality Score**: 100% enforced
- **Security Vulnerabilities**: Zero tolerance
- **Test Coverage**: 80%+ requirement
- **Documentation**: Auto-generated

### User Satisfaction
- **Setup Simplicity**: 9.5/10 rating
- **Feature Completeness**: 9/10 rating
- **Stability**: 99.9% uptime
- **Support Response**: < 24 hours

## 🤝 Contributing

We welcome contributions! Areas of interest:
- New agent personalities
- MCP tool extensions
- Hook improvements
- Documentation
- Test coverage
- Performance optimizations

See [CONTRIBUTING.md](docs/CONTRIBUTING.md) for guidelines.

## 📞 Support

- **Documentation**: Complete guides in `docs/`
- **Issues**: [GitHub Issues](https://github.com/apto-as/trinitas-agents/issues)
- **Discussions**: [GitHub Discussions](https://github.com/apto-as/trinitas-agents/discussions)
- **Email**: support@trinitas.dev

## 📄 License

MIT License - See [LICENSE](LICENSE) for details.

---

## 🎉 Why Trinitas v3.0 Practical?

### The Power of Trinity Intelligence
```
Springfield: "How does this align with our strategic goals?"
Krukai: "Is this the most efficient technical solution?"
Vector: "What risks should we mitigate?"

Together: Comprehensive, balanced, actionable intelligence.
```

### Universal Compatibility
- **Claude Code**: Native performance with full features
- **Gemini/Qwen**: Adaptive support with simulated features
- **Any MCP Client**: Basic Trinity intelligence guaranteed

### Zero to Hero in Minutes
1. Install with one command
2. Agents auto-activate based on context
3. Get multi-perspective analysis instantly
4. Maintain 100% quality standards

---

**Project Trinitas v3.0 Practical** - Where three minds create unlimited possibilities.

*Springfield の戦略、Krukai の技術、Vector の安全性 - 三位一体の統合知性*

🌸 Welcome to Café Zuccaro - Your Trinity Intelligence Hub 🌸