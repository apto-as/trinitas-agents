#!/bin/bash

# Trinitas v3.5 Installation Script
# Installs Local LLM Integration to ~/.claude/trinitas/

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}     Trinitas v3.5 - Hybrid Intelligence Installation${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
echo ""

# Check if Claude installation exists
CLAUDE_DIR="$HOME/.claude"
TRINITAS_DIR="$CLAUDE_DIR/trinitas"

if [ ! -d "$CLAUDE_DIR" ]; then
    echo -e "${RED}❌ Claude directory not found at $CLAUDE_DIR${NC}"
    echo -e "${YELLOW}Please ensure Claude Code is installed first${NC}"
    exit 1
fi

# Create trinitas directory if it doesn't exist
if [ ! -d "$TRINITAS_DIR" ]; then
    echo -e "${YELLOW}📁 Creating Trinitas directory...${NC}"
    mkdir -p "$TRINITAS_DIR"
fi

# Get the script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

echo -e "${BLUE}📦 Installing v3.5 Components...${NC}"
echo ""

# Copy Local LLM components
echo -e "${GREEN}→ Installing Local LLM Integration...${NC}"
cp -r "$PROJECT_ROOT/local-llm" "$TRINITAS_DIR/"

# Update config with user's Local LLM endpoint
echo ""
echo -e "${YELLOW}🔧 Configuration Required:${NC}"
echo -e "Local LLM Server endpoint is currently set to: ${GREEN}http://192.168.99.102:1234${NC}"
echo ""
read -p "Is this correct? (y/n): " -n 1 -r
echo ""

if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo ""
    read -p "Enter your Local LLM server endpoint (e.g., http://localhost:8080): " ENDPOINT
    
    # Update the config file
    CONFIG_FILE="$TRINITAS_DIR/local-llm/config.yaml"
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        sed -i '' "s|endpoint: .*|endpoint: \"$ENDPOINT/v1\"|" "$CONFIG_FILE"
    else
        # Linux
        sed -i "s|endpoint: .*|endpoint: \"$ENDPOINT/v1\"|" "$CONFIG_FILE"
    fi
    
    echo -e "${GREEN}✅ Updated endpoint to: $ENDPOINT/v1${NC}"
fi

# Check Python dependencies
echo ""
echo -e "${BLUE}📚 Checking Python dependencies...${NC}"

# Required packages
REQUIRED_PACKAGES="aiohttp pyyaml pytest pytest-asyncio"

for package in $REQUIRED_PACKAGES; do
    if python -c "import $package" 2>/dev/null; then
        echo -e "  ✅ $package"
    else
        echo -e "  ⚠️  $package not found, installing..."
        pip install $package
    fi
done

# Create MCP server configuration
echo ""
echo -e "${BLUE}🔧 Creating MCP Server configuration...${NC}"

MCP_CONFIG_FILE="$CLAUDE_DIR/claude_desktop_config.json"

# Check if config exists
if [ -f "$MCP_CONFIG_FILE" ]; then
    echo -e "${YELLOW}Existing MCP configuration found${NC}"
    
    # Backup existing config
    cp "$MCP_CONFIG_FILE" "$MCP_CONFIG_FILE.backup.$(date +%Y%m%d_%H%M%S)"
    echo -e "${GREEN}✅ Backup created${NC}"
else
    # Create new config
    echo "{}" > "$MCP_CONFIG_FILE"
fi

# Add Trinitas v3.5 MCP server to config using Python
python << EOF
import json
import os

config_file = "$MCP_CONFIG_FILE"

# Read existing config
with open(config_file, 'r') as f:
    config = json.load(f)

# Ensure mcpServers exists
if 'mcpServers' not in config:
    config['mcpServers'] = {}

# Add Trinitas v3.5 server
config['mcpServers']['trinitas-v35'] = {
    "command": "python",
    "args": ["$TRINITAS_DIR/local-llm/connector/llm_connector.py"],
    "env": {
        "TRINITAS_MODE": "hybrid",
        "LOCAL_LLM_ENDPOINT": os.environ.get('LOCAL_LLM_ENDPOINT', 'http://192.168.99.102:1234/v1'),
        "LOCAL_LLM_API_KEY": os.environ.get('LOCAL_LLM_API_KEY', '')
    }
}

# Write updated config
with open(config_file, 'w') as f:
    json.dump(config, f, indent=2)

print("✅ MCP server configuration updated")
EOF

# Test Local LLM connection
echo ""
echo -e "${BLUE}🔌 Testing Local LLM connection...${NC}"

cd "$TRINITAS_DIR/local-llm"
python tests/test_real_connection.py 2>&1 | head -20

# Check if test passed
if [ ${PIPESTATUS[0]} -eq 0 ]; then
    echo -e "${GREEN}✅ Local LLM connection successful!${NC}"
else
    echo -e "${YELLOW}⚠️  Could not connect to Local LLM server${NC}"
    echo -e "Please ensure your Local LLM server is running and try again"
fi

# Create quick test script
cat > "$TRINITAS_DIR/test_v35.py" << 'EOF'
#!/usr/bin/env python3
"""Quick test for Trinitas v3.5"""

import asyncio
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'local-llm'))

from connector.llm_connector import LocalLLMConnector, TaskRequest, CognitiveComplexity
from delegation.delegation_engine import CognitiveDelegationEngine

async def test():
    print("🧪 Testing Trinitas v3.5 Hybrid Intelligence")
    print("=" * 50)
    
    engine = CognitiveDelegationEngine()
    await engine.initialize()
    
    # Test delegation decision
    task = TaskRequest(
        id="test-001",
        type="file_search",
        description="Find all Python files",
        estimated_tokens=1000,
        required_tools=["file_operations"]
    )
    
    decision = await engine.decide_delegation(task)
    print(f"✅ Task delegation: {decision.executor.value}")
    print(f"   Reason: {decision.reason}")
    print(f"   Confidence: {decision.confidence:.0%}")
    
    print("\n✅ Trinitas v3.5 is ready!")

if __name__ == "__main__":
    asyncio.run(test())
EOF

chmod +x "$TRINITAS_DIR/test_v35.py"

# Final summary
echo ""
echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}              Installation Complete! 🎉${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
echo ""
echo -e "${GREEN}Installed Components:${NC}"
echo -e "  ✅ Local LLM Connector"
echo -e "  ✅ Cognitive Delegation Engine"
echo -e "  ✅ Sparring Partner System"
echo -e "  ✅ Test Automation Pipeline"
echo ""
echo -e "${GREEN}Installation Location:${NC}"
echo -e "  📁 $TRINITAS_DIR/local-llm/"
echo ""
echo -e "${GREEN}Quick Test:${NC}"
echo -e "  Run: ${YELLOW}python $TRINITAS_DIR/test_v35.py${NC}"
echo ""
echo -e "${GREEN}Next Steps:${NC}"
echo -e "  1. Ensure your Local LLM server is running"
echo -e "  2. Set LOCAL_LLM_API_KEY if required"
echo -e "  3. Restart Claude Code to load new MCP configuration"
echo ""
echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"