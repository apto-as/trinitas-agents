# Project Trinitas v3.5 - Project Summary

## Overview

Project Trinitas v3.5 is a sophisticated AI development support system designed for a native experience within Claude Code. It features a core of five AI personas with a dual naming scheme (Mythology and Developer modes), and a powerful, newly introduced Memory System.

*   **Athena (Strategic):** Focuses on high-level strategy, project planning, and architectural design.
*   **Artemis (Technical):** Specializes in code optimization, performance enhancements, and best-practice implementation.
*   **Hestia (Security):** Dedicated to identifying security vulnerabilities, conducting risk analysis, and ensuring compliance.
*   **Bellona (Tactical):** Specializes in parallel task coordination and resource optimization.
*   **Seshat (Documentation):** Focuses on knowledge management and documentation generation.

## Core Components

*   **AI Agents:** Defined in Markdown files, these agents encapsulate the knowledge and behavior of the different AI personas.
*   **Persona Definitions:** A central YAML file (`TRINITAS_PERSONA_DEFINITIONS.yaml`) that defines the characteristics, capabilities, and trigger keywords for each persona.
*   **Memory System:** A new, sophisticated component that provides agents with short-term and long-term memory, enabling them to learn and recall information from past interactions.
*   **Optional MCP Tools:** A Python-based component (`v35-mcp-tools`) that provides advanced features, including the new memory tools.

## Tech Stack

*   **AI Agent Definition:** Markdown
*   **MCP Tools & Memory System:** Python
*   **Installation:** Shell scripts
*   **Code Formatting:** `black`
*   **Linting:** `ruff`
*   **Type Checking:** `mypy`
*   **Testing:** `pytest`

## Key Changes

The project has evolved significantly with two major changes:
1.  **Architecture Simplification:** The complex `v35-mcp-engine` has been deprecated in favor of a more streamlined, native Claude Code experience.
2.  **Introduction of the Memory System:** A powerful new feature that allows agents to learn and remember, adding a new dimension to their capabilities.
