"""
Middleware configuration for TMWS API.
"""

import logging
import time
from typing import Callable, Dict, Any
import uuid

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.middleware.sessions import SessionMiddleware

from ..core.config import get_settings
from .security import SecurityHeaders

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


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Rate limiting middleware."""
    
    def __init__(self, app, calls: int = 100, period: int = 60):
        super().__init__(app)
        self.calls = calls
        self.period = period
        self.clients = {}
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        if not settings.rate_limit_enabled:
            return await call_next(request)
        
        client_ip = request.client.host if request.client else "unknown"
        current_time = time.time()
        
        # Clean old entries
        self.clients = {
            ip: times for ip, times in self.clients.items()
            if times[-1] > current_time - self.period
        }
        
        # Check rate limit
        if client_ip in self.clients:
            # Remove old requests outside the time window
            self.clients[client_ip] = [
                req_time for req_time in self.clients[client_ip]
                if req_time > current_time - self.period
            ]
            
            # Check if limit exceeded
            if len(self.clients[client_ip]) >= self.calls:
                logger.warning(f"Rate limit exceeded for IP: {client_ip}")
                return Response(
                    content="Rate limit exceeded",
                    status_code=429,
                    headers={
                        "Retry-After": str(self.period),
                        "X-RateLimit-Limit": str(self.calls),
                        "X-RateLimit-Remaining": "0",
                        "X-RateLimit-Reset": str(int(current_time + self.period)),
                    }
                )
        else:
            self.clients[client_ip] = []
        
        # Add current request
        self.clients[client_ip].append(current_time)
        
        # Process request
        response = await call_next(request)
        
        # Add rate limit headers
        remaining = max(0, self.calls - len(self.clients[client_ip]))
        response.headers["X-RateLimit-Limit"] = str(self.calls)
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        response.headers["X-RateLimit-Reset"] = str(int(current_time + self.period))
        
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
    
    # 3. Rate limiting
    if settings.rate_limit_enabled:
        app.add_middleware(
            RateLimitMiddleware,
            calls=settings.rate_limit_requests,
            period=settings.rate_limit_period
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
            https_only=settings.session_cookie_secure,
            httponly=settings.session_cookie_httponly
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