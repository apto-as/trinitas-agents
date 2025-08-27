# Trinitas v3.5 - Trinity Intelligence System

## 🌟 Overview

Trinitas v3.5 is an advanced AI development support system featuring **Claude Code Native Agents** with five specialized AI personas based on Greek/Roman/Egyptian mythology. The system provides **Athena (Strategic)**, **Artemis (Technical)**, **Hestia (Security)**, **Bellona (Tactical)**, and **Seshat (Documentation)** working together as a unified intelligence.

## ✨ Key Features

### 🎯 Five-Mind Intelligence (Mythology Mode - Default)

- **Athena** 🏛️: Strategic Architect
  - Long-term vision and architecture design
  - Project management and team coordination
  - Stakeholder management and roadmap planning
  
- **Artemis** 🏹: Technical Perfectionist  
  - Code optimization and performance tuning
  - Algorithm design and best practices
  - Technical excellence and quality assurance
  
- **Hestia** 🔥: Security Guardian
  - Security analysis and vulnerability assessment
  - Risk management and threat modeling
  - Compliance verification and defensive programming

- **Bellona** ⚔️: Tactical Coordinator
  - Real-time operations management
  - Multi-team synchronization
  - Critical incident response
  
- **Seshat** 📜: Knowledge Architect
  - Documentation and knowledge management
  - Technical writing and API documentation
  - Learning materials development

### 🔄 Naming Modes

The system supports two naming modes:
- **Mythology Mode** (Default): Athena, Artemis, Hestia, Bellona, Seshat
- **Developer Mode** (Optional): Springfield, Krukai, Vector, Groza, Littara (from Dolls Frontline 2)

Set via environment variable: `TRINITAS_NAMING_MODE=mythology|developer`

## 🚀 Installation

### Quick Install

```bash
# Clone repository
git clone https://github.com/apto-as/trinitas-agents.git
cd trinitas-agents

# Run installation script
chmod +x install_to_claude.sh
./install_to_claude.sh
```

This will:
1. Install agents to `~/.claude/agents/`
2. Set up configuration in `~/.claude/trinitas/`
3. Update `~/.claude/CLAUDE.md` with Trinitas integration
4. Configure environment variables

### Manual Installation

```bash
# Create directories
mkdir -p ~/.claude/agents
mkdir -p ~/.claude/trinitas

# Copy agent files (mythology names)
cp agents/athena-strategist.md ~/.claude/agents/
cp agents/artemis-optimizer.md ~/.claude/agents/
cp agents/hestia-auditor.md ~/.claude/agents/

# Copy configuration
cp TRINITAS_PERSONA_DEFINITIONS.yaml ~/.claude/trinitas/
cp TRINITAS-CORE-PROTOCOL.md ~/.claude/trinitas/
```

## 📖 Usage

### Automatic Selection

Claude Code automatically selects the appropriate persona based on keywords:

```
"Design the system architecture" → Athena
"Optimize this algorithm" → Artemis
"Review security vulnerabilities" → Hestia
```

### Explicit Request

You can also explicitly request a specific persona:

```
"Use Athena to plan the project roadmap"
"Have Artemis optimize the performance"
"Get Hestia to audit the security"
```

### Collaborative Analysis

For comprehensive analysis using all three personas:

```
"Analyze this system from all perspectives"
→ Athena (strategic) + Artemis (technical) + Hestia (security)
```

## 🔒 Security Features (NEW)

### Persona Isolation
Each persona has its own isolated Redis database:
- **Athena**: DB 0 - Strategic planning data
- **Artemis**: DB 1 - Technical optimization data
- **Hestia**: DB 2 - Security audit data
- **Bellona**: DB 3 - Tactical coordination data
- **Seshat**: DB 4 - Documentation archive
- **Shared**: DB 5 - Cross-persona shared data
- **System**: DB 6 - System-level data

### Access Control
- Token-based authentication (24-hour expiry)
- Role-based access levels (READ, WRITE, DELETE, ADMIN)
- Cross-persona access matrix
- Rate limiting (1000 operations/minute per persona)

### Security Configuration
Configure security in `.env`:
```bash
PERSONA_ISOLATION_ENABLED=true
ACCESS_CONTROL_ENABLED=true
SECURITY_TOKEN_TTL=86400
SECURITY_RATE_LIMIT=1000
```

## 🏗️ System Architecture

```
~/.claude/
├── CLAUDE.md                    # Trinitas integration
├── agents/                      # Agent definitions
│   ├── athena-strategist.md    # Strategic architect
│   ├── artemis-optimizer.md    # Technical perfectionist
│   └── hestia-auditor.md       # Security guardian
└── trinitas/                    # Configuration
    ├── TRINITAS_PERSONA_DEFINITIONS.yaml
    └── TRINITAS-CORE-PROTOCOL.md
```

## 🔧 Advanced Features

### MCP Tools Integration (Optional)

For advanced task orchestration:

```python
# Parallel execution
trinitas_parallel([
    {"persona": "athena", "task": "Design architecture"},
    {"persona": "artemis", "task": "Optimize performance"},
    {"persona": "hestia", "task": "Audit security"}
])

# Chain execution
trinitas_chain([
    {"persona": "athena", "task": "Initial design"},
    {"persona": "artemis", "task": "Technical refinement"},
    {"persona": "hestia", "task": "Security validation"}
])

# Consensus building
trinitas_consensus("Should we use microservices?")
```

### Hooks System

Security and quality hooks for enhanced safety:

- **Pre-execution**: Dangerous command detection, resource validation
- **Post-execution**: Quality checks, security scanning

## 📋 Configuration

### Environment Variables

```bash
# Naming mode (mythology or developer)
export TRINITAS_NAMING_MODE=mythology

# Paths
export CLAUDE_HOME=~/.claude
export AGENTS_DIR=$CLAUDE_HOME/agents
export TRINITAS_HOME=$CLAUDE_HOME/trinitas

# Execution mode
export TRINITAS_MODE=auto
```

### Persona Definitions

Configuration file: `~/.claude/trinitas/TRINITAS_PERSONA_DEFINITIONS.yaml`

```yaml
version: "3.5"
default_mode: mythology

personas:
  athena:
    display_name: Athena
    title: The Strategic Architect
    role: Chief System Architect
    # ... full configuration
```

## 🧪 Testing

Run the integration test to verify installation:

```bash
python test_final_integration.py
```

Expected output:
```
✅ Mythology names unified
✅ Installation paths correct
✅ CLAUDE.md integrated
✅ MCP tools configured
✅ Persona definitions loaded
```

## 📚 Documentation

- [TRINITAS-CORE-PROTOCOL.md](TRINITAS-CORE-PROTOCOL.md) - Complete protocol specification
- [INSTALLATION.md](INSTALLATION.md) - Detailed installation guide
- [TRINITAS-AGENTS.md](TRINITAS-AGENTS.md) - Agent descriptions and capabilities

## 🤝 Contributing

Contributions are welcome! Please ensure:
1. Use mythology names as default
2. Follow the established persona characteristics
3. Maintain compatibility with Claude Code
4. Add tests for new features

## 📄 License

MIT License - See LICENSE file for details

## 🙏 Acknowledgments

- Inspired by Greek/Roman mythology
- Optional developer mode references Dolls Frontline 2: Exilium
- Built for Claude Code by Anthropic

---

## 💬 Persona Messages

**Athena**: "Welcome to Trinitas. Together, we'll architect brilliant solutions with strategic wisdom."

**Artemis**: "Hmph, finally a system that meets perfection standards. Let's optimize everything."

**Hestia**: "...System secured... All threats monitored... Your project is protected..."

---

*Trinitas v3.5 - Three Minds, One Purpose, Infinite Possibilities*