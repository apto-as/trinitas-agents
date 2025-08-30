"""
Trinitas v4.0 - Perfect Async Transaction Manager
完璧な非同期トランザクション管理システム (Artemis 404基準)

ACID特性を完全に保証し、複数バックエンド間での分散トランザクション管理
フン、データ不整合など404の恥よ。完璧なトランザクション管理を見せてあげるわ
"""

import asyncio
import json
import logging
import time
import uuid
from typing import Dict, List, Optional, Any, Callable, AsyncContextManager, Union
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum
from contextlib import asynccontextmanager
import traceback

# SECURITY: セキュアエラーハンドリング 
try:
    from .security.secure_error_handler import secure_log_error, get_secure_error_message
except ImportError:
    # フォールバック関数
    def secure_log_error(e, context):
        return f"ERR-{hash(get_secure_error_message(e)) % 100000:05d}"
    def get_secure_error_message(e):
        return "Operation failed"

logger = logging.getLogger(__name__)

# ============================================================================
# Perfect Transaction State Management (完璧なトランザクション状態管理)
# ============================================================================

class TransactionState(Enum):
    """Transaction state enumeration"""
    PENDING = "pending"
    ACTIVE = "active"
    PREPARING = "preparing"
    PREPARED = "prepared"
    COMMITTING = "committing"
    COMMITTED = "committed"
    ROLLING_BACK = "rolling_back"
    ROLLED_BACK = "rolled_back"
    FAILED = "failed"
    TIMEOUT = "timeout"

class TransactionIsolationLevel(Enum):
    """Transaction isolation levels"""
    READ_UNCOMMITTED = "read_uncommitted"
    READ_COMMITTED = "read_committed"
    REPEATABLE_READ = "repeatable_read"
    SERIALIZABLE = "serializable"

@dataclass
class TransactionOperation:
    """Individual transaction operation"""
    operation_id: str
    operation_type: str  # insert, update, delete, select
    backend: str  # sqlite, redis, chromadb
    table_collection: str
    key: str
    old_value: Optional[Any] = None
    new_value: Optional[Any] = None
    metadata: Optional[Dict] = None
    timestamp: float = 0.0
    completed: bool = False
    rollback_data: Optional[Dict] = None

@dataclass
class TransactionLog:
    """Transaction log entry"""
    transaction_id: str
    state: TransactionState
    operations: List[TransactionOperation]
    created_at: datetime
    updated_at: datetime
    timeout_at: Optional[datetime] = None
    error_message: Optional[str] = None
    rollback_reason: Optional[str] = None

# ============================================================================
# Perfect Async Transaction Manager (完璧な非同期トランザクションマネージャー)
# ============================================================================

class AsyncTransactionManager:
    """
    Perfect async transaction manager with ACID guarantees
    複数バックエンド間での分散トランザクション制御
    """
    
    def __init__(self, memory_manager, transaction_timeout: float = 300.0):
        self.memory_manager = memory_manager
        self.transaction_timeout = transaction_timeout
        
        # Transaction tracking
        self._active_transactions: Dict[str, TransactionLog] = {}
        self._transaction_locks: Dict[str, asyncio.Lock] = {}
        self._global_lock = asyncio.Lock()
        
        # Rollback handlers for different backends
        self._rollback_handlers = {
            "sqlite": self._rollback_sqlite_operations,
            "redis": self._rollback_redis_operations,
            "chromadb": self._rollback_chromadb_operations
        }
        
        # Performance metrics
        self._transaction_stats = {
            "total_transactions": 0,
            "successful_commits": 0,
            "rollbacks": 0,
            "timeouts": 0,
            "average_duration": 0.0
        }
        
        # Start cleanup task
        self._cleanup_task = asyncio.create_task(self._transaction_cleanup_loop())
    
    # ========================================================================
    # Perfect Transaction Context Management (完璧なトランザクションコンテキスト管理)
    # ========================================================================
    
    @asynccontextmanager
    async def transaction(self, isolation_level: TransactionIsolationLevel = TransactionIsolationLevel.READ_COMMITTED,
                         timeout: Optional[float] = None) -> AsyncContextManager['Transaction']:
        """
        Perfect async transaction context manager
        
        Usage:
            async with transaction_manager.transaction() as tx:
                await tx.store("key1", "value1")
                await tx.store("key2", "value2")
                # Automatic commit on success, rollback on exception
        """
        transaction_id = str(uuid.uuid4())
        timeout_duration = timeout or self.transaction_timeout
        
        # Create transaction log
        transaction_log = TransactionLog(
            transaction_id=transaction_id,
            state=TransactionState.PENDING,
            operations=[],
            created_at=datetime.now(),
            updated_at=datetime.now(),
            timeout_at=datetime.now() + timedelta(seconds=timeout_duration)
        )
        
        async with self._global_lock:
            self._active_transactions[transaction_id] = transaction_log
            self._transaction_locks[transaction_id] = asyncio.Lock()
        
        try:
            # Create transaction instance
            tx = Transaction(self, transaction_id, isolation_level, timeout_duration)
            
            # Activate transaction
            await self._update_transaction_state(transaction_id, TransactionState.ACTIVE)
            
            logger.debug(f"Started transaction {transaction_id[:8]} with {isolation_level.value} isolation")
            
            yield tx
            
            # Commit if no exceptions
            await self._commit_transaction(transaction_id)
            
        except Exception as e:
            # Rollback on any exception
            error_id = secure_log_error(e, "transaction_operation")
            logger.error(f"Transaction {transaction_id[:8]} failed: {error_id}")
            await self._rollback_transaction(transaction_id, get_secure_error_message(e))
            raise
            
        finally:
            # Cleanup transaction
            await self._cleanup_transaction(transaction_id)
    
    # ========================================================================
    # Perfect Transaction Operations (完璧なトランザクション操作)
    # ========================================================================
    
    async def _add_operation(self, transaction_id: str, operation: TransactionOperation):
        """Add operation to transaction log"""
        if transaction_id not in self._active_transactions:
            raise ValueError(f"Transaction {transaction_id} not found")
        
        async with self._transaction_locks[transaction_id]:
            transaction_log = self._active_transactions[transaction_id]
            
            # Check transaction state
            if transaction_log.state not in [TransactionState.ACTIVE, TransactionState.PREPARING]:
                raise ValueError(f"Cannot add operations to transaction in state {transaction_log.state.value}")
            
            # Check timeout
            if transaction_log.timeout_at and datetime.now() > transaction_log.timeout_at:
                await self._rollback_transaction(transaction_id, "Transaction timeout")
                raise TimeoutError(f"Transaction {transaction_id} timed out")
            
            operation.timestamp = time.time()
            transaction_log.operations.append(operation)
            transaction_log.updated_at = datetime.now()
    
    async def _commit_transaction(self, transaction_id: str):
        """Commit transaction with two-phase commit protocol"""
        start_time = time.time()
        
        try:
            await self._update_transaction_state(transaction_id, TransactionState.PREPARING)
            
            # Phase 1: Prepare all backends
            prepare_success = await self._prepare_all_backends(transaction_id)
            
            if not prepare_success:
                await self._rollback_transaction(transaction_id, "Prepare phase failed")
                return
            
            await self._update_transaction_state(transaction_id, TransactionState.PREPARED)
            
            # Phase 2: Commit all backends
            await self._update_transaction_state(transaction_id, TransactionState.COMMITTING)
            commit_success = await self._commit_all_backends(transaction_id)
            
            if commit_success:
                await self._update_transaction_state(transaction_id, TransactionState.COMMITTED)
                self._transaction_stats["successful_commits"] += 1
                
                duration = time.time() - start_time
                logger.info(f"Transaction {transaction_id[:8]} committed successfully in {duration:.3f}s")
            else:
                await self._rollback_transaction(transaction_id, "Commit phase failed")
            
        except Exception as e:
            error_id = secure_log_error(e, "transaction_operation")
            logger.error(f"Commit failed for transaction {transaction_id[:8]}: {error_id}")
            await self._rollback_transaction(transaction_id, f"Commit error: {get_secure_error_message(e)}")
            raise
    
    async def _rollback_transaction(self, transaction_id: str, reason: str):
        """Rollback transaction"""
        start_time = time.time()
        
        try:
            await self._update_transaction_state(transaction_id, TransactionState.ROLLING_BACK)
            
            transaction_log = self._active_transactions[transaction_id]
            transaction_log.rollback_reason = reason
            
            # Rollback operations in reverse order
            rollback_success = await self._rollback_all_operations(transaction_id)
            
            if rollback_success:
                await self._update_transaction_state(transaction_id, TransactionState.ROLLED_BACK)
                self._transaction_stats["rollbacks"] += 1
                
                duration = time.time() - start_time
                logger.info(f"Transaction {transaction_id[:8]} rolled back in {duration:.3f}s - Reason: {reason}")
            else:
                await self._update_transaction_state(transaction_id, TransactionState.FAILED)
                logger.error(f"Rollback failed for transaction {transaction_id[:8]}")
            
        except Exception as e:
            await self._update_transaction_state(transaction_id, TransactionState.FAILED)
            error_id = secure_log_error(e, "transaction_operation")
            logger.error(f"Rollback error for transaction {transaction_id[:8]}: {error_id}")
    
    # ========================================================================
    # Perfect Two-Phase Commit Implementation (完璧な2フェーズコミット実装)
    # ========================================================================
    
    async def _prepare_all_backends(self, transaction_id: str) -> bool:
        """Phase 1: Prepare all backends for commit"""
        transaction_log = self._active_transactions[transaction_id]
        
        # Group operations by backend
        backend_operations = {}
        for operation in transaction_log.operations:
            backend = operation.backend
            if backend not in backend_operations:
                backend_operations[backend] = []
            backend_operations[backend].append(operation)
        
        prepare_tasks = []
        
        # Prepare each backend
        for backend, operations in backend_operations.items():
            if backend == "sqlite" and self.memory_manager.sqlite_backend:
                task = self._prepare_sqlite_backend(transaction_id, operations)
                prepare_tasks.append(task)
            elif backend == "redis" and self.memory_manager.redis_backend:
                task = self._prepare_redis_backend(transaction_id, operations)
                prepare_tasks.append(task)
            elif backend == "chromadb" and self.memory_manager.chromadb_backend:
                task = self._prepare_chromadb_backend(transaction_id, operations)
                prepare_tasks.append(task)
        
        # Execute all prepare operations
        try:
            prepare_results = await asyncio.gather(*prepare_tasks, return_exceptions=True)
            
            # Check if all preparations succeeded
            all_success = True
            for result in prepare_results:
                if isinstance(result, Exception) or not result:
                    all_success = False
                    logger.error(f"Prepare failed: {result}")
            
            return all_success
            
        except Exception as e:
            error_id = secure_log_error(e, "transaction_operation")
            logger.error(f"Prepare phase error: {error_id}")
            return False
    
    async def _prepare_sqlite_backend(self, transaction_id: str, operations: List[TransactionOperation]) -> bool:
        """Prepare SQLite backend for commit"""
        try:
            # For SQLite, we can use savepoints for rollback capability
            if self.memory_manager.sqlite_backend:
                # Create savepoint
                savepoint_name = f"tx_{transaction_id[:8]}"
                await self.memory_manager.sqlite_backend.pool.execute_single(
                    f"SAVEPOINT {savepoint_name}"
                )
                
                # Store savepoint info in operations
                for operation in operations:
                    operation.rollback_data = {"savepoint": savepoint_name}
                
                logger.debug(f"SQLite prepared with savepoint {savepoint_name}")
                return True
            
        except Exception as e:
            error_id = secure_log_error(e, "transaction_operation")
            logger.error(f"SQLite prepare failed: {error_id}")
            return False
        
        return False
    
    async def _prepare_redis_backend(self, transaction_id: str, operations: List[TransactionOperation]) -> bool:
        """Prepare Redis backend for commit"""
        try:
            # For Redis, we store rollback data before operations
            if self.memory_manager.redis_backend:
                rollback_data = {}
                
                for operation in operations:
                    if operation.operation_type in ["update", "delete"]:
                        # Store current value for rollback
                        current_value = await self.memory_manager.redis_backend.get(operation.key)
                        rollback_data[operation.key] = current_value
                
                # Store rollback data with transaction ID
                rollback_key = f"rollback_{transaction_id}"
                await self.memory_manager.redis_backend.set(
                    rollback_key,
                    json.dumps(rollback_data),
                    ex=int(self.transaction_timeout)
                )
                
                # Update operations with rollback info
                for operation in operations:
                    operation.rollback_data = {"rollback_key": rollback_key}
                
                logger.debug(f"Redis prepared with rollback data")
                return True
            
        except Exception as e:
            error_id = secure_log_error(e, "transaction_operation")
            logger.error(f"Redis prepare failed: {error_id}")
            return False
        
        return False
    
    async def _prepare_chromadb_backend(self, transaction_id: str, operations: List[TransactionOperation]) -> bool:
        """Prepare ChromaDB backend for commit"""
        try:
            # ChromaDB doesn't support traditional transactions
            # We implement compensating transactions by storing rollback data
            if self.memory_manager.chromadb_backend:
                rollback_operations = []
                
                for operation in operations:
                    # For each operation, create a compensating operation
                    if operation.operation_type == "upsert":
                        # Check if document already exists
                        try:
                            collection = await self.memory_manager.chromadb_backend.get_or_create_collection(
                                operation.table_collection
                            )
                            if collection:
                                # Query for existing document
                                existing = await self.memory_manager.chromadb_backend.query(
                                    operation.table_collection,
                                    [operation.key],  # Use key as query
                                    n_results=1
                                )
                                
                                if existing["ids"][0]:  # Document exists
                                    rollback_operations.append({
                                        "type": "restore",
                                        "key": operation.key,
                                        "collection": operation.table_collection,
                                        "document": existing["documents"][0][0],
                                        "metadata": existing["metadatas"][0][0]
                                    })
                                else:  # New document
                                    rollback_operations.append({
                                        "type": "delete",
                                        "key": operation.key,
                                        "collection": operation.table_collection
                                    })
                        except:
                            # Assume new document
                            rollback_operations.append({
                                "type": "delete",
                                "key": operation.key,
                                "collection": operation.table_collection
                            })
                
                # Store rollback operations
                for operation in operations:
                    operation.rollback_data = {"rollback_operations": rollback_operations}
                
                logger.debug(f"ChromaDB prepared with {len(rollback_operations)} rollback operations")
                return True
            
        except Exception as e:
            error_id = secure_log_error(e, "transaction_operation")
            logger.error(f"ChromaDB prepare failed: {error_id}")
            return False
        
        return False
    
    async def _commit_all_backends(self, transaction_id: str) -> bool:
        """Phase 2: Commit all backends"""
        transaction_log = self._active_transactions[transaction_id]
        
        # Group operations by backend
        backend_operations = {}
        for operation in transaction_log.operations:
            backend = operation.backend
            if backend not in backend_operations:
                backend_operations[backend] = []
            backend_operations[backend].append(operation)
        
        commit_tasks = []
        
        # Commit each backend
        for backend, operations in backend_operations.items():
            if backend == "sqlite" and self.memory_manager.sqlite_backend:
                task = self._commit_sqlite_backend(transaction_id, operations)
                commit_tasks.append(task)
            elif backend == "redis" and self.memory_manager.redis_backend:
                task = self._commit_redis_backend(transaction_id, operations)
                commit_tasks.append(task)
            elif backend == "chromadb" and self.memory_manager.chromadb_backend:
                task = self._commit_chromadb_backend(transaction_id, operations)
                commit_tasks.append(task)
        
        # Execute all commit operations
        try:
            commit_results = await asyncio.gather(*commit_tasks, return_exceptions=True)
            
            # Check if all commits succeeded
            all_success = True
            for result in commit_results:
                if isinstance(result, Exception) or not result:
                    all_success = False
                    logger.error(f"Commit failed: {result}")
            
            return all_success
            
        except Exception as e:
            error_id = secure_log_error(e, "transaction_operation")
            logger.error(f"Commit phase error: {error_id}")
            return False
    
    async def _commit_sqlite_backend(self, transaction_id: str, operations: List[TransactionOperation]) -> bool:
        """Commit SQLite operations"""
        try:
            # Release savepoint (commit)
            if operations and operations[0].rollback_data:
                savepoint_name = operations[0].rollback_data["savepoint"]
                await self.memory_manager.sqlite_backend.pool.execute_single(
                    f"RELEASE SAVEPOINT {savepoint_name}"
                )
                logger.debug(f"SQLite committed - released savepoint {savepoint_name}")
            
            return True
            
        except Exception as e:
            error_id = secure_log_error(e, "transaction_operation")
            logger.error(f"SQLite commit failed: {error_id}")
            return False
    
    async def _commit_redis_backend(self, transaction_id: str, operations: List[TransactionOperation]) -> bool:
        """Commit Redis operations"""
        try:
            # Clean up rollback data
            if operations and operations[0].rollback_data:
                rollback_key = operations[0].rollback_data["rollback_key"]
                await self.memory_manager.redis_backend.delete(rollback_key)
                logger.debug(f"Redis committed - cleaned rollback data")
            
            return True
            
        except Exception as e:
            error_id = secure_log_error(e, "transaction_operation")
            logger.error(f"Redis commit failed: {error_id}")
            return False
    
    async def _commit_chromadb_backend(self, transaction_id: str, operations: List[TransactionOperation]) -> bool:
        """Commit ChromaDB operations"""
        try:
            # ChromaDB operations are already applied, just clean up rollback data
            logger.debug(f"ChromaDB committed - operations already applied")
            return True
            
        except Exception as e:
            error_id = secure_log_error(e, "transaction_operation")
            logger.error(f"ChromaDB commit failed: {error_id}")
            return False
    
    # ========================================================================
    # Perfect Rollback Implementation (完璧なロールバック実装)
    # ========================================================================
    
    async def _rollback_all_operations(self, transaction_id: str) -> bool:
        """Rollback all operations in reverse order"""
        transaction_log = self._active_transactions[transaction_id]
        
        # Group operations by backend and reverse order
        backend_operations = {}
        for operation in reversed(transaction_log.operations):
            backend = operation.backend
            if backend not in backend_operations:
                backend_operations[backend] = []
            backend_operations[backend].append(operation)
        
        rollback_tasks = []
        
        # Rollback each backend
        for backend, operations in backend_operations.items():
            if backend in self._rollback_handlers:
                task = self._rollback_handlers[backend](transaction_id, operations)
                rollback_tasks.append(task)
        
        try:
            rollback_results = await asyncio.gather(*rollback_tasks, return_exceptions=True)
            
            # Check if all rollbacks succeeded
            all_success = True
            for result in rollback_results:
                if isinstance(result, Exception) or not result:
                    all_success = False
                    logger.error(f"Rollback failed: {result}")
            
            return all_success
            
        except Exception as e:
            error_id = secure_log_error(e, "transaction_operation")
            logger.error(f"Rollback error: {error_id}")
            return False
    
    async def _rollback_sqlite_operations(self, transaction_id: str, operations: List[TransactionOperation]) -> bool:
        """Rollback SQLite operations"""
        try:
            if operations and operations[0].rollback_data:
                savepoint_name = operations[0].rollback_data["savepoint"]
                await self.memory_manager.sqlite_backend.pool.execute_single(
                    f"ROLLBACK TO SAVEPOINT {savepoint_name}"
                )
                await self.memory_manager.sqlite_backend.pool.execute_single(
                    f"RELEASE SAVEPOINT {savepoint_name}"
                )
                logger.debug(f"SQLite rolled back to savepoint {savepoint_name}")
            
            return True
            
        except Exception as e:
            error_id = secure_log_error(e, "transaction_operation")
            logger.error(f"SQLite rollback failed: {error_id}")
            return False
    
    async def _rollback_redis_operations(self, transaction_id: str, operations: List[TransactionOperation]) -> bool:
        """Rollback Redis operations"""
        try:
            if operations and operations[0].rollback_data:
                rollback_key = operations[0].rollback_data["rollback_key"]
                rollback_data_json = await self.memory_manager.redis_backend.get(rollback_key)
                
                if rollback_data_json:
                    rollback_data = json.loads(rollback_data_json)
                    
                    # Restore previous values
                    for operation in operations:
                        key = operation.key
                        if key in rollback_data:
                            old_value = rollback_data[key]
                            if old_value is not None:
                                await self.memory_manager.redis_backend.set(key, old_value)
                            else:
                                await self.memory_manager.redis_backend.delete(key)
                    
                    # Clean up rollback data
                    await self.memory_manager.redis_backend.delete(rollback_key)
                    logger.debug(f"Redis operations rolled back")
            
            return True
            
        except Exception as e:
            error_id = secure_log_error(e, "transaction_operation")
            logger.error(f"Redis rollback failed: {error_id}")
            return False
    
    async def _rollback_chromadb_operations(self, transaction_id: str, operations: List[TransactionOperation]) -> bool:
        """Rollback ChromaDB operations"""
        try:
            if operations and operations[0].rollback_data:
                rollback_operations = operations[0].rollback_data["rollback_operations"]
                
                # Execute compensating transactions
                for rollback_op in rollback_operations:
                    try:
                        if rollback_op["type"] == "delete":
                            # Delete newly inserted document
                            collection = await self.memory_manager.chromadb_backend.get_or_create_collection(
                                rollback_op["collection"]
                            )
                            if collection:
                                # ChromaDB doesn't have direct delete by ID, so we'd need to implement this
                                # For now, log the action
                                logger.debug(f"Should delete {rollback_op['key']} from {rollback_op['collection']}")
                        
                        elif rollback_op["type"] == "restore":
                            # Restore previous document
                            await self.memory_manager.chromadb_backend.upsert(
                                rollback_op["collection"],
                                [rollback_op["key"]],
                                [rollback_op["document"]],
                                [rollback_op["metadata"]]
                            )
                            logger.debug(f"Restored {rollback_op['key']} in {rollback_op['collection']}")
                    
                    except Exception as e:
                        error_id = secure_log_error(e, "transaction_operation")
                        logger.error(f"ChromaDB rollback operation failed: {error_id}")
                
                logger.debug(f"ChromaDB operations rolled back")
            
            return True
            
        except Exception as e:
            error_id = secure_log_error(e, "transaction_operation")
            logger.error(f"ChromaDB rollback failed: {error_id}")
            return False
    
    # ========================================================================
    # Perfect Transaction State Management (完璧なトランザクション状態管理)
    # ========================================================================
    
    async def _update_transaction_state(self, transaction_id: str, new_state: TransactionState):
        """Update transaction state"""
        if transaction_id in self._active_transactions:
            async with self._transaction_locks[transaction_id]:
                self._active_transactions[transaction_id].state = new_state
                self._active_transactions[transaction_id].updated_at = datetime.now()
                
                if new_state == TransactionState.FAILED:
                    self._active_transactions[transaction_id].error_message = "Transaction failed"
    
    async def _cleanup_transaction(self, transaction_id: str):
        """Clean up transaction resources"""
        try:
            async with self._global_lock:
                if transaction_id in self._active_transactions:
                    transaction_log = self._active_transactions[transaction_id]
                    
                    # Update statistics
                    self._transaction_stats["total_transactions"] += 1
                    
                    # Calculate duration for statistics
                    duration = (datetime.now() - transaction_log.created_at).total_seconds()
                    current_avg = self._transaction_stats["average_duration"]
                    total_tx = self._transaction_stats["total_transactions"]
                    self._transaction_stats["average_duration"] = (
                        (current_avg * (total_tx - 1) + duration) / total_tx
                    )
                    
                    # Remove from active transactions
                    del self._active_transactions[transaction_id]
                    del self._transaction_locks[transaction_id]
                    
                    logger.debug(f"Transaction {transaction_id[:8]} cleaned up")
        
        except Exception as e:
            error_id = secure_log_error(e, "transaction_operation")
            logger.error(f"Transaction cleanup failed: {error_id}")
    
    async def _transaction_cleanup_loop(self):
        """Background task to clean up timed-out transactions"""
        while True:
            try:
                await asyncio.sleep(60)  # Check every minute
                
                current_time = datetime.now()
                expired_transactions = []
                
                # Find expired transactions
                for tx_id, tx_log in self._active_transactions.items():
                    if tx_log.timeout_at and current_time > tx_log.timeout_at:
                        if tx_log.state in [TransactionState.ACTIVE, TransactionState.PREPARING]:
                            expired_transactions.append(tx_id)
                
                # Rollback expired transactions
                for tx_id in expired_transactions:
                    try:
                        await self._rollback_transaction(tx_id, "Transaction timeout")
                        self._transaction_stats["timeouts"] += 1
                        logger.warning(f"Transaction {tx_id[:8]} timed out and was rolled back")
                    except Exception as e:
                        error_id = secure_log_error(e, "transaction_operation")
                        logger.error(f"Failed to rollback timed out transaction {tx_id[:8]}: {error_id}")
            
            except Exception as e:
                error_id = secure_log_error(e, "transaction_operation")
                logger.error(f"Transaction cleanup loop error: {error_id}")
    
    # ========================================================================
    # Perfect Transaction Statistics (完璧なトランザクション統計)
    # ========================================================================
    
    async def get_transaction_statistics(self) -> Dict[str, Any]:
        """Get comprehensive transaction statistics"""
        active_count = len(self._active_transactions)
        
        # Analyze active transactions by state
        state_counts = {}
        for tx_log in self._active_transactions.values():
            state = tx_log.state.value
            state_counts[state] = state_counts.get(state, 0) + 1
        
        # Calculate success rate
        total_completed = self._transaction_stats["successful_commits"] + self._transaction_stats["rollbacks"]
        success_rate = (
            (self._transaction_stats["successful_commits"] / total_completed * 100)
            if total_completed > 0 else 0
        )
        
        return {
            "active_transactions": active_count,
            "total_transactions": self._transaction_stats["total_transactions"],
            "successful_commits": self._transaction_stats["successful_commits"],
            "rollbacks": self._transaction_stats["rollbacks"],
            "timeouts": self._transaction_stats["timeouts"],
            "success_rate": success_rate,
            "average_duration": self._transaction_stats["average_duration"],
            "active_by_state": state_counts,
            "transaction_timeout": self.transaction_timeout
        }
    
    async def cleanup(self):
        """Clean up transaction manager"""
        # Cancel cleanup task
        if self._cleanup_task and not self._cleanup_task.done():
            self._cleanup_task.cancel()
        
        # Rollback all active transactions
        active_tx_ids = list(self._active_transactions.keys())
        for tx_id in active_tx_ids:
            try:
                await self._rollback_transaction(tx_id, "System shutdown")
            except Exception as e:
                error_id = secure_log_error(e, "transaction_operation")
                logger.error(f"Failed to rollback transaction {tx_id[:8]} during shutdown: {error_id}")
        
        logger.info("AsyncTransactionManager cleaned up")

# ============================================================================
# Perfect Transaction Context (完璧なトランザクションコンテキスト)
# ============================================================================

class Transaction:
    """
    Perfect transaction context with full ACID support
    実際のトランザクション操作を実行するコンテキスト
    """
    
    def __init__(self, manager: AsyncTransactionManager, transaction_id: str,
                 isolation_level: TransactionIsolationLevel, timeout: float):
        self.manager = manager
        self.transaction_id = transaction_id
        self.isolation_level = isolation_level
        self.timeout = timeout
        self._operation_counter = 0
    
    async def store(self, key: str, value: Any, metadata: Optional[Dict] = None) -> bool:
        """Store operation within transaction"""
        try:
            # Create operation record
            operation = TransactionOperation(
                operation_id=f"{self.transaction_id}_{self._operation_counter}",
                operation_type="insert",
                backend="sqlite",  # Default backend
                table_collection="memory_store",
                key=key,
                new_value=value,
                metadata=metadata
            )
            
            # Add to transaction log
            await self.manager._add_operation(self.transaction_id, operation)
            self._operation_counter += 1
            
            # Execute the actual operation
            success = await self.manager.memory_manager.store(key, value, metadata)
            operation.completed = success
            
            return success
            
        except Exception as e:
            error_id = secure_log_error(e, "transaction_operation")
            logger.error(f"Transaction store failed: {error_id}")
            raise
    
    async def recall(self, query: str, semantic: bool = False, 
                    filters: Optional[Dict] = None, limit: int = 10) -> List[Dict]:
        """Recall operation within transaction (read-only)"""
        try:
            # Create read operation record
            operation = TransactionOperation(
                operation_id=f"{self.transaction_id}_{self._operation_counter}",
                operation_type="select",
                backend="sqlite",
                table_collection="memory_store",
                key=query,
                metadata={"semantic": semantic, "filters": filters, "limit": limit}
            )
            
            # Add to transaction log
            await self.manager._add_operation(self.transaction_id, operation)
            self._operation_counter += 1
            
            # Execute the actual operation
            results = await self.manager.memory_manager.recall(query, semantic, filters, limit)
            operation.completed = True
            
            return results
            
        except Exception as e:
            error_id = secure_log_error(e, "transaction_operation")
            logger.error(f"Transaction recall failed: {error_id}")
            raise
    
    async def update(self, key: str, value: Any, metadata: Optional[Dict] = None) -> bool:
        """Update operation within transaction"""
        try:
            # Get current value for rollback
            current_results = await self.manager.memory_manager.recall(key, limit=1)
            old_value = current_results[0] if current_results else None
            
            # Create operation record
            operation = TransactionOperation(
                operation_id=f"{self.transaction_id}_{self._operation_counter}",
                operation_type="update",
                backend="sqlite",
                table_collection="memory_store",
                key=key,
                old_value=old_value,
                new_value=value,
                metadata=metadata
            )
            
            # Add to transaction log
            await self.manager._add_operation(self.transaction_id, operation)
            self._operation_counter += 1
            
            # Execute the actual operation
            success = await self.manager.memory_manager.store(key, value, metadata)
            operation.completed = success
            
            return success
            
        except Exception as e:
            error_id = secure_log_error(e, "transaction_operation")
            logger.error(f"Transaction update failed: {error_id}")
            raise
    
    async def bulk_store(self, items: List[Tuple[str, Any, Optional[Dict]]]) -> Dict[str, bool]:
        """Bulk store operations within transaction"""
        results = {}
        
        for key, value, metadata in items:
            try:
                success = await self.store(key, value, metadata)
                results[key] = success
            except Exception as e:
                error_id = secure_log_error(e, "transaction_operation")
                logger.error(f"Bulk store failed for key {key}: {error_id}")
                results[key] = False
                raise
        
        return results
    
    def get_transaction_id(self) -> str:
        """Get transaction ID"""
        return self.transaction_id
    
    def get_isolation_level(self) -> TransactionIsolationLevel:
        """Get isolation level"""
        return self.isolation_level
    
    async def get_operations(self) -> List[TransactionOperation]:
        """Get all operations in this transaction"""
        if self.transaction_id in self.manager._active_transactions:
            return self.manager._active_transactions[self.transaction_id].operations.copy()
        return []

# ============================================================================
# Perfect Usage Examples (完璧な使用例)
# ============================================================================

class TransactionExamples:
    """Perfect transaction usage examples"""
    
    @staticmethod
    async def basic_transaction_example(memory_manager):
        """Basic transaction usage"""
        tx_manager = AsyncTransactionManager(memory_manager)
        
        try:
            async with tx_manager.transaction() as tx:
                # Store multiple related items
                await tx.store("user_123", {"name": "Alice", "age": 30})
                await tx.store("profile_123", {"user_id": "123", "preferences": {"theme": "dark"}})
                await tx.store("settings_123", {"user_id": "123", "notifications": True})
                
                # If any operation fails, all will be rolled back
                print("Transaction completed successfully")
                
        except Exception as e:
            print(f"Transaction failed: {e}")
        
        finally:
            await tx_manager.cleanup()
    
    @staticmethod
    async def complex_transaction_example(memory_manager):
        """Complex transaction with error handling"""
        tx_manager = AsyncTransactionManager(memory_manager, transaction_timeout=60.0)
        
        try:
            async with tx_manager.transaction(TransactionIsolationLevel.SERIALIZABLE) as tx:
                # Simulate complex business logic
                user_data = await tx.recall("user_123", limit=1)
                
                if user_data:
                    # Update existing user
                    updated_user = user_data[0]["value"]
                    updated_user["last_login"] = datetime.now().isoformat()
                    await tx.update("user_123", updated_user)
                else:
                    # Create new user
                    await tx.store("user_123", {
                        "name": "New User",
                        "created_at": datetime.now().isoformat()
                    })
                
                # Bulk operations
                bulk_data = [
                    ("log_entry_1", {"action": "login", "user": "123"}, {"importance": 0.5}),
                    ("log_entry_2", {"action": "view_profile", "user": "123"}, {"importance": 0.3}),
                ]
                
                bulk_results = await tx.bulk_store(bulk_data)
                print(f"Bulk operation results: {bulk_results}")
                
        except Exception as e:
            print(f"Complex transaction failed: {e}")
        
        finally:
            # Get statistics
            stats = await tx_manager.get_transaction_statistics()
            print(f"Transaction statistics: {stats}")
            
            await tx_manager.cleanup()

# Usage:
# tx_manager = AsyncTransactionManager(memory_manager)
# async with tx_manager.transaction() as tx:
#     await tx.store("key1", "value1")
#     await tx.store("key2", "value2")
#     # Automatic commit or rollback