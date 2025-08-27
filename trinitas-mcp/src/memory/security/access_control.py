"""
Access Control Module for Trinitas Memory System
Implements authentication and authorization for memory operations
"""

import logging
import hashlib
import secrets
from typing import Dict, List, Optional, Set, Tuple
from enum import Enum, IntEnum
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import json

logger = logging.getLogger(__name__)


class AccessLevel(IntEnum):
    """Access levels for memory operations"""
    NONE = 0
    READ = 1
    WRITE = 2
    DELETE = 3
    ADMIN = 4


class MemoryOperation(Enum):
    """Types of memory operations"""
    STORE = "store"
    RETRIEVE = "retrieve"
    SEARCH = "search"
    DELETE = "delete"
    UPDATE = "update"
    LIST = "list"


@dataclass
class AccessToken:
    """Access token for authenticated operations"""
    token_id: str
    persona: str
    created_at: datetime
    expires_at: datetime
    access_level: AccessLevel
    allowed_operations: Set[MemoryOperation] = field(default_factory=set)
    allowed_memory_types: Set[str] = field(default_factory=set)
    metadata: Dict = field(default_factory=dict)
    
    def is_valid(self) -> bool:
        """Check if token is still valid"""
        return datetime.now() < self.expires_at
    
    def can_perform(self, operation: MemoryOperation) -> bool:
        """Check if token allows specific operation"""
        return operation in self.allowed_operations


@dataclass
class AccessPolicy:
    """Access policy for persona interactions"""
    persona: str
    can_read_from: Set[str] = field(default_factory=set)  # Other personas this can read from
    can_write_to: Set[str] = field(default_factory=set)   # Other personas this can write to
    can_share_with: Set[str] = field(default_factory=set)  # Personas that can access shared memories
    restricted_memory_types: Set[str] = field(default_factory=set)  # Restricted memory types
    max_memory_size: int = 1000000  # Maximum memory items
    rate_limit: int = 1000  # Operations per minute


class AccessControlManager:
    """Manages access control for the Trinitas Memory System"""
    
    # Default access matrix - defines who can access whose memories
    DEFAULT_ACCESS_MATRIX = {
        'athena': {
            'can_read_from': {'shared', 'artemis', 'hestia', 'bellona', 'seshat'},  # Strategic oversight
            'can_write_to': {'shared', 'athena'},
            'can_share_with': {'artemis', 'hestia', 'bellona', 'seshat'},
            'access_level': AccessLevel.ADMIN
        },
        'artemis': {
            'can_read_from': {'shared', 'artemis', 'hestia'},  # Technical collaboration
            'can_write_to': {'shared', 'artemis'},
            'can_share_with': {'athena', 'hestia'},
            'access_level': AccessLevel.WRITE
        },
        'hestia': {
            'can_read_from': {'shared', 'athena', 'artemis', 'hestia', 'bellona', 'seshat'},  # Security oversight
            'can_write_to': {'shared', 'hestia', 'system'},  # Can write security logs to system
            'can_share_with': {'athena'},  # Only share security info with leadership
            'access_level': AccessLevel.ADMIN
        },
        'bellona': {
            'can_read_from': {'shared', 'bellona', 'athena'},  # Tactical coordination
            'can_write_to': {'shared', 'bellona'},
            'can_share_with': {'athena', 'artemis', 'seshat'},
            'access_level': AccessLevel.WRITE
        },
        'seshat': {
            'can_read_from': {'shared', 'athena', 'artemis', 'hestia', 'bellona', 'seshat'},  # Documentation needs
            'can_write_to': {'shared', 'seshat'},
            'can_share_with': {'athena', 'artemis', 'hestia', 'bellona'},  # Documentation available to all
            'access_level': AccessLevel.WRITE
        }
    }
    
    def __init__(self):
        """Initialize the Access Control Manager"""
        self.tokens: Dict[str, AccessToken] = {}
        self.policies: Dict[str, AccessPolicy] = {}
        self.operation_log: List[Dict] = []
        self.rate_limiters: Dict[str, List[datetime]] = {}
        self._initialize_policies()
        
    def _initialize_policies(self):
        """Initialize default access policies for each persona"""
        for persona, config in self.DEFAULT_ACCESS_MATRIX.items():
            self.policies[persona] = AccessPolicy(
                persona=persona,
                can_read_from=set(config.get('can_read_from', [])),
                can_write_to=set(config.get('can_write_to', [])),
                can_share_with=set(config.get('can_share_with', [])),
                max_memory_size=config.get('max_memory_size', 1000000),
                rate_limit=config.get('rate_limit', 1000)
            )
        
        logger.info(f"Initialized access policies for {len(self.policies)} personas")
    
    async def authenticate(self, persona: str, credentials: Optional[Dict] = None) -> Optional[AccessToken]:
        """Authenticate a persona and generate access token"""
        persona_lower = persona.lower()
        
        # Check if persona exists in policies
        if persona_lower not in self.policies:
            logger.warning(f"Authentication failed: unknown persona {persona}")
            return None
        
        # Generate secure token
        token_id = secrets.token_urlsafe(32)
        token_hash = hashlib.sha256(token_id.encode()).hexdigest()
        
        # Determine access level and permissions
        access_config = self.DEFAULT_ACCESS_MATRIX.get(persona_lower, {})
        access_level = access_config.get('access_level', AccessLevel.READ)
        
        # Create token with appropriate permissions
        token = AccessToken(
            token_id=token_hash,
            persona=persona_lower,
            created_at=datetime.now(),
            expires_at=datetime.now() + timedelta(hours=24),  # 24 hour expiry
            access_level=access_level,
            allowed_operations=self._get_allowed_operations(access_level),
            allowed_memory_types=self._get_allowed_memory_types(persona_lower),
            metadata={'original_token': token_id}  # Store original for client
        )
        
        # Store token
        self.tokens[token_hash] = token
        
        # Log authentication
        self._log_operation(persona_lower, "authenticate", {"status": "success"})
        
        logger.info(f"Authenticated {persona} with access level {access_level}")
        return token
    
    def _get_allowed_operations(self, access_level: AccessLevel) -> Set[MemoryOperation]:
        """Get allowed operations based on access level"""
        operations = set()
        
        if access_level >= AccessLevel.READ:
            operations.update({MemoryOperation.RETRIEVE, MemoryOperation.SEARCH, MemoryOperation.LIST})
        
        if access_level >= AccessLevel.WRITE:
            operations.update({MemoryOperation.STORE, MemoryOperation.UPDATE})
        
        if access_level >= AccessLevel.DELETE:
            operations.add(MemoryOperation.DELETE)
        
        if access_level >= AccessLevel.ADMIN:
            # Admin has all operations
            operations = set(MemoryOperation)
        
        return operations
    
    def _get_allowed_memory_types(self, persona: str) -> Set[str]:
        """Get allowed memory types for a persona"""
        # All personas can access all memory types by default
        # Can be customized per persona if needed
        return {'working', 'episodic', 'semantic', 'procedural'}
    
    async def authorize(
        self,
        token: str,
        operation: MemoryOperation,
        target_persona: Optional[str] = None,
        memory_type: Optional[str] = None
    ) -> Tuple[bool, Optional[str]]:
        """Authorize an operation with a token"""
        
        # Check if token exists and is valid
        if token not in self.tokens:
            return False, "Invalid token"
        
        access_token = self.tokens[token]
        
        if not access_token.is_valid():
            # Remove expired token
            del self.tokens[token]
            return False, "Token expired"
        
        # Check rate limiting
        if not self._check_rate_limit(access_token.persona):
            return False, "Rate limit exceeded"
        
        # Check operation permission
        if not access_token.can_perform(operation):
            return False, f"Operation {operation.value} not allowed"
        
        # Check memory type permission
        if memory_type and memory_type not in access_token.allowed_memory_types:
            return False, f"Memory type {memory_type} not allowed"
        
        # Check cross-persona access
        if target_persona and target_persona != access_token.persona:
            authorized = await self._authorize_cross_persona_access(
                access_token.persona,
                target_persona,
                operation
            )
            if not authorized:
                return False, f"Cross-persona access denied from {access_token.persona} to {target_persona}"
        
        # Log successful authorization
        self._log_operation(
            access_token.persona,
            f"authorize_{operation.value}",
            {"target": target_persona, "memory_type": memory_type}
        )
        
        return True, None
    
    async def _authorize_cross_persona_access(
        self,
        source_persona: str,
        target_persona: str,
        operation: MemoryOperation
    ) -> bool:
        """Authorize cross-persona memory access"""
        
        if source_persona not in self.policies:
            return False
        
        policy = self.policies[source_persona]
        
        # Check read operations
        if operation in {MemoryOperation.RETRIEVE, MemoryOperation.SEARCH, MemoryOperation.LIST}:
            return target_persona in policy.can_read_from
        
        # Check write operations
        if operation in {MemoryOperation.STORE, MemoryOperation.UPDATE}:
            return target_persona in policy.can_write_to
        
        # Check delete operations - only allowed on own memories or with admin access
        if operation == MemoryOperation.DELETE:
            if source_persona == target_persona:
                return True
            access_config = self.DEFAULT_ACCESS_MATRIX.get(source_persona, {})
            return access_config.get('access_level') == AccessLevel.ADMIN
        
        return False
    
    def _check_rate_limit(self, persona: str) -> bool:
        """Check if persona has exceeded rate limit"""
        now = datetime.now()
        
        # Initialize rate limiter for persona if not exists
        if persona not in self.rate_limiters:
            self.rate_limiters[persona] = []
        
        # Remove operations older than 1 minute
        self.rate_limiters[persona] = [
            timestamp for timestamp in self.rate_limiters[persona]
            if (now - timestamp).seconds < 60
        ]
        
        # Check rate limit
        policy = self.policies.get(persona)
        if policy and len(self.rate_limiters[persona]) >= policy.rate_limit:
            return False
        
        # Add current operation
        self.rate_limiters[persona].append(now)
        return True
    
    def _log_operation(self, persona: str, operation: str, details: Dict):
        """Log an access control operation"""
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'persona': persona,
            'operation': operation,
            'details': details
        }
        
        self.operation_log.append(log_entry)
        
        # Keep only last 10000 entries
        if len(self.operation_log) > 10000:
            self.operation_log = self.operation_log[-10000:]
    
    async def revoke_token(self, token: str) -> bool:
        """Revoke an access token"""
        if token in self.tokens:
            persona = self.tokens[token].persona
            del self.tokens[token]
            self._log_operation(persona, "revoke_token", {"status": "success"})
            logger.info(f"Revoked token for {persona}")
            return True
        return False
    
    async def get_access_matrix(self, persona: str) -> Optional[Dict]:
        """Get access matrix for a persona"""
        if persona not in self.policies:
            return None
        
        policy = self.policies[persona]
        return {
            'persona': persona,
            'can_read_from': list(policy.can_read_from),
            'can_write_to': list(policy.can_write_to),
            'can_share_with': list(policy.can_share_with),
            'restricted_memory_types': list(policy.restricted_memory_types),
            'max_memory_size': policy.max_memory_size,
            'rate_limit': policy.rate_limit
        }
    
    async def update_access_policy(
        self,
        persona: str,
        updates: Dict
    ) -> bool:
        """Update access policy for a persona (requires admin)"""
        if persona not in self.policies:
            return False
        
        policy = self.policies[persona]
        
        # Update allowed fields
        if 'can_read_from' in updates:
            policy.can_read_from = set(updates['can_read_from'])
        
        if 'can_write_to' in updates:
            policy.can_write_to = set(updates['can_write_to'])
        
        if 'can_share_with' in updates:
            policy.can_share_with = set(updates['can_share_with'])
        
        if 'rate_limit' in updates:
            policy.rate_limit = updates['rate_limit']
        
        self._log_operation("system", "update_policy", {"persona": persona, "updates": updates})
        logger.info(f"Updated access policy for {persona}")
        return True
    
    def get_audit_log(
        self,
        persona: Optional[str] = None,
        operation: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict]:
        """Get audit log of access control operations"""
        logs = self.operation_log
        
        # Filter by persona if specified
        if persona:
            logs = [log for log in logs if log['persona'] == persona]
        
        # Filter by operation if specified
        if operation:
            logs = [log for log in logs if log['operation'] == operation]
        
        # Return limited results
        return logs[-limit:]
    
    def get_active_tokens(self) -> Dict[str, Dict]:
        """Get information about active tokens"""
        active = {}
        
        for token_hash, token_obj in self.tokens.items():
            if token_obj.is_valid():
                active[token_hash] = {
                    'persona': token_obj.persona,
                    'created_at': token_obj.created_at.isoformat(),
                    'expires_at': token_obj.expires_at.isoformat(),
                    'access_level': token_obj.access_level.name
                }
        
        return active
    
    async def cleanup_expired_tokens(self):
        """Remove expired tokens"""
        expired = []
        
        for token_hash, token_obj in self.tokens.items():
            if not token_obj.is_valid():
                expired.append(token_hash)
        
        for token_hash in expired:
            del self.tokens[token_hash]
        
        if expired:
            logger.info(f"Cleaned up {len(expired)} expired tokens")
        
        return len(expired)


# Singleton instance
_access_control_manager: Optional[AccessControlManager] = None


def get_access_control_manager() -> AccessControlManager:
    """Get or create the singleton AccessControlManager instance"""
    global _access_control_manager
    
    if _access_control_manager is None:
        _access_control_manager = AccessControlManager()
    
    return _access_control_manager