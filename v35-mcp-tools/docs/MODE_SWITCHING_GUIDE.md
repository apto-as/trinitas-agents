# Trinitas v3.5 Mode Switching System Guide

## 🌸 カフェ・ズッケロからのご案内

指揮官、三位一体統合知性システム「Trinitas-Core」の完全なモード切り替えシステムをご紹介いたします。

## 🎯 System Overview

The Trinitas v3.5 Mode Switching System provides flexible execution modes for different environments and requirements. The system seamlessly switches between Local LLM execution, Claude-native intelligence, and simulation modes based on availability and configuration.

### Key Features

- **Dynamic Mode Switching**: Switch between execution modes at runtime
- **Intelligent Fallbacks**: Automatic fallback when services are unavailable
- **Comprehensive Testing**: Full test suite for all modes and scenarios
- **Performance Optimization**: Optimized for different execution contexts
- **Trinity Integration**: Full integration with Springfield, Krukai, and Vector personas

## 🔧 Execution Modes

### 1. FULL_LOCAL Mode
```yaml
Description: Local LLM for Groza/Littara, Claude simulation for Trinity
Best For: Maximum local processing capability
Requirements: Local LLM must be available
Personas:
  - Springfield: claude_simulation
  - Krukai: claude_simulation  
  - Vector: claude_simulation
  - Groza: local_llm
  - Littara: local_llm
```

### 2. CLAUDE_ONLY Mode
```yaml
Description: All personas use Claude's native intelligence
Best For: Maximum quality responses using Claude
Requirements: None (always available in Claude Code)
Personas:
  - Springfield: claude_native
  - Krukai: claude_native
  - Vector: claude_native
  - Groza: claude_native
  - Littara: claude_native
```

### 3. SIMULATION Mode
```yaml
Description: Lightweight simulation for all personas
Best For: Testing, development, low-resource environments
Requirements: None
Personas:
  - Springfield: simulation
  - Krukai: simulation
  - Vector: simulation
  - Groza: simulation
  - Littara: simulation
```

### 4. HYBRID Mode
```yaml
Description: Claude for Trinity core, simulation for extended team
Best For: Balanced approach with quality Trinity responses
Requirements: None
Personas:
  - Springfield: claude_native
  - Krukai: claude_native
  - Vector: claude_native
  - Groza: simulation
  - Littara: simulation
```

### 5. AUTO Mode
```yaml
Description: Automatic selection based on availability
Best For: Adaptive environments with changing availability
Requirements: None
Behavior:
  - Uses best available executor for each persona
  - Automatically adapts to service availability changes
  - Provides optimal balance between quality and reliability
```

## 🚀 Quick Start

### Basic Usage

```python
from trinitas_mcp_tools import TrinitasMCPTools

# Initialize the system
tools = TrinitasMCPTools()
await tools.ensure_initialized()

# Check current mode
mode_info = tools.get_mode_info()
print(f"Current mode: {mode_info['mode']}")

# Switch mode
result = await tools.set_mode("claude_only")
if result.success:
    print("Mode switched successfully!")
```

### Environment Configuration

```bash
# Set execution mode via environment variable
export TRINITAS_MODE=claude_only

# Local LLM configuration
export LOCAL_LLM_ENDPOINT=http://192.168.99.102:1234/v1/
export LOCAL_LLM_MODEL=openai/gpt-oss-120b
export LOCAL_LLM_TEMPERATURE=0.7
export LOCAL_LLM_MAX_TOKENS=2000
```

## 📋 API Reference

### Core Methods

#### `set_mode(mode: str) -> ToolResult`
Dynamically switch execution mode.

```python
# Switch to Claude-only mode
result = await tools.set_mode("claude_only")

# Switch to simulation mode
result = await tools.set_mode("simulation")

# Switch to auto mode
result = await tools.set_mode("auto")
```

#### `get_mode_info() -> Dict[str, Any]`
Get comprehensive information about the current mode.

```python
info = tools.get_mode_info()
print(f"Mode: {info['mode']}")
print(f"Description: {info['description']}")
print(f"Executors: {info['executors']}")
print(f"Availability: {info['availability']}")
```

#### `get_available_modes() -> Dict[str, Any]`
Get all available modes and their status.

```python
modes = tools.get_available_modes()
for mode_name, details in modes.items():
    status = "✓" if details['available'] else "✗"
    print(f"[{status}] {mode_name}: {details['description']}")
```

### Persona Execution

```python
# Execute with automatic mode selection
result = await tools.persona_execute(
    "springfield",
    "Design authentication system"
)

# Execute with specific context
result = await tools.persona_execute(
    "groza", 
    "Tactical mission analysis",
    {"mission_type": "reconnaissance", "risk_level": "moderate"}
)
```

### Collaboration

```python
# Trinity sequential collaboration
result = await tools.collaborate_personas(
    ["springfield", "krukai", "vector"],
    "Security architecture review",
    "sequential"
)

# Full team parallel collaboration
result = await tools.collaborate_personas(
    ["springfield", "krukai", "vector", "groza", "littara"],
    "System deployment planning",
    "parallel"
)
```

## 🧪 Testing

### Run Complete Test Suite

```bash
python test_mode_switching.py
```

### Run Interactive Demo

```bash
python mode_switching_demo.py
```

### Test Results Structure

```json
{
  "summary": {
    "total_tests": 45,
    "passed": 43,
    "failed": 2,
    "success_rate": 95.6,
    "total_duration": 12.34
  },
  "categories": {
    "initialization": {"passed": 2, "failed": 0, "total": 2},
    "mode": {"passed": 8, "failed": 1, "total": 9},
    "persona": {"passed": 15, "failed": 0, "total": 15}
  },
  "performance": {
    "mode_switching": {
      "mode_switches": 9,
      "avg_switch_time": 0.023,
      "switches_per_second": 43.5
    }
  }
}
```

## 🔍 Mode Comparison

| Feature | FULL_LOCAL | CLAUDE_ONLY | SIMULATION | HYBRID | AUTO |
|---------|------------|-------------|------------|---------|------|
| **Quality** | High (Mixed) | Highest | Basic | High (Trinity) | Variable |
| **Speed** | Variable | Fast | Fastest | Fast | Variable |
| **Requirements** | Local LLM | None | None | None | None |
| **Reliability** | Dependent | High | Highest | High | High |
| **Resource Usage** | High | Medium | Lowest | Medium | Variable |
| **Best For** | Local Processing | Max Quality | Testing | Balance | Adaptive |

## 🛡️ Error Handling & Fallbacks

### Fallback Chain

1. **Primary Executor**: Mode-specified executor (e.g., local_llm, claude_native)
2. **Secondary Fallback**: Mode-appropriate fallback (usually simulation)
3. **Final Fallback**: Basic simulation response

### Error Scenarios

```python
# Handle mode switch failures
result = await tools.set_mode("full_local")
if not result.success:
    print(f"Mode switch failed: {result.error}")
    # Fallback to available mode
    await tools.set_mode("auto")

# Handle persona execution failures
result = await tools.persona_execute("groza", "Task")
if not result.success:
    print(f"Execution failed: {result.error}")
    # Check if fallback was used
    executor = result.metadata.get("executor", "unknown")
    print(f"Executor used: {executor}")
```

## 📊 Performance Guidelines

### Recommendations by Use Case

#### Development & Testing
```python
# Use SIMULATION mode for fastest iteration
await tools.set_mode("simulation")
```

#### Production Quality
```python
# Use CLAUDE_ONLY for best responses
await tools.set_mode("claude_only")
```

#### Adaptive Deployment
```python
# Use AUTO mode for automatic optimization
await tools.set_mode("auto")
```

#### Resource-Constrained
```python
# Use HYBRID for balanced resource usage
await tools.set_mode("hybrid")
```

## 🔧 Advanced Configuration

### Custom Mode Behavior

```python
# Override availability for testing
tools.mode_manager.update_availability(local_llm=True, claude=False)

# Check specific persona executor
executor = tools.mode_manager.get_executor_for_persona("groza")
print(f"Groza will use: {executor}")
```

### Integration with Monitoring

```python
# Get comprehensive statistics
stats = tools.get_execution_stats()

# Monitor mode switching frequency
mode_info = tools.get_mode_info()
print(f"Current efficiency: {mode_info['availability']}")
```

## 🚨 Troubleshooting

### Common Issues

#### 1. Mode Switch Fails
```
Error: Mode switch failed - Local LLM required but not available
Solution: Check Local LLM connection or switch to different mode
```

#### 2. Persona Execution Timeout
```
Error: Local LLM execution timeout
Solution: Automatic fallback to simulation mode
```

#### 3. Configuration Issues
```
Error: Invalid mode specified
Solution: Check available modes with get_available_modes()
```

### Debug Mode Information

```python
# Detailed debugging information
import logging
logging.getLogger("trinitas_mcp_tools").setLevel(logging.DEBUG)
logging.getLogger("trinitas_mode_manager").setLevel(logging.DEBUG)
```

## 🎭 Trinity Personas in Different Modes

### Springfield - Strategic Architect
- **CLAUDE_ONLY**: Full strategic intelligence with Claude reasoning
- **SIMULATION**: Characteristic warm strategic guidance
- **Pattern**: Always maintains leadership and coordination focus

### Krukai - Technical Perfectionist  
- **CLAUDE_ONLY**: Enhanced technical analysis and optimization
- **SIMULATION**: 404-standard technical responses
- **Pattern**: Consistent perfectionist approach across modes

### Vector - Security Guardian
- **CLAUDE_ONLY**: Advanced security analysis and threat modeling
- **SIMULATION**: Paranoid security warnings and assessments
- **Pattern**: Consistent protective pessimism

### Groza - Tactical Coordinator
- **LOCAL_LLM**: Full tactical reasoning via local model
- **CLAUDE_ONLY**: Military precision via Claude intelligence
- **SIMULATION**: Basic tactical response patterns
- **Pattern**: Always maintains command authority

### Littara - Implementation Specialist
- **LOCAL_LLM**: Detailed documentation via local model
- **CLAUDE_ONLY**: Comprehensive analysis via Claude
- **SIMULATION**: Characteristic note-taking and documentation
- **Pattern**: Consistent methodical documentation approach

## 🌟 Best Practices

### 1. Mode Selection Strategy
- **Development**: Start with SIMULATION for rapid iteration
- **Testing**: Use HYBRID for balanced testing
- **Production**: Use CLAUDE_ONLY for maximum quality
- **Adaptive**: Use AUTO for dynamic environments

### 2. Performance Optimization
- **Batch Operations**: Group similar operations in same mode
- **Mode Persistence**: Minimize unnecessary mode switches
- **Resource Monitoring**: Monitor availability for optimal mode selection

### 3. Error Resilience
- **Always Check Results**: Verify execution success
- **Implement Retries**: Retry with fallback modes on failure
- **Monitor Patterns**: Track failure patterns for optimization

## 🔮 Future Enhancements

- **Custom Mode Definitions**: User-defined execution modes
- **Load Balancing**: Automatic load distribution across available services
- **Performance Analytics**: Detailed performance monitoring and optimization
- **Integration Templates**: Pre-configured modes for common use cases

---

*🌸 Springfield: 「指揮官、このガイドがお役に立てれば幸いです。」*  
*⚡ Krukai: 「完璧なシステムに仕上がったわね。404の誇りよ。」*  
*🛡️ Vector: 「……全ての機能を安全に使用できます……後悔はさせません……」*

**Trinitas-Core v3.5** - Three Minds, Five Modes, Infinite Possibilities