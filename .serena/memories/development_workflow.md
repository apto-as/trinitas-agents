# Development Workflow

This document outlines the development workflow for the Trinitas Agents project, including coding style, linting, formatting, and testing procedures.

## Coding Style

The project enforces a consistent coding style for all Python code using a combination of `black`, `ruff`, and `mypy`.

### Python

*   **Formatter:** `black` is used for automatic code formatting.
*   **Linter:** `ruff` is used for linting.
*   **Type Checking:** `mypy` is used for static type checking.

### Shell Scripts

Shell scripts should follow standard best practices and be clear and well-documented.

## Development Process

1.  **Make changes:** Implement new features or fix bugs.
2.  **Format code:** Before committing, ensure your Python code is formatted with `black`.
3.  **Lint code:** Run `ruff` to check for any linting errors.
4.  **Run type checker:** Use `mypy` to verify type correctness.
5.  **Run tests:** Execute the integration test suite to ensure your changes haven't introduced any regressions.
6.  **Commit and push:** Once all checks pass, commit your changes with a clear and descriptive commit message.

## Testing

The project uses a final integration test script to verify the correctness of the entire system.

To run the integration tests, use the following command:

```bash
python test_final_integration.py
```
