---
name: trinitas
description: Execute Trinitas v4.0 commands with memory-focused intelligence
icon: 🎯
---

# Trinitas v4.0 Command Interface

Execute Trinitas operations with memory and learning capabilities.

## Usage

```
/trinitas <operation> [options]
```

## Available Operations

### 1. Execute with Persona
```
/trinitas execute <persona> <task>
/trinitas exec <persona> <task>
```
Execute task with specified persona using memory context.

**Personas**: athena, artemis, hestia, bellona, seshat

**Examples**:
```
/trinitas execute athena "Design microservice architecture"
/trinitas exec artemis "Optimize database queries"
```

### 2. Memory Operations
```
/trinitas remember <key> <value> [--persona NAME] [--importance 0.0-1.0]
/trinitas recall <query> [--semantic] [--limit N]
```

**Examples**:
```
/trinitas remember project_architecture "Microservices with Redis" --persona athena --importance 0.9
/trinitas recall architecture --semantic --limit 5
```

### 3. Pattern Learning
```
/trinitas learn <pattern_name>
/trinitas apply <pattern_name> <task>
```

**Examples**:
```
/trinitas learn optimization_pattern_v2
/trinitas apply optimization_pattern_v2 "Optimize API endpoints"
```

### 4. Status and Reports
```
/trinitas status [component]
/trinitas report <type>
```

**Components**: all, bellona, seshat, memory, learning
**Report Types**: usage, optimization, learning

**Examples**:
```
/trinitas status memory
/trinitas report optimization
```

### 5. Parallel Analysis (Multiple Personas)
```
/trinitas analyze <task> [--personas p1,p2,p3]
```

**Examples**:
```
/trinitas analyze "Review security vulnerabilities" --personas hestia,artemis,athena
```

### 6. Local LLM Control
```
/trinitas llm <enable|disable|status>
/trinitas llm route <task> [--force]
```

**Examples**:
```
/trinitas llm enable
/trinitas llm route "Format documentation" --force
```

## Implementation

```python
import asyncio
import json
from typing import Dict, Any, Optional, List

async def handle_trinitas_command(args: str) -> str:
    """
    Handle /trinitas command execution
    """
    parts = args.strip().split(maxsplit=2)
    if not parts:
        return show_help()
    
    operation = parts[0].lower()
    
    # Route to appropriate handler
    handlers = {
        'execute': handle_execute,
        'exec': handle_execute,
        'remember': handle_remember,
        'recall': handle_recall,
        'learn': handle_learn,
        'apply': handle_apply,
        'status': handle_status,
        'report': handle_report,
        'analyze': handle_analyze,
        'llm': handle_llm
    }
    
    if operation in handlers:
        return await handlers[operation](parts[1:] if len(parts) > 1 else [])
    else:
        return f"Unknown operation: {operation}\n\n{show_help()}"

async def handle_execute(args: List[str]) -> str:
    """Execute with specific persona"""
    if len(args) < 2:
        return "Usage: /trinitas execute <persona> <task>"
    
    persona = args[0].lower()
    task = args[1]
    
    valid_personas = ['athena', 'artemis', 'hestia', 'bellona', 'seshat']
    if persona not in valid_personas:
        return f"Invalid persona. Choose from: {', '.join(valid_personas)}"
    
    # Call MCP tool
    result = await mcp__trinitas-mcp__execute_with_memory(
        persona=persona,
        task=task
    )
    
    if result.get('success'):
        return format_execution_result(result)
    else:
        return f"Execution failed: {result.get('error', 'Unknown error')}"

async def handle_remember(args: List[str]) -> str:
    """Store in memory"""
    if len(args) < 2:
        return "Usage: /trinitas remember <key> <value> [--persona NAME] [--importance N]"
    
    key = args[0]
    # Parse remaining arguments for value and options
    remaining = ' '.join(args[1:])
    
    # Extract options
    persona = None
    importance = 0.5
    
    if '--persona' in remaining:
        parts = remaining.split('--persona')
        value = parts[0].strip()
        persona_part = parts[1].strip().split()[0]
        persona = persona_part
    else:
        value = remaining
    
    if '--importance' in remaining:
        import_parts = remaining.split('--importance')
        importance = float(import_parts[1].strip().split()[0])
    
    # Call MCP tool
    result = await mcp__trinitas-mcp__memory_store(
        key=key,
        value=value,
        persona=persona,
        importance=importance
    )
    
    if result.get('success'):
        return f"✅ Stored '{key}' with importance {importance}"
    else:
        return f"❌ Failed to store: {result.get('error')}"

async def handle_recall(args: List[str]) -> str:
    """Recall from memory"""
    if not args:
        return "Usage: /trinitas recall <query> [--semantic] [--limit N]"
    
    query = args[0]
    semantic = '--semantic' in ' '.join(args)
    
    # Extract limit
    limit = 10
    if '--limit' in ' '.join(args):
        for i, arg in enumerate(args):
            if arg == '--limit' and i + 1 < len(args):
                limit = int(args[i + 1])
    
    # Call MCP tool
    result = await mcp__trinitas-mcp__memory_recall(
        query=query,
        semantic=semantic,
        limit=limit
    )
    
    if result.get('success'):
        return format_recall_results(result)
    else:
        return f"❌ Recall failed: {result.get('error')}"

async def handle_analyze(args: List[str]) -> str:
    """Parallel analysis with multiple personas"""
    if not args:
        return "Usage: /trinitas analyze <task> [--personas p1,p2,p3]"
    
    task = args[0]
    personas = ['athena', 'artemis', 'hestia']  # Default
    
    if '--personas' in ' '.join(args):
        for i, arg in enumerate(args):
            if arg == '--personas' and i + 1 < len(args):
                personas = args[i + 1].split(',')
    
    # Execute with each persona
    results = []
    for persona in personas:
        result = await mcp__trinitas-mcp__execute_with_memory(
            persona=persona,
            task=task
        )
        results.append(result)
    
    return format_parallel_results(results, task)

async def handle_llm(args: List[str]) -> str:
    """Control Local LLM settings"""
    if not args:
        return "Usage: /trinitas llm <enable|disable|status|route>"
    
    action = args[0].lower()
    
    if action == 'status':
        result = await mcp__trinitas-mcp__get_status(component='bellona')
        llm_enabled = result.get('bellona', {}).get('llm_enabled', False)
        return f"Local LLM: {'Enabled' if llm_enabled else 'Disabled'}"
    
    elif action == 'enable':
        # Would need to update config
        return "⚠️ LLM enabling requires configuration update in .env file"
    
    elif action == 'disable':
        # Would need to update config
        return "⚠️ LLM disabling requires configuration update in .env file"
    
    elif action == 'route' and len(args) > 1:
        task = args[1]
        force = '--force' in ' '.join(args)
        
        result = await mcp__trinitas-mcp__execute_with_memory(
            persona='bellona',
            task=task,
            use_llm=force
        )
        
        return format_execution_result(result)
    
    return "Unknown LLM action"

def format_execution_result(result: Dict) -> str:
    """Format execution result for display"""
    output = []
    output.append(f"🎯 Execution {'Successful' if result.get('success') else 'Failed'}")
    output.append(f"Persona: {result.get('persona')}")
    output.append(f"Processor: {result.get('distribution', {}).get('processor')}")
    output.append(f"Priority: {result.get('distribution', {}).get('priority', 0):.2f}")
    output.append(f"Time: {result.get('execution_time_seconds', 0):.2f}s")
    
    if result.get('memory_usage'):
        memory = result['memory_usage']
        output.append(f"Memory Sections: {', '.join(memory.get('memory_sections_needed', []))}")
        if memory.get('optimization_suggestions'):
            output.append(f"💡 Suggestion: {memory['optimization_suggestions'][0]}")
    
    if result.get('result'):
        output.append(f"\n📝 Result: {result['result'].get('response', 'No response')}")
    
    return '\n'.join(output)

def format_recall_results(result: Dict) -> str:
    """Format recall results"""
    output = []
    output.append(f"🔍 Found {result.get('count', 0)} memories for '{result.get('query')}'")
    
    for i, memory in enumerate(result.get('results', [])[:5], 1):
        output.append(f"\n{i}. {memory.get('key')}")
        output.append(f"   Value: {str(memory.get('value'))[:100]}...")
        if memory.get('metadata'):
            output.append(f"   Persona: {memory['metadata'].get('persona')}")
            output.append(f"   Importance: {memory['metadata'].get('importance', 0):.2f}")
    
    return '\n'.join(output)

def format_parallel_results(results: List[Dict], task: str) -> str:
    """Format parallel analysis results"""
    output = []
    output.append(f"🔄 Parallel Analysis: {task[:50]}...")
    output.append("="*50)
    
    for result in results:
        if result.get('success'):
            output.append(f"\n✅ {result['persona'].upper()}")
            output.append(f"   {result.get('result', {}).get('response', 'No response')}")
            output.append(f"   Priority: {result['distribution']['priority']:.2f}")
        else:
            output.append(f"\n❌ {result.get('persona', 'Unknown').upper()} - Failed")
    
    return '\n'.join(output)

def show_help() -> str:
    """Show command help"""
    return """
🎯 Trinitas v4.0 Command Interface

Usage: /trinitas <operation> [options]

Operations:
  execute <persona> <task>     - Execute with specific persona
  remember <key> <value>       - Store in memory
  recall <query>               - Retrieve from memory
  learn <pattern>              - Learn pattern
  apply <pattern> <task>       - Apply pattern
  status [component]           - Show status
  report <type>                - Generate report
  analyze <task>               - Multi-persona analysis
  llm <action>                 - Control Local LLM

Examples:
  /trinitas execute athena "Design system architecture"
  /trinitas remember project_config "Redis cluster setup" --importance 0.9
  /trinitas recall architecture --semantic
  /trinitas analyze "Security audit" --personas hestia,artemis
  /trinitas status memory
  /trinitas llm status

For detailed help, see the documentation.
"""

# Register command handler
if __name__ == "__main__":
    # This would be called by Claude when /trinitas is invoked
    import sys
    args = ' '.join(sys.argv[1:]) if len(sys.argv) > 1 else ""
    result = asyncio.run(handle_trinitas_command(args))
    print(result)
```