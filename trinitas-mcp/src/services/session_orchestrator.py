#!/usr/bin/env python3
"""
Trinitas v3.5 MCP Tools - Multi-Session Orchestrator

🌸 Springfield: "ふふ、複数のお客様を同時にお迎えするのは、カフェの腕の見せ所ですね。
             すべてのセッションに最高のサービスをお届けします。"
⚡ Krukai: "完璧な並行処理アーキテクチャで、リソース効率を最大化してやる！"
🛡️ Vector: "……各セッションの分離と、共有リソースの安全性を保証する……"

Advanced session management with pooling, migration, and resource allocation.
"""

import asyncio
import threading
import time
import uuid
import json
import logging
from typing import Dict, Any, List, Optional, Set, Callable, Coroutine, Union
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor, Future
from collections import defaultdict, deque
from queue import Queue, PriorityQueue
import weakref
from contextlib import asynccontextmanager
import resource
import psutil
import gc

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class SessionPriority:
    """Session priority levels"""
    CRITICAL = 100
    HIGH = 80
    NORMAL = 50
    LOW = 20
    BACKGROUND = 10


@dataclass
class ResourceLimits:
    """Resource limits for sessions"""
    max_memory_mb: int = 256
    max_cpu_percent: float = 25.0
    max_concurrent_requests: int = 10
    max_session_duration_hours: int = 24
    max_context_size_mb: int = 32


@dataclass
class SessionMetrics:
    """Session performance metrics"""
    requests_processed: int = 0
    total_response_time: float = 0.0
    memory_usage_peak_mb: float = 0.0
    cpu_time_used: float = 0.0
    cache_hit_rate: float = 0.0
    error_count: int = 0
    created_at: datetime = field(default_factory=datetime.now)
    last_activity: datetime = field(default_factory=datetime.now)
    
    @property
    def avg_response_time(self) -> float:
        return self.total_response_time / max(1, self.requests_processed)
    
    @property
    def uptime_hours(self) -> float:
        return (datetime.now() - self.created_at).total_seconds() / 3600.0


@dataclass
class SessionConfig:
    """Session configuration"""
    session_id: str
    user_id: str
    priority: int = SessionPriority.NORMAL
    resource_limits: ResourceLimits = field(default_factory=ResourceLimits)
    persona_preferences: List[str] = field(default_factory=list)
    workflow_templates: List[str] = field(default_factory=list)
    auto_cleanup: bool = True
    enable_context_sharing: bool = False
    custom_settings: Dict[str, Any] = field(default_factory=dict)


class SessionContext:
    """Enhanced session context with resource tracking"""
    
    def __init__(self, config: SessionConfig):
        self.config = config
        self.context_data = {}
        self.shared_context = {}
        self.persona_contexts = defaultdict(dict)
        self.workflow_states = {}
        self.resource_monitor = ResourceMonitor(config.resource_limits)
        self.metrics = SessionMetrics()
        self.lock = threading.RLock()
        self.active_requests = set()
        self.request_queue = PriorityQueue()
        
        # Session state
        self.is_active = True
        self.is_migrating = False
        self.migration_target = None
        
        # Cleanup tracking
        self.last_cleanup = datetime.now()
        self.cleanup_interval = timedelta(minutes=30)
    
    def add_context(self, key: str, data: Any, persona_type: str = None, 
                   shared: bool = False) -> bool:
        """Add context data with persona awareness"""
        with self.lock:
            try:
                # Check resource limits
                if not self.resource_monitor.check_memory_limit(data):
                    logger.warning(f"Context addition rejected: memory limit exceeded")
                    return False
                
                if shared and self.config.enable_context_sharing:
                    self.shared_context[key] = data
                elif persona_type:
                    self.persona_contexts[persona_type][key] = data
                else:
                    self.context_data[key] = data
                
                self.metrics.last_activity = datetime.now()
                return True
                
            except Exception as e:
                logger.error(f"Failed to add context: {e}")
                return False
    
    def get_context(self, key: str, persona_type: str = None) -> Any:
        """Get context data with persona awareness"""
        with self.lock:
            # Try persona-specific context first
            if persona_type and key in self.persona_contexts[persona_type]:
                return self.persona_contexts[persona_type][key]
            
            # Try shared context
            if key in self.shared_context:
                return self.shared_context[key]
            
            # Try general context
            return self.context_data.get(key)
    
    def update_workflow_state(self, workflow_id: str, state: Dict[str, Any]):
        """Update workflow state"""
        with self.lock:
            self.workflow_states[workflow_id] = {
                'state': state,
                'updated_at': datetime.now()
            }
            self.metrics.last_activity = datetime.now()
    
    def cleanup_expired_data(self):
        """Clean up expired context data"""
        if datetime.now() - self.last_cleanup < self.cleanup_interval:
            return
        
        with self.lock:
            # Clean up old workflow states
            cutoff_time = datetime.now() - timedelta(hours=2)
            expired_workflows = [
                wf_id for wf_id, wf_data in self.workflow_states.items()
                if wf_data['updated_at'] < cutoff_time
            ]
            
            for wf_id in expired_workflows:
                del self.workflow_states[wf_id]
            
            # Force garbage collection
            gc.collect()
            
            self.last_cleanup = datetime.now()
            if expired_workflows:
                logger.info(f"Cleaned up {len(expired_workflows)} expired workflow states")
    
    def get_memory_usage(self) -> float:
        """Get current memory usage in MB"""
        return self.resource_monitor.get_current_memory_mb()
    
    def can_accept_request(self) -> bool:
        """Check if session can accept new requests"""
        return (
            self.is_active and 
            not self.is_migrating and
            len(self.active_requests) < self.config.resource_limits.max_concurrent_requests and
            self.resource_monitor.within_limits()
        )


class ResourceMonitor:
    """Monitor and enforce resource limits for sessions"""
    
    def __init__(self, limits: ResourceLimits):
        self.limits = limits
        self.process = psutil.Process()
        self.baseline_memory = self.process.memory_info().rss
        
    def check_memory_limit(self, additional_data: Any = None) -> bool:
        """Check if adding data would exceed memory limits"""
        current_mb = self.get_current_memory_mb()
        
        if additional_data:
            # Estimate additional memory needed
            try:
                import pickle
                additional_mb = len(pickle.dumps(additional_data)) / (1024 * 1024)
                return current_mb + additional_mb <= self.limits.max_memory_mb
            except Exception:
                # Conservative estimate if serialization fails
                return current_mb <= self.limits.max_memory_mb * 0.8
        
        return current_mb <= self.limits.max_memory_mb
    
    def get_current_memory_mb(self) -> float:
        """Get current memory usage in MB"""
        current_memory = self.process.memory_info().rss
        return (current_memory - self.baseline_memory) / (1024 * 1024)
    
    def get_cpu_percent(self) -> float:
        """Get current CPU usage percentage"""
        return self.process.cpu_percent()
    
    def within_limits(self) -> bool:
        """Check if session is within all resource limits"""
        return (
            self.get_current_memory_mb() <= self.limits.max_memory_mb and
            self.get_cpu_percent() <= self.limits.max_cpu_percent
        )


class SessionPool:
    """Intelligent session pool with recycling"""
    
    def __init__(self, min_size: int = 5, max_size: int = 50):
        self.min_size = min_size
        self.max_size = max_size
        self.available_sessions = deque()
        self.active_sessions = {}
        self.lock = threading.RLock()
        
        # Pre-populate pool
        self._populate_pool()
    
    def get_session(self, user_id: str, config: SessionConfig = None) -> SessionContext:
        """Get session from pool or create new one"""
        with self.lock:
            session = None
            
            # Try to reuse from pool
            if self.available_sessions:
                session = self.available_sessions.popleft()
                session.config = config or SessionConfig(
                    session_id=str(uuid.uuid4()),
                    user_id=user_id
                )
                session.context_data.clear()
                session.persona_contexts.clear()
                session.workflow_states.clear()
                session.metrics = SessionMetrics()
                session.is_active = True
                session.is_migrating = False
            else:
                # Create new session
                session_config = config or SessionConfig(
                    session_id=str(uuid.uuid4()),
                    user_id=user_id
                )
                session = SessionContext(session_config)
            
            self.active_sessions[session.config.session_id] = session
            return session
    
    def return_session(self, session: SessionContext):
        """Return session to pool"""
        with self.lock:
            session_id = session.config.session_id
            
            if session_id in self.active_sessions:
                del self.active_sessions[session_id]
            
            # Clean up session
            session.cleanup_expired_data()
            session.is_active = False
            
            # Return to pool if under max size
            if len(self.available_sessions) < self.max_size:
                self.available_sessions.append(session)
            
            # Maintain minimum pool size
            self._maintain_pool_size()
    
    def _populate_pool(self):
        """Pre-populate pool with minimum sessions"""
        for _ in range(self.min_size):
            session = SessionContext(SessionConfig(
                session_id=f"pool-{uuid.uuid4()}",
                user_id="pool"
            ))
            session.is_active = False
            self.available_sessions.append(session)
    
    def _maintain_pool_size(self):
        """Ensure pool maintains minimum size"""
        while len(self.available_sessions) < self.min_size:
            session = SessionContext(SessionConfig(
                session_id=f"pool-{uuid.uuid4()}",
                user_id="pool"
            ))
            session.is_active = False
            self.available_sessions.append(session)
    
    def get_pool_stats(self) -> Dict[str, int]:
        """Get pool statistics"""
        with self.lock:
            return {
                'available': len(self.available_sessions),
                'active': len(self.active_sessions),
                'total': len(self.available_sessions) + len(self.active_sessions)
            }


class SessionMigrator:
    """Handle session migration between instances"""
    
    def __init__(self, cache_manager=None):
        self.cache_manager = cache_manager
        self.migration_queue = Queue()
        self.active_migrations = {}
        
    async def migrate_session(self, session: SessionContext, 
                            target_instance: str) -> bool:
        """Migrate session to target instance"""
        session.is_migrating = True
        session.migration_target = target_instance
        
        try:
            # Serialize session state
            session_state = self._serialize_session(session)
            
            # Store in cache for target instance to pick up
            if self.cache_manager:
                migration_key = f"migration:{session.config.session_id}:{target_instance}"
                self.cache_manager.put(
                    migration_key,
                    session_state,
                    tags=['migration', 'session'],
                    custom_ttl=300  # 5 minutes to complete migration
                )
            
            # Mark migration as active
            self.active_migrations[session.config.session_id] = {
                'target': target_instance,
                'started_at': datetime.now(),
                'state': 'in_progress'
            }
            
            logger.info(f"Session {session.config.session_id} migration initiated to {target_instance}")
            return True
            
        except Exception as e:
            logger.error(f"Session migration failed: {e}")
            session.is_migrating = False
            session.migration_target = None
            return False
    
    def restore_session(self, session_id: str, source_instance: str) -> Optional[SessionContext]:
        """Restore migrated session from cache"""
        try:
            if not self.cache_manager:
                return None
            
            migration_key = f"migration:{session_id}:{source_instance}"
            session_state = self.cache_manager.get(migration_key)
            
            if session_state:
                session = self._deserialize_session(session_state)
                
                # Clean up migration data
                self.cache_manager.remove(migration_key)
                
                # Update migration status
                if session_id in self.active_migrations:
                    self.active_migrations[session_id]['state'] = 'completed'
                
                logger.info(f"Session {session_id} restored from migration")
                return session
            
            return None
            
        except Exception as e:
            logger.error(f"Session restoration failed: {e}")
            return None
    
    def _serialize_session(self, session: SessionContext) -> Dict[str, Any]:
        """Serialize session state for migration"""
        return {
            'config': {
                'session_id': session.config.session_id,
                'user_id': session.config.user_id,
                'priority': session.config.priority,
                'persona_preferences': session.config.persona_preferences,
                'workflow_templates': session.config.workflow_templates,
                'custom_settings': session.config.custom_settings
            },
            'context_data': session.context_data,
            'persona_contexts': dict(session.persona_contexts),
            'workflow_states': session.workflow_states,
            'metrics': {
                'requests_processed': session.metrics.requests_processed,
                'total_response_time': session.metrics.total_response_time,
                'error_count': session.metrics.error_count,
                'created_at': session.metrics.created_at.isoformat()
            },
            'migration_timestamp': datetime.now().isoformat()
        }
    
    def _deserialize_session(self, state: Dict[str, Any]) -> SessionContext:
        """Deserialize session state after migration"""
        config = SessionConfig(**state['config'])
        session = SessionContext(config)
        
        session.context_data = state['context_data']
        session.persona_contexts = defaultdict(dict, state['persona_contexts'])
        session.workflow_states = state['workflow_states']
        
        # Restore metrics
        metrics_data = state['metrics']
        session.metrics.requests_processed = metrics_data['requests_processed']
        session.metrics.total_response_time = metrics_data['total_response_time']
        session.metrics.error_count = metrics_data['error_count']
        session.metrics.created_at = datetime.fromisoformat(metrics_data['created_at'])
        
        return session


class LoadBalancer:
    """Intelligent load balancing for session distribution"""
    
    def __init__(self, instances: List[str], strategy: str = "least_connections"):
        self.instances = instances
        self.strategy = strategy
        self.instance_stats = {instance: {'connections': 0, 'load': 0.0} 
                             for instance in instances}
        self.lock = threading.RLock()
    
    def select_instance(self, session_config: SessionConfig) -> str:
        """Select optimal instance for new session"""
        with self.lock:
            if self.strategy == "least_connections":
                return min(self.instances, 
                          key=lambda x: self.instance_stats[x]['connections'])
            
            elif self.strategy == "least_load":
                return min(self.instances,
                          key=lambda x: self.instance_stats[x]['load'])
            
            elif self.strategy == "priority_aware":
                # High priority sessions go to least loaded instances
                if session_config.priority >= SessionPriority.HIGH:
                    return min(self.instances,
                              key=lambda x: self.instance_stats[x]['load'])
                else:
                    return min(self.instances,
                              key=lambda x: self.instance_stats[x]['connections'])
            
            else:  # round_robin
                return self.instances[hash(session_config.session_id) % len(self.instances)]
    
    def update_instance_stats(self, instance: str, connections: int, load: float):
        """Update instance statistics"""
        with self.lock:
            if instance in self.instance_stats:
                self.instance_stats[instance] = {
                    'connections': connections,
                    'load': load
                }


class MultiSessionOrchestrator:
    """
    🌸 Springfield: "Main orchestrator for multi-session management"
    ⚡ Krukai: "Perfect concurrent session handling with optimal resource allocation"
    🛡️ Vector: "......secure session isolation with integrity verification......"
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.session_pool = SessionPool(
            min_size=self.config.get('min_pool_size', 5),
            max_size=self.config.get('max_pool_size', 50)
        )
        self.session_migrator = SessionMigrator()
        self.load_balancer = LoadBalancer(
            instances=self.config.get('instances', ['local']),
            strategy=self.config.get('load_strategy', 'least_connections')
        )
        
        # Active session management
        self.active_sessions = {}
        self.session_locks = defaultdict(threading.RLock)
        self.executor = ThreadPoolExecutor(
            max_workers=self.config.get('max_workers', 20)
        )
        
        # Resource monitoring
        self.global_resource_monitor = GlobalResourceMonitor()
        
        # Background maintenance
        self.maintenance_active = True
        self.maintenance_thread = threading.Thread(
            target=self._maintenance_worker, daemon=True
        )
        self.maintenance_thread.start()
    
    async def create_session(self, user_id: str, 
                           config: SessionConfig = None) -> SessionContext:
        """Create new session with intelligent resource allocation"""
        
        # Check global resource availability
        if not self.global_resource_monitor.can_create_session():
            raise ResourceError("Global resource limits exceeded")
        
        # Select optimal instance
        session_config = config or SessionConfig(
            session_id=str(uuid.uuid4()),
            user_id=user_id
        )
        
        target_instance = self.load_balancer.select_instance(session_config)
        
        # Get session from pool
        session = self.session_pool.get_session(user_id, session_config)
        
        # Register session
        with self.session_locks[session.config.session_id]:
            self.active_sessions[session.config.session_id] = session
        
        logger.info(f"Created session {session.config.session_id} for user {user_id}")
        return session
    
    async def get_session(self, session_id: str) -> Optional[SessionContext]:
        """Get existing session by ID"""
        return self.active_sessions.get(session_id)
    
    async def execute_request(self, session_id: str, 
                            request_func: Callable,
                            *args, **kwargs) -> Any:
        """Execute request in session context with resource monitoring"""
        
        session = self.active_sessions.get(session_id)
        if not session:
            raise SessionError(f"Session {session_id} not found")
        
        if not session.can_accept_request():
            raise ResourceError(f"Session {session_id} cannot accept new requests")
        
        request_id = str(uuid.uuid4())
        
        with self.session_locks[session_id]:
            session.active_requests.add(request_id)
        
        try:
            start_time = time.time()
            
            # Execute request with resource monitoring
            if asyncio.iscoroutinefunction(request_func):
                result = await request_func(*args, **kwargs)
            else:
                result = await asyncio.get_event_loop().run_in_executor(
                    self.executor, request_func, *args, **kwargs
                )
            
            # Update session metrics
            execution_time = time.time() - start_time
            session.metrics.requests_processed += 1
            session.metrics.total_response_time += execution_time
            session.metrics.last_activity = datetime.now()
            
            # Update memory peak
            current_memory = session.get_memory_usage()
            if current_memory > session.metrics.memory_usage_peak_mb:
                session.metrics.memory_usage_peak_mb = current_memory
            
            return result
            
        except Exception as e:
            session.metrics.error_count += 1
            logger.error(f"Request execution failed in session {session_id}: {e}")
            raise
        
        finally:
            with self.session_locks[session_id]:
                session.active_requests.discard(request_id)
    
    async def migrate_session(self, session_id: str, target_instance: str) -> bool:
        """Migrate session to target instance"""
        session = self.active_sessions.get(session_id)
        if not session:
            return False
        
        return await self.session_migrator.migrate_session(session, target_instance)
    
    async def close_session(self, session_id: str, cleanup: bool = True):
        """Close and cleanup session"""
        session = self.active_sessions.get(session_id)
        if not session:
            return
        
        with self.session_locks[session_id]:
            # Wait for active requests to complete
            while session.active_requests:
                await asyncio.sleep(0.1)
            
            # Remove from active sessions
            del self.active_sessions[session_id]
            
            # Return to pool or cleanup
            if cleanup and session.config.auto_cleanup:
                self.session_pool.return_session(session)
        
        # Clean up lock
        if session_id in self.session_locks:
            del self.session_locks[session_id]
        
        logger.info(f"Closed session {session_id}")
    
    def get_session_metrics(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get comprehensive session metrics"""
        session = self.active_sessions.get(session_id)
        if not session:
            return None
        
        return {
            'session_id': session_id,
            'user_id': session.config.user_id,
            'priority': session.config.priority,
            'uptime_hours': session.metrics.uptime_hours,
            'requests_processed': session.metrics.requests_processed,
            'avg_response_time': session.metrics.avg_response_time,
            'memory_usage_mb': session.get_memory_usage(),
            'memory_peak_mb': session.metrics.memory_usage_peak_mb,
            'cache_hit_rate': session.metrics.cache_hit_rate,
            'error_count': session.metrics.error_count,
            'active_requests': len(session.active_requests),
            'is_migrating': session.is_migrating
        }
    
    def get_orchestrator_status(self) -> Dict[str, Any]:
        """Get comprehensive orchestrator status"""
        pool_stats = self.session_pool.get_pool_stats()
        global_stats = self.global_resource_monitor.get_stats()
        
        active_sessions_by_priority = defaultdict(int)
        for session in self.active_sessions.values():
            active_sessions_by_priority[session.config.priority] += 1
        
        return {
            'active_sessions': len(self.active_sessions),
            'pool_stats': pool_stats,
            'sessions_by_priority': dict(active_sessions_by_priority),
            'global_resource_stats': global_stats,
            'instance_stats': self.load_balancer.instance_stats,
            'maintenance_active': self.maintenance_active
        }
    
    def _maintenance_worker(self):
        """Background maintenance tasks"""
        while self.maintenance_active:
            try:
                # Clean up expired sessions
                expired_sessions = []
                current_time = datetime.now()
                
                for session_id, session in list(self.active_sessions.items()):
                    # Check for session timeout
                    max_duration = timedelta(
                        hours=session.config.resource_limits.max_session_duration_hours
                    )
                    
                    if (current_time - session.metrics.created_at > max_duration or
                        current_time - session.metrics.last_activity > timedelta(hours=2)):
                        expired_sessions.append(session_id)
                
                # Close expired sessions
                for session_id in expired_sessions:
                    asyncio.create_task(self.close_session(session_id))
                
                # Clean up individual sessions
                for session in self.active_sessions.values():
                    session.cleanup_expired_data()
                
                # Update global resource stats
                self.global_resource_monitor.update_stats()
                
                # Sleep for 5 minutes
                time.sleep(300)
                
            except Exception as e:
                logger.error(f"Maintenance worker error: {e}")
                time.sleep(60)  # Shorter sleep on error
    
    def shutdown(self):
        """Graceful shutdown"""
        self.maintenance_active = False
        
        # Close all active sessions
        for session_id in list(self.active_sessions.keys()):
            asyncio.create_task(self.close_session(session_id))
        
        # Shutdown executor
        self.executor.shutdown(wait=True)


class GlobalResourceMonitor:
    """Monitor global system resources"""
    
    def __init__(self):
        self.max_memory_percent = 80.0
        self.max_cpu_percent = 75.0
        self.stats = {}
        
    def can_create_session(self) -> bool:
        """Check if system can handle new session"""
        memory_percent = psutil.virtual_memory().percent
        cpu_percent = psutil.cpu_percent(interval=1)
        
        return (memory_percent < self.max_memory_percent and 
                cpu_percent < self.max_cpu_percent)
    
    def update_stats(self):
        """Update global resource statistics"""
        self.stats = {
            'memory_percent': psutil.virtual_memory().percent,
            'cpu_percent': psutil.cpu_percent(),
            'disk_usage_percent': psutil.disk_usage('/').percent,
            'load_average': psutil.getloadavg()[0] if hasattr(psutil, 'getloadavg') else 0,
            'timestamp': datetime.now().isoformat()
        }
    
    def get_stats(self) -> Dict[str, Any]:
        """Get current global resource statistics"""
        return self.stats


# Exception classes
class SessionError(Exception):
    """Session-related errors"""
    pass


class ResourceError(Exception):
    """Resource-related errors"""
    pass


# Factory function
def create_session_orchestrator(config: Dict[str, Any] = None) -> MultiSessionOrchestrator:
    """
    🌸 Springfield: "Create production-ready session orchestrator"
    """
    default_config = {
        'min_pool_size': 5,
        'max_pool_size': 50,
        'max_workers': 20,
        'instances': ['local'],
        'load_strategy': 'least_connections'
    }
    
    final_config = {**default_config, **(config or {})}
    return MultiSessionOrchestrator(final_config)


if __name__ == "__main__":
    async def example_usage():
        """Example usage of session orchestrator"""
        orchestrator = create_session_orchestrator()
        
        # Create a session
        session = await orchestrator.create_session("user123")
        
        # Execute a request
        async def example_request():
            await asyncio.sleep(0.1)  # Simulate work
            return "Hello from session!"
        
        result = await orchestrator.execute_request(
            session.config.session_id,
            example_request
        )
        
        print(f"Result: {result}")
        
        # Get session metrics
        metrics = orchestrator.get_session_metrics(session.config.session_id)
        print(f"Session metrics: {json.dumps(metrics, indent=2)}")
        
        # Close session
        await orchestrator.close_session(session.config.session_id)
        
        # Get orchestrator status
        status = orchestrator.get_orchestrator_status()
        print(f"Orchestrator status: {json.dumps(status, indent=2)}")
        
        orchestrator.shutdown()
    
    # Run example
    asyncio.run(example_usage())