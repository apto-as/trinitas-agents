"""
Middleware configuration for TMWS API.
"""

import logging
import time
from typing import Callable, Dict, Any, Optional
import uuid
import json
import hashlib

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.middleware.sessions import SessionMiddleware

try:
    import redis.asyncio as redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    logger.warning("Redis not available, using in-memory rate limiting")

from ..core.config import get_settings
from .security import SecurityHeaders
from ..security.audit_integration import log_security_event
from ..security.audit_logger_async import SecurityEventType, SecurityEventSeverity

logger = logging.getLogger(__name__)
settings = get_settings()


class SecurityMiddleware(BaseHTTPMiddleware):
    """Custom security middleware."""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Add request ID for tracing
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id
        
        # Log request
        start_time = time.time()
        logger.info(
            f"Request started",
            extra={
                "request_id": request_id,
                "method": request.method,
                "url": str(request.url),
                "client_ip": request.client.host if request.client else None,
                "user_agent": request.headers.get("user-agent"),
            }
        )
        
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
        logger.info(
            f"Request completed",
            extra={
                "request_id": request_id,
                "status_code": response.status_code,
                "process_time": process_time,
            }
        )
        
        return response


class DistributedRateLimitMiddleware(BaseHTTPMiddleware):
    """
    Distributed rate limiting middleware with Redis support.
    Falls back to in-memory limiting if Redis is unavailable.
    """
    
    def __init__(self, app, calls: int = 100, period: int = 60, redis_url: Optional[str] = None):
        super().__init__(app)
        self.calls = calls
        self.period = period
        self.redis_url = redis_url or "redis://localhost:6379/0"
        self.redis_client: Optional[redis.Redis] = None
        self.fallback_clients = {}  # In-memory fallback
        self.use_redis = REDIS_AVAILABLE
        
        if self.use_redis:
            try:
                self.redis_client = redis.from_url(
                    self.redis_url,
                    encoding="utf-8",
                    decode_responses=True
                )
            except Exception as e:
                logger.error(f"Failed to connect to Redis: {e}")
                self.use_redis = False
    
    async def _check_rate_limit_redis(self, client_id: str) -> tuple[bool, int]:
        """Check rate limit using Redis with sliding window."""
        try:
            key = f"rate_limit:{client_id}"
            current_time = time.time()
            window_start = current_time - self.period
            
            # Use Redis pipeline for atomic operations
            async with self.redis_client.pipeline() as pipe:
                # Remove old entries
                await pipe.zremrangebyscore(key, 0, window_start)
                # Count current entries
                await pipe.zcard(key)
                # Add current request
                await pipe.zadd(key, {str(uuid.uuid4()): current_time})
                # Set expiry
                await pipe.expire(key, self.period)
                
                results = await pipe.execute()
                request_count = results[1]
                
                if request_count >= self.calls:
                    return False, 0
                
                return True, max(0, self.calls - request_count - 1)
                
        except Exception as e:
            logger.error(f"Redis rate limit check failed: {e}")
            # Fall back to in-memory
            return await self._check_rate_limit_memory(client_id)
    
    async def _check_rate_limit_memory(self, client_id: str) -> tuple[bool, int]:
        """Fallback in-memory rate limiting."""
        current_time = time.time()
        
        # Clean old entries
        self.fallback_clients = {
            ip: times for ip, times in self.fallback_clients.items()
            if times and times[-1] > current_time - self.period
        }
        
        if client_id not in self.fallback_clients:
            self.fallback_clients[client_id] = []
        
        # Remove old requests
        self.fallback_clients[client_id] = [
            req_time for req_time in self.fallback_clients[client_id]
            if req_time > current_time - self.period
        ]
        
        # Check if limit exceeded
        if len(self.fallback_clients[client_id]) >= self.calls:
            return False, 0
        
        # Add current request
        self.fallback_clients[client_id].append(current_time)
        remaining = max(0, self.calls - len(self.fallback_clients[client_id]))
        
        return True, remaining
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        if not settings.rate_limit_enabled:
            return await call_next(request)
        
        # Generate client identifier
        client_ip = request.client.host if request.client else "unknown"
        user_agent = request.headers.get("user-agent", "")
        client_id = hashlib.md5(f"{client_ip}:{user_agent}".encode()).hexdigest()
        
        # Check rate limit
        if self.use_redis and self.redis_client:
            allowed, remaining = await self._check_rate_limit_redis(client_id)
        else:
            allowed, remaining = await self._check_rate_limit_memory(client_id)
        
        if not allowed:
            logger.warning(f"Rate limit exceeded for client: {client_id} (IP: {client_ip})")
            
            # Log security event asynchronously
            await log_security_event(
                event_type=SecurityEventType.RATE_LIMIT_EXCEEDED,
                request=request,
                severity=SecurityEventSeverity.MEDIUM,
                details={"client_id": client_id, "client_ip": client_ip}
            )
            
            return Response(
                content=json.dumps({"error": "Rate limit exceeded"}),
                status_code=429,
                media_type="application/json",
                headers={
                    "Retry-After": str(self.period),
                    "X-RateLimit-Limit": str(self.calls),
                    "X-RateLimit-Remaining": "0",
                    "X-RateLimit-Reset": str(int(time.time() + self.period)),
                }
            )
        
        # Process request
        response = await call_next(request)
        
        # Add rate limit headers
        response.headers["X-RateLimit-Limit"] = str(self.calls)
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        response.headers["X-RateLimit-Reset"] = str(int(time.time() + self.period))
        
        return response


class ErrorHandlingMiddleware(BaseHTTPMiddleware):
    """Global error handling middleware."""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        try:
            return await call_next(request)
        except Exception as exc:
            request_id = getattr(request.state, 'request_id', 'unknown')
            
            logger.error(
                f"Unhandled exception in request {request_id}: {str(exc)}",
                exc_info=True,
                extra={
                    "request_id": request_id,
                    "method": request.method,
                    "url": str(request.url),
                }
            )
            
            # Return generic error response for security
            if settings.is_production:
                return Response(
                    content='{"detail": "Internal server error"}',
                    status_code=500,
                    media_type="application/json",
                    headers={"X-Request-ID": request_id}
                )
            else:
                # In development, show more details
                return Response(
                    content=f'{{"detail": "Internal server error: {str(exc)}"}}',
                    status_code=500,
                    media_type="application/json",
                    headers={"X-Request-ID": request_id}
                )


def setup_middleware(app: FastAPI) -> None:
    """Setup all middleware for the FastAPI application."""
    
    # 1. Error handling (should be first to catch all errors)
    app.add_middleware(ErrorHandlingMiddleware)
    
    # 2. Security middleware
    app.add_middleware(SecurityMiddleware)
    
    # 3. Distributed Rate limiting with Redis
    if settings.rate_limit_enabled:
        redis_url = getattr(settings, 'redis_url', None) or "redis://localhost:6379/0"
        app.add_middleware(
            DistributedRateLimitMiddleware,
            calls=settings.rate_limit_requests,
            period=settings.rate_limit_period,
            redis_url=redis_url
        )
    
    # 4. CORS middleware
    if settings.cors_origins:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=settings.cors_origins,
            allow_credentials=settings.cors_credentials,
            allow_methods=settings.cors_methods,
            allow_headers=settings.cors_headers,
        )
        logger.info(f"CORS enabled for origins: {settings.cors_origins}")
    
    # 5. Trusted host middleware (in production)
    if settings.is_production:
        allowed_hosts = []
        for origin in settings.cors_origins:
            if origin.startswith(('http://', 'https://')):
                host = origin.split('//')[1].split('/')[0].split(':')[0]
                allowed_hosts.append(host)
        
        if allowed_hosts:
            app.add_middleware(
                TrustedHostMiddleware,
                allowed_hosts=allowed_hosts
            )
            logger.info(f"Trusted hosts: {allowed_hosts}")
    
    # 6. Session middleware (if sessions are needed)
    if settings.secret_key:
        app.add_middleware(
            SessionMiddleware,
            secret_key=settings.secret_key,
            session_cookie="tmws_session",
            max_age=1800,  # 30 minutes
            same_site=settings.session_cookie_samesite,
            https_only=settings.session_cookie_secure
        )
    
    # 7. Gzip compression (should be last)
    app.add_middleware(GZipMiddleware, minimum_size=1000)
    
    logger.info("All middleware configured successfully")


class RequestContextMiddleware(BaseHTTPMiddleware):
    """Middleware to add request context."""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Add useful context to request state
        request.state.start_time = time.time()
        request.state.user_agent = request.headers.get("user-agent", "unknown")
        request.state.client_ip = request.client.host if request.client else "unknown"
        request.state.request_size = len(await request.body()) if hasattr(request, 'body') else 0
        
        # Process request
        response = await call_next(request)
        
        # Add response metadata
        response.headers["X-Response-Time"] = str(int((time.time() - request.state.start_time) * 1000))
        response.headers["X-Content-Length"] = str(len(response.body) if hasattr(response, 'body') else 0)
        
        return response


def setup_development_middleware(app: FastAPI) -> None:
    """Setup additional middleware for development environment."""
    if not settings.is_development:
        return
    
    # Add request context middleware for development
    app.add_middleware(RequestContextMiddleware)
    
    # Add detailed logging middleware
    @app.middleware("http")
    async def log_requests(request: Request, call_next):
        start_time = time.time()
        
        logger.debug(
            f"Request details",
            extra={
                "method": request.method,
                "url": str(request.url),
                "headers": dict(request.headers),
                "query_params": dict(request.query_params),
            }
        )
        
        response = await call_next(request)
        
        process_time = time.time() - start_time
        logger.debug(
            f"Response details",
            extra={
                "status_code": response.status_code,
                "process_time": process_time,
                "response_headers": dict(response.headers),
            }
        )
        
        return response
    
    logger.info("Development middleware configured")


def get_middleware_stats() -> Dict[str, Any]:
    """Get middleware statistics (for monitoring)."""
    return {
        "security_middleware": "active",
        "rate_limiting": "active" if settings.rate_limit_enabled else "disabled",
        "cors": "active" if settings.cors_origins else "disabled",
        "compression": "active",
        "session_management": "active" if settings.secret_key else "disabled",
        "trusted_hosts": "active" if settings.is_production else "disabled",
    }