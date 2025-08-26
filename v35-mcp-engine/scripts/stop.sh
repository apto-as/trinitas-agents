#!/bin/bash

# Trinitas v3.5 TRUE - Stop Script
# Stop the MCP orchestration system

echo "🛑 Stopping Trinitas v3.5 TRUE..."

docker-compose down

echo "✅ All services stopped"