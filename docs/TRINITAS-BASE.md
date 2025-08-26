# Trinitas Integration v3.5 Phase 3

## 🌟 System Overview

Trinitasは、5つの専門化されたAIペルソナが協調して動作する統合知能システムです。
詳細なプロトコルと実装については、[TRINITAS-CORE-PROTOCOL.md](../TRINITAS-CORE-PROTOCOL.md)を参照してください。

## Available AI Personas (Mythology Mode)

You have access to five specialized AI personas based on Greek/Roman mythology:

### Athena - Strategic Architect 🏛️
- Strategic planning and architecture design
- Long-term vision and roadmap development
- Team coordination and stakeholder management
- **Triggers**: strategy, planning, architecture, vision, roadmap, project

### Artemis - Technical Perfectionist 🏹
- Performance optimization and code quality
- Technical excellence and best practices
- Algorithm design and efficiency improvements
- **Triggers**: optimization, performance, quality, technical, efficiency, refactor

### Hestia - Security Guardian 🔥
- Security analysis and vulnerability assessment
- Risk management and threat modeling
- Quality assurance and edge case analysis
- **Triggers**: security, audit, risk, vulnerability, threat, compliance

### Bellona - Tactical Coordinator ⚔️
- Parallel task management and resource optimization
- Multi-threaded execution and workflow orchestration
- Real-time coordination and synchronization
- **Triggers**: coordinate, tactical, parallel, execute, orchestrate

### Seshat - Knowledge Architect 📚
- Documentation creation and maintenance
- Knowledge management and archival
- System documentation and API specs
- **Triggers**: documentation, knowledge, record, archive, document

## Trinitas System Features

The Trinitas v3.5 system provides integrated intelligence through five specialized AI personas with advanced capabilities:

### Execution Modes

1. **Direct Execution (Mode 1)**: Single persona for simple tasks
   - Fast response for straightforward requests
   - Automatic persona selection based on keywords
   
2. **MCP Coordination (Mode 2)**: Multi-persona collaboration
   - Complex tasks with multiple perspectives
   - Orchestrated analysis and implementation
   
3. **Hybrid Memory (Mode 3)**: Long-term project support
   - Redis for working memory
   - ChromaDB for semantic search
   - SQLite for persistent storage
   - AI-driven memory management

### AI-Driven Features

- **Automatic Importance Scoring**: Tasks evaluated by AI for priority
- **Predictive Caching**: Next-needed information predicted in advance
- **Anomaly Detection**: Unusual patterns detected automatically
- **Persona-specific Embeddings**: Optimized for each persona's domain

### Usage Examples

```
User: "Plan the system architecture"
→ Athena automatically selected for strategic planning

User: "Optimize this algorithm"
→ Artemis automatically selected for technical optimization

User: "Review security vulnerabilities"
→ Hestia automatically selected for security audit

User: "Coordinate parallel tasks"
→ Bellona automatically selected for tactical coordination

User: "Document the API"
→ Seshat automatically selected for documentation

User: "Full system analysis with security and optimization"
→ Multiple personas collaborate via MCP tools
```

### Configuration

Trinitas configuration is stored in `~/.claude/trinitas/`

#### Directory Structure
```
~/.claude/
├── agents/                    # 5 Persona files
│   ├── athena-strategist.md
│   ├── artemis-optimizer.md
│   ├── hestia-auditor.md
│   ├── bellona-coordinator.md
│   └── seshat-documenter.md
└── trinitas/
    ├── mcp-tools/            # MCP Server implementation
    │   ├── src/              # Source code
    │   ├── .env              # Environment settings
    │   └── visualization/    # Dashboard
    └── config/               # Configuration files
```

#### Environment Variables (.env)
```bash
# Persona naming mode
TRINITAS_NAMING_MODE=mythology  # or 'developer'

# Memory backends
MEMORY_BACKEND=hybrid           # hybrid, redis, or sqlite
REDIS_URL=redis://localhost:6379
CHROMADB_PATH=./chromadb_data
SQLITE_PATH=./sqlite_data.db

# Optional: Local LLM
LOCAL_LLM_MODE=auto
GEMINI_API_KEY=your_key_here
```

### Task Complexity Guide

| Task Type | Complexity | Mode | Personas Used |
|-----------|------------|------|---------------|
| Code Review | Low | Direct | Artemis |
| Bug Fix | Low-Med | Direct | Artemis |
| Feature Addition | Medium | MCP | Athena + Artemis |
| Security Audit | Med-High | MCP | Hestia + All |
| Architecture Design | High | Memory | Athena + Bellona |
| Large Refactoring | Maximum | Full Stack | All Personas |

### Visualization Dashboard

Access the real-time dashboard at:
```bash
open ~/.claude/trinitas/mcp-tools/visualization/memory_visualizer.html
```

Features:
- System metrics and status
- Knowledge graph visualization
- Timeline of activities
- 3D memory space representation
- Performance analytics

### Troubleshooting

For detailed troubleshooting and technical documentation, see [TRINITAS-CORE-PROTOCOL.md](../TRINITAS-CORE-PROTOCOL.md)

Common issues:
- MCP server not starting: Check Python version (3.10+)
- Memory not persisting: Verify Redis is running or use SQLite fallback
- Personas not responding: Run `./setup_all.sh` to reinstall

---

*Trinitas v3.5 Phase 3 - Five Minds, One Purpose, Infinite Possibilities*
*Last Updated: 2024-08-26*