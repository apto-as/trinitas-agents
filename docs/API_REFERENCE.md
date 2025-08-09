# Trinitas Agents - API Reference

## 📚 Python API Reference

### Core Module (`trinitas_hooks.core`)

#### Class: `HookStatus`

Enumeration for hook execution status.

```python
from trinitas_hooks.core import HookStatus

class HookStatus(Enum):
    SUCCESS = "success"   # Operation completed successfully
    WARNING = "warning"   # Operation completed with warnings
    ERROR = "error"       # Operation failed
    BLOCKED = "blocked"   # Operation blocked for security reasons
```

#### Class: `HookResult`

Data class for hook execution results.

```python
from trinitas_hooks.core import HookResult

@dataclass
class HookResult:
    status: HookStatus
    message: str
    details: Optional[str] = None
    data: Optional[Dict[str, Any]] = None
    
    def to_shell_format(self) -> str:
        """Format result for shell output with colors."""
```

**Example Usage**:
```python
result = HookResult(
    status=HookStatus.SUCCESS,
    message="Analysis completed",
    details="Found 3 potential improvements",
    data={"improvements": [...]}
)
print(result.to_shell_format())
```

#### Class: `TrinitasHook`

Abstract base class for all Trinitas hooks.

```python
from trinitas_hooks.core import TrinitasHook

class TrinitasHook(ABC):
    def __init__(self) -> None:
        """Initialize with Claude environment variables."""
        
    def validate_environment(self) -> bool:
        """Validate Claude Code environment."""
        
    @abstractmethod
    def run(self) -> HookResult:
        """Execute the hook logic. Must be implemented by subclasses."""
        
    def execute(self) -> int:
        """Execute hook and return shell exit code."""
```

**Creating Custom Hooks**:
```python
from trinitas_hooks.core import TrinitasHook, HookResult, HookStatus

class MyCustomHook(TrinitasHook):
    def run(self) -> HookResult:
        # Your hook logic here
        return HookResult(
            status=HookStatus.SUCCESS,
            message="Custom hook executed"
        )

# Usage
if __name__ == "__main__":
    hook = MyCustomHook()
    exit_code = hook.execute()
```

### MCP Client Module (`trinitas_hooks.mcp_client`)

#### Class: `AsyncMCPClient`

Async context manager for MCP server communication (mock implementation).

```python
from trinitas_hooks.mcp_client import AsyncMCPClient

class AsyncMCPClient(AsyncContextManager['AsyncMCPClient']):
    def __init__(
        self,
        server_url: Optional[str] = None,
        timeout: float = 30.0,
        retry_count: int = 3
    ) -> None:
        """Initialize MCP client."""
    
    async def request(
        self,
        payload: Dict[str, Any],
        timeout: Optional[float] = None
    ) -> Dict[str, Any]:
        """Send request to MCP server."""
    
    async def batch_request(
        self,
        payloads: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Send multiple requests in parallel."""
```

**Example Usage**:
```python
import asyncio
from trinitas_hooks.mcp_client import AsyncMCPClient

async def search_example():
    async with AsyncMCPClient() as client:
        # Web search
        response = await client.request({
            "type": "web_search",
            "query": "Python async programming",
            "max_results": 5
        })
        print(response)
        
        # Batch requests
        responses = await client.batch_request([
            {"type": "web_search", "query": "AI agents"},
            {"type": "arxiv_search", "query": "machine learning"}
        ])

# Run async function
asyncio.run(search_example())
```

### Analyzers Module (`trinitas_hooks.analyzers`)

#### Class: `CodeAnalyzer`

Analyzes code for quality metrics and patterns.

```python
from trinitas_hooks.analyzers import CodeAnalyzer

class CodeAnalyzer:
    def __init__(self, file_path: str):
        """Initialize analyzer with file path."""
    
    def analyze_complexity(self) -> Dict[str, Any]:
        """Analyze cyclomatic complexity."""
    
    def find_patterns(self, patterns: List[str]) -> List[Dict[str, Any]]:
        """Find specific patterns in code."""
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get comprehensive code metrics."""
```

**Example Usage**:
```python
from trinitas_hooks.analyzers import CodeAnalyzer

analyzer = CodeAnalyzer("src/main.py")
metrics = analyzer.get_metrics()
print(f"Complexity: {metrics['complexity']}")
print(f"Lines of code: {metrics['lines_of_code']}")
```

#### Class: `SecurityAnalyzer`

Performs security analysis on code.

```python
from trinitas_hooks.analyzers import SecurityAnalyzer

class SecurityAnalyzer:
    def __init__(self, project_dir: str):
        """Initialize security analyzer."""
    
    def scan_vulnerabilities(self) -> List[Dict[str, Any]]:
        """Scan for security vulnerabilities."""
    
    def check_dependencies(self) -> Dict[str, Any]:
        """Check dependency security."""
```

### Quality Module (`trinitas_hooks.quality`)

#### Class: `QualityChecker`

Comprehensive code quality checking.

```python
from trinitas_hooks.quality import QualityChecker

class QualityChecker:
    def __init__(self, file_paths: List[str]):
        """Initialize with files to check."""
    
    def check_style(self) -> List[Dict[str, Any]]:
        """Check code style issues."""
    
    def check_type_hints(self) -> List[Dict[str, Any]]:
        """Check type hint coverage."""
    
    def generate_report(self) -> Dict[str, Any]:
        """Generate quality report."""
```

## 🐚 Shell Hook API

### Pre-execution Hooks

Located in `/hooks/pre-execution/`

#### Safety Check Hook

**File**: `01_safety_check.sh`

**Purpose**: Validates commands for safety before execution.

**Usage**:
```bash
export CLAUDE_TOOL_NAME="Bash"
export CLAUDE_TOOL_ARGUMENTS='{"command": "rm -rf /"}'
./hooks/pre-execution/01_safety_check.sh
```

**Exit Codes**:
- `0`: Command is safe
- `1`: Command is dangerous or blocked

#### Resource Validator Hook

**File**: `02_resource_validator.sh`

**Purpose**: Checks resource availability before operations.

### Post-execution Hooks

Located in `/hooks/post-execution/`

#### Result Processor Hook

**File**: `01_process_results.sh`

**Purpose**: Processes and formats execution results.

**Environment Variables**:
```bash
CLAUDE_TOOL_EXIT_CODE    # Exit code from tool execution
CLAUDE_TOOL_OUTPUT        # Output from tool execution
```

## 🔧 Configuration API

### YAML Configuration

**File**: `~/.claude/agents/trinitas/config.yaml`

```yaml
# Core configuration
core:
  mode: production | development
  trinity_enabled: boolean
  
# Agent configuration  
agents:
  auto_detect: boolean
  timeout: integer (seconds)
  max_concurrent: integer
  
# Security configuration
security:
  safety_level: LOW | MEDIUM | HIGH
  audit_enabled: boolean
  
# Performance configuration
performance:
  cache_enabled: boolean
  cache_ttl: integer (seconds)
```

### Environment Variables

Override configuration with environment variables:

```bash
# Core overrides
export TRINITAS_MODE="development"
export TRINITAS_TRINITY_ENABLED="true"

# Security overrides
export TRINITAS_SAFETY_LEVEL="HIGH"
export TRINITAS_AUDIT_ENABLED="true"

# Performance overrides
export TRINITAS_CACHE_ENABLED="true"
export TRINITAS_CACHE_TTL="3600"
```

## 🎭 Agent Selection API

### Natural Language Triggers

Agents are automatically selected based on keywords:

```python
# Trigger patterns for each agent
AGENT_TRIGGERS = {
    "springfield-strategist": [
        "strategy", "planning", "architecture",
        "roadmap", "project management"
    ],
    "krukai-optimizer": [
        "optimize", "performance", "refactor",
        "efficiency", "code quality"
    ],
    "vector-auditor": [
        "security", "audit", "vulnerability",
        "risk", "threat", "compliance"
    ]
}
```

### Programmatic Selection

```python
# Force specific agent selection
claude_response = await claude.ask(
    "/springfield - Plan our Q2 roadmap"
)

# Trinity coordination
claude_response = await claude.ask(
    "/trinitas - Comprehensive analysis of our system"
)
```

## 📊 Metrics and Monitoring API

### Performance Metrics

```python
from trinitas_hooks.metrics import MetricsCollector

collector = MetricsCollector()

# Collect metrics
metrics = collector.collect({
    "agent_execution_time": 2.3,
    "memory_usage_mb": 245,
    "cache_hit_rate": 0.85
})

# Export metrics
collector.export_prometheus()  # Prometheus format
collector.export_json()        # JSON format
```

### Logging API

```python
from trinitas_hooks.logging import TrinitasLogger

logger = TrinitasLogger("my_component")

# Log with severity levels
logger.debug("Debug information")
logger.info("Information message")
logger.warning("Warning message")
logger.error("Error message")

# Character-specific logging
logger.springfield("Strategic insight")
logger.krukai("Technical detail")
logger.vector("Security concern")
```

## 🔄 Workflow API

### Sequential Workflow

```python
from trinitas_hooks.workflow import Workflow, Task

workflow = Workflow("analysis_workflow")

# Add tasks
workflow.add_task(Task(
    agent="springfield-strategist",
    action="analyze_requirements"
))
workflow.add_task(Task(
    agent="krukai-optimizer",
    action="optimize_implementation"
))
workflow.add_task(Task(
    agent="vector-auditor",
    action="security_review"
))

# Execute workflow
results = await workflow.execute()
```

### Parallel Workflow (Simulated)

```python
from trinitas_hooks.workflow import ParallelWorkflow

workflow = ParallelWorkflow("trinity_analysis")

# Add parallel tasks
workflow.add_agents([
    "springfield-strategist",
    "krukai-optimizer",
    "vector-auditor"
])

# Execute (simulated parallel)
results = await workflow.execute_parallel(task="Analyze system")
```

## 🔐 Security API

### Input Validation

```python
from trinitas_hooks.security import InputValidator

validator = InputValidator()

# Validate command
is_safe = validator.validate_command("rm -rf /")
# Returns: False

# Validate file path
is_safe = validator.validate_path("../../etc/passwd")
# Returns: False
```

### Audit Logging

```python
from trinitas_hooks.security import AuditLogger

audit = AuditLogger()

# Log security event
audit.log_event({
    "type": "command_blocked",
    "command": "sudo rm -rf /",
    "user": "current_user",
    "timestamp": "2024-01-15T10:30:00Z"
})

# Query audit logs
events = audit.query(
    start_time="2024-01-15T00:00:00Z",
    event_type="command_blocked"
)
```

## 📦 Package Management API

### Installation

```python
# Development installation
pip install -e /path/to/trinitas-agents

# Production installation
pip install trinitas-agents

# With extras
pip install trinitas-agents[dev,mcp]
```

### Import Structure

```python
# Core imports
from trinitas_hooks import (
    TrinitasHook,
    HookResult,
    HookStatus
)

# Specific modules
from trinitas_hooks.analyzers import CodeAnalyzer
from trinitas_hooks.security import SecurityValidator
from trinitas_hooks.mcp_client import AsyncMCPClient
```

## 🔍 Error Handling

### Standard Error Response

```python
from trinitas_hooks.errors import TrinitasError

try:
    # Operation that might fail
    result = dangerous_operation()
except TrinitasError as e:
    print(f"Error: {e.message}")
    print(f"Code: {e.error_code}")
    print(f"Details: {e.details}")
```

### Error Codes

| Code | Description | Recovery Action |
|------|-------------|-----------------|
| E001 | Invalid environment | Check Claude Code setup |
| E002 | Security violation | Review command/input |
| E003 | Resource limit exceeded | Reduce operation scope |
| E004 | Configuration error | Check config.yaml |
| E005 | Agent not found | Verify agent installation |

## 🎯 Best Practices

### Type Safety

Always use type hints:
```python
from typing import Dict, List, Optional, Any

def process_data(
    data: Dict[str, Any],
    options: Optional[Dict[str, str]] = None
) -> List[Dict[str, Any]]:
    """Process data with optional configuration."""
    # Implementation
```

### Async Operations

Use async/await for I/O operations:
```python
async def fetch_data(url: str) -> Dict[str, Any]:
    async with AsyncMCPClient() as client:
        return await client.request({
            "type": "web_fetch",
            "url": url
        })
```

### Error Handling

Always handle specific exceptions:
```python
try:
    result = risky_operation()
except FileNotFoundError as e:
    logger.error(f"File not found: {e}")
    return default_value
except PermissionError as e:
    logger.error(f"Permission denied: {e}")
    raise TrinitasError("Insufficient permissions", code="E002")
```

---

*API Reference Version: 3.0.0*
*Last Updated: 2024-01-15*