#!/bin/bash

# Trinitas-Core Protocol v4.0 Installation Script
# This script installs the updated protocol to the production environment

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROTOCOL_FILE="$SCRIPT_DIR/protocols/TRINITAS-CORE-PROTOCOL.md"
TARGET_FILE="$HOME/.claude/TRINITAS-CORE-PROTOCOL.md"

echo "🌸 Installing Trinitas-Core Protocol v4.0..."

# Check if protocol file exists
if [ ! -f "$PROTOCOL_FILE" ]; then
    echo "❌ Protocol file not found: $PROTOCOL_FILE"
    exit 1
fi

# Backup existing protocol if it exists
if [ -f "$TARGET_FILE" ]; then
    echo "📦 Backing up existing protocol..."
    cp "$TARGET_FILE" "$TARGET_FILE.backup.$(date +%Y%m%d_%H%M%S)"
fi

# Install new protocol
echo "📥 Installing new protocol..."
cp "$PROTOCOL_FILE" "$TARGET_FILE"

# Verify installation
if [ -f "$TARGET_FILE" ]; then
    VERSION=$(grep "Protocol v" "$TARGET_FILE" | head -1)
    echo "✅ Successfully installed: $VERSION"
    echo "📍 Location: $TARGET_FILE"
    
    # Display key changes
    echo ""
    echo "🔥 Key Changes in v4.0:"
    echo "  - Springfield: 優しさで100%品質を強制する鋼鉄の意志"
    echo "  - Krukai: 404 = ZERO defects, ZERO shortcuts, ZERO compromises"
    echo "  - Vector: 全ての脅威に対策済み、楽観を1ミリも許さない"
    echo "  - Quality Standard: 100%のみが成功、99.9%は失敗"
else
    echo "❌ Installation failed"
    exit 1
fi

echo ""
echo "🎯 Protocol v4.0 is now active. 妥協なき品質追求を開始します。"