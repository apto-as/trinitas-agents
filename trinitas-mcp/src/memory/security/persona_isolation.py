"""
Persona Isolation Module for Trinitas Memory System
Provides data separation between different personas using separate Redis databases
"""

import logging
from typing import Dict, Optional, Any
from enum import IntEnum
import redis.asyncio as redis
from dataclasses import dataclass

logger = logging.getLogger(__name__)


class PersonaDB(IntEnum):
    """Redis database numbers for each persona"""
    ATHENA = 0
    ARTEMIS = 1
    HESTIA = 2
    BELLONA = 3
    SESHAT = 4
    SHARED = 5  # For cross-persona shared memories
    SYSTEM = 6  # For system-level data


@dataclass
class PersonaConfig:
    """Configuration for persona-specific settings"""
    name: str
    db_number: int
    max_memory_size: int = 1000000  # Maximum memories per persona
    ttl_multiplier: float = 1.0  # TTL adjustment factor
    access_level: str = "standard"  # standard, privileged, restricted


class PersonaIsolationManager:
    """Manages data isolation between different personas"""
    
    PERSONA_MAP: Dict[str, PersonaDB] = {
        'athena': PersonaDB.ATHENA,
        'artemis': PersonaDB.ARTEMIS,
        'hestia': PersonaDB.HESTIA,
        'bellona': PersonaDB.BELLONA,
        'seshat': PersonaDB.SESHAT,
        'shared': PersonaDB.SHARED,
        'system': PersonaDB.SYSTEM,
    }
    
    PERSONA_CONFIGS: Dict[str, PersonaConfig] = {
        'athena': PersonaConfig(
            name='athena',
            db_number=PersonaDB.ATHENA,
            max_memory_size=1500000,  # Strategic planning needs more memory
            ttl_multiplier=1.2,  # Keep strategic data longer
            access_level="privileged"
        ),
        'artemis': PersonaConfig(
            name='artemis',
            db_number=PersonaDB.ARTEMIS,
            max_memory_size=1000000,
            ttl_multiplier=0.8,  # Technical data can expire faster
            access_level="standard"
        ),
        'hestia': PersonaConfig(
            name='hestia',
            db_number=PersonaDB.HESTIA,
            max_memory_size=1200000,  # Security logs need space
            ttl_multiplier=1.5,  # Security data kept longer
            access_level="privileged"
        ),
        'bellona': PersonaConfig(
            name='bellona',
            db_number=PersonaDB.BELLONA,
            max_memory_size=800000,  # Tactical data is more transient
            ttl_multiplier=0.6,
            access_level="standard"
        ),
        'seshat': PersonaConfig(
            name='seshat',
            db_number=PersonaDB.SESHAT,
            max_memory_size=2000000,  # Documentation needs most space
            ttl_multiplier=2.0,  # Archive data kept longest
            access_level="privileged"
        ),
    }
    
    def __init__(self, redis_host: str = 'localhost', redis_port: int = 6379):
        """Initialize the Persona Isolation Manager"""
        self.redis_host = redis_host
        self.redis_port = redis_port
        self.connections: Dict[str, redis.Redis] = {}
        self._initialized = False
        
    async def initialize(self):
        """Initialize Redis connections for each persona"""
        if self._initialized:
            return
            
        logger.info("Initializing Persona Isolation Manager...")
        
        for persona_name, config in self.PERSONA_CONFIGS.items():
            try:
                # Create separate Redis connection for each persona
                connection = redis.Redis(
                    host=self.redis_host,
                    port=self.redis_port,
                    db=int(config.db_number),  # Convert IntEnum to int
                    decode_responses=False,
                    max_connections=10
                )
                
                # Test connection
                await connection.ping()
                self.connections[persona_name] = connection
                logger.info(f"Initialized Redis DB {config.db_number} for {persona_name}")
                
            except Exception as e:
                logger.error(f"Failed to initialize connection for {persona_name}: {e}")
                # Create fallback connection to shared DB
                self.connections[persona_name] = await self._create_fallback_connection()
        
        # Initialize shared and system connections
        await self._initialize_special_connections()
        self._initialized = True
        logger.info("Persona Isolation Manager initialized successfully")
    
    async def _initialize_special_connections(self):
        """Initialize shared and system database connections"""
        for special_name in ['shared', 'system']:
            try:
                db_number = self.PERSONA_MAP[special_name]
                connection = redis.Redis(
                    host=self.redis_host,
                    port=self.redis_port,
                    db=int(db_number),  # Convert IntEnum to int
                    decode_responses=False,
                    max_connections=5
                )
                await connection.ping()
                self.connections[special_name] = connection
                logger.info(f"Initialized {special_name} Redis DB {db_number}")
            except Exception as e:
                logger.error(f"Failed to initialize {special_name} connection: {e}")
    
    async def _create_fallback_connection(self) -> redis.Redis:
        """Create a fallback connection to the shared database"""
        return redis.Redis(
            host=self.redis_host,
            port=self.redis_port,
            db=int(PersonaDB.SHARED),  # Convert IntEnum to int
            decode_responses=False,
            max_connections=5
        )
    
    def get_connection(self, persona: str) -> Optional[redis.Redis]:
        """Get Redis connection for a specific persona"""
        persona_lower = persona.lower()
        
        if persona_lower not in self.connections:
            logger.warning(f"No connection found for persona {persona}, using shared DB")
            return self.connections.get('shared')
        
        return self.connections[persona_lower]
    
    def get_db_number(self, persona: str) -> int:
        """Get the database number for a specific persona"""
        persona_lower = persona.lower()
        return self.PERSONA_MAP.get(persona_lower, PersonaDB.SHARED)
    
    def get_config(self, persona: str) -> PersonaConfig:
        """Get configuration for a specific persona"""
        persona_lower = persona.lower()
        return self.PERSONA_CONFIGS.get(
            persona_lower,
            PersonaConfig(name=persona, db_number=PersonaDB.SHARED)
        )
    
    async def check_isolation(self, persona: str) -> Dict[str, Any]:
        """Check isolation status for a persona"""
        config = self.get_config(persona)
        connection = self.get_connection(persona)
        
        if not connection:
            return {
                'persona': persona,
                'isolated': False,
                'reason': 'No connection available'
            }
        
        try:
            # Check current database
            info = await connection.info('keyspace')
            db_key = f'db{int(config.db_number)}'  # Convert IntEnum to int
            
            return {
                'persona': persona,
                'isolated': True,
                'db_number': config.db_number,
                'keys_count': info.get(db_key, {}).get('keys', 0),
                'max_memory': config.max_memory_size,
                'ttl_multiplier': config.ttl_multiplier,
                'access_level': config.access_level
            }
        except Exception as e:
            return {
                'persona': persona,
                'isolated': False,
                'reason': str(e)
            }
    
    async def migrate_existing_data(self, source_db: int = 0):
        """Migrate existing data from a single database to persona-specific databases"""
        logger.info(f"Starting data migration from DB {source_db}")
        
        # Connect to source database
        source_conn = redis.Redis(
            host=self.redis_host,
            port=self.redis_port,
            db=source_db,
            decode_responses=False
        )
        
        try:
            # Scan all keys in source database
            cursor = 0
            migrated_count = 0
            
            while True:
                cursor, keys = await source_conn.scan(cursor, count=100)
                
                for key in keys:
                    # Determine persona from key pattern
                    key_str = key.decode('utf-8') if isinstance(key, bytes) else key
                    persona = self._extract_persona_from_key(key_str)
                    
                    if persona and persona in self.connections:
                        # Get data from source
                        data = await source_conn.get(key)
                        ttl = await source_conn.ttl(key)
                        
                        # Write to persona-specific database
                        target_conn = self.connections[persona]
                        if ttl > 0:
                            await target_conn.setex(key, ttl, data)
                        else:
                            await target_conn.set(key, data)
                        
                        # Delete from source (optional, can be commented out for safety)
                        # await source_conn.delete(key)
                        
                        migrated_count += 1
                        
                        if migrated_count % 100 == 0:
                            logger.info(f"Migrated {migrated_count} keys...")
                
                if cursor == 0:
                    break
            
            logger.info(f"Migration completed. Migrated {migrated_count} keys.")
            return migrated_count
            
        except Exception as e:
            logger.error(f"Migration failed: {e}")
            raise
    
    def _extract_persona_from_key(self, key: str) -> Optional[str]:
        """Extract persona name from Redis key pattern"""
        # Expected patterns: "persona:athena:*", "memory:athena:*", etc.
        parts = key.split(':')
        
        for part in parts:
            if part.lower() in self.PERSONA_MAP:
                return part.lower()
        
        return None
    
    async def cleanup(self):
        """Clean up all connections"""
        logger.info("Cleaning up Persona Isolation Manager...")
        
        for persona, connection in self.connections.items():
            try:
                await connection.aclose()  # Use aclose for modern Redis
                logger.info(f"Closed connection for {persona}")
            except Exception as e:
                logger.error(f"Error closing connection for {persona}: {e}")
        
        self.connections.clear()
        self._initialized = False
        logger.info("Persona Isolation Manager cleaned up")
    
    async def get_statistics(self) -> Dict[str, Dict[str, Any]]:
        """Get statistics for all persona databases"""
        stats = {}
        
        for persona, connection in self.connections.items():
            try:
                info = await connection.info('keyspace')
                config = self.get_config(persona)
                db_key = f'db{config.db_number}'
                
                stats[persona] = {
                    'db_number': config.db_number,
                    'keys_count': info.get(db_key, {}).get('keys', 0),
                    'expires': info.get(db_key, {}).get('expires', 0),
                    'avg_ttl': info.get(db_key, {}).get('avg_ttl', 0),
                    'max_memory_size': config.max_memory_size,
                    'access_level': config.access_level
                }
            except Exception as e:
                stats[persona] = {'error': str(e)}
        
        return stats


# Singleton instance
_isolation_manager: Optional[PersonaIsolationManager] = None


async def get_isolation_manager(
    redis_host: str = 'localhost',
    redis_port: int = 6379
) -> PersonaIsolationManager:
    """Get or create the singleton PersonaIsolationManager instance"""
    global _isolation_manager
    
    if _isolation_manager is None:
        _isolation_manager = PersonaIsolationManager(redis_host, redis_port)
        await _isolation_manager.initialize()
    
    return _isolation_manager