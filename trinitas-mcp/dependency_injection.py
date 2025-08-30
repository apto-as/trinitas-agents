"""
Dependency Injection Implementation - Trinitas v4.0
高度な依存関係注入システムの実装

Author: Athena - Strategic Architect  
Date: 2025-08-30

このモジュールは、Trinitas v4.0システムのための完全な依存関係注入フレームワークを提供します。
設定ベース、アノテーションベース、コンベンションベースの3つのアプローチをサポートします。
"""

import asyncio
import inspect
import logging
from abc import ABC, abstractmethod
from contextlib import asynccontextmanager
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import (
    Any, Dict, List, Optional, Protocol, Type, TypeVar, Generic,
    Union, Callable, Awaitable, get_type_hints, get_origin, get_args
)
import weakref
from functools import wraps
import json

# ===== TYPE DEFINITIONS =====

T = TypeVar('T')
ServiceType = TypeVar('ServiceType')

class LifetimeScope(Enum):
    """サービスライフタイム"""
    SINGLETON = "singleton"      # アプリケーション全体で単一インスタンス
    SCOPED = "scoped"           # スコープ内で単一インスタンス  
    TRANSIENT = "transient"     # 毎回新しいインスタンス
    POOLED = "pooled"          # オブジェクトプール使用

class InjectionMode(Enum):
    """注入モード"""
    CONSTRUCTOR = "constructor"  # コンストラクタ注入
    PROPERTY = "property"       # プロパティ注入
    METHOD = "method"          # メソッド注入

# ===== DECORATORS =====

def injectable(lifetime: LifetimeScope = LifetimeScope.TRANSIENT):
    """注入可能マーカーデコレータ"""
    def decorator(cls):
        cls._injectable_lifetime = lifetime
        cls._injectable = True
        return cls
    return decorator

def inject(name: Optional[str] = None):
    """依存関係注入マーカー"""
    def decorator(func_or_field):
        if isinstance(func_or_field, property):
            func_or_field.fget._inject_name = name
            func_or_field.fget._inject = True
        else:
            func_or_field._inject_name = name
            func_or_field._inject = True
        return func_or_field
    return decorator

def service_factory(interface: Type[T]):
    """サービスファクトリーデコレータ"""
    def decorator(func: Callable[..., Union[T, Awaitable[T]]]):
        func._factory_for = interface
        func._is_factory = True
        return func
    return decorator

# ===== CONFIGURATION =====

@dataclass
class DependencyDescriptor:
    """依存関係記述子"""
    interface: Type
    implementation: Optional[Type] = None
    factory: Optional[Callable] = None
    lifetime: LifetimeScope = LifetimeScope.TRANSIENT
    name: Optional[str] = None
    condition: Optional[Callable[[Dict[str, Any]], bool]] = None
    initialization_order: int = 0
    configuration: Dict[str, Any] = field(default_factory=dict)

@dataclass  
class ServiceConfiguration:
    """サービス設定"""
    # Core Services
    memory_backend: str = "hybrid"
    redis_url: str = "redis://localhost:6379"
    sqlite_path: str = "./data/trinitas.db"
    chromadb_path: str = "./data/chromadb"
    
    # LLM Configuration
    local_llm_enabled: bool = False
    local_llm_endpoint: str = "http://localhost:1234"
    llm_timeout: float = 30.0
    
    # Performance
    cache_size: int = 1000
    max_connections: int = 10
    connection_timeout: float = 5.0
    
    # Monitoring
    enable_monitoring: bool = True
    enable_metrics: bool = True
    metrics_interval: float = 60.0
    
    # Learning System
    enable_learning: bool = True
    auto_learn: bool = True
    pattern_threshold: float = 0.8
    
    # Security
    enable_audit: bool = True
    max_memory_size: int = 1000000
    encrypt_storage: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        """辞書形式に変換"""
        return {
            field.name: getattr(self, field.name)
            for field in self.__dataclass_fields__.values()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ServiceConfiguration':
        """辞書から作成"""
        return cls(**data)
    
    @classmethod
    def load_from_file(cls, path: Path) -> 'ServiceConfiguration':
        """ファイルから設定読み込み"""
        if path.suffix.lower() == '.json':
            with open(path, 'r') as f:
                data = json.load(f)
        else:
            # 環境変数形式
            data = {}
            with open(path, 'r') as f:
                for line in f:
                    if '=' in line and not line.startswith('#'):
                        key, value = line.strip().split('=', 1)
                        # 型変換
                        if value.lower() in ('true', 'false'):
                            value = value.lower() == 'true'
                        elif value.isdigit():
                            value = int(value)
                        elif '.' in value and value.replace('.', '').isdigit():
                            value = float(value)
                        data[key.lower()] = value
        
        return cls.from_dict(data)

# ===== CONTAINER IMPLEMENTATION =====

class CircularDependencyError(Exception):
    """循環依存エラー"""
    pass

class ServiceNotFoundError(Exception):
    """サービス未登録エラー"""
    pass

class ServiceScope:
    """サービススコープ"""
    
    def __init__(self, parent: Optional['ServiceScope'] = None):
        self.parent = parent
        self._instances: Dict[Type, Any] = {}
        self._disposed = False
    
    def get_instance(self, service_type: Type) -> Optional[Any]:
        """インスタンス取得"""
        if self._disposed:
            raise RuntimeError("Scope has been disposed")
        
        if service_type in self._instances:
            return self._instances[service_type]
        
        if self.parent:
            return self.parent.get_instance(service_type)
        
        return None
    
    def set_instance(self, service_type: Type, instance: Any):
        """インスタンス設定"""
        if self._disposed:
            raise RuntimeError("Scope has been disposed")
        
        self._instances[service_type] = instance
    
    async def dispose(self):
        """リソース解放"""
        if self._disposed:
            return
        
        self._disposed = True
        
        # 全インスタンスを解放
        for instance in self._instances.values():
            if hasattr(instance, 'dispose'):
                if asyncio.iscoroutinefunction(instance.dispose):
                    await instance.dispose()
                else:
                    instance.dispose()
        
        self._instances.clear()

class AdvancedDIContainer:
    """高度な依存関係注入コンテナ"""
    
    def __init__(self, configuration: ServiceConfiguration):
        self.configuration = configuration
        self._descriptors: Dict[Type, DependencyDescriptor] = {}
        self._named_descriptors: Dict[str, DependencyDescriptor] = {}
        self._singletons: Dict[Type, Any] = {}
        self._building: set = set()  # 循環依存検出
        self._object_pools: Dict[Type, List[Any]] = {}
        self._root_scope = ServiceScope()
        self._current_scope = self._root_scope
        self.logger = logging.getLogger(__name__)
    
    # ===== REGISTRATION METHODS =====
    
    def register_singleton(
        self, 
        interface: Type[T], 
        implementation: Optional[Type[T]] = None,
        factory: Optional[Callable[..., Union[T, Awaitable[T]]]] = None,
        name: Optional[str] = None,
        condition: Optional[Callable[[Dict[str, Any]], bool]] = None,
        **config
    ) -> 'AdvancedDIContainer':
        """シングルトン登録"""
        return self._register(
            interface, implementation, factory, 
            LifetimeScope.SINGLETON, name, condition, **config
        )
    
    def register_scoped(
        self, 
        interface: Type[T], 
        implementation: Optional[Type[T]] = None,
        factory: Optional[Callable[..., Union[T, Awaitable[T]]]] = None,
        name: Optional[str] = None,
        condition: Optional[Callable[[Dict[str, Any]], bool]] = None,
        **config
    ) -> 'AdvancedDIContainer':
        """スコープ付き登録"""
        return self._register(
            interface, implementation, factory,
            LifetimeScope.SCOPED, name, condition, **config
        )
    
    def register_transient(
        self, 
        interface: Type[T], 
        implementation: Optional[Type[T]] = None,
        factory: Optional[Callable[..., Union[T, Awaitable[T]]]] = None,
        name: Optional[str] = None,
        condition: Optional[Callable[[Dict[str, Any]], bool]] = None,
        **config
    ) -> 'AdvancedDIContainer':
        """一時的登録"""
        return self._register(
            interface, implementation, factory,
            LifetimeScope.TRANSIENT, name, condition, **config
        )
    
    def register_pooled(
        self, 
        interface: Type[T], 
        implementation: Optional[Type[T]] = None,
        factory: Optional[Callable[..., Union[T, Awaitable[T]]]] = None,
        pool_size: int = 10,
        name: Optional[str] = None,
        condition: Optional[Callable[[Dict[str, Any]], bool]] = None,
        **config
    ) -> 'AdvancedDIContainer':
        """プール登録"""
        config['pool_size'] = pool_size
        return self._register(
            interface, implementation, factory,
            LifetimeScope.POOLED, name, condition, **config
        )
    
    def _register(
        self,
        interface: Type[T],
        implementation: Optional[Type[T]],
        factory: Optional[Callable],
        lifetime: LifetimeScope,
        name: Optional[str],
        condition: Optional[Callable],
        **config
    ) -> 'AdvancedDIContainer':
        """内部登録メソッド"""
        
        descriptor = DependencyDescriptor(
            interface=interface,
            implementation=implementation,
            factory=factory,
            lifetime=lifetime,
            name=name,
            condition=condition,
            configuration=config
        )
        
        self._descriptors[interface] = descriptor
        
        if name:
            self._named_descriptors[name] = descriptor
        
        self.logger.debug(f"Registered service: {interface} with lifetime {lifetime}")
        return self
    
    # ===== AUTO-REGISTRATION =====
    
    def register_from_module(self, module) -> 'AdvancedDIContainer':
        """モジュールから自動登録"""
        for name in dir(module):
            obj = getattr(module, name)
            if (inspect.isclass(obj) and 
                hasattr(obj, '_injectable') and 
                obj._injectable):
                
                lifetime = getattr(obj, '_injectable_lifetime', LifetimeScope.TRANSIENT)
                
                # インターフェース検出
                bases = [base for base in obj.__bases__ 
                        if base != object and hasattr(base, '__abstractmethods__')]
                
                if bases:
                    interface = bases[0]  # 最初の抽象基底クラスをインターフェースとする
                    self._register(interface, obj, None, lifetime, None, None)
                else:
                    # 具象クラスとして登録
                    self._register(obj, obj, None, lifetime, None, None)
        
        return self
    
    def register_factories_from_module(self, module) -> 'AdvancedDIContainer':
        """ファクトリー関数から自動登録"""
        for name in dir(module):
            obj = getattr(module, name)
            if (callable(obj) and 
                hasattr(obj, '_is_factory') and 
                obj._is_factory):
                
                interface = getattr(obj, '_factory_for')
                self._register(interface, None, obj, LifetimeScope.SINGLETON, None, None)
        
        return self
    
    # ===== RESOLUTION =====
    
    async def resolve(self, interface: Type[T], name: Optional[str] = None) -> T:
        """サービス解決"""
        if interface in self._building:
            raise CircularDependencyError(
                f"Circular dependency detected for {interface}"
            )
        
        # 名前付き解決
        if name:
            if name not in self._named_descriptors:
                raise ServiceNotFoundError(f"Named service '{name}' not found")
            descriptor = self._named_descriptors[name]
        else:
            if interface not in self._descriptors:
                raise ServiceNotFoundError(f"Service {interface} not registered")
            descriptor = self._descriptors[interface]
        
        # 条件チェック
        if descriptor.condition and not descriptor.condition(self.configuration.to_dict()):
            raise ServiceNotFoundError(f"Service condition not met for {interface}")
        
        return await self._resolve_with_descriptor(descriptor)
    
    async def _resolve_with_descriptor(self, descriptor: DependencyDescriptor) -> Any:
        """記述子を使用したサービス解決"""
        interface = descriptor.interface
        
        # ライフタイム別処理
        if descriptor.lifetime == LifetimeScope.SINGLETON:
            return await self._resolve_singleton(descriptor)
        elif descriptor.lifetime == LifetimeScope.SCOPED:
            return await self._resolve_scoped(descriptor)
        elif descriptor.lifetime == LifetimeScope.POOLED:
            return await self._resolve_pooled(descriptor)
        else:  # TRANSIENT
            return await self._create_instance(descriptor)
    
    async def _resolve_singleton(self, descriptor: DependencyDescriptor) -> Any:
        """シングルトン解決"""
        interface = descriptor.interface
        
        if interface not in self._singletons:
            self._building.add(interface)
            try:
                self._singletons[interface] = await self._create_instance(descriptor)
            finally:
                self._building.discard(interface)
        
        return self._singletons[interface]
    
    async def _resolve_scoped(self, descriptor: DependencyDescriptor) -> Any:
        """スコープ付き解決"""
        interface = descriptor.interface
        
        instance = self._current_scope.get_instance(interface)
        if instance is not None:
            return instance
        
        self._building.add(interface)
        try:
            instance = await self._create_instance(descriptor)
            self._current_scope.set_instance(interface, instance)
            return instance
        finally:
            self._building.discard(interface)
    
    async def _resolve_pooled(self, descriptor: DependencyDescriptor) -> Any:
        """プール解決"""
        interface = descriptor.interface
        pool_size = descriptor.configuration.get('pool_size', 10)
        
        if interface not in self._object_pools:
            self._object_pools[interface] = []
        
        pool = self._object_pools[interface]
        
        # プールからインスタンス取得
        if pool:
            return pool.pop()
        
        # プールが空の場合は新規作成
        return await self._create_instance(descriptor)
    
    async def _create_instance(self, descriptor: DependencyDescriptor) -> Any:
        """インスタンス作成"""
        if descriptor.factory:
            return await self._create_from_factory(descriptor)
        elif descriptor.implementation:
            return await self._create_from_implementation(descriptor)
        else:
            raise ValueError(f"No factory or implementation for {descriptor.interface}")
    
    async def _create_from_factory(self, descriptor: DependencyDescriptor) -> Any:
        """ファクトリーからインスタンス作成"""
        factory = descriptor.factory
        
        # ファクトリー依存関係解決
        sig = inspect.signature(factory)
        kwargs = {}
        
        for param_name, param in sig.parameters.items():
            if param_name == 'self':
                continue
            
            # パラメータアノテーションから型を取得
            if param.annotation != param.empty:
                dependency = await self.resolve(param.annotation)
                kwargs[param_name] = dependency
            elif param_name in descriptor.configuration:
                kwargs[param_name] = descriptor.configuration[param_name]
        
        # ファクトリー実行
        if asyncio.iscoroutinefunction(factory):
            return await factory(**kwargs)
        else:
            return factory(**kwargs)
    
    async def _create_from_implementation(self, descriptor: DependencyDescriptor) -> Any:
        """実装からインスタンス作成"""
        implementation = descriptor.implementation
        
        # コンストラクタ依存関係解決
        sig = inspect.signature(implementation.__init__)
        args = []
        kwargs = {}
        
        for param_name, param in sig.parameters.items():
            if param_name == 'self':
                continue
            
            # パラメータアノテーションから型を取得
            if param.annotation != param.empty:
                if param_name in descriptor.configuration:
                    # 設定値を優先
                    kwargs[param_name] = descriptor.configuration[param_name]
                else:
                    # 依存関係解決
                    dependency = await self.resolve(param.annotation)
                    kwargs[param_name] = dependency
            elif param_name in descriptor.configuration:
                kwargs[param_name] = descriptor.configuration[param_name]
        
        # インスタンス作成
        instance = implementation(**kwargs)
        
        # 初期化メソッド実行
        if hasattr(instance, 'initialize'):
            if asyncio.iscoroutinefunction(instance.initialize):
                await instance.initialize()
            else:
                instance.initialize()
        
        return instance
    
    # ===== SCOPE MANAGEMENT =====
    
    @asynccontextmanager
    async def create_scope(self):
        """新しいスコープ作成"""
        old_scope = self._current_scope
        new_scope = ServiceScope(parent=old_scope)
        self._current_scope = new_scope
        
        try:
            yield new_scope
        finally:
            await new_scope.dispose()
            self._current_scope = old_scope
    
    # ===== UTILITY METHODS =====
    
    async def validate_registrations(self) -> List[str]:
        """登録の妥当性検証"""
        issues = []
        
        for interface, descriptor in self._descriptors.items():
            try:
                # 循環依存チェック
                self._check_circular_dependencies(descriptor, set())
                
                # 依存関係存在チェック
                await self._validate_dependencies(descriptor)
                
            except Exception as e:
                issues.append(f"{interface}: {str(e)}")
        
        return issues
    
    def _check_circular_dependencies(self, descriptor: DependencyDescriptor, visited: set):
        """循環依存チェック"""
        if descriptor.interface in visited:
            raise CircularDependencyError(f"Circular dependency: {' -> '.join(map(str, visited))}")
        
        visited.add(descriptor.interface)
        
        # 依存関係の循環チェック（実装では詳細な解析が必要）
        if descriptor.implementation:
            sig = inspect.signature(descriptor.implementation.__init__)
            for param in sig.parameters.values():
                if param.annotation != param.empty and param.annotation in self._descriptors:
                    self._check_circular_dependencies(
                        self._descriptors[param.annotation], 
                        visited.copy()
                    )
    
    async def _validate_dependencies(self, descriptor: DependencyDescriptor):
        """依存関係妥当性検証"""
        if descriptor.implementation:
            sig = inspect.signature(descriptor.implementation.__init__)
            for param_name, param in sig.parameters.items():
                if param_name == 'self':
                    continue
                
                if (param.annotation != param.empty and 
                    param.annotation not in self._descriptors and
                    param_name not in descriptor.configuration):
                    raise ServiceNotFoundError(
                        f"Dependency {param.annotation} not registered for {descriptor.interface}"
                    )
    
    def get_registration_info(self) -> Dict[str, Dict[str, Any]]:
        """登録情報取得"""
        info = {}
        
        for interface, descriptor in self._descriptors.items():
            info[str(interface)] = {
                'implementation': str(descriptor.implementation) if descriptor.implementation else None,
                'factory': str(descriptor.factory) if descriptor.factory else None,
                'lifetime': descriptor.lifetime.value,
                'name': descriptor.name,
                'has_condition': descriptor.condition is not None,
                'configuration': descriptor.configuration
            }
        
        return info
    
    async def health_check(self) -> Dict[str, Any]:
        """ヘルスチェック"""
        start_time = datetime.now()
        
        try:
            # 主要サービスの解決テスト
            issues = await self.validate_registrations()
            
            # 統計情報
            stats = {
                'total_registered': len(self._descriptors),
                'singletons_created': len(self._singletons),
                'named_services': len(self._named_descriptors),
                'validation_issues': len(issues),
                'health_check_duration': (datetime.now() - start_time).total_seconds()
            }
            
            return {
                'healthy': len(issues) == 0,
                'issues': issues,
                'statistics': stats
            }
            
        except Exception as e:
            return {
                'healthy': False,
                'error': str(e),
                'duration': (datetime.now() - start_time).total_seconds()
            }

# ===== CONVENIENCE FUNCTIONS =====

def create_container(config: ServiceConfiguration) -> AdvancedDIContainer:
    """標準コンテナ作成"""
    container = AdvancedDIContainer(config)
    
    # 設定サービス自体を登録
    container.register_singleton(
        ServiceConfiguration, 
        factory=lambda: config
    )
    
    return container

async def bootstrap_trinitas_container(config_path: Optional[Path] = None) -> AdvancedDIContainer:
    """Trinitas専用コンテナブートストラップ"""
    
    # 設定読み込み
    if config_path and config_path.exists():
        config = ServiceConfiguration.load_from_file(config_path)
    else:
        config = ServiceConfiguration()
    
    # コンテナ作成
    container = create_container(config)
    
    # 標準サービス登録（実際の実装では適切なクラスを指定）
    # container.register_singleton(IMemoryManager, EnhancedMemoryManager)
    # container.register_singleton(ITaskDistributor, BellonaTaskDistributor)
    # container.register_singleton(ILLMClient, LocalLLMClient)
    # container.register_singleton(IMonitor, SeshatMemoryMonitor)
    # container.register_singleton(ILearningSystem, LearningSystem)
    
    # 妥当性検証
    issues = await container.validate_registrations()
    if issues:
        logging.warning(f"Container validation issues: {issues}")
    
    return container

# ===== TESTING UTILITIES =====

class MockServiceContainer(AdvancedDIContainer):
    """テスト用モックコンテナ"""
    
    def __init__(self, config: ServiceConfiguration):
        super().__init__(config)
        self._mocks: Dict[Type, Any] = {}
    
    def register_mock(self, interface: Type[T], mock: T) -> 'MockServiceContainer':
        """モック登録"""
        self._mocks[interface] = mock
        self.register_singleton(interface, factory=lambda: mock)
        return self
    
    async def resolve(self, interface: Type[T], name: Optional[str] = None) -> T:
        """モック優先解決"""
        if interface in self._mocks:
            return self._mocks[interface]
        
        return await super().resolve(interface, name)

# ===== EXAMPLE USAGE =====

async def example_usage():
    """使用例"""
    
    # 設定
    config = ServiceConfiguration(
        memory_backend="hybrid",
        local_llm_enabled=True,
        enable_monitoring=True
    )
    
    # コンテナ作成
    container = create_container(config)
    
    # サービス登録例
    # container.register_singleton(IMemoryManager, HybridMemoryManager)
    
    # スコープ使用例
    async with container.create_scope() as scope:
        # service = await container.resolve(SomeService)
        pass
    
    # ヘルスチェック
    health = await container.health_check()
    print(f"Container health: {health}")

if __name__ == "__main__":
    asyncio.run(example_usage())