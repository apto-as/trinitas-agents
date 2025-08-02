# Trinitas Python Enhancement Layer

## Overview

The Python Enhancement Layer provides advanced code analysis, security scanning, and quality metrics using Python's powerful AST parsing and optional third-party tools.

## Features

### Core Features (No Extra Dependencies)
- **AST-based Code Analysis**: Deep Python code analysis
- **Security Pattern Detection**: Find common vulnerabilities
- **Quality Metrics**: Cyclomatic complexity, maintainability index
- **Beautiful Output**: Rich terminal output with character personalities

### Enhanced Features (Optional)
- **Tree-sitter Support**: Multi-language parsing
- **Bandit Integration**: Python security linter
- **Safety Integration**: Dependency vulnerability scanning
- **Rich Terminal UI**: Beautiful reports and progress indicators

## Installation

### Quick Setup

```bash
# Install uv and setup Python environment
./hooks/python/setup_uv.sh

# Install with enhanced features
./hooks/python/setup_uv.sh --enhanced --security
```

### Manual Setup

1. Install uv (if not already installed):
```bash
# macOS
brew install uv

# Linux/macOS (alternative)
curl -LsSf https://astral.sh/uv/install.sh | sh
```

2. Create virtual environment:
```bash
cd hooks/python
uv venv .venv
source .venv/bin/activate
```

3. Install dependencies:
```bash
# Core only
uv pip install -e .

# With all features
uv pip install -e ".[dev,enhanced,security]"
```

## Usage

### As a Claude Code Hook

Update your `settings.json`:

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Write|Edit|MultiEdit",
        "hooks": [
          {
            "type": "command",
            "command": "~/.claude/trinitas/hooks/python/run_python_hook.sh ~/.claude/trinitas/hooks/python/enhanced_quality_check.py"
          }
        ]
      }
    ],
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": "~/.claude/trinitas/hooks/python/run_python_hook.sh ~/.claude/trinitas/hooks/python/security_scanner.py"
          }
        ]
      }
    ]
  }
}
```

### Standalone Usage

```bash
# Activate environment
source hooks/python/.venv/bin/activate

# Run quality check
export CLAUDE_TOOL_NAME="Write"
export CLAUDE_TOOL_ARGUMENTS='{"file_path":"example.py"}'
python hooks/python/enhanced_quality_check.py

# Run security scan
python hooks/python/security_scanner.py
```

## Available Hooks

### enhanced_quality_check.py
- Advanced code quality analysis
- Language-specific checks
- Detailed metrics and reports
- Integration with Krukai's perfectionist standards

### security_scanner.py
- Deep security vulnerability scanning
- Command injection detection
- Dependency vulnerability warnings
- Vector's paranoid security checks

## Development

### Running Tests

```bash
# Activate environment
source hooks/python/.venv/bin/activate

# Run tests
pytest

# With coverage
pytest --cov=trinitas_hooks
```

### Adding New Analyzers

1. Create a new analyzer in `trinitas_hooks/analyzers.py`
2. Inherit from appropriate base class
3. Implement analysis logic
4. Add tests in `tests/`

Example:
```python
class MyAnalyzer:
    def analyze(self, file_path: str) -> List[CodeIssue]:
        issues = []
        # Your analysis logic
        return issues
```

## Architecture

```
trinitas_hooks/
├── __init__.py         # Package exports
├── core.py            # Base classes and utilities
├── analyzers.py       # Code and security analyzers
├── quality.py         # Quality metrics and checks
└── logging.py         # Rich output and character logging

hooks/
├── enhanced_quality_check.py  # Main quality hook
└── security_scanner.py        # Main security hook
```

## Performance Considerations

- The Python layer adds ~100-200ms overhead
- Use Shell hooks for critical path operations
- Python hooks are best for comprehensive analysis
- Cache analysis results when possible

## Troubleshooting

### uv not found
- Ensure uv is in your PATH
- Try: `export PATH="$HOME/.cargo/bin:$PATH"`

### Import errors
- Activate virtual environment: `source .venv/bin/activate`
- Reinstall: `uv pip install -e .`

### No rich output
- Install enhanced features: `uv pip install -e ".[enhanced]"`

## Future Enhancements

- Integration with more security tools
- Machine learning-based code smell detection
- Custom rule engine
- Performance profiling integration
- Multi-language support via tree-sitter