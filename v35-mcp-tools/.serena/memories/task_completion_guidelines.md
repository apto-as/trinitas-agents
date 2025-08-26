When a development task (e.g., adding a feature, fixing a bug) is completed, the following steps should be performed to ensure code quality and consistency:

1.  **Formatting:** Run the code formatter to ensure the new code adheres to the project's style standards.
    ```bash
    ruff format .
    ```
2.  **Linting:** Run the linter to check for potential errors, bugs, and stylistic issues.
    ```bash
    ruff check .
    ```
3.  **Type Checking:** Run the static type checker to catch type-related errors.
    ```bash
    mypy .
    ```
4.  **Testing:** Run the entire test suite to ensure that the changes have not introduced any regressions.
    ```bash
    pytest v35-mcp-tools/
    ```

Only after all these checks pass without errors should the code be considered for merging.