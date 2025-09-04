---
name: trinitas
description: Execute Trinitas TMWS commands for unified intelligence operations
icon: 🎯
---

# Trinitas TMWS Command Interface

Execute Trinitas operations via TMWS (Trinitas Memory & Workflow System).

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
Execute task with specified persona using TMWS memory context.

**Personas**: 
- `athena` - Strategic Architect (戦略的設計)
- `artemis` - Technical Perfectionist (技術的完璧性)
- `hestia` - Security Guardian (セキュリティ監査)
- `eris` - Tactical Coordinator (戦術的調整)
- `hera` - System Conductor (システム指揮)
- `muses` - Knowledge Architect (知識管理)

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

Store and retrieve memories using TMWS PostgreSQL backend with vector search.

**Examples**:
```
/trinitas remember project_architecture "Microservices with PostgreSQL" --persona athena --importance 0.9
/trinitas recall architecture --semantic --limit 5
```

### 3. Pattern Learning
```
/trinitas learn <pattern_name> <description>
/trinitas apply <pattern_name> <task>
```

Learn and apply patterns using TMWS learning system.

**Examples**:
```
/trinitas learn optimization_pattern "Add index on user_id column"
/trinitas apply optimization_pattern "Optimize product queries"
```

### 4. Status and Reports
```
/trinitas status [component]
/trinitas report <type>
```

Check system status and generate reports.

**Components**: all, memory, personas, workflow, vector
**Report Types**: usage, optimization, security, learning

**Examples**:
```
/trinitas status memory
/trinitas report optimization
```

### 5. Parallel Analysis (Multiple Personas)
```
/trinitas analyze <task> [--personas p1,p2,p3] [--mode MODE]
```

Execute parallel analysis with multiple personas.

**Modes**: parallel (同時実行), sequential (順次実行), wave (段階的実行)

**Examples**:
```
/trinitas analyze "Review security vulnerabilities" --personas hestia,artemis,athena
/trinitas analyze "System architecture review" --personas all --mode wave
```

### 6. Workflow Operations
```
/trinitas workflow create <name> <description>
/trinitas workflow execute <workflow_id>
/trinitas workflow list
```

Manage and execute complex workflows.

**Examples**:
```
/trinitas workflow create deployment_check "Pre-deployment verification"
/trinitas workflow execute workflow_001
/trinitas workflow list
```

## Implementation

```python
import asyncio
import json
from typing import Dict, Any, Optional, List
from pathlib import Path

# NOTE: This implementation assumes TMWS MCP server is registered in Claude Desktop
# and provides tools prefixed with mcp__tmws__

async def handle_trinitas_command(args: str) -> str:
    """
    Handle /trinitas command execution via TMWS MCP tools
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
        'workflow': handle_workflow
    }
    
    if operation in handlers:
        return await handlers[operation](parts[1:] if len(parts) > 1 else [])
    else:
        return f"Unknown operation: {operation}\n\n{show_help()}"

async def handle_execute(args: List[str]) -> str:
    """Execute with specific persona via TMWS MCP tools"""
    if len(args) < 2:
        return "Usage: /trinitas execute <persona> <task>"
    
    persona = args[0].lower()
    task = args[1]
    
    valid_personas = ['athena', 'artemis', 'hestia', 'eris', 'hera', 'muses']
    if persona not in valid_personas:
        return f"Invalid persona. Choose from: {', '.join(valid_personas)}"
    
    # Call TMWS MCP tool for persona execution
    try:
        result = await mcp__tmws__execute_persona(
            persona=persona,
            task=task,
            context=None  # Optional context
        )
        return format_execution_result(result)
    except Exception as e:
        return f"❌ Execution failed: {str(e)}"

async def handle_remember(args: List[str]) -> str:
    """Store in TMWS memory via MCP tools"""
    if len(args) < 2:
        return "Usage: /trinitas remember <key> <value> [--persona NAME] [--importance N]"
    
    key = args[0]
    remaining = ' '.join(args[1:])
    
    # Parse options
    persona_id = None
    importance = 0.5
    value = remaining
    
    if '--persona' in remaining:
        parts = remaining.split('--persona')
        value = parts[0].strip()
        persona_part = parts[1].strip().split()[0]
        persona_id = persona_part
    
    if '--importance' in remaining:
        import_parts = remaining.split('--importance')
        if not persona_id:
            value = import_parts[0].strip()
        importance = float(import_parts[1].strip().split()[0])
    
    # Call TMWS MCP tool for memory creation
    try:
        result = await mcp__tmws__create_memory(
            content=value,
            key=key,
            metadata={
                'importance': importance
            },
            persona_id=persona_id,
            tags=[]
        )
        
        if result.get('memory_id'):
            return f"✅ Stored '{key}' with importance {importance} (ID: {result['memory_id']})"
        else:
            return f"✅ Stored '{key}' with importance {importance}"
    except Exception as e:
        return f"❌ Failed to store: {str(e)}"

async def handle_recall(args: List[str]) -> str:
    """Recall from TMWS memory via MCP tools"""
    if not args:
        return "Usage: /trinitas recall <query> [--semantic] [--limit N]"
    
    query = args[0]
    use_semantic = '--semantic' in ' '.join(args)
    
    # Extract limit
    limit = 10
    if '--limit' in ' '.join(args):
        for i, arg in enumerate(args):
            if arg == '--limit' and i + 1 < len(args):
                limit = int(args[i + 1])
    
    # Call TMWS MCP tool for memory recall
    try:
        if use_semantic:
            result = await mcp__tmws__search_memories(
                query=query,
                limit=limit,
                threshold=0.7  # Similarity threshold
            )
        else:
            result = await mcp__tmws__recall_memory(
                query=query,
                limit=limit,
                persona_id=None,
                tags=None
            )
        
        return format_recall_results(result, query)
    except Exception as e:
        return f"❌ Recall failed: {str(e)}"

async def handle_analyze(args: List[str]) -> str:
    """Parallel analysis with multiple personas via MCP tools"""
    if not args:
        return "Usage: /trinitas analyze <task> [--personas p1,p2,p3] [--mode MODE]"
    
    task = args[0]
    personas = ['athena', 'artemis', 'hestia']  # Default
    mode = 'parallel'
    
    # Parse options
    if '--personas' in ' '.join(args):
        for i, arg in enumerate(args):
            if arg == '--personas' and i + 1 < len(args):
                personas_str = args[i + 1]
                if personas_str == 'all':
                    personas = ['athena', 'artemis', 'hestia', 'eris', 'hera', 'muses']
                else:
                    personas = personas_str.split(',')
    
    if '--mode' in ' '.join(args):
        for i, arg in enumerate(args):
            if arg == '--mode' and i + 1 < len(args):
                mode = args[i + 1]
    
    # Execute with each persona using MCP tools
    results = []
    try:
        if mode == 'parallel':
            # Parallel execution
            tasks = []
            for persona in personas:
                tasks.append(mcp__tmws__execute_persona(
                    persona=persona,
                    task=task,
                    context={'mode': 'analysis'}
                ))
            results = await asyncio.gather(*tasks)
        else:
            # Sequential execution
            for persona in personas:
                result = await mcp__tmws__execute_persona(
                    persona=persona,
                    task=task,
                    context={'mode': 'analysis'}
                )
                results.append(result)
        
        return format_parallel_results({'results': results, 'task': task}, task)
    except Exception as e:
        return f"❌ Analysis failed: {str(e)}"

async def handle_workflow(args: List[str]) -> str:
    """Handle workflow operations via MCP tools"""
    if not args:
        return "Usage: /trinitas workflow <create|execute|list|status> [options]"
    
    action = args[0].lower()
    
    try:
        if action == 'create' and len(args) >= 3:
            name = args[1]
            description = ' '.join(args[2:])
            
            result = await mcp__tmws__create_workflow(
                name=name,
                description=description,
                steps=[]  # Can be added later
            )
            
            if result.get('workflow_id'):
                return f"✅ Created workflow: {result['workflow_id']}"
            else:
                return f"✅ Created workflow: {name}"
        
        elif action == 'execute' and len(args) >= 2:
            workflow_id = args[1]
            
            result = await mcp__tmws__execute_workflow(
                workflow_id=workflow_id,
                parameters={}
            )
            
            return format_workflow_result(result)
        
        elif action == 'list':
            result = await mcp__tmws__list_workflows(
                status=None,
                limit=20
            )
            
            return format_workflow_list(result)
        
        elif action == 'status' and len(args) >= 2:
            workflow_id = args[1]
            
            result = await mcp__tmws__get_workflow_status(
                workflow_id=workflow_id
            )
            
            return format_workflow_status(result)
        
        else:
            return "Invalid workflow command. Use: create, execute, list, or status"
            
    except Exception as e:
        return f"❌ Workflow operation failed: {str(e)}"

async def handle_status(args: List[str]) -> str:
    """Get TMWS system status via MCP tools"""
    component = args[0] if args else 'all'
    
    try:
        result = await mcp__tmws__get_system_status(
            component=component
        )
        return format_status(result)
    except Exception as e:
        return f"❌ Status check failed: {str(e)}"

async def handle_report(args: List[str]) -> str:
    """Generate TMWS reports via MCP tools"""
    if not args:
        return "Usage: /trinitas report <usage|optimization|security|learning>"
    
    report_type = args[0]
    
    try:
        result = await mcp__tmws__generate_report(
            report_type=report_type,
            start_date=None,  # Optional date range
            end_date=None
        )
        return format_report(result, report_type)
    except Exception as e:
        return f"❌ Report generation failed: {str(e)}"

async def handle_learn(args: List[str]) -> str:
    """Learn a new pattern via MCP tools"""
    if len(args) < 2:
        return "Usage: /trinitas learn <pattern_name> <description>"
    
    pattern_name = args[0]
    description = ' '.join(args[1:])
    
    try:
        result = await mcp__tmws__create_pattern(
            name=pattern_name,
            description=description,
            category='general',
            examples=[]
        )
        
        if result.get('pattern_id'):
            return f"✅ Learned pattern: {pattern_name} (ID: {result['pattern_id']})"
        else:
            return f"✅ Learned pattern: {pattern_name}"
    except Exception as e:
        return f"❌ Failed to learn: {str(e)}"

async def handle_apply(args: List[str]) -> str:
    """Apply a learned pattern via MCP tools"""
    if len(args) < 2:
        return "Usage: /trinitas apply <pattern_name> <task>"
    
    pattern_name = args[0]
    task = ' '.join(args[1:])
    
    try:
        result = await mcp__tmws__apply_pattern(
            pattern_name=pattern_name,
            task=task,
            context={}
        )
        
        return format_apply_result(result)
    except Exception as e:
        return f"❌ Failed to apply: {str(e)}"

# Formatting functions
def format_execution_result(result: Dict) -> str:
    """Format execution result for display"""
    output = []
    output.append(f"🎯 Execution Successful")
    output.append(f"Persona: {result.get('persona', 'Unknown')}")
    output.append(f"Time: {result.get('execution_time', 0):.2f}s")
    
    if result.get('response'):
        output.append(f"\n📝 Result:\n{result['response']}")
    
    if result.get('memory_used'):
        output.append(f"\n💾 Memory: {result['memory_used']} items accessed")
    
    return '\n'.join(output)

def format_recall_results(result: Dict, query: str) -> str:
    """Format recall results"""
    output = []
    output.append(f"🔍 Found {result.get('count', 0)} memories for '{query}'")
    
    for i, memory in enumerate(result.get('items', [])[:5], 1):
        output.append(f"\n{i}. {memory.get('key', 'Unknown')}")
        output.append(f"   Value: {str(memory.get('value', ''))[:100]}...")
        if memory.get('metadata'):
            meta = memory['metadata']
            output.append(f"   Persona: {meta.get('persona', 'N/A')}")
            output.append(f"   Importance: {meta.get('importance', 0):.2f}")
            output.append(f"   Created: {meta.get('created_at', 'Unknown')}")
    
    return '\n'.join(output)

def format_parallel_results(result: Dict, task: str) -> str:
    """Format parallel analysis results"""
    output = []
    output.append(f"🔄 Parallel Analysis: {task[:50]}...")
    output.append("="*50)
    
    for persona_result in result.get('results', []):
        persona = persona_result.get('persona', 'Unknown')
        status = '✅' if persona_result.get('success') else '❌'
        output.append(f"\n{status} {persona.upper()}")
        
        if persona_result.get('response'):
            response = persona_result['response'][:200]
            output.append(f"   {response}...")
        
        if persona_result.get('confidence'):
            output.append(f"   Confidence: {persona_result['confidence']:.2f}")
    
    if result.get('consensus'):
        output.append(f"\n📊 Consensus: {result['consensus']}")
    
    return '\n'.join(output)

def format_workflow_result(result: Dict) -> str:
    """Format workflow execution result"""
    output = []
    output.append(f"⚙️ Workflow Execution: {result.get('workflow_id', 'Unknown')}")
    output.append(f"Status: {result.get('status', 'Unknown')}")
    
    if result.get('steps'):
        output.append("\nSteps:")
        for step in result['steps']:
            status_icon = '✅' if step.get('completed') else '⏳'
            output.append(f"  {status_icon} {step.get('name', 'Unknown')}")
    
    if result.get('output'):
        output.append(f"\nOutput: {result['output']}")
    
    return '\n'.join(output)

def format_workflow_status(result: Dict) -> str:
    """Format workflow status"""
    output = []
    output.append(f"📊 Workflow Status: {result.get('workflow_id', 'Unknown')}")
    output.append(f"Status: {result.get('status', 'Unknown')}")
    output.append(f"Progress: {result.get('progress', 0)}%")
    
    if result.get('current_step'):
        output.append(f"Current Step: {result['current_step']}")
    
    if result.get('started_at'):
        output.append(f"Started: {result['started_at']}")
    
    if result.get('completed_at'):
        output.append(f"Completed: {result['completed_at']}")
    
    return '\n'.join(output)

def format_workflow_list(result: Dict) -> str:
    """Format workflow list"""
    output = []
    output.append("📋 Available Workflows:")
    
    for workflow in result.get('workflows', []):
        output.append(f"\n• {workflow.get('id', 'Unknown')}")
        output.append(f"  Name: {workflow.get('name', 'Unknown')}")
        output.append(f"  Description: {workflow.get('description', 'No description')}")
    
    return '\n'.join(output)

def format_status(result: Dict) -> str:
    """Format system status"""
    output = []
    output.append("🔧 TMWS System Status")
    output.append("="*30)
    
    # Database status
    if result.get('database'):
        db = result['database']
        output.append(f"\n💾 Database: {db.get('status', 'Unknown')}")
        output.append(f"   Connections: {db.get('active_connections', 0)}/{db.get('max_connections', 0)}")
    
    # Memory status
    if result.get('memory'):
        mem = result['memory']
        output.append(f"\n🧠 Memory: {mem.get('total_items', 0)} items")
        output.append(f"   Vector index: {mem.get('vector_index_size', 0)} vectors")
    
    # Personas status
    if result.get('personas'):
        output.append(f"\n👥 Personas: {', '.join(result['personas'].get('active', []))}")
    
    # API status
    if result.get('api'):
        api = result['api']
        output.append(f"\n🌐 API: {api.get('status', 'Unknown')}")
        output.append(f"   Uptime: {api.get('uptime', 'Unknown')}")
    
    return '\n'.join(output)

def format_report(result: Dict, report_type: str) -> str:
    """Format report output"""
    output = []
    output.append(f"📊 {report_type.title()} Report")
    output.append("="*30)
    
    if report_type == 'usage':
        output.append(f"\nTotal Executions: {result.get('total_executions', 0)}")
        output.append("\nPersona Usage:")
        for persona, count in result.get('persona_usage', {}).items():
            output.append(f"  • {persona}: {count} times")
    
    elif report_type == 'optimization':
        output.append(f"\nCache Hit Rate: {result.get('cache_hit_rate', 0):.1%}")
        output.append(f"Avg Response Time: {result.get('avg_response_time', 0):.2f}s")
        output.append(f"Vector Search Performance: {result.get('vector_search_ms', 0):.1f}ms")
    
    elif report_type == 'security':
        output.append(f"\nAuthentication: {result.get('auth_enabled', False)}")
        output.append(f"Failed Attempts: {result.get('failed_auth_attempts', 0)}")
        output.append(f"Rate Limit Hits: {result.get('rate_limit_hits', 0)}")
    
    elif report_type == 'learning':
        output.append(f"\nPatterns Learned: {result.get('patterns_count', 0)}")
        output.append(f"Pattern Applications: {result.get('applications_count', 0)}")
        output.append("\nTop Patterns:")
        for pattern in result.get('top_patterns', [])[:5]:
            output.append(f"  • {pattern.get('name', 'Unknown')}: {pattern.get('usage', 0)} uses")
    
    return '\n'.join(output)

def format_apply_result(result: Dict) -> str:
    """Format pattern application result"""
    output = []
    output.append(f"🔄 Pattern Applied: {result.get('pattern_name', 'Unknown')}")
    output.append(f"Success: {'Yes' if result.get('success') else 'No'}")
    
    if result.get('output'):
        output.append(f"\nOutput:\n{result['output']}")
    
    if result.get('improvements'):
        output.append(f"\n💡 Improvements: {result['improvements']}")
    
    return '\n'.join(output)

def show_help() -> str:
    """Show command help"""
    return """
🎯 Trinitas TMWS Command Interface

Usage: /trinitas <operation> [options]

Operations:
  execute <persona> <task>      - Execute with specific persona
  remember <key> <value>        - Store in memory
  recall <query>                - Retrieve from memory
  learn <pattern> <desc>        - Learn pattern
  apply <pattern> <task>        - Apply pattern
  status [component]            - Show status
  report <type>                 - Generate report
  analyze <task>                - Multi-persona analysis
  workflow <action> [options]   - Manage workflows

Personas:
  athena  - Strategic Architect
  artemis - Technical Perfectionist
  hestia  - Security Guardian
  eris    - Tactical Coordinator
  hera    - System Conductor
  muses   - Knowledge Architect

Examples:
  /trinitas execute athena "Design system architecture"
  /trinitas remember project_config "PostgreSQL cluster" --importance 0.9
  /trinitas recall architecture --semantic --limit 5
  /trinitas analyze "Security audit" --personas hestia,artemis
  /trinitas workflow create deployment "Deployment workflow"
  /trinitas status memory
  /trinitas report optimization

For detailed documentation, see TMWS documentation.
"""

# Register command handler
if __name__ == "__main__":
    # This would be called by Claude when /trinitas is invoked
    import sys
    args = ' '.join(sys.argv[1:]) if len(sys.argv) > 1 else ""
    result = asyncio.run(handle_trinitas_command(args))
    print(result)
```