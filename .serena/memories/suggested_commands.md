# Suggested Commands

This file provides a list of useful commands for installing and testing the Trinitas Agents project.

## Installation

*   **Main Installation Script:**

    ```bash
    ./install_to_claude.sh
    ```

## Testing

*   **Run Final Integration Tests:**

    ```bash
    python test_final_integration.py
    ```

## Memory System (via MCP Tools)

*   **Remember Information:**

    ```bash
    # Example using a hypothetical mcp-cli
    mcp call trinitas_remember --persona athena --content "The project uses a mythology-based naming convention."
    ```

*   **Recall Information:**

    ```bash
    # Example using a hypothetical mcp-cli
    mcp call trinitas_recall --persona athena --query "naming convention"
    ```
