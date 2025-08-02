# Trinitas Hooks System v3.0

## Overview

The Trinitas Hooks System provides automated safety checks, quality assurance, and test execution for Claude Code operations. Built with a Shell Script core for reliability and optional Python enhancements for advanced features.

## Architecture

```
hooks/
├── core/               # Core libraries and utilities
│   ├── common_lib.sh   # Shared functions and logging
│   └── safety_check.sh # Security validation module
├── pre-execution/      # Hooks that run before tool execution
│   └── 01_safety_check.sh
├── post-execution/     # Hooks that run after tool execution
│   ├── 01_code_quality_check.sh
│   └── 02_test_runner.sh
├── tests/              # TDD test framework
│   ├── test_framework.sh
│   ├── unit/           # Unit tests
│   └── integration/    # Integration tests
└── examples/           # Example configurations
    └── settings.json
```

## Installation

The hooks are automatically installed by the main Trinitas installer:

```bash
./install.sh
```

This will:
1. Copy hook scripts to `~/.claude/trinitas/hooks/`
2. Update your `settings.json` with hook configurations
3. Make all scripts executable

## Configuration

### Minimal Mode
- Pre-execution safety checks for Bash commands only

### Standard Mode (Recommended)
- Pre-execution safety checks for Bash commands
- Post-execution code quality checks for file modifications

### Comprehensive Mode
- All standard features plus:
- File safety checks for write operations
- Automatic test execution after code changes

## Testing

Run the test suite:

```bash
# Run all tests
./hooks/tests/test_framework.sh ./hooks/tests/unit/test_*.sh

# Run specific test
./hooks/tests/unit/test_safety_check.sh
```

## Security Features

### Dangerous Command Detection
- Prevents execution of destructive commands (rm -rf /, dd to devices, etc.)
- Blocks sudo operations
- Detects fork bombs

### Path Safety Validation
- Prevents writes to system directories
- Validates project directory boundaries

### Network Safety
- Blocks piping network content to shells
- Validates safe network operations

### Git Operation Safety
- Prevents force push to main branches
- Blocks dangerous reset operations

## Code Quality Checks

### Universal Checks
- File size limits
- Line length validation
- Trailing whitespace detection
- Mixed indentation detection

### Language-Specific
- JavaScript: console.log, debugger statements
- Python: print statements, bare except clauses
- Shell: unquoted variables, backtick usage

## Character Personalities

The hooks incorporate the Trinitas-Core personalities:

- **Springfield**: Provides encouraging feedback and strategic guidance
- **Krukai**: Enforces strict quality standards and optimization
- **Vector**: Focuses on security threats and risk mitigation

## Extending the System

### Adding New Hooks

1. Create a new script in the appropriate directory
2. Source the common library
3. Implement your hook logic
4. Update settings.json to register the hook

Example:
```bash
#!/bin/bash
source "$HOOKS_ROOT/core/common_lib.sh"

main() {
    # Your hook logic here
    format_hook_result "success" "Hook completed"
}

main "$@"
```

### Writing Tests

Use the TDD framework:
```bash
test_my_feature() {
    describe "My Feature"
    it "should do something"
    assert_equals "expected" "actual" "Test description"
}
```

## Troubleshooting

### Hooks Not Running
- Check that settings.json contains hook configurations
- Verify scripts are executable: `chmod +x ~/.claude/trinitas/hooks/**/*.sh`
- Check Claude Code logs for errors

### Test Failures
- Run tests individually to isolate issues
- Check for environment variable dependencies
- Ensure all required tools are installed

## Future Enhancements (Phase 2)

- Python enhancement layer with uv package manager
- Advanced static analysis
- Multi-language linting integration
- Performance profiling
- Security scanning with external tools