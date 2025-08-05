# Trinitas Parallel Agents Architecture

## 🏗️ System Architecture Overview

The Trinitas Parallel Agents system leverages Claude Code's native hooks to enable concurrent execution of multiple specialized AI agents, providing comprehensive analysis from multiple perspectives.

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    User Prompt Input                        │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│              PreToolUse Hook (Task Tool)                    │
│         prepare_parallel_tasks.py analyzes prompt           │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│                 Prompt Analysis Engine                       │
│  - Complexity scoring (1-5 scale)                           │
│  - Keyword matching for agent selection                     │
│  - Parallelization decision                                │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│              Parallel Task Distribution                      │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐          │
│  │ Springfield │ │   Krukai    │ │   Vector    │          │
│  │ Strategist  │ │ Optimizer   │ │  Auditor    │          │
│  └──────┬──────┘ └──────┬──────┘ └──────┬──────┘          │
│         │               │               │                   │
│         ▼               ▼               ▼                   │
│    Strategic      Technical       Security                  │
│    Analysis      Optimization     Assessment               │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│             SubagentStop Hook (Per Agent)                   │
│         capture_subagent_result.sh saves results            │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│              Result Integration Engine                       │
│         integrate_parallel_results.py combines              │
│         all agent outputs into unified response             │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│                  Integrated Response                         │
│            Comprehensive multi-perspective analysis          │
└─────────────────────────────────────────────────────────────┘
```

## 🔄 Execution Flow

### 1. Task Initiation Phase

When a user invokes the Task tool:

```python
# User prompt triggers Task tool
Task(prompt="Analyze security and optimize performance of auth system")
```

### 2. Pre-Execution Analysis

The `prepare_parallel_tasks.py` hook:

1. **Analyzes prompt complexity**
   ```python
   complexity_score = analyze_complexity(prompt)
   # Factors: word count, technical terms, multi-aspect requests
   ```

2. **Identifies suitable agents**
   ```python
   agents = identify_agents_by_keywords(prompt)
   # Matches keywords to agent capabilities
   ```

3. **Decides on parallelization**
   ```python
   if complexity_score >= 3 and len(agents) >= 2:
       enable_parallel_execution()
   ```

### 3. Parallel Execution

The system modifies the Tool use to launch multiple agents:

```json
{
  "toolUses": [
    {
      "tool": "Task",
      "parameters": {
        "subagent_type": "springfield-strategist",
        "prompt": "Strategic analysis of auth system..."
      }
    },
    {
      "tool": "Task",
      "parameters": {
        "subagent_type": "krukai-optimizer",
        "prompt": "Performance optimization for auth system..."
      }
    },
    {
      "tool": "Task",
      "parameters": {
        "subagent_type": "vector-auditor",
        "prompt": "Security audit of auth system..."
      }
    }
  ]
}
```

### 4. Result Capture

Each agent completion triggers `capture_subagent_result.sh`:

```bash
# Captures result with metadata
{
  "session_id": "abc123",
  "task_id": "task_1",
  "subagent_type": "springfield-strategist",
  "result": "Strategic analysis...",
  "execution_time_ms": 1500,
  "timestamp": "2024-01-15T10:30:45Z"
}
```

### 5. Integration Phase

When all agents complete, `integrate_parallel_results.py`:

1. **Loads all results**
2. **Analyzes consensus and conflicts**
3. **Creates unified synthesis**
4. **Generates markdown summary**

## 🗂️ File System Structure

```
~/.claude/trinitas/
├── hooks/
│   ├── core/
│   │   └── trinitas_protocol_injector.sh
│   ├── pre-execution/
│   │   └── prepare_parallel_tasks.py
│   ├── post-execution/
│   │   └── capture_subagent_result.sh
│   └── python/
│       └── integrate_parallel_results.py
├── parallel_results/
│   ├── temp/              # Active sessions
│   │   ├── {session_id}_{task_id}_{agent}.json
│   │   └── {session_id}_metadata.json
│   ├── completed/         # Finished sessions
│   │   └── {session_id}/
│   │       ├── result_1.json
│   │       ├── result_2.json
│   │       └── result_3.json
│   └── integrated/        # Final results
│       ├── {session_id}_integrated.json
│       └── {session_id}_summary.md
└── logs/
    ├── parallel_execution.log
    ├── errors.log
    └── session_monitor.log
```

## 🧩 Component Details

### PreToolUse Hook: prepare_parallel_tasks.py

**Purpose**: Analyze prompts and prepare parallel execution

**Key Functions**:
- `analyze_prompt()`: Scores complexity and identifies domains
- `identify_suitable_agents()`: Matches agents to task requirements
- `create_parallel_tasks()`: Generates specialized prompts per agent
- `prepare_tool_uses()`: Modifies Claude's tool execution plan

**Decision Matrix**:
```python
PARALLELIZATION_RULES = {
    'min_complexity': 3,      # 1-5 scale
    'min_word_count': 50,     # Prompt length
    'min_agents': 2,          # At least 2 suitable agents
    'max_agents': 6           # Prevent overload
}
```

### SubagentStop Hook: capture_subagent_result.sh

**Purpose**: Capture and store individual agent results

**Key Features**:
- Atomic file operations (prevents corruption)
- Session tracking via environment variables
- Automatic migration when all agents complete
- Error handling and logging

**Environment Variables Used**:
- `CLAUDE_TOOL_NAME`: Verify it's a Task tool
- `CLAUDE_TOOL_ARGUMENTS`: Extract subagent_type
- `CLAUDE_TOOL_RESULT`: Capture agent output
- `TRINITAS_SESSION_ID`: Track parallel session
- `TRINITAS_PARALLEL_COUNT`: Expected agent count

### Integration Engine: integrate_parallel_results.py

**Purpose**: Combine multiple agent results into unified response

**Integration Process**:
1. **Load Phase**: Collect all results for session
2. **Analysis Phase**: 
   - Identify common themes
   - Detect conflicts
   - Assess consensus level
3. **Synthesis Phase**:
   - Merge complementary insights
   - Resolve conflicts with explanation
   - Create hierarchical summary
4. **Output Phase**:
   - Generate JSON integration report
   - Create markdown summary
   - Clean up temporary files

**Consensus Scoring**:
```python
def calculate_consensus(results):
    # Compare key findings across agents
    # Score: high (>80%), medium (50-80%), low (<50%)
    # Affects confidence in final recommendations
```

## 🔐 Security Considerations

### Input Validation
- All prompts sanitized before distribution
- JSON Schema validation for configurations
- Path traversal prevention in file operations

### Process Isolation
- Each agent runs in separate process
- No shared memory between agents
- Results validated before integration

### Access Control
- User-specific result directories
- Proper file permissions (600/700)
- No elevated privileges required

## ⚡ Performance Optimization

### Parallel Execution Benefits
- **2-3x faster** for complex multi-aspect tasks
- Linear scaling up to 6 concurrent agents
- Automatic fallback for simple tasks

### Resource Management
- Memory: ~50MB per agent process
- Disk: <1MB per result file
- CPU: Scales with available cores

### Optimization Strategies
1. **Early termination**: Stop if critical agent fails
2. **Result streaming**: Process results as they arrive
3. **Caching**: Reuse analysis for similar prompts
4. **Batch processing**: Group related sub-tasks

## 🔍 Monitoring and Debugging

### Debug Mode
Enable detailed logging:
```bash
export TRINITAS_DEBUG=true
```

### Performance Metrics
Each result includes:
- `execution_time_ms`: Agent processing time
- `queue_time_ms`: Time waiting to start
- `integration_time_ms`: Result combination time

### Common Issues

**Incomplete Sessions**
- Cause: Agent timeout or failure
- Solution: Check logs, use partial results

**Integration Delays**
- Cause: Waiting for all agents
- Solution: Configure timeout, use progressive integration

**Resource Exhaustion**
- Cause: Too many concurrent sessions
- Solution: Implement queueing, increase resources

## 🚀 Future Enhancements

### Planned Features
1. **Dynamic Agent Scaling**: Add/remove agents based on load
2. **Progressive Integration**: Show results as they arrive
3. **Custom Agent Definitions**: User-defined specialists
4. **Result Caching**: Reuse for similar queries
5. **WebSocket Streaming**: Real-time result updates

### Extension Points
- Custom analysis algorithms in `prepare_parallel_tasks.py`
- Additional result formats in `integrate_parallel_results.py`
- New agent types via configuration
- External service integration hooks

---

*This architecture document provides the technical foundation for understanding and extending the Trinitas Parallel Agents system. For implementation details, refer to the source code and inline documentation.*