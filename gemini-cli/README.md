# Trinitas Agents for Gemini-CLI

This directory contains the implementation of the Trinitas Agents concept, adapted for use with `gemini-cli`.
It provides a powerful, persona-driven interface for interacting with Google's Gemini models, enabling complex, multi-perspective analysis and development workflows.

## Features

- **Persona-Driven Execution**: Run `gemini-cli` with different core personalities (Springfield, Krukai, Vector, etc.).
- **Parallel Analysis**: Execute multiple personas simultaneously to get a comprehensive analysis from strategic, technical, and risk perspectives in a fraction of the time.
- **Advanced Workflow Integration**: A built-in MCP server provides tools for complex logic, like achieving consensus among personas (demonstration).

## Directory Structure

- `config/`: Configuration files for `gemini-cli`, such as MCP server connections.
- `mcp_server/`: A Python-based MCP server that exposes advanced collaboration logic as tools.
- `personas/`: Markdown files defining the system prompts for each Trinitas persona.
- `scripts/`: The main entry point and wrapper scripts for using the system.

## Setup

1.  **Install `gemini-cli`**: Ensure you have `gemini-cli` installed and configured on your system.

2.  **Start the MCP Server** (Optional, for advanced workflows):
    ```bash
    python3 ./gemini-cli/mcp_server/server.py
    ```
    This will start the local server on port 8080, which `gemini-cli` will automatically connect to if configured.

3.  **Set `gemini-cli` Configuration**:
    To enable the MCP server, you can tell `gemini-cli` to use the provided configuration file:
    ```bash
    gemini-cli config set -p ./gemini-cli/config/settings.json
    ```

## Usage

The primary way to interact with this system is through the `trinitas` wrapper script.

### 1. Single Persona Mode

Run `gemini-cli` with a specific persona loaded.

**Syntax**:
`./gemini-cli/scripts/trinitas --persona=<persona_name> "<your_prompt>"`

**Example**:
```bash
./gemini-cli/scripts/trinitas --persona=krukai-optimizer "Refactor this function for maximum performance."
```

### 2. Parallel Analysis Mode

Run the three core personas (Springfield, Krukai, Vector) in parallel on the same prompt.

**Syntax**:
`./gemini-cli/scripts/trinitas --parallel "<your_prompt>"`

**Example**:
```bash
./gemini-cli/scripts/trinitas --parallel "Review this system architecture design document."
```

### 3. Listing Personas

To see a list of all available personas:
```bash
./gemini-cli/scripts/trinitas --list-personas
```
