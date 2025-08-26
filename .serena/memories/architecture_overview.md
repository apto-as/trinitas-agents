# Architecture Overview

This document provides a high-level overview of the simplified Trinitas Agents system architecture.

## Core Philosophy: Streamlined, Claude-Native, and Learning

The architecture of Trinitas v3.5 has been significantly refactored to prioritize a streamlined, maintainable, and native experience within Claude Code, with the new addition of a powerful memory system that allows the agents to learn and evolve.

## Core Components

1.  **Agents (`agents/*.md`)**
    *   The core intelligence of the system, defining the behavior of the five AI personas.
    *   Designed for direct execution within Claude Code for most tasks.

2.  **Persona Definitions (`TRINITAS_PERSONA_DEFINITIONS.yaml`)**
    *   A centralized YAML file that acts as the single source of truth for all persona-related information.

3.  **Memory System (`v35-mcp-tools/src/memory`)**
    *   A sophisticated new component that provides agents with short-term and long-term memory.
    *   It's based on a cognitive architecture with different memory types (working, episodic, semantic, procedural) and allows agents to learn from past interactions.

4.  **Optional MCP Tools (`v35-mcp-tools`)**
    *   A self-contained Python component that provides advanced, optional features, including the new memory tools (`trinitas_remember`, `trinitas_recall`, etc.).

## Simplified Execution Flow

*   **Standard Tasks:** Handled directly by the native agents within Claude Code, based on keyword triggers.
*   **Advanced Tasks:** Can optionally leverage the `v35-mcp-tools` for more complex, multi-agent collaboration and memory operations.

This architecture results in a system that is not only simple and maintainable but also capable of learning and adapting over time.
