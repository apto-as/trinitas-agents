# Trinitas v3.5 Technical Specification - Hybrid Intelligence Architecture

## 1. System Architecture

### 1.1 Component Overview
```yaml
system_components:
  primary_intelligence:
    name: "Claude Code + Trinitas Core"
    role: "Strategic thinking, critical analysis, final decisions"
    context_limit: 200000
    
  secondary_intelligence:
    name: "Qwen Code + GPT-OSS-120B (Local)"
    role: "Computational tasks, testing, documentation"
    context_limit: 120000
    optimization: "English language processing"
    
  orchestration_layer:
    name: "Hybrid Intelligence Controller"
    components:
      - Context Monitor
      - Task Delegator
      - Result Synthesizer
      - State Synchronizer
```

### 1.2 Communication Architecture
```python
# communication/protocol.py
class HybridCommunicationProtocol:
    """
    Manages communication between Claude and Local LLM
    """
    
    def __init__(self):
        self.claude_endpoint = "native"  # Direct Claude Code access
        self.local_endpoint = "http://localhost:8080/v1/chat/completions"
        self.mcp_bridge = "http://localhost:5000/mcp/v1"
        
    async def send_to_local(self, request: TaskRequest) -> TaskResponse:
        """
        Send task to local LLM with English optimization
        """
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.local_api_key}"
        }
        
        # Format for English-optimized processing
        payload = {
            "model": "gpt-oss-120b",
            "messages": [
                {
                    "role": "system",
                    "content": "You are an expert software engineer. Use MCP tools effectively."
                },
                {
                    "role": "user",
                    "content": self.format_english_prompt(request)
                }
            ],
            "tools": self.get_mcp_tools(request.required_tools),
            "tool_choice": "auto",
            "temperature": 0.7,
            "max_tokens": 8000
        }
        
        response = await self.http_client.post(
            self.local_endpoint,
            json=payload,
            headers=headers
        )
        
        return self.parse_response(response)
```

## 2. Task Delegation System

### 2.1 Delegation Rules Engine
```python
# delegation/rules.py
class DelegationRules:
    """
    Intelligent task routing based on task characteristics
    """
    
    # Cognitive Complexity Levels
    COMPLEXITY_LEVELS = {
        "mechanical": 1,      # Simple, repetitive tasks
        "analytical": 2,      # Pattern matching, basic analysis
        "reasoning": 3,       # Logic and inference required
        "creative": 4,        # Novel solutions needed
        "strategic": 5,       # Long-term implications
    }
    
    DELEGATION_MATRIX = {
        # Task Type -> (Preferred Executor, Confidence, Complexity)
        "file_search": ("local", 0.95, "mechanical"),
        "large_file_analysis": ("local", 0.98, "mechanical"),
        "test_execution": ("local", 0.99, "mechanical"),
        "documentation_generation": ("local", 0.85, "analytical"),
        "test_generation": ("local", 0.90, "analytical"),
        "pattern_detection": ("local", 0.85, "analytical"),
        
        # High complexity - Always Claude
        "code_generation": ("claude", 0.95, "creative"),
        "algorithm_design": ("claude", 0.99, "creative"),
        "security_audit": ("claude", 0.99, "reasoning"),
        "architecture_design": ("claude", 0.95, "strategic"),
        "api_design": ("claude", 0.90, "strategic"),
        "complex_debugging": ("claude", 0.95, "reasoning"),
        
        # Hybrid - Requires both
        "performance_optimization": ("hybrid", 0.80, "reasoning"),
        "bug_investigation": ("hybrid", 0.75, "analytical"),
        "refactoring": ("hybrid", 0.70, "creative"),
        "system_analysis": ("hybrid", 0.85, "strategic"),
    }
    
    CONTEXT_THRESHOLDS = {
        "claude_warning": 100000,    # Start considering delegation
        "claude_critical": 150000,   # Must delegate
        "local_warning": 80000,      # Local LLM warning
        "local_critical": 100000,    # Local LLM limit
    }
    
    def decide_delegation(self, task: Task, context_state: ContextState) -> str:
        """
        Returns: 'claude', 'local', or 'hybrid'
        Based on cognitive complexity AND computational load
        """
        # Step 1: Get task characteristics
        if task.type in self.DELEGATION_MATRIX:
            executor, confidence, complexity = self.DELEGATION_MATRIX[task.type]
            complexity_level = self.COMPLEXITY_LEVELS[complexity]
        else:
            complexity_level = self.estimate_complexity(task)
            executor = None
            confidence = 0.5
        
        # Step 2: High complexity ALWAYS goes to Claude (even if heavy)
        if complexity_level >= 4:  # Creative or Strategic
            if task.estimated_tokens > 100000:
                # Too heavy even for Claude - decompose
                return "hybrid"
            return "claude"
        
        # Step 3: Check if task has explicit routing with high confidence
        if executor and confidence > 0.90:
            return executor
        
        # Step 4: Context-aware routing for medium complexity
        if complexity_level == 3:  # Reasoning required
            if context_state.claude_usage > self.CONTEXT_THRESHOLDS["claude_warning"]:
                # Try hybrid to preserve Claude context
                return "hybrid"
            return "claude"  # Prefer Claude for reasoning
        
        # Step 5: Low complexity tasks - consider computational load
        if complexity_level <= 2:  # Mechanical or Analytical
            if task.estimated_tokens > 20000:
                return "local"  # Heavy but simple - perfect for local
            
            if task.requires_tools and len(task.required_tools) > 3:
                return "local"  # Tool-heavy but simple
            
            if context_state.claude_usage > self.CONTEXT_THRESHOLDS["claude_warning"]:
                return "local"  # Save Claude's context
        
        # Step 6: Default based on context pressure
        if context_state.claude_usage > self.CONTEXT_THRESHOLDS["claude_critical"]:
            return "local" if complexity_level <= 2 else "hybrid"
        
        return "claude"  # When in doubt, use Claude
    
    def estimate_complexity(self, task: Task) -> int:
        """
        Estimate cognitive complexity of unknown tasks
        """
        indicators = {
            "creative": ["design", "create", "invent", "novel", "innovative"],
            "strategic": ["architecture", "plan", "roadmap", "long-term", "system"],
            "reasoning": ["why", "debug", "analyze", "understand", "explain"],
            "analytical": ["find", "search", "compare", "measure", "count"],
            "mechanical": ["copy", "move", "run", "execute", "list"],
        }
        
        task_text = task.description.lower()
        
        for level, keywords in indicators.items():
            if any(keyword in task_text for keyword in keywords):
                return self.COMPLEXITY_LEVELS[level]
        
        # Check for decision-making indicators
        if any(word in task_text for word in ["decide", "choose", "evaluate", "judge"]):
            return 3  # Reasoning
        
        # Default to analytical for unknown tasks
        return 2
```

### 2.2 Cognitive-Aware Task Decomposition
```python
# delegation/cognitive_decomposer.py
class CognitiveTaskDecomposer:
    """
    Breaks complex tasks based on cognitive requirements, not just size
    """
    
    def decompose(self, task: Task) -> TaskDecomposition:
        """
        Separate mechanical work from cognitive work
        """
        complexity = self.assess_cognitive_load(task)
        
        if complexity.is_heavy_but_simple:
            # Large dataset processing, file operations, etc.
            return TaskDecomposition(
                local_tasks=[
                    Task("data_gathering", "Collect all relevant data"),
                    Task("initial_processing", "Process and format data"),
                    Task("pattern_extraction", "Find obvious patterns"),
                ],
                claude_tasks=[
                    Task("interpret_results", "Understand implications"),
                    Task("make_decision", "Decide on action"),
                ],
                synthesis_required=True
            )
        
        elif complexity.is_heavy_and_complex:
            # Complex analysis of large systems
            return TaskDecomposition(
                local_tasks=[
                    Task("mechanical_analysis", "Gather metrics and facts"),
                    Task("data_preparation", "Organize information"),
                ],
                claude_tasks=[
                    Task("deep_analysis", "Understand complex relationships"),
                    Task("creative_solution", "Design novel approach"),
                    Task("strategic_planning", "Plan implementation"),
                ],
                synthesis_required=True,
                claude_priority=True  # Claude leads this work
            )
        
        elif task.type == "performance_optimization":
            return TaskDecomposition(
                local_tasks=[
                    Task("profile_code", "Run performance profiling", complexity="mechanical"),
                    Task("collect_metrics", "Gather performance data", complexity="mechanical"),
                    Task("identify_hotspots", "Find slow operations", complexity="analytical"),
                ],
                claude_tasks=[
                    Task("analyze_architecture", "Understand design implications", complexity="strategic"),
                    Task("design_optimizations", "Create optimization strategy", complexity="creative"),
                    Task("validate_approach", "Ensure correctness", complexity="reasoning"),
                ],
                synthesis_required=True
            )
        
        elif task.type == "bug_investigation":
            return TaskDecomposition(
                local_tasks=[
                    Task("search_error_patterns", "Find error occurrences"),
                    Task("trace_execution", "Follow code paths"),
                    Task("collect_logs", "Gather relevant logs"),
                ],
                claude_tasks=[
                    Task("analyze_root_cause", "Identify bug source"),
                    Task("design_fix", "Create solution"),
                    Task("verify_fix", "Validate solution"),
                ],
                synthesis_required=True
            )
        
        # Add more decomposition patterns...
        return TaskDecomposition([task], [], False)
```

## 3. Sparring Partner Implementation

### 3.1 Sparring Session Manager
```python
# sparring/manager.py
class SparringSessionManager:
    """
    Orchestrates problem-solving collaboration between Claude and Local LLM
    """
    
    def __init__(self):
        self.session_types = {
            "devil_advocate": self.run_devil_advocate,
            "alternative_finder": self.run_alternative_finder,
            "edge_case_hunter": self.run_edge_case_hunter,
            "perspective_shift": self.run_perspective_shift,
        }
    
    async def initiate_sparring(
        self, 
        problem: str, 
        current_solution: str,
        mode: str = "auto"
    ) -> SparringResult:
        """
        Start a sparring session
        """
        if mode == "auto":
            mode = self.determine_best_mode(problem, current_solution)
        
        session = SparringSession(
            id=self.generate_session_id(),
            problem=problem,
            initial_solution=current_solution,
            mode=mode,
            timestamp=datetime.now()
        )
        
        # Execute sparring
        result = await self.session_types[mode](session)
        
        # Synthesize insights
        final_solution = await self.synthesize_solutions(
            session,
            result
        )
        
        return SparringResult(
            original=current_solution,
            challenges=result.challenges,
            alternatives=result.alternatives,
            synthesis=final_solution,
            confidence=self.calculate_confidence(result)
        )
    
    async def run_devil_advocate(self, session: SparringSession):
        """
        Local LLM challenges assumptions
        """
        prompt = f"""
        As a devil's advocate, critically analyze this solution:
        
        Problem: {session.problem}
        Proposed Solution: {session.initial_solution}
        
        Tasks:
        1. Identify hidden assumptions
        2. Find potential failure modes
        3. Question design decisions
        4. Suggest stress test scenarios
        5. Point out missing edge cases
        
        Use MCP tools to:
        - Search for similar implementations that failed
        - Find security vulnerabilities
        - Check performance implications
        
        Provide structured criticism with evidence.
        """
        
        response = await self.local_llm.analyze(
            prompt,
            tools=["mcp_search", "code_analysis", "security_scan"]
        )
        
        return response
```

### 3.2 Solution Synthesis
```python
# sparring/synthesizer.py
class SolutionSynthesizer:
    """
    Combines insights from sparring sessions
    """
    
    async def synthesize(
        self,
        original: Solution,
        challenges: List[Challenge],
        alternatives: List[Solution]
    ) -> Solution:
        """
        Create optimal solution from multiple inputs
        """
        # Step 1: Address critical challenges
        modified = original
        for challenge in challenges:
            if challenge.severity == "critical":
                modified = await self.address_challenge(modified, challenge)
        
        # Step 2: Integrate best alternative ideas
        for alt in alternatives:
            valuable_aspects = await self.extract_valuable_aspects(alt)
            modified = await self.integrate_aspects(modified, valuable_aspects)
        
        # Step 3: Claude final review
        final = await self.claude_review(
            original=original,
            modified=modified,
            rationale=self.generate_change_rationale(original, modified)
        )
        
        return final
```

## 4. Automated Testing Pipeline

### 4.1 Test Generation Delegator
```python
# testing/delegator.py
class TestGenerationDelegator:
    """
    Manages automated test generation and execution
    """
    
    def __init__(self):
        self.local_llm = LocalLLMConnector()
        self.test_frameworks = {
            "python": "pytest",
            "javascript": "jest",
            "typescript": "jest",
            "go": "testing",
            "rust": "cargo test",
        }
    
    async def generate_tests(self, code: str, language: str) -> TestSuite:
        """
        Delegate test generation to local LLM
        """
        framework = self.test_frameworks.get(language, "generic")
        
        prompt = f"""
        Generate comprehensive tests for this code:
        
        ```{language}
        {code}
        ```
        
        Requirements:
        1. Use {framework} framework
        2. Cover happy paths (40%)
        3. Cover edge cases (40%)
        4. Cover error conditions (20%)
        5. Include performance tests if applicable
        6. Add integration tests for external dependencies
        
        Use MCP tools to:
        - Check existing test patterns in the project
        - Validate test completeness
        - Ensure proper mocking
        
        Output format: Executable test code with comments
        """
        
        tests = await self.local_llm.generate(
            prompt,
            tools=["file_read", "code_search", "mcp_trinity"]
        )
        
        # Validate generated tests
        validation = await self.validate_tests(tests, code)
        
        if validation.has_issues():
            tests = await self.fix_test_issues(tests, validation.issues)
        
        return TestSuite(
            tests=tests,
            coverage=await self.estimate_coverage(tests, code),
            language=language,
            framework=framework
        )
```

### 4.2 Test Execution Manager
```python
# testing/executor.py
class TestExecutionManager:
    """
    Manages test execution on local LLM
    """
    
    async def execute_tests(
        self, 
        test_suite: TestSuite,
        options: TestOptions = None
    ) -> TestResults:
        """
        Execute tests using local LLM's tool capabilities
        """
        # Prepare test environment
        env_setup = await self.setup_test_environment(test_suite)
        
        # Execute via local LLM with tools
        execution_prompt = f"""
        Execute these tests and provide detailed results:
        
        Test Suite: {test_suite.name}
        Framework: {test_suite.framework}
        
        Steps:
        1. Set up test environment
        2. Run tests with coverage
        3. Capture all output
        4. Generate report
        
        Use tools:
        - bash: Run test commands
        - file_write: Save test results
        - mcp_server: Coordinate with Trinity
        """
        
        results = await self.local_llm.execute(
            execution_prompt,
            tools=["bash", "file_write", "mcp_server"],
            timeout=300  # 5 minutes max
        )
        
        # Parse and analyze results
        parsed = self.parse_test_output(results)
        
        # Critical failures go to Claude
        if parsed.has_critical_failures():
            claude_analysis = await self.escalate_to_claude(
                parsed.critical_failures,
                test_suite,
                results
            )
            parsed.add_analysis(claude_analysis)
        
        return parsed
```

## 5. State Synchronization

### 5.1 Shared State Manager
```python
# state/manager.py
class SharedStateManager:
    """
    Maintains synchronized state between Claude and Local LLM
    """
    
    def __init__(self):
        self.state_store = {
            "project_context": {},
            "active_tasks": {},
            "delegation_history": [],
            "test_results": {},
            "sparring_sessions": {},
        }
        self.mcp_state_sync = MCPStateSync()
    
    async def sync_state(self, source: str, update: StateUpdate):
        """
        Synchronize state changes across systems
        """
        # Update local store
        self.state_store[update.category][update.key] = update.value
        
        # Propagate via MCP
        await self.mcp_state_sync.broadcast(update)
        
        # Log for audit
        self.log_state_change(source, update)
    
    async def get_state(self, category: str, key: str = None):
        """
        Retrieve synchronized state
        """
        if key:
            return self.state_store.get(category, {}).get(key)
        return self.state_store.get(category, {})
```

## 6. Performance Optimization

### 6.1 Caching Strategy
```python
# optimization/cache.py
class HybridCache:
    """
    Intelligent caching for hybrid system
    """
    
    def __init__(self):
        self.claude_cache = LRUCache(maxsize=1000)
        self.local_cache = LRUCache(maxsize=5000)
        self.shared_cache = RedisCache()  # For larger artifacts
    
    async def get_or_compute(
        self,
        key: str,
        compute_func: Callable,
        executor: str = "auto"
    ):
        """
        Cache-aware computation
        """
        # Check caches
        if cached := await self.check_caches(key):
            return cached
        
        # Determine executor
        if executor == "auto":
            executor = self.determine_best_executor(compute_func)
        
        # Compute
        if executor == "local":
            result = await self.compute_local(compute_func)
            self.local_cache.set(key, result)
        else:
            result = await self.compute_claude(compute_func)
            self.claude_cache.set(key, result)
        
        # Share if valuable
        if self.is_valuable_for_sharing(result):
            await self.shared_cache.set(key, result)
        
        return result
```

## 7. Monitoring and Metrics

### 7.1 Performance Metrics
```python
# monitoring/metrics.py
class HybridMetrics:
    """
    Track hybrid system performance
    """
    
    METRICS = {
        "delegation_count": Counter(),
        "context_saved": Histogram(),
        "task_latency": Histogram(),
        "sparring_improvements": Counter(),
        "test_coverage": Gauge(),
        "cost_reduction": Gauge(),
    }
    
    def record_delegation(self, task: Task, executor: str, result: Result):
        """
        Track delegation metrics
        """
        self.METRICS["delegation_count"].labels(
            task_type=task.type,
            executor=executor
        ).inc()
        
        self.METRICS["context_saved"].observe(
            task.estimated_tokens - result.actual_tokens
        )
        
        self.METRICS["task_latency"].labels(
            executor=executor
        ).observe(result.duration)
```

## 8. Error Handling and Fallback

### 8.1 Resilience Manager
```python
# resilience/manager.py
class ResilienceManager:
    """
    Handles failures and fallbacks
    """
    
    async def execute_with_fallback(
        self,
        task: Task,
        primary_executor: str,
        fallback_executor: str = "claude"
    ):
        """
        Execute with automatic fallback
        """
        try:
            # Try primary executor
            if primary_executor == "local":
                return await self.local_execute(task)
            else:
                return await self.claude_execute(task)
                
        except LocalLLMUnavailable:
            self.log_warning("Local LLM unavailable, falling back")
            if fallback_executor == "claude":
                return await self.claude_execute(task)
            else:
                raise SystemUnavailable("No executor available")
                
        except ContextLimitExceeded as e:
            # Decompose and retry
            subtasks = await self.emergency_decompose(task)
            results = []
            for subtask in subtasks:
                result = await self.execute_with_fallback(
                    subtask,
                    "local",  # Try local first for subtasks
                    "claude"
                )
                results.append(result)
            return self.merge_results(results)
```

## 9. Configuration

### 9.1 System Configuration
```yaml
# config/hybrid.yaml
hybrid_system:
  version: "3.5"
  
  claude:
    max_context: 200000
    reserve_context: 20000  # Always keep free
    
  local_llm:
    endpoint: "http://localhost:8080/v1"
    model: "gpt-oss-120b"
    max_context: 120000
    timeout: 30
    
  delegation:
    auto_delegate_threshold: 100000
    force_delegate_threshold: 150000
    prefer_local_for:
      - file_operations
      - test_execution
      - documentation
      - large_searches
    
  sparring:
    auto_trigger_on:
      - complex_problems
      - architecture_decisions
      - performance_issues
    modes:
      - devil_advocate
      - alternative_finder
      - edge_case_hunter
    
  testing:
    delegate_to_local: true
    coverage_target: 0.85
    frameworks:
      python: pytest
      javascript: jest
      go: testing
    
  monitoring:
    metrics_port: 9090
    log_level: INFO
    trace_delegations: true
```

---

**Technical Specification v3.5** - Engineering Excellence Through Hybrid Intelligence