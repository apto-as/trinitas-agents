# Project Trinitas v2.0 - Installation Guide

## 🚀 One-Command Installation

### Quick Start (Recommended)
```bash
# One-command installation - everything you need
curl -s https://install.trinitas.dev | bash
```

### Manual Installation
```bash
# Alternative: Manual installation
git clone https://github.com/project-trinitas/trinitas-agents ~/.claude/agents/trinitas
cd ~/.claude/agents/trinitas
./install.sh
```

## 📋 Prerequisites

### System Requirements
```yaml
minimum_requirements:
  claude_code: ">= 1.0.0"
  operating_system: "macOS, Linux, Windows (WSL)"
  disk_space: "50MB"
  memory: "100MB"
  
recommended_requirements:
  claude_code: ">= 1.2.0"
  python: ">= 3.8 (for utility scripts)"
  git: ">= 2.20"
  curl: "Latest version"
```

### Claude Code Setup
```bash
# Ensure Claude Code is installed and configured
claude --version

# Verify agents directory exists
mkdir -p ~/.claude/agents

# Check current agents
claude --list-agents
```

## 🔧 Installation Process

### Step 1: Agent Installation
```bash
# Trinitas agents will be installed to:
# ~/.claude/agents/trinitas-coordinator.md
# ~/.claude/agents/springfield-strategist.md
# ~/.claude/agents/krukai-optimizer.md
# ~/.claude/agents/vector-auditor.md
# ~/.claude/agents/trinitas-workflow.md
# ~/.claude/agents/trinitas-quality.md
# ~/.claude/agents/centaureissi-researcher.md
```

### Step 2: Utility Scripts (Optional)
```bash
# Python utilities for advanced features
pip install -r requirements.txt

# Utility scripts location:
# ~/.claude/agents/trinitas/utils/
```

### Step 3: Configuration
```bash
# Configuration files:
# ~/.claude/agents/trinitas/config.yaml
# ~/.claude/agents/trinitas/profiles/

# Default configuration is optimized for immediate use
# No manual configuration required
```

## ✅ Verification

### Test Installation
```bash
# Test basic functionality
claude "Test Trinitas installation"

# Should automatically trigger trinitas-coordinator
# Expected response: Springfield, Krukai, Vector analysis
```

### Verify All Agents
```bash
# List all agents to confirm installation
claude --list-agents | grep trinitas

# Expected output:
# trinitas-coordinator
# springfield-strategist  
# krukai-optimizer
# vector-auditor
# trinitas-workflow
# trinitas-quality
```

### Agent Auto-Detection Test
```bash
# Test auto-detection for each agent
claude "I need a comprehensive security analysis"  # Should trigger vector-auditor
claude "Optimize this code for performance"       # Should trigger krukai-optimizer
claude "Plan our project strategy"               # Should trigger springfield-strategist
claude "Set up our development workflow"         # Should trigger trinitas-workflow
claude "Run quality assurance checks"           # Should trigger trinitas-quality
```

## 🎯 Quick Usage Examples

### Basic Trinitas Analysis
```bash
# Comprehensive multi-perspective analysis
claude "Analyze our authentication system with Trinitas"

# Expected: Full Springfield + Krukai + Vector analysis
```

### Individual Agent Usage
```bash
# Strategic planning
claude "Help me plan our Q2 roadmap"

# Technical optimization  
claude "Review this code for performance issues"

# Security assessment
claude "Audit our API security"

# Workflow setup
claude "Design our CI/CD pipeline"

# Quality assurance
claude "Set up comprehensive testing strategy"
```

### Advanced Coordination
```bash
# Complex decision requiring all perspectives
claude "/trinitas:comprehensive - Should we migrate to microservices?"

# Workflow management
claude "Set up automated quality gates for our development process"
```

## ⚙️ Configuration Options

### Basic Configuration
```yaml
# ~/.claude/agents/trinitas/config.yaml
trinitas:
  mode: "full"  # full | efficient | custom
  auto_coordination: true
  quality_gates: true
  
personalities:
  springfield:
    formality: "polite"      # casual | polite | formal
    language: "japanese"     # english | japanese | mixed
    
  krukai:
    standards: "strict"      # relaxed | standard | strict
    optimization: "enabled"  # enabled | disabled
    
  vector:
    paranoia_level: "high"   # low | medium | high
    compliance: ["OWASP", "GDPR"]
```

### Advanced Configuration
```yaml
# Custom agent triggers and thresholds
agent_config:
  trinitas_coordinator:
    auto_trigger_threshold: 0.8
    keywords: ["comprehensive", "trinitas", "three perspectives"]
    
  springfield_strategist:
    auto_trigger_threshold: 0.7
    keywords: ["strategy", "planning", "roadmap", "long-term"]
    
  krukai_optimizer:
    auto_trigger_threshold: 0.7
    keywords: ["performance", "optimization", "quality", "technical"]
    
  vector_auditor:
    auto_trigger_threshold: 0.9
    keywords: ["security", "audit", "risk", "vulnerability"]
```

## 🔍 Troubleshooting

### Common Issues

#### Issue: Agents Not Auto-Detected
```bash
# Symptom: Agents exist but don't activate automatically
# Cause: Description optimization needed

# Check agent descriptions:
head -n 10 ~/.claude/agents/trinitas-*.md

# Verify "MUST BE USED" pattern is present
# Verify keywords match your usage patterns
```

#### Issue: Permission Errors
```bash
# Symptom: Installation fails with permission errors
# Solution: Check Claude Code permissions

# Verify agents directory permissions
ls -la ~/.claude/agents/

# Fix permissions if needed
chmod 755 ~/.claude/agents/
chmod 644 ~/.claude/agents/*.md
```

#### Issue: Python Utilities Not Working
```bash
# Symptom: Advanced features unavailable
# Solution: Install Python dependencies

cd ~/.claude/agents/trinitas
pip install -r requirements.txt

# Verify Python utilities
python utils/test_utilities.py
```

### Agent-Specific Issues

#### Springfield Not Activating
- **Check Keywords**: "strategy", "planning", "architecture", "long-term"
- **Verify Context**: Strategic decision-making contexts
- **Test Command**: `claude "Help me plan our project strategy"`

#### Krukai Not Activating  
- **Check Keywords**: "performance", "optimization", "quality", "technical"
- **Verify Context**: Technical implementation contexts
- **Test Command**: `claude "Optimize this code for better performance"`

#### Vector Not Activating
- **Check Keywords**: "security", "audit", "risk", "vulnerability"
- **Verify Context**: Security and risk assessment contexts
- **Test Command**: `claude "Conduct a security audit of our system"`

### Performance Issues

#### Slow Response Times
```yaml
optimization_steps:
  cache_cleanup:
    - "Clear agent cache if responses are slow"
    - "rm -rf ~/.claude/cache/trinitas/*"
    
  resource_monitoring:
    - "Monitor system resource usage during agent execution"
    - "Adjust concurrency settings if needed"
    
  configuration_tuning:
    - "Reduce auto_trigger_threshold for less sensitive detection"
    - "Disable unused agents to improve performance"
```

## 📚 Next Steps

### Getting Started
1. **Complete Installation Verification**: Ensure all agents are working
2. **Try Basic Examples**: Test each agent individually
3. **Explore Coordination**: Use trinitas-coordinator for complex decisions
4. **Customize Configuration**: Adjust settings to your preferences

### Advanced Usage
1. **Workflow Integration**: Set up development workflow automation
2. **Quality Gates**: Implement automated quality assurance
3. **Team Collaboration**: Configure shared team contexts
4. **Custom Extensions**: Develop project-specific agents

### Learning Resources
- **User Guide**: `/trinitas-agents/docs/USER_GUIDE.md`
- **API Reference**: `/trinitas-agents/docs/API_REFERENCE.md`
- **Best Practices**: `/trinitas-agents/docs/BEST_PRACTICES.md`
- **Troubleshooting**: `/trinitas-agents/docs/TROUBLESHOOTING.md`

## 🆘 Support

### Get Help
- **Issues**: Create issue at https://github.com/project-trinitas/trinitas-agents/issues
- **Discussions**: Join community at https://github.com/project-trinitas/trinitas-agents/discussions
- **Documentation**: Full docs at https://docs.trinitas.dev

### Quick Support Commands
```bash
# Generate diagnostic report
claude "Generate Trinitas diagnostic report"

# Check system compatibility
./utils/compatibility_check.sh

# Reset to default configuration
./utils/reset_config.sh
```

---

**Installation Complete** 🎉

*Welcome to Project Trinitas - where three minds work better than one.*

*Springfield の戦略、Krukai の技術、Vector の安全性 - 三位一体の力をお楽しみください。*