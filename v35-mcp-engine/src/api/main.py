#!/usr/bin/env python3
"""
Trinitas v3.5 MCP Engine API
REST API for MCP Engine backend service
"""

from fastapi import FastAPI, HTTPException, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import Dict, Any, Optional, List
import logging
from datetime import datetime

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.mcp_engine import engine
from core.engine_config import config

# Configure logging
logging.basicConfig(
    level=getattr(logging, config.log_level),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI
app = FastAPI(
    title="Trinitas MCP Engine API",
    description="Backend service for Trinitas v3.5 persona execution",
    version="3.5.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request/Response models
class TaskRequest(BaseModel):
    """Single task execution request"""
    persona: str = Field(..., description="Persona name (any variant)")
    task: str = Field(..., description="Task description")
    context: Optional[Dict[str, Any]] = Field(default=None, description="Task context")
    force_executor: Optional[str] = Field(default=None, description="Force specific executor")

class CollaborativeTaskRequest(BaseModel):
    """Collaborative task execution request"""
    task: str = Field(..., description="Task description")
    personas: List[str] = Field(..., description="List of persona names")
    context: Optional[Dict[str, Any]] = Field(default=None, description="Task context")
    mode: str = Field(default="sequential", description="Execution mode: sequential or parallel")

class TaskResponse(BaseModel):
    """Task execution response"""
    success: bool
    persona: str
    mythology_name: str
    executor: str
    result: Any
    duration: float
    timestamp: str

# Authentication dependency
async def verify_api_key(x_api_key: str = Header(None)):
    """Verify API key if authentication is enabled"""
    if config.enable_auth:
        if not x_api_key or x_api_key != config.api_key:
            raise HTTPException(status_code=401, detail="Invalid or missing API key")
    return True

# Lifecycle events
@app.on_event("startup")
async def startup_event():
    """Initialize engine on startup"""
    try:
        await engine.initialize()
        logger.info("MCP Engine API started successfully")
    except Exception as e:
        logger.error(f"Failed to start MCP Engine API: {e}")
        raise

@app.on_event("shutdown")
async def shutdown_event():
    """Clean shutdown"""
    await engine.shutdown()
    logger.info("MCP Engine API shutdown complete")

# Health endpoints
@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "Trinitas MCP Engine",
        "version": "3.5.0",
        "status": "online",
        "mode": config.mode.value
    }

@app.get("/health")
async def health():
    """Health check endpoint"""
    status = await engine.get_status()
    
    # Determine overall health
    is_healthy = (
        status["initialized"] and
        (status["services"]["claude"] or status["services"]["local_llm"])
    )
    
    return {
        "healthy": is_healthy,
        "status": status,
        "timestamp": datetime.now().isoformat()
    }

@app.get("/status")
async def get_status(authenticated: bool = Depends(verify_api_key)):
    """Detailed status endpoint"""
    return await engine.get_status()

# Task execution endpoints
@app.post("/execute", response_model=TaskResponse)
async def execute_task(
    request: TaskRequest,
    authenticated: bool = Depends(verify_api_key)
):
    """Execute a single task with specified persona"""
    try:
        result = await engine.execute_task(
            persona=request.persona,
            task=request.task,
            context=request.context,
            force_executor=request.force_executor
        )
        return TaskResponse(**result)
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error in execute_task: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.post("/execute/collaborative")
async def execute_collaborative(
    request: CollaborativeTaskRequest,
    authenticated: bool = Depends(verify_api_key)
):
    """Execute task collaboratively with multiple personas"""
    try:
        result = await engine.execute_collaborative(
            task=request.task,
            personas=request.personas,
            context=request.context,
            mode=request.mode
        )
        return result
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error in execute_collaborative: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

# Persona management endpoints
@app.get("/personas")
async def list_personas(authenticated: bool = Depends(verify_api_key)):
    """List all available personas"""
    from core.engine_config import personas
    
    all_personas = personas.get_all()
    return {
        "personas": [
            {
                "name": config.name,
                "display_name": config.display_name,
                "mythology_name": config.mythology_name,
                "capabilities": config.capabilities,
                "preferred_executor": config.executor_preference
            }
            for config in all_personas.values()
        ]
    }

@app.get("/personas/{persona_name}")
async def get_persona(
    persona_name: str,
    authenticated: bool = Depends(verify_api_key)
):
    """Get details for specific persona"""
    from core.engine_config import personas
    
    persona_config = personas.get_by_name(persona_name)
    if not persona_config:
        raise HTTPException(status_code=404, detail=f"Persona not found: {persona_name}")
    
    return {
        "name": persona_config.name,
        "display_name": persona_config.display_name,
        "mythology_name": persona_config.mythology_name,
        "capabilities": persona_config.capabilities,
        "preferred_executor": persona_config.executor_preference,
        "temperature": persona_config.temperature,
        "max_tokens": persona_config.max_tokens
    }

# Metrics endpoint (if enabled)
@app.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint"""
    if not config.enable_metrics:
        raise HTTPException(status_code=404, detail="Metrics not enabled")
    
    # This would normally return Prometheus metrics
    # For now, return basic metrics
    status = await engine.get_status()
    return {
        "services_available": sum(1 for v in status["services"].values() if v),
        "personas_available": sum(1 for p in status["personas"].values() if p["available"]),
        "engine_mode": config.mode.value,
        "timestamp": datetime.now().isoformat()
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host=config.host,
        port=config.port,
        log_level=config.log_level.lower()
    )