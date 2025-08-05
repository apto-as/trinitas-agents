# Trinitas Parallel Agents Guide

## 🌸 Overview

Trinitas Parallel Agents is an advanced feature that enables multiple AI agents to work simultaneously on complex tasks, providing comprehensive analysis from multiple perspectives in significantly less time.

### Key Benefits

- **⚡ Speed**: 2-3x faster analysis through parallel execution
- **🎯 Quality**: Multiple perspectives ensure comprehensive coverage
- **🔄 Integration**: Unified results from specialized agents
- **🛡️ Safety**: Built-in error handling and graceful degradation

## 📋 Prerequisites

Before enabling parallel agents, ensure:

1. **Trinitas v2.0 installed**: Run `./install.sh` from the project root
2. **Python 3.7+**: Required for task preparation and result integration
3. **jq**: Recommended for JSON processing (will fallback if not available)
4. **Sufficient disk space**: At least 100MB free for results storage

## 🚀 Quick Start

### 1. Enable Parallel Agents

```bash
# Merge parallel agent settings with your existing configuration
python3 hooks/migration/settings_merger.py ~/.claude/settings.json

# Or manually copy the example settings
cp hooks/examples/parallel_agents_settings.json ~/.claude/settings.json
```

### 2. Verify Installation

```bash
# Run health check
./hooks/monitoring/health_check.sh

# Expected output:
# ✅ All checks passed!
```

### 3. Test Parallel Execution

```bash
# Run the demo
./examples/parallel_analysis_demo.sh
```

## 🔧 Configuration

### Environment Variables

- `TRINITAS_PARALLEL_ENABLED`: Enable/disable parallel execution (default: true)
- `TRINITAS_RESULTS_DIR`: Directory for storing results (default: ~/.claude/trinitas/parallel_results)
- `TRINITAS_PARALLEL_COUNT`: Expected number of parallel agents (set automatically)

### Settings.json Configuration

The parallel agents require specific hooks in your `settings.json`:

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Task",
        "hooks": [{
          "type": "command",
          "command": "~/.claude/trinitas/hooks/python/prepare_parallel_tasks.py",
          "environment": {
            "TRINITAS_PARALLEL_ENABLED": "true"
          }
        }]
      }
    ],
    "SubagentStop": [
      {
        "matcher": "Task",
        "hooks": [{
          "type": "command",
          "command": "~/.claude/trinitas/hooks/post-execution/capture_subagent_result.sh"
        }]
      }
    ]
  }
}
```

## 🎭 Available Agents

### Core Trinity Agents

1. **trinitas-coordinator**: Integrates results from all agents
2. **springfield-strategist**: Strategic planning and architecture
3. **krukai-optimizer**: Technical optimization and performance
4. **vector-auditor**: Security analysis and risk assessment

### Specialized Agents

5. **trinitas-quality**: Quality assurance and testing
6. **trinitas-workflow**: Workflow automation and process optimization

## 📊 How It Works

### 1. Task Analysis

When you use the Task tool with a complex prompt, the system:
- Analyzes prompt complexity (1-5 scale)
- Identifies suitable agents based on keywords
- Determines if parallel execution would be beneficial

### 2. Parallel Execution

If parallelization is triggered:
- Creates specialized prompts for each agent
- Launches agents simultaneously
- Each agent works independently

### 3. Result Integration

After all agents complete:
- Results are captured and stored
- Integration process combines all perspectives
- Unified response is generated

## 🛡️ Safety & Error Handling

### Built-in Safeguards

- **Timeout Protection**: 30-second timeout per agent
- **Partial Completion**: Works even if some agents fail
- **Resource Limits**: Prevents excessive memory/disk usage
- **Conflict Detection**: Identifies incompatible settings

### Error Recovery

If issues occur:

```bash
# Check system health
./hooks/monitoring/health_check.sh

# View recent errors
tail -50 ~/.claude/trinitas/logs/errors.log

# Clean stale results
find ~/.claude/trinitas/parallel_results/temp -name "*.json" -mtime +1 -delete
```

## 🔍 Monitoring & Debugging

### View Parallel Results

```bash
# List recent sessions
ls -la ~/.claude/trinitas/parallel_results/completed/

# View integrated results
cat ~/.claude/trinitas/parallel_results/integrated/*_summary.md
```

### Debug Mode

Enable detailed logging:

```bash
export TRINITAS_DEBUG=true
```

### Performance Metrics

Results include execution times:
- Individual agent times
- Total parallel execution time
- Integration overhead

## ⚠️ Limitations & Considerations

### When Parallel Agents Are Used

- Complex prompts with multiple aspects
- Tasks mentioning multiple domains (security, performance, etc.)
- Prompts with 50+ words and complexity score ≥ 3

### When They're NOT Used

- Simple, single-purpose tasks
- Direct questions with clear answers
- Tasks with explicit agent specification

### Resource Considerations

- Each agent consumes memory and CPU
- Results are stored on disk (auto-cleaned after 7 days)
- Network latency affects overall performance

## 🔄 Upgrading

To upgrade parallel agents:

```bash
# Pull latest changes
git pull

# Run upgrade script
./upgrade.sh

# Verify health
./hooks/monitoring/health_check.sh
```

## 🐛 Troubleshooting

### Common Issues

**1. "No parallel tasks created"**
- Prompt may be too simple
- Check TRINITAS_PARALLEL_ENABLED=true
- Verify hooks are properly configured

**2. "Results not integrating"**
- Check SubagentStop hook is configured
- Ensure Python environment is working
- Look for errors in integration log

**3. "Performance not improved"**
- Some tasks aren't parallelizable
- Check agent execution times in results
- Consider network/system load

### Getting Help

1. Run health check: `./hooks/monitoring/health_check.sh`
2. Check documentation: This guide and PARALLEL_AGENTS_ARCHITECTURE.md
3. Enable debug mode for detailed logs
4. Report issues: https://github.com/apto-as/trinitas-agents/issues

## 🎯 Best Practices

### Optimal Use Cases

✅ **Perfect for:**
- Code review from multiple perspectives
- Security audit + performance analysis
- Architecture planning with risk assessment
- Comprehensive project analysis

❌ **Not ideal for:**
- Simple lookups or calculations
- Sequential tasks with dependencies
- Real-time responses needed
- Limited system resources

### Performance Tips

1. **Batch Complex Tasks**: Combine related analyses
2. **Monitor Resources**: Use health check regularly
3. **Clean Old Results**: Remove old session data
4. **Optimize Prompts**: Be specific about needed perspectives

## 🚧 Advanced Configuration

### Custom Agent Selection

Modify `AGENT_CAPABILITIES` in `prepare_parallel_tasks.py`:

```python
AGENT_CAPABILITIES['custom-agent'] = {
    'strengths': ['custom analysis'],
    'keywords': ['specific', 'keywords'],
    'max_parallel': 2
}
```

### Result Storage Customization

```bash
# Change results directory
export TRINITAS_RESULTS_DIR=/custom/path/results

# Adjust retention (default: 7 days)
find $TRINITAS_RESULTS_DIR -mtime +3 -delete  # 3 days
```

### Integration Webhooks

For CI/CD integration, modify `integrate_parallel_results.py` to send results to external systems.

---

## 🌸 Summary

Trinitas Parallel Agents represent the next evolution in AI-assisted development, bringing the power of multiple specialized perspectives to every complex task. By following this guide, you can safely enable and optimize parallel execution for your workflow.

Remember: **With great parallelism comes great responsibility**. Monitor your system, start with simple tests, and gradually increase complexity as you become comfortable with the system.

*Welcome to the future of parallel AI analysis - Trinitas-Core v2.0* 🎊