# TMWS Quick Start Guide

## Installation

```bash
# Clone repository
git clone https://github.com/apto-as/trinitas-agents.git
cd trinitas-agents/tmws

# Run installation script
./install.sh
```

## Configuration for Claude Desktop

Add to `~/Library/Application Support/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "tmws": {
      "command": "python",
      "args": ["-m", "unified_server", "--mcp-mode"],
      "cwd": "/absolute/path/to/tmws",
      "env": {
        "PYTHONPATH": "."
      }
    }
  }
}
```

**Note:** Replace `/absolute/path/to/tmws` with the actual path to your TMWS directory.

## Starting Services

### API Server Only
```bash
source .venv/bin/activate
uvicorn src.api.app:app --host 0.0.0.0 --port 8000 --reload
```

### Unified Server (MCP + API)
```bash
source .venv/bin/activate
python -m unified_server
```

## Verification

1. Check API health:
```bash
curl http://localhost:8000/health
```

2. View API documentation:
Open http://localhost:8000/docs in your browser

## Environment Variables

Key configuration in `.env`:
- `TMWS_DATABASE_URL` - PostgreSQL connection string
- `TMWS_REDIS_URL` - Redis connection string
- `TMWS_SECRET_KEY` - Application secret key
- `TMWS_JWT_SECRET` - JWT signing key