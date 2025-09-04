"""
Redis-based Distributed Rate Limiting Middleware for TMWS API.
Scalable rate limiting across multiple application instances.
"""

import logging
import time
import json
from typing import Callable, Dict, Any, Optional
import uuid
import asyncio
import redis.asyncio as redis

from fastapi import FastAPI, Request, Response, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.middleware.sessions import SessionMiddleware
from starlette.responses import JSONResponse

from ..core.config import get_settings
from .security import SecurityHeaders

logger = logging.getLogger(__name__)
settings = get_settings()


class DistributedRateLimitMiddleware(BaseHTTPMiddleware):
    """
    Redis-based distributed rate limiting middleware.
    Supports sliding window rate limiting across multiple instances.
    """
    
    def __init__(
        self, 
        app, 
        calls: int = 100, 
        period: int = 60,
        redis_url: str = None,
        enable_fallback: bool = True
    ):
        """
        Initialize distributed rate limiter.
        
        Args:
            app: FastAPI application
            calls: Number of allowed calls per period
            period: Time period in seconds
            redis_url: Redis connection URL
            enable_fallback: Enable in-memory fallback if Redis is unavailable
        """
        super().__init__(app)
        self.calls = calls
        self.period = period
        self.redis_url = redis_url or settings.redis_url or "redis://localhost:6379"
        self.enable_fallback = enable_fallback
        self.redis_client: Optional[redis.Redis] = None
        
        # Fallback to in-memory if Redis unavailable
        self.fallback_clients = {}
        self.using_fallback = False
        
        # Initialize Redis connection
        asyncio.create_task(self._init_redis())
    
    async def _init_redis(self) -> None:
        """Initialize Redis connection with retry logic."""
        max_retries = 3
        retry_delay = 1
        
        for attempt in range(max_retries):
            try:
                self.redis_client = redis.from_url(
                    self.redis_url,
                    encoding="utf-8",
                    decode_responses=True,
                    socket_connect_timeout=5,
                    socket_timeout=5
                )
                
                # Test connection
                await self.redis_client.ping()
                self.using_fallback = False
                logger.info(f"Connected to Redis for rate limiting: {self.redis_url}")
                return
                
            except Exception as e:
                logger.warning(f"Redis connection attempt {attempt + 1} failed: {e}")
                if attempt < max_retries - 1:
                    await asyncio.sleep(retry_delay)
                    retry_delay *= 2
        
        # Fall back to in-memory
        if self.enable_fallback:
            self.using_fallback = True
            logger.warning("Redis unavailable, using in-memory rate limiting")
        else:
            logger.error("Redis unavailable and fallback disabled")
    
    async def _check_rate_limit_redis(self, client_id: str) -> tuple[bool, dict]:
        """
        Check rate limit using Redis sliding window.
        
        Returns:
            Tuple of (is_allowed, metadata)
        """
        if not self.redis_client or self.using_fallback:
            return await self._check_rate_limit_memory(client_id)
        
        try:
            current_time = time.time()
            window_start = current_time - self.period
            key = f"rate_limit:{client_id}"
            
            # Use Redis pipeline for atomic operations
            async with self.redis_client.pipeline() as pipe:
                # Remove old entries
                await pipe.zremrangebyscore(key, 0, window_start)
                
                # Count current requests in window
                await pipe.zcard(key)
                
                # Add current request if under limit (will check after)
                await pipe.zadd(key, {str(uuid.uuid4()): current_time})
                
                # Set expiry to clean up old keys
                await pipe.expire(key, self.period + 10)
                
                # Execute pipeline
                results = await pipe.execute()
                
                request_count = results[1]  # zcard result
                
                # Check if limit exceeded
                if request_count >= self.calls:
                    # Remove the just-added entry
                    await self.redis_client.zremrangebyscore(
                        key, current_time - 0.001, current_time + 0.001
                    )
                    
                    # Calculate reset time
                    oldest = await self.redis_client.zrange(key, 0, 0, withscores=True)
                    reset_time = oldest[0][1] + self.period if oldest else current_time
                    
                    return False, {
                        "limit": self.calls,
                        "remaining": 0,
                        "reset": int(reset_time),
                        "retry_after": int(reset_time - current_time)
                    }
                
                return True, {
                    "limit": self.calls,
                    "remaining": self.calls - request_count - 1,
                    "reset": int(current_time + self.period)
                }
                
        except Exception as e:
            logger.error(f"Redis rate limit check failed: {e}")
            
            # Fall back to in-memory if enabled
            if self.enable_fallback:
                self.using_fallback = True
                return await self._check_rate_limit_memory(client_id)
            
            # If no fallback, allow request but log error
            return True, {"limit": self.calls, "remaining": -1, "error": str(e)}
    
    async def _check_rate_limit_memory(self, client_id: str) -> tuple[bool, dict]:
        """
        Fallback in-memory rate limiting (not distributed).
        """
        current_time = time.time()
        window_start = current_time - self.period
        
        # Clean old entries
        self.fallback_clients = {
            ip: [t for t in times if t > window_start]
            for ip, times in self.fallback_clients.items()
            if times and times[-1] > window_start
        }
        
        # Get client's request times
        client_times = self.fallback_clients.get(client_id, [])
        
        # Check if limit exceeded
        if len(client_times) >= self.calls:
            reset_time = client_times[0] + self.period
            return False, {
                "limit": self.calls,
                "remaining": 0,
                "reset": int(reset_time),
                "retry_after": int(reset_time - current_time)
            }
        
        # Add current request
        client_times.append(current_time)
        self.fallback_clients[client_id] = client_times
        
        return True, {
            "limit": self.calls,
            "remaining": self.calls - len(client_times),
            "reset": int(current_time + self.period)
        }
    
    def _get_client_id(self, request: Request) -> str:
        """
        Get unique client identifier for rate limiting.
        Uses IP + User ID if authenticated, otherwise just IP.
        """
        client_ip = request.client.host if request.client else "unknown"
        
        # Check for authenticated user
        user_id = None
        if hasattr(request.state, "user_id"):
            user_id = request.state.user_id
        elif "user_id" in request.headers:
            user_id = request.headers["user_id"]
        
        # Combine IP and user ID for more granular limiting
        if user_id:
            return f"{client_ip}:{user_id}"
        return client_ip
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process request with rate limiting."""
        
        # Skip rate limiting if disabled
        if not settings.rate_limit_enabled:
            return await call_next(request)
        
        # Skip rate limiting for health checks
        if request.url.path in ["/health", "/metrics", "/healthz"]:
            return await call_next(request)
        
        # Get client identifier
        client_id = self._get_client_id(request)
        
        # Check rate limit
        allowed, metadata = await self._check_rate_limit_redis(client_id)
        
        # Add rate limit headers
        response = None
        if allowed:
            response = await call_next(request)
        else:
            # Rate limit exceeded
            response = JSONResponse(
                status_code=429,
                content={
                    "error": "Rate limit exceeded",
                    "message": f"Too many requests. Please retry after {metadata['retry_after']} seconds",
                    "retry_after": metadata["retry_after"]
                }
            )
        
        # Add rate limit headers
        response.headers["X-RateLimit-Limit"] = str(metadata.get("limit", self.calls))
        response.headers["X-RateLimit-Remaining"] = str(metadata.get("remaining", 0))
        response.headers["X-RateLimit-Reset"] = str(metadata.get("reset", 0))
        
        if not allowed:
            response.headers["Retry-After"] = str(metadata.get("retry_after", self.period))
        
        # Add Redis status header (for monitoring)
        response.headers["X-RateLimit-Backend"] = "redis" if not self.using_fallback else "memory"
        
        return response
    
    async def cleanup(self) -> None:
        """Cleanup Redis connection."""
        if self.redis_client:
            await self.redis_client.close()


class SecurityMiddleware(BaseHTTPMiddleware):
    """Enhanced security middleware with distributed logging."""
    
    def __init__(self, app, redis_client: Optional[redis.Redis] = None):
        super().__init__(app)
        self.redis_client = redis_client
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Add request ID for tracing
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id
        
        # Log request (optionally to Redis for centralized logging)
        start_time = time.time()
        
        log_entry = {
            "timestamp": start_time,
            "request_id": request_id,
            "method": request.method,
            "url": str(request.url),
            "client_ip": request.client.host if request.client else None,
            "user_agent": request.headers.get("user-agent"),
        }
        
        # Store in Redis if available (for distributed logging)
        if self.redis_client:
            try:
                await self.redis_client.xadd(
                    "security:requests",
                    {"data": json.dumps(log_entry)},
                    maxlen=10000  # Keep last 10k entries
                )
            except Exception as e:
                logger.warning(f"Failed to log to Redis: {e}")
        
        logger.info(f"Request started", extra=log_entry)
        
        # Process request
        response = await call_next(request)
        
        # Add security headers
        security_headers = SecurityHeaders.get_security_headers()
        for header_name, header_value in security_headers.items():
            response.headers[header_name] = header_value
        
        # Add request ID to response
        response.headers["X-Request-ID"] = request_id
        
        # Log response
        process_time = time.time() - start_time
        
        response_log = {
            "request_id": request_id,
            "status_code": response.status_code,
            "process_time": process_time,
        }
        
        # Store response metrics in Redis
        if self.redis_client:
            try:
                # Update request metrics
                await self.redis_client.hincrby("metrics:status_codes", str(response.status_code), 1)
                await self.redis_client.lpush(
                    "metrics:response_times",
                    process_time
                )
                await self.redis_client.ltrim("metrics:response_times", 0, 999)  # Keep last 1000
            except Exception as e:
                logger.warning(f"Failed to update metrics in Redis: {e}")
        
        logger.info(f"Request completed", extra=response_log)
        
        return response


def setup_middleware(app: FastAPI) -> None:
    """
    Configure all middleware for the application.
    Enhanced with Redis-based distributed features.
    """
    
    # Initialize Redis client for shared use
    redis_client = None
    if settings.redis_url:
        try:
            redis_client = redis.from_url(
                settings.redis_url,
                encoding="utf-8",
                decode_responses=True
            )
            logger.info("Redis client initialized for middleware")
        except Exception as e:
            logger.warning(f"Failed to initialize Redis client: {e}")
    
    # Session middleware (can use Redis for distributed sessions)
    if settings.secret_key:
        app.add_middleware(
            SessionMiddleware,
            secret_key=settings.secret_key,
            session_cookie="tmws_session",
            max_age=86400,  # 24 hours
            same_site="lax",
            https_only=settings.environment == "production"
        )
    
    # CORS middleware
    if settings.cors_enabled:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=settings.cors_origins,
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
            expose_headers=["X-Request-ID", "X-RateLimit-*"]
        )
    
    # GZip compression
    app.add_middleware(
        GZipMiddleware,
        minimum_size=1000  # Only compress responses > 1KB
    )
    
    # Trusted host middleware (production only)
    if settings.environment == "production" and settings.allowed_hosts:
        app.add_middleware(
            TrustedHostMiddleware,
            allowed_hosts=settings.allowed_hosts
        )
    
    # Distributed rate limiting with Redis
    app.add_middleware(
        DistributedRateLimitMiddleware,
        calls=settings.rate_limit_calls,
        period=settings.rate_limit_period,
        redis_url=settings.redis_url,
        enable_fallback=True
    )
    
    # Enhanced security middleware
    app.add_middleware(
        SecurityMiddleware,
        redis_client=redis_client
    )
    
    logger.info("Middleware stack configured with Redis enhancements")