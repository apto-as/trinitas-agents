#!/usr/bin/env python3
"""
Trinitas v3.5 MCP Engine Configuration
Central configuration for the MCP Engine backend service
"""

import os
from dataclasses import dataclass
from typing import Dict, Optional, List
from enum import Enum

class ServiceMode(Enum):
    """Service operation modes"""
    STANDALONE = "standalone"      # Engine runs independently
    INTEGRATED = "integrated"      # Engine integrates with v35-mcp-tools
    DISTRIBUTED = "distributed"    # Engine runs in distributed mode

@dataclass
class EngineConfig:
    """Main engine configuration"""
    # Service endpoints
    host: str = "0.0.0.0"
    port: int = 8000
    
    # Backend services
    claude_mcp_url: str = "http://localhost:8001"
    local_llm_url: str = "http://localhost:8002"
    redis_url: str = "redis://localhost:6379"
    
    # Operation mode
    mode: ServiceMode = ServiceMode.INTEGRATED
    
    # Performance settings
    max_concurrent_tasks: int = 10
    request_timeout: int = 60
    cache_ttl: int = 3600
    
    # Security settings
    enable_auth: bool = True
    api_key: Optional[str] = None
    
    # Monitoring
    enable_metrics: bool = True
    metrics_port: int = 9090
    
    # Logging
    log_level: str = "INFO"
    log_format: str = "json"
    
    @classmethod
    def from_env(cls) -> 'EngineConfig':
        """Load configuration from environment variables"""
        return cls(
            host=os.getenv("ENGINE_HOST", "0.0.0.0"),
            port=int(os.getenv("ENGINE_PORT", "8000")),
            claude_mcp_url=os.getenv("CLAUDE_MCP_URL", "http://localhost:8001"),
            local_llm_url=os.getenv("LOCAL_LLM_URL", "http://localhost:8002"),
            redis_url=os.getenv("REDIS_URL", "redis://localhost:6379"),
            mode=ServiceMode(os.getenv("ENGINE_MODE", "integrated")),
            max_concurrent_tasks=int(os.getenv("MAX_CONCURRENT_TASKS", "10")),
            request_timeout=int(os.getenv("REQUEST_TIMEOUT", "60")),
            cache_ttl=int(os.getenv("CACHE_TTL", "3600")),
            enable_auth=os.getenv("ENABLE_AUTH", "true").lower() == "true",
            api_key=os.getenv("API_KEY"),
            enable_metrics=os.getenv("ENABLE_METRICS", "true").lower() == "true",
            metrics_port=int(os.getenv("METRICS_PORT", "9090")),
            log_level=os.getenv("LOG_LEVEL", "INFO"),
            log_format=os.getenv("LOG_FORMAT", "json")
        )

@dataclass
class PersonaConfig:
    """Persona-specific configuration"""
    name: str
    display_name: str
    mythology_name: str
    executor_preference: str  # 'claude' or 'local_llm'
    capabilities: List[str]
    temperature: float = 0.7
    max_tokens: int = 2000
    
class PersonaConfigs:
    """All persona configurations"""
    
    SPRINGFIELD = PersonaConfig(
        name="springfield",
        display_name="Springfield",
        mythology_name="Athena",
        executor_preference="claude",
        capabilities=["strategy", "architecture", "planning", "coordination"],
        temperature=0.7
    )
    
    KRUKAI = PersonaConfig(
        name="krukai",
        display_name="Krukai",
        mythology_name="Artemis",
        executor_preference="claude",
        capabilities=["optimization", "performance", "technical_excellence", "quality"],
        temperature=0.5
    )
    
    VECTOR = PersonaConfig(
        name="vector",
        display_name="Vector",
        mythology_name="Hestia",
        executor_preference="claude",
        capabilities=["security", "risk_assessment", "vulnerability_analysis", "compliance"],
        temperature=0.3
    )
    
    GROZA = PersonaConfig(
        name="groza",
        display_name="Groza",
        mythology_name="Bellona",
        executor_preference="local_llm",
        capabilities=["tactical", "leadership", "coordination", "execution"],
        temperature=0.6
    )
    
    LITTARA = PersonaConfig(
        name="littara",
        display_name="Littara",
        mythology_name="Seshat",
        executor_preference="local_llm",
        capabilities=["documentation", "implementation", "details", "precision"],
        temperature=0.4
    )
    
    @classmethod
    def get_all(cls) -> Dict[str, PersonaConfig]:
        """Get all persona configurations"""
        return {
            "springfield": cls.SPRINGFIELD,
            "krukai": cls.KRUKAI,
            "vector": cls.VECTOR,
            "groza": cls.GROZA,
            "littara": cls.LITTARA
        }
    
    @classmethod
    def get_by_name(cls, name: str) -> Optional[PersonaConfig]:
        """Get persona config by any name variant"""
        name_lower = name.lower()
        
        # Direct mapping
        all_configs = cls.get_all()
        if name_lower in all_configs:
            return all_configs[name_lower]
        
        # Check display names and mythology names
        for config in all_configs.values():
            if name_lower in [config.display_name.lower(), config.mythology_name.lower()]:
                return config
        
        return None

# Global configuration instance
config = EngineConfig.from_env()
personas = PersonaConfigs()