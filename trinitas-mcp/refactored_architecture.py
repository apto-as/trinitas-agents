"""
Refactored Architecture - Trinitas v4.0 依存関係整理版
インターフェース分離とDependency Injectionによる疎結合実現

Author: Athena - Strategic Architect
Date: 2025-08-30
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional, Protocol, Union, Type
from dataclasses import dataclass, field
from datetime import datetime
import asyncio
import logging
from enum import Enum
from pathlib import Path
import weakref
from contextlib import asynccontextmanager

# ===== DOMAIN INTERFACES (抽象層) =====

class IMemoryManager(Protocol):
    """メモリ管理インターフェース"""
    
    async def store_memory(
        self, 
        content: str, 
        importance: float = 0.5,
        persona: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """メモリを保存"""
        ...
    
    async def recall_memories(
        self,
        query: str,
        limit: int = 10,
        semantic: bool = False,
        persona: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """メモリを検索・取得"""
        ...
    
    async def optimize_memory(self) -> Dict[str, Any]:
        """メモリの最適化"""
        ...

class ITaskDistributor(Protocol):
    """タスク分散インターフェース"""
    
    async def distribute_task(
        self,
        task: str,
        personas: List[str],
        mode: str = "parallel"
    ) -> Dict[str, Any]:
        """タスクを分散実行"""
        ...
    
    async def get_task_status(self, task_id: str) -> Dict[str, Any]:
        """タスクステータス取得"""
        ...

class ILLMClient(Protocol):
    """LLM通信インターフェース"""
    
    async def generate_response(
        self,
        prompt: str,
        model: Optional[str] = None,
        options: Optional[Dict[str, Any]] = None
    ) -> str:
        """LLMレスポンス生成"""
        ...
    
    async def is_available(self) -> bool:
        """LLM利用可能性確認"""
        ...

class IMonitor(Protocol):
    """監視システムインターフェース"""
    
    async def track_performance(self, operation: str, duration: float) -> None:
        """パフォーマンス追跡"""
        ...
    
    async def log_operation(self, operation: str, metadata: Dict[str, Any]) -> None:
        """操作ログ記録"""
        ...
    
    async def get_metrics(self) -> Dict[str, Any]:
        """メトリクス取得"""
        ...

class ILearningSystem(Protocol):
    """学習システムインターフェース"""
    
    async def learn_pattern(
        self,
        pattern_type: str,
        content: str,
        context: Dict[str, Any]
    ) -> None:
        """パターン学習"""
        ...
    
    async def apply_pattern(
        self,
        pattern_type: str,
        context: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """パターン適用"""
        ...

# ===== CONFIGURATION & DEPENDENCY INJECTION =====

@dataclass
class ServiceConfiguration:
    """サービス設定"""
    memory_backend: str = "hybrid"
    redis_url: str = "redis://localhost:6379"
    sqlite_path: str = "./data/trinitas.db"
    chromadb_path: str = "./data/chromadb"
    local_llm_enabled: bool = False
    local_llm_endpoint: str = "http://localhost:1234"
    cache_size: int = 1000
    logging_level: str = "INFO"
    enable_monitoring: bool = True
    enable_learning: bool = True

class ServiceLifetime(Enum):
    """サービスのライフタイム"""
    SINGLETON = "singleton"
    TRANSIENT = "transient"
    SCOPED = "scoped"

@dataclass
class ServiceDescriptor:
    """サービス記述子"""
    interface: Type
    implementation: Type
    lifetime: ServiceLifetime = ServiceLifetime.SINGLETON
    factory: Optional[callable] = None
    dependencies: List[Type] = field(default_factory=list)

class DependencyInjectionContainer:
    """依存関係注入コンテナ"""
    
    def __init__(self, config: ServiceConfiguration):
        self.config = config
        self._services: Dict[Type, ServiceDescriptor] = {}
        self._instances: Dict[Type, Any] = {}
        self._scoped_instances: Dict[Type, Any] = {}
        self._building: set = set()  # 循環依存検出用
        self.logger = logging.getLogger(__name__)
    
    def register_singleton(
        self, 
        interface: Type, 
        implementation: Type,
        factory: Optional[callable] = None
    ) -> 'DependencyInjectionContainer':
        """シングルトンサービス登録"""
        descriptor = ServiceDescriptor(
            interface=interface,
            implementation=implementation,
            lifetime=ServiceLifetime.SINGLETON,
            factory=factory,
            dependencies=self._extract_dependencies(implementation)
        )
        self._services[interface] = descriptor
        return self
    
    def register_transient(
        self, 
        interface: Type, 
        implementation: Type,
        factory: Optional[callable] = None
    ) -> 'DependencyInjectionContainer':
        """一時的サービス登録"""
        descriptor = ServiceDescriptor(
            interface=interface,
            implementation=implementation,
            lifetime=ServiceLifetime.TRANSIENT,
            factory=factory,
            dependencies=self._extract_dependencies(implementation)
        )
        self._services[interface] = descriptor
        return self
    
    def register_scoped(
        self, 
        interface: Type, 
        implementation: Type,
        factory: Optional[callable] = None
    ) -> 'DependencyInjectionContainer':
        """スコープ付きサービス登録"""
        descriptor = ServiceDescriptor(
            interface=interface,
            implementation=implementation,
            lifetime=ServiceLifetime.SCOPED,
            factory=factory,
            dependencies=self._extract_dependencies(implementation)
        )
        self._services[interface] = descriptor
        return self
    
    async def resolve(self, interface: Type) -> Any:
        """サービス解決"""
        if interface in self._building:
            raise ValueError(f"Circular dependency detected for {interface}")
        
        if interface not in self._services:
            raise ValueError(f"Service {interface} not registered")
        
        descriptor = self._services[interface]
        
        # シングルトン
        if descriptor.lifetime == ServiceLifetime.SINGLETON:
            if interface not in self._instances:
                self._building.add(interface)
                try:
                    self._instances[interface] = await self._create_instance(descriptor)
                finally:
                    self._building.discard(interface)
            return self._instances[interface]
        
        # スコープ付き
        elif descriptor.lifetime == ServiceLifetime.SCOPED:
            if interface not in self._scoped_instances:
                self._building.add(interface)
                try:
                    self._scoped_instances[interface] = await self._create_instance(descriptor)
                finally:
                    self._building.discard(interface)
            return self._scoped_instances[interface]
        
        # 一時的
        else:
            self._building.add(interface)
            try:
                return await self._create_instance(descriptor)
            finally:
                self._building.discard(interface)
    
    async def _create_instance(self, descriptor: ServiceDescriptor) -> Any:
        """インスタンス作成"""
        if descriptor.factory:
            return await descriptor.factory(self)
        
        # 依存関係を解決
        dependencies = []
        for dep_type in descriptor.dependencies:
            dep_instance = await self.resolve(dep_type)
            dependencies.append(dep_instance)
        
        # インスタンス作成
        if asyncio.iscoroutinefunction(descriptor.implementation.__init__):
            instance = descriptor.implementation()
            if hasattr(instance, 'initialize'):
                await instance.initialize(*dependencies)
            return instance
        else:
            return descriptor.implementation(*dependencies)
    
    def _extract_dependencies(self, implementation: Type) -> List[Type]:
        """依存関係抽出（簡単な実装）"""
        # 実際にはより高度な解析が必要
        # アノテーションベースまたは設定ベースで依存関係を定義
        return []
    
    @asynccontextmanager
    async def create_scope(self):
        """スコープ作成"""
        old_scoped = self._scoped_instances.copy()
        try:
            yield self
        finally:
            # スコープ終了時にリソースをクリーンアップ
            for instance in self._scoped_instances.values():
                if hasattr(instance, 'dispose'):
                    await instance.dispose()
            self._scoped_instances = old_scoped

# ===== EVENT-DRIVEN ARCHITECTURE =====

class DomainEvent:
    """ドメインイベント基底クラス"""
    
    def __init__(self, event_type: str, payload: Dict[str, Any]):
        self.event_type = event_type
        self.payload = payload
        self.timestamp = datetime.now()
        self.event_id = f"{event_type}_{self.timestamp.isoformat()}"

class EventBus:
    """イベントバス（Observer Pattern実装）"""
    
    def __init__(self):
        self._handlers: Dict[str, List[callable]] = {}
        self.logger = logging.getLogger(__name__)
    
    def subscribe(self, event_type: str, handler: callable):
        """イベントハンドラー購読"""
        if event_type not in self._handlers:
            self._handlers[event_type] = []
        
        # WeakReference使用でメモリリーク防止
        if hasattr(handler, '__self__'):
            weak_handler = weakref.WeakMethod(handler)
        else:
            weak_handler = weakref.ref(handler)
        
        self._handlers[event_type].append(weak_handler)
    
    async def publish(self, event: DomainEvent):
        """イベント発行"""
        if event.event_type not in self._handlers:
            return
        
        # 有効なハンドラーのみ実行
        valid_handlers = []
        for weak_handler in self._handlers[event.event_type]:
            handler = weak_handler()
            if handler is not None:
                valid_handlers.append(handler)
        
        # 無効なハンドラーを削除
        self._handlers[event.event_type] = [
            wh for wh in self._handlers[event.event_type] 
            if wh() is not None
        ]
        
        # 並列実行
        if valid_handlers:
            await asyncio.gather(
                *[self._safe_handle(handler, event) for handler in valid_handlers],
                return_exceptions=True
            )
    
    async def _safe_handle(self, handler: callable, event: DomainEvent):
        """安全なハンドラー実行"""
        try:
            if asyncio.iscoroutinefunction(handler):
                await handler(event)
            else:
                handler(event)
        except Exception as e:
            self.logger.error(f"Error in event handler: {e}")

# ===== MEDIATOR PATTERN =====

class Request:
    """リクエスト基底クラス"""
    pass

class Response:
    """レスポンス基底クラス"""
    
    def __init__(self, success: bool = True, data: Any = None, error: str = None):
        self.success = success
        self.data = data
        self.error = error

class IRequestHandler(Protocol):
    """リクエストハンドラーインターフェース"""
    
    async def handle(self, request: Request) -> Response:
        """リクエスト処理"""
        ...

class Mediator:
    """メディエーターパターン実装"""
    
    def __init__(self, container: DependencyInjectionContainer):
        self.container = container
        self._handlers: Dict[Type, Type] = {}
        self.logger = logging.getLogger(__name__)
    
    def register_handler(self, request_type: Type, handler_type: Type):
        """ハンドラー登録"""
        self._handlers[request_type] = handler_type
    
    async def send(self, request: Request) -> Response:
        """リクエスト送信"""
        request_type = type(request)
        
        if request_type not in self._handlers:
            return Response(
                success=False, 
                error=f"No handler registered for {request_type}"
            )
        
        try:
            handler_type = self._handlers[request_type]
            handler = await self.container.resolve(handler_type)
            return await handler.handle(request)
        except Exception as e:
            self.logger.error(f"Error handling request {request_type}: {e}")
            return Response(success=False, error=str(e))

# ===== FACTORY PATTERNS =====

class ServiceFactory:
    """サービスファクトリー"""
    
    @staticmethod
    async def create_memory_manager(container: DependencyInjectionContainer) -> IMemoryManager:
        """メモリマネージャー作成"""
        config = container.config
        
        # 設定に基づいて適切な実装を選択
        if config.memory_backend == "redis":
            from memory_implementations import RedisMemoryManager
            return RedisMemoryManager(config)
        elif config.memory_backend == "sqlite":
            from memory_implementations import SQLiteMemoryManager
            return SQLiteMemoryManager(config)
        else:  # hybrid
            from memory_implementations import HybridMemoryManager
            return HybridMemoryManager(config)
    
    @staticmethod
    async def create_llm_client(container: DependencyInjectionContainer) -> ILLMClient:
        """LLMクライアント作成"""
        config = container.config
        
        if config.local_llm_enabled:
            from llm_implementations import LocalLLMClient
            return LocalLLMClient(config)
        else:
            from llm_implementations import RemoteLLMClient
            return RemoteLLMClient(config)

# ===== APPLICATION SERVICE LAYER =====

class TrinitasApplicationService:
    """Trinitasアプリケーションサービス（ファサード）"""
    
    def __init__(
        self,
        memory_manager: IMemoryManager,
        task_distributor: ITaskDistributor,
        llm_client: ILLMClient,
        monitor: IMonitor,
        learning_system: ILearningSystem,
        event_bus: EventBus,
        mediator: Mediator
    ):
        self.memory_manager = memory_manager
        self.task_distributor = task_distributor
        self.llm_client = llm_client
        self.monitor = monitor
        self.learning_system = learning_system
        self.event_bus = event_bus
        self.mediator = mediator
        self.logger = logging.getLogger(__name__)
    
    async def execute_persona_task(
        self,
        persona: str,
        task: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """ペルソナタスク実行（メインエントリーポイント）"""
        start_time = datetime.now()
        
        try:
            # イベント発行
            await self.event_bus.publish(
                DomainEvent("task_started", {
                    "persona": persona,
                    "task": task,
                    "context": context
                })
            )
            
            # 過去の学習パターン適用
            pattern = await self.learning_system.apply_pattern(
                f"{persona}_task",
                {"task": task, "context": context}
            )
            
            # タスク分散実行
            result = await self.task_distributor.distribute_task(
                task,
                [persona],
                mode="single"
            )
            
            # 結果をメモリに保存
            memory_id = await self.memory_manager.store_memory(
                content=f"Task: {task}, Result: {result}",
                importance=0.7,
                persona=persona,
                metadata={"task_type": "persona_execution"}
            )
            
            # パフォーマンス追跡
            duration = (datetime.now() - start_time).total_seconds()
            await self.monitor.track_performance(f"persona_task_{persona}", duration)
            
            # 成功パターンを学習
            await self.learning_system.learn_pattern(
                f"{persona}_success",
                task,
                {"result": result, "duration": duration}
            )
            
            # イベント発行
            await self.event_bus.publish(
                DomainEvent("task_completed", {
                    "persona": persona,
                    "task": task,
                    "result": result,
                    "memory_id": memory_id
                })
            )
            
            return {
                "success": True,
                "result": result,
                "memory_id": memory_id,
                "duration": duration
            }
            
        except Exception as e:
            self.logger.error(f"Error in persona task execution: {e}")
            
            # エラーイベント発行
            await self.event_bus.publish(
                DomainEvent("task_failed", {
                    "persona": persona,
                    "task": task,
                    "error": str(e)
                })
            )
            
            return {
                "success": False,
                "error": str(e),
                "duration": (datetime.now() - start_time).total_seconds()
            }

# ===== BOOTSTRAP CONFIGURATION =====

def configure_services(config: ServiceConfiguration) -> DependencyInjectionContainer:
    """サービス設定"""
    container = DependencyInjectionContainer(config)
    
    # インフラストラクチャサービス
    container.register_singleton(EventBus, EventBus)
    
    # ドメインサービス
    container.register_singleton(
        IMemoryManager, 
        None,  # 実装は実際のクラスに置き換え
        factory=ServiceFactory.create_memory_manager
    )
    
    container.register_singleton(
        ILLMClient,
        None,  # 実装は実際のクラスに置き換え
        factory=ServiceFactory.create_llm_client
    )
    
    # アプリケーションサービス
    container.register_singleton(
        TrinitasApplicationService,
        TrinitasApplicationService
    )
    
    # メディエーター
    container.register_singleton(Mediator, Mediator)
    
    return container

# ===== EXAMPLE USAGE =====

async def example_usage():
    """使用例"""
    
    # 設定
    config = ServiceConfiguration(
        memory_backend="hybrid",
        local_llm_enabled=True,
        enable_monitoring=True
    )
    
    # コンテナ設定
    container = configure_services(config)
    
    # アプリケーションサービス取得
    app_service = await container.resolve(TrinitasApplicationService)
    
    # タスク実行
    result = await app_service.execute_persona_task(
        persona="athena",
        task="システムアーキテクチャ分析",
        context={"project": "trinitas-v4"}
    )
    
    print(f"Result: {result}")

if __name__ == "__main__":
    asyncio.run(example_usage())