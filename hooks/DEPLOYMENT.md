# Trinitas v5.0 Deployment Instructions

## Overview

Trinitas v5.0 uses two complementary systems:
1. **trinitas-mcp**: Full persona execution, memory, and collaboration (already deployed)
2. **Minimal Hooks**: Protocol injection at SessionStart and PreCompact only

## What Changed in v5.0

### Removed (functionality moved to trinitas-mcp)
- All safety checks (except truly critical ones)
- Parallel agent coordination 
- Code quality checks
- Monitoring and recovery
- 46 unnecessary files

### Added
- TRINITAS-CORE-PROTOCOL.md v5.0 with real MCP tool commands
- Minimal protocol injector (Python)
- Simplified configuration

### Kept
- Protocol injection at SessionStart and PreCompact events (not available in trinitas-mcp)

## Files to Deploy

```bash
# From project to production (~/.claude/)
trinitas-agents/
├── TRINITAS-CORE-PROTOCOL.md        → ~/.claude/TRINITAS-CORE-PROTOCOL.md
├── hooks/
│   ├── core/
│   │   └── protocol_injector.py     → ~/.claude/hooks/core/
│   ├── settings_minimal.json        → ~/.claude/hooks/settings.json
│   └── .env                         → ~/.claude/hooks/.env
```

## Deployment Commands

```bash
# 1. Deploy TRINITAS-CORE-PROTOCOL v5.0
cp TRINITAS-CORE-PROTOCOL.md ~/.claude/TRINITAS-CORE-PROTOCOL.md

# 2. Deploy minimal hooks
cp hooks/core/protocol_injector.py ~/.claude/hooks/core/protocol_injector.py
cp hooks/settings_minimal.json ~/.claude/hooks/settings.json
cp hooks/.env ~/.claude/hooks/.env

# 3. Test deployment
cd ~/.claude/hooks
python3 core/protocol_injector.py test

# 4. Enable in Claude Code
# Settings → Hooks → Enable
```

## Testing

### Test Protocol Injection
```bash
# Test SessionStart
python3 ~/.claude/hooks/core/protocol_injector.py session_start | jq .

# Test PreCompact
python3 ~/.claude/hooks/core/protocol_injector.py pre_compact

# Full test
python3 ~/.claude/hooks/core/protocol_injector.py test
```

### Test MCP Tools
```bash
# In Claude Code, test actual MCP commands:
mcp__trinitas-mcp__trinitas_status()

mcp__trinitas-mcp__trinitas_remember(
    key="test",
    value="Testing v5.0",
    importance=1.0
)

mcp__trinitas-mcp__trinitas_recall(query="test")
```

## Configuration

### Minimal Hooks (.env)
```bash
# Only protocol injection settings needed
PROTOCOL_FILE=/Users/apto-as/.claude/TRINITAS-CORE-PROTOCOL.md
PROTOCOL_INJECTION_ENABLED=true
```

### trinitas-mcp (.env)
```bash
# Already configured at ~/.claude/trinitas/mcp-tools/.env
TRINITAS_NAMING_MODE=mythology
MEMORY_BACKEND=hybrid
# ... (existing configuration)
```

## Verification Checklist

- [ ] TRINITAS-CORE-PROTOCOL.md v5.0 deployed to ~/.claude/
- [ ] Protocol injector deployed to ~/.claude/hooks/core/
- [ ] Minimal settings.json deployed
- [ ] .env configuration updated
- [ ] Protocol injection test passes
- [ ] MCP tools accessible in Claude Code
- [ ] SessionStart hook triggers on new session
- [ ] PreCompact hook triggers on context compression

## Rollback Instructions

If issues occur:

```bash
# Restore previous protocol
cp ~/.claude/TRINITAS-CORE-PROTOCOL.md.backup ~/.claude/TRINITAS-CORE-PROTOCOL.md

# Disable hooks temporarily
mv ~/.claude/hooks/settings.json ~/.claude/hooks/settings.json.disabled

# Re-enable after fixing
mv ~/.claude/hooks/settings.json.disabled ~/.claude/hooks/settings.json
```

## Summary

**v5.0 Architecture:**
- **Execution**: trinitas-mcp handles all persona execution via MCP tools
- **Injection**: Minimal hooks inject protocol at key moments
- **Memory**: trinitas-mcp manages hybrid memory system
- **Safety**: Permissive mode with minimal critical blocks only

This achieves the user's vision: "理想的な協調動作を、実際のMCPツールで実現"

---

*Deployment Guide v5.0 - Created: 2024-12-28*