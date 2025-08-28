# Minimal Hooks Implementation v3.0

## Purpose

This minimal hooks implementation serves ONLY ONE PURPOSE:
- **Protocol Injection**: Automatically inject TRINITAS-CORE-PROTOCOL.md at SessionStart and PreCompact events

All other functionality has been migrated to trinitas-mcp.

## Files Retained

```
hooks/
├── core/
│   └── protocol_injector.py      # Protocol injection only
├── settings.json                  # Minimal settings for protocol injection
├── .env                          # Config for protocol path
└── MINIMAL_HOOKS_README.md       # This file
```

## Why Keep This?

After thorough investigation, trinitas-mcp does NOT have:
1. SessionStart hook capability
2. PreCompact (prompt compression) hook capability  
3. Protocol injection functionality

These are critical for ensuring the TRINITAS-CORE-PROTOCOL.md is always available to Claude, especially during long conversations when context compression occurs.

## Configuration

### .env
```bash
PROTOCOL_FILE=$HOME/.claude/TRINITAS-CORE-PROTOCOL.md
PROTOCOL_INJECTION_ENABLED=true
```

### settings.json
```json
{
  "hooks": {
    "SessionStart": [
      {
        "matcher": "*",
        "hooks": [{
          "type": "command",
          "command": "python3 ~/.claude/hooks/core/protocol_injector.py session_start"
        }]
      }
    ],
    "PreCompact": [
      {
        "matcher": "*",
        "hooks": [{
          "type": "command",
          "command": "python3 ~/.claude/hooks/core/protocol_injector.py pre_compact"
        }]
      }
    ]
  }
}
```

## Installation

```bash
# Copy minimal hooks to production
cp hooks/core/protocol_injector.py ~/.claude/hooks/core/
cp hooks/settings.json ~/.claude/hooks/
cp hooks/.env ~/.claude/hooks/

# Test
python3 ~/.claude/hooks/core/protocol_injector.py test
```

## What Was Removed

All other hooks functionality has been removed because:
1. **Safety checks** → Not needed with permissive mode
2. **Parallel agents** → Handled by trinitas-mcp 
3. **Code quality** → Handled by Artemis persona
4. **Monitoring** → Handled by trinitas-mcp metrics
5. **Recovery** → Handled by trinitas-mcp error handling

## Integration with trinitas-mcp

The minimal hooks work alongside trinitas-mcp:
- **Hooks**: Protocol injection at session start and prompt compression
- **trinitas-mcp**: Everything else (personas, memory, collaboration, etc.)

This achieves the user's goal: "Hooksはプロンプト圧縮が入るタイミングでTRINITAS-CORE-PROTOCOL.mdを強制的に読み込ませる機能がv2.0までは存在したので、その機能だけ残したい"