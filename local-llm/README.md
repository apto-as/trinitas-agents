# Trinitas v3.5 - Local LLM Integration

## Overview
Hybrid Intelligence system that intelligently delegates tasks between Claude and Local LLM based on cognitive complexity.

## Architecture

### Core Components

1. **Local LLM Connector** (`connector/llm_connector.py`)
   - Manages communication with Qwen Code + GPT-OSS-120B
   - English-optimized prompting
   - Excellent tool use capabilities

2. **Cognitive Delegation Engine** (`delegation/delegation_engine.py`)
   - Routes tasks based on cognitive complexity (5 levels)
   - Handles context pressure management
   - Supports hybrid execution for heavy+complex tasks

3. **Sparring Partner System** (`sparring/sparring_partner.py`)
   - 4 modes: Devil's Advocate, Alternative Finder, Edge Case Hunter, Perspective Shift
   - Uses Local LLM for intelligent problem-solving assistance

4. **Test Automation Pipeline** (`testing/test_automation.py`)
   - Delegates test generation based on complexity
   - Mechanical tests → Local LLM
   - Strategic tests → Claude

## Setup Requirements

### 1. Local LLM Server Setup

You need to run Qwen Code with GPT-OSS-120B model:

```bash
# Start your Local LLM server
# Make sure it's listening on http://localhost:8080

# Set API key if required
export LOCAL_LLM_API_KEY="your-api-key"
```

### 2. Configuration

Edit `config.yaml` to match your setup:

```yaml
local_llm:
  connection:
    endpoint: "http://localhost:8080/v1"  # Your server endpoint
    api_key: "${LOCAL_LLM_API_KEY}"       # From environment variable
```

### 3. Test Connection

```bash
# Test if Local LLM server is accessible
python tests/test_real_connection.py
```

## Cognitive Complexity Levels

| Level | Type | Description | Executor |
|-------|------|-------------|----------|
| 1 | Mechanical | Simple, repetitive tasks | Local LLM |
| 2 | Analytical | Pattern matching, analysis | Local LLM |
| 3 | Reasoning | Logic and inference | Context-dependent |
| 4 | Creative | Novel solutions | Claude |
| 5 | Strategic | Long-term planning | Claude |

## Task Delegation Rules

### Always Local LLM
- Large file operations
- Test execution
- Documentation generation
- Log analysis
- Metric collection

### Always Claude
- Security audits
- Architecture decisions
- API design
- Algorithm creation
- Strategic planning

### Hybrid Execution
Tasks that are both heavy (>100K tokens) AND complex (level 4-5):
1. Local LLM: Data gathering and initial analysis
2. Claude: Deep analysis and strategic decisions
3. Synthesis: Combine both results

## Usage Examples

### Basic Task Execution

```python
from connector.llm_connector import LocalLLMConnector, TaskRequest, CognitiveComplexity

async def example():
    connector = LocalLLMConnector()
    await connector.initialize()
    
    task = TaskRequest(
        id="task-001",
        type="file_search",
        description="Find all Python files with async functions",
        estimated_tokens=5000,
        required_tools=["file_operations"],
        complexity=CognitiveComplexity.MECHANICAL
    )
    
    response = await connector.execute(task)
    print(f"Result: {response.result}")
    
    await connector.cleanup()
```

### Cognitive Delegation

```python
from delegation.delegation_engine import CognitiveDelegationEngine

async def delegate_example():
    engine = CognitiveDelegationEngine()
    await engine.initialize()
    
    # Complex task - will go to Claude
    complex_task = TaskRequest(
        id="complex-001",
        type="algorithm_design",
        description="Design distributed consensus algorithm",
        estimated_tokens=10000,
        required_tools=[]
    )
    
    decision = await engine.decide_delegation(complex_task)
    print(f"Executor: {decision.executor.value}")
    print(f"Reason: {decision.reason}")
```

### Sparring Session

```python
from sparring.sparring_partner import SparringPartnerSystem, SparringMode

async def sparring_example():
    sparring = SparringPartnerSystem()
    await sparring.initialize()
    
    session = await sparring.conduct_sparring(
        problem="Design caching system for 1M req/s",
        current_solution="Use simple LRU cache",
        mode=SparringMode.DEVIL_ADVOCATE
    )
    
    print(f"Challenges found: {len(session.challenges)}")
    for challenge in session.challenges:
        print(f"- [{challenge.severity}] {challenge.description}")
```

## Testing

### Run All Tests
```bash
./tests/run_tests.sh
```

### Test Coverage
```bash
./tests/run_tests.sh --coverage
```

### Performance Tests
```bash
./tests/run_tests.sh --performance
```

## Troubleshooting

### Server Not Available
If you see "Cannot connect to server at http://localhost:8080/v1":

1. Check if Qwen Code is running
2. Verify the endpoint in `config.yaml`
3. Check firewall/network settings
4. Ensure API key is set (if required)

### Test Hanging Issues
Some tests may hang due to fixture issues. Run individual test files:

```bash
python -m pytest tests/test_delegation.py -v
python -m pytest tests/test_simple.py -v
```

### Import Errors
Ensure you're in the correct directory:
```bash
cd local-llm
python -m pytest tests/
```

## Performance Considerations

- **Local LLM**: Best for high-volume, mechanical tasks
- **Claude**: Best for complex reasoning and creative tasks
- **Hybrid**: Automatically triggered for heavy+complex tasks
- **Context Pressure**: System automatically manages token usage

## Future Improvements

1. Real-time performance monitoring
2. Automatic model switching based on load
3. Enhanced error recovery
4. Multi-model ensemble support
5. Streaming response support