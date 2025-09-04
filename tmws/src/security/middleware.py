"""
Security Middleware Module
Hestia's Comprehensive Request Protection System

"……すべてのリクエストを疑って、完璧な防御を提供します……"
"""

import time
import logging
import asyncio
from typing import Callable, Dict, Any, Optional
from datetime import datetime

from fastapi import Request, Response, HTTPException, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from .validators import InputValidator, SQLInjectionValidator, VectorValidator, ValidationError
from .rate_limiter import RateLimiter, DDoSProtection
from .audit_logger import SecurityAuditLogger, SecurityEvent, SecurityEventType, SecurityEventSeverity, get_audit_logger
from ..core.config import get_settings

logger = logging.getLogger(__name__)


class SecurityMiddleware(BaseHTTPMiddleware):
    """
    Comprehensive security middleware.
    Hestia's All-in-One Request Protection System.
    """
    
    def __init__(
        self,
        app: ASGIApp,
        rate_limiter: Optional[RateLimiter] = None,
        audit_logger: Optional[SecurityAuditLogger] = None
    ):
        """Initialize security middleware."""
        super().__init__(app)
        self.settings = get_settings()
        self.rate_limiter = rate_limiter or RateLimiter()
        self.ddos_protection = DDoSProtection(self.rate_limiter)
        self.audit_logger = audit_logger or get_audit_logger()
        
        # Validators
        self.input_validator = InputValidator()
        self.sql_validator = SQLInjectionValidator()
        self.vector_validator = VectorValidator()
        
        # Security headers
        self.security_headers = HestiaSecurityHeaders(self.settings)
        
        # Statistics
        self.stats = {
            'total_requests': 0,
            'blocked_requests': 0,
            'security_violations': 0,
            'start_time': datetime.utcnow()
        }
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Process request through security checks.
        
        Args:
            request: Incoming request
            call_next: Next middleware/handler
            
        Returns:
            Response with security headers
        """
        start_time = time.time()
        self.stats['total_requests'] += 1
        
        try:
            # Skip security checks for health endpoints (but still add headers)
            if self._is_health_endpoint(request):
                response = await call_next(request)
                return self._add_security_headers(response)
            
            # Phase 1: Pre-request Security Checks
            await self._pre_request_security_checks(request)
            
            # Phase 2: Process Request
            response = await call_next(request)
            
            # Phase 3: Post-request Security Processing
            await self._post_request_security_processing(request, response, start_time)
            
            # Phase 4: Add Security Headers
            response = self._add_security_headers(response)
            
            return response
            
        except HTTPException as e:
            # Security violation - log and return secure error response
            await self._handle_security_violation(request, e, start_time)
            raise
            
        except Exception as e:
            # Unexpected error - log and return generic error
            logger.error(f"Unexpected error in security middleware: {e}")
            
            await self.audit_logger.log_event(
                event_type=SecurityEventType.SYSTEM_COMPROMISE,
                severity=SecurityEventSeverity.CRITICAL,
                client_ip=self._get_client_ip(request),
                message="Unexpected error in security middleware",
                request=request,
                details={'error': str(e)}
            )
            
            # Return generic error response (don't expose internal details)
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={"detail": "Internal server error"},
                headers=self.security_headers.get_headers()
            )
    
    async def _pre_request_security_checks(self, request: Request) -> None:
        """Run pre-request security checks."""
        client_ip = self._get_client_ip(request)
        
        # 1. DDoS Protection
        if not await self.ddos_protection.analyze_traffic(request):
            self.stats['blocked_requests'] += 1
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Service temporarily unavailable"
            )
        
        # 2. Rate Limiting
        endpoint_type = self._get_endpoint_type(request)
        try:
            await self.rate_limiter.check_rate_limit(request, endpoint_type)
        except HTTPException:
            self.stats['blocked_requests'] += 1
            raise
        
        # 3. Input Validation
        await self._validate_request_inputs(request)
        
        # 4. Security Pattern Detection
        await self._detect_security_patterns(request)
    
    async def _validate_request_inputs(self, request: Request) -> None:
        """Validate all request inputs."""
        try:
            # Validate URL path
            path = str(request.url.path)
            self.input_validator.validate_string(
                path, "url_path", max_length=2048, required=False
            )
            
            # Check for SQL injection in URL
            self.sql_validator.validate_query_parameter(path, "url_path")
            
            # Validate query parameters
            for key, value in request.query_params.items():
                self.input_validator.validate_string(
                    key, f"query_key_{key}", max_length=256
                )
                self.input_validator.validate_string(
                    value, f"query_param_{key}", max_length=2048, required=False
                )
                self.sql_validator.validate_query_parameter(value, f"query_param_{key}")
            
            # Validate headers (selective)
            critical_headers = ['User-Agent', 'Referer', 'Origin']
            for header_name in critical_headers:
                header_value = request.headers.get(header_name)
                if header_value:
                    self.input_validator.validate_string(
                        header_value, f"header_{header_name}", 
                        max_length=2048, required=False
                    )
            
            # Note: Request body validation is handled by individual endpoints
            # since different endpoints accept different data formats
            
        except ValidationError as e:
            self.stats['security_violations'] += 1
            
            await self.audit_logger.log_event(
                event_type=SecurityEventType.INPUT_VALIDATION_FAILED,
                severity=SecurityEventSeverity.HIGH,
                client_ip=self._get_client_ip(request),
                message=f"Input validation failed: {e.message}",
                request=request,
                details={'field': e.field, 'value': str(e.value)[:100]},
                blocked=True
            )
            
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid input data"
            )
    
    async def _detect_security_patterns(self, request: Request) -> None:
        """Detect malicious patterns in requests."""
        client_ip = self._get_client_ip(request)
        url_path = str(request.url.path).lower()
        user_agent = request.headers.get('User-Agent', '').lower()
        
        # SQL injection patterns in URL
        sql_patterns = [
            'union select', 'drop table', 'insert into', 'delete from',
            'exec xp_', 'sp_executesql', "' or '1'='1", '" or "1"="1'
        ]
        
        for pattern in sql_patterns:
            if pattern in url_path or pattern in str(request.url.query).lower():
                await self.audit_logger.log_event(
                    event_type=SecurityEventType.SQL_INJECTION_ATTEMPT,
                    severity=SecurityEventSeverity.CRITICAL,
                    client_ip=client_ip,
                    message=f"SQL injection pattern detected: {pattern}",
                    request=request,
                    details={'pattern': pattern},
                    blocked=True
                )
                
                self.stats['security_violations'] += 1
                
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Forbidden"
                )
        
        # XSS patterns
        xss_patterns = [
            '<script', 'javascript:', 'vbscript:', 'onload=', 'onerror='
        ]
        
        for pattern in xss_patterns:
            if pattern in url_path:
                await self.audit_logger.log_event(
                    event_type=SecurityEventType.XSS_ATTEMPT,
                    severity=SecurityEventSeverity.HIGH,
                    client_ip=client_ip,
                    message=f"XSS pattern detected: {pattern}",
                    request=request,
                    details={'pattern': pattern},
                    blocked=True
                )
                
                self.stats['security_violations'] += 1
                
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Forbidden"
                )
        
        # Path traversal patterns
        traversal_patterns = ['../../../', '..\\..\\..\\', '%2e%2e%2f', '%2e%2e%5c']
        
        for pattern in traversal_patterns:
            if pattern in url_path:
                await self.audit_logger.log_event(
                    event_type=SecurityEventType.PATH_TRAVERSAL_ATTEMPT,
                    severity=SecurityEventSeverity.HIGH,
                    client_ip=client_ip,
                    message=f"Path traversal pattern detected: {pattern}",
                    request=request,
                    details={'pattern': pattern},
                    blocked=True
                )
                
                self.stats['security_violations'] += 1
                
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Forbidden"
                )
    
    async def _post_request_security_processing(
        self, 
        request: Request, 
        response: Response,
        start_time: float
    ) -> None:
        """Process security after request completion."""
        processing_time = time.time() - start_time
        client_ip = self._get_client_ip(request)
        
        # Log successful requests (for monitoring)
        if response.status_code < 400:
            # Only log sensitive operations
            if self._is_sensitive_endpoint(request):
                await self.audit_logger.log_event(
                    event_type=SecurityEventType.SENSITIVE_DATA_ACCESS,
                    severity=SecurityEventSeverity.MEDIUM,
                    client_ip=client_ip,
                    message="Sensitive endpoint accessed",
                    request=request,
                    details={
                        'status_code': response.status_code,
                        'processing_time': processing_time
                    }
                )
        
        # Log error responses
        elif response.status_code >= 400:
            severity = (
                SecurityEventSeverity.HIGH if response.status_code == 403
                else SecurityEventSeverity.MEDIUM
            )
            
            await self.audit_logger.log_event(
                event_type=SecurityEventType.UNAUTHORIZED_ACCESS,
                severity=severity,
                client_ip=client_ip,
                message=f"HTTP {response.status_code} response",
                request=request,
                details={
                    'status_code': response.status_code,
                    'processing_time': processing_time
                }
            )
    
    async def _handle_security_violation(
        self,
        request: Request,
        exception: HTTPException,
        start_time: float
    ) -> None:
        """Handle security violation."""
        self.stats['blocked_requests'] += 1
        self.stats['security_violations'] += 1
        
        processing_time = time.time() - start_time
        client_ip = self._get_client_ip(request)
        
        # Determine event type based on status code
        event_type = {
            401: SecurityEventType.UNAUTHORIZED_ACCESS,
            403: SecurityEventType.PERMISSION_DENIED,
            429: SecurityEventType.RATE_LIMIT_EXCEEDED,
        }.get(exception.status_code, SecurityEventType.UNAUTHORIZED_ACCESS)
        
        await self.audit_logger.log_event(
            event_type=event_type,
            severity=SecurityEventSeverity.HIGH,
            client_ip=client_ip,
            message=f"Security violation: {exception.detail}",
            request=request,
            details={
                'status_code': exception.status_code,
                'processing_time': processing_time,
                'blocked': True
            },
            blocked=True
        )
    
    def _add_security_headers(self, response: Response) -> Response:
        """Add security headers to response."""
        headers = self.security_headers.get_headers()
        
        for name, value in headers.items():
            response.headers[name] = value
        
        return response
    
    def _get_client_ip(self, request: Request) -> str:
        """Extract client IP address."""
        # Same logic as RateLimiter
        forwarded = request.headers.get('X-Forwarded-For')
        if forwarded:
            return forwarded.split(',')[0].strip()
        
        real_ip = request.headers.get('X-Real-IP')
        if real_ip:
            return real_ip
        
        return request.client.host if request.client else "unknown"
    
    def _get_endpoint_type(self, request: Request) -> str:
        """Determine endpoint type for rate limiting."""
        path = request.url.path.lower()
        
        if '/auth/login' in path:
            return 'login'
        elif '/auth/register' in path:
            return 'register'
        elif '/memory/search' in path:
            return 'search'
        elif '/embeddings' in path:
            return 'embedding'
        else:
            return 'default'
    
    def _is_health_endpoint(self, request: Request) -> bool:
        """Check if endpoint is a health check."""
        health_paths = ['/health', '/status', '/ping', '/metrics']
        return any(path in request.url.path.lower() for path in health_paths)
    
    def _is_sensitive_endpoint(self, request: Request) -> bool:
        """Check if endpoint handles sensitive data."""
        sensitive_paths = ['/admin', '/users', '/memory', '/personas']
        return any(path in request.url.path.lower() for path in sensitive_paths)
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get middleware statistics."""
        uptime = (datetime.utcnow() - self.stats['start_time']).total_seconds()
        
        return {
            'uptime_seconds': uptime,
            'total_requests': self.stats['total_requests'],
            'blocked_requests': self.stats['blocked_requests'],
            'security_violations': self.stats['security_violations'],
            'block_rate': (
                self.stats['blocked_requests'] / max(self.stats['total_requests'], 1)
            ),
            'requests_per_second': self.stats['total_requests'] / max(uptime, 1),
            'rate_limiter_stats': self.rate_limiter.get_statistics()
        }


class HestiaSecurityHeaders:
    """
    Security headers management.
    Hestia's Paranoid Header Policy.
    """
    
    def __init__(self, settings):
        """Initialize security headers."""
        self.settings = settings
        self._base_headers = self._get_base_security_headers()
        self._csp_policy = self._build_csp_policy()
    
    def _get_base_security_headers(self) -> Dict[str, str]:
        """Get base security headers."""
        headers = {
            # Prevent MIME type sniffing
            "X-Content-Type-Options": "nosniff",
            
            # Prevent clickjacking
            "X-Frame-Options": "DENY",
            
            # XSS protection (legacy but still useful)
            "X-XSS-Protection": "1; mode=block",
            
            # Referrer policy
            "Referrer-Policy": "strict-origin-when-cross-origin",
            
            # Remove server information
            "Server": "TMWS",
            
            # Permissions policy (disable dangerous features)
            "Permissions-Policy": (
                "geolocation=(), microphone=(), camera=(), "
                "payment=(), usb=(), magnetometer=(), gyroscope=(), speaker=()"
            ),
        }
        
        # Add HSTS in production
        if self.settings.is_production:
            headers["Strict-Transport-Security"] = (
                "max-age=31536000; includeSubDomains; preload"
            )
        
        return headers
    
    def _build_csp_policy(self) -> str:
        """Build Content Security Policy."""
        if self.settings.is_development:
            # Relaxed CSP for development
            return (
                "default-src 'self'; "
                "script-src 'self' 'unsafe-inline' 'unsafe-eval'; "
                "style-src 'self' 'unsafe-inline'; "
                "img-src 'self' data: https:; "
                "font-src 'self'; "
                "connect-src 'self'; "
                "frame-ancestors 'none'"
            )
        else:
            # Strict CSP for production
            return (
                "default-src 'self'; "
                "script-src 'self'; "
                "style-src 'self'; "
                "img-src 'self' data: https:; "
                "font-src 'self'; "
                "connect-src 'self'; "
                "frame-ancestors 'none'; "
                "base-uri 'self'; "
                "form-action 'self'"
            )
    
    def get_headers(self) -> Dict[str, str]:
        """Get all security headers."""
        headers = self._base_headers.copy()
        
        # Add CSP if enabled
        if self.settings.csp_enabled:
            headers["Content-Security-Policy"] = self._csp_policy
        
        return headers
    
    def get_cors_headers(self, origin: str = None) -> Dict[str, str]:
        """Get CORS headers."""
        if not origin or origin not in self.settings.cors_origins:
            return {}
        
        return {
            "Access-Control-Allow-Origin": origin,
            "Access-Control-Allow-Credentials": str(self.settings.cors_credentials).lower(),
            "Access-Control-Allow-Methods": ", ".join(self.settings.cors_methods),
            "Access-Control-Allow-Headers": ", ".join(self.settings.cors_headers),
            "Access-Control-Max-Age": "86400"  # 24 hours
        }


class RequestBodyValidator:
    """
    Request body validation middleware (for specific endpoints).
    Use this for endpoints that need request body validation.
    """
    
    def __init__(self):
        self.input_validator = InputValidator()
        self.vector_validator = VectorValidator()
    
    async def validate_json_body(
        self, 
        body: Dict[str, Any], 
        endpoint: str
    ) -> Dict[str, Any]:
        """
        Validate JSON request body.
        
        Args:
            body: Request body data
            endpoint: Endpoint path for context
            
        Returns:
            Validated and sanitized body
            
        Raises:
            ValidationError: If validation fails
        """
        # General JSON validation
        validated_body = self.input_validator.validate_json_field(
            body, "request_body", max_depth=5
        )
        
        # Endpoint-specific validation
        if '/memory' in endpoint:
            validated_body = await self._validate_memory_request(validated_body)
        elif '/embeddings' in endpoint:
            validated_body = await self._validate_embedding_request(validated_body)
        elif '/auth' in endpoint:
            validated_body = await self._validate_auth_request(validated_body)
        
        return validated_body
    
    async def _validate_memory_request(self, body: Dict[str, Any]) -> Dict[str, Any]:
        """Validate memory-related requests."""
        # Validate vector data if present
        if 'vector' in body:
            body['vector'] = self.vector_validator.validate_vector(body['vector'])
        
        if 'embedding' in body:
            body['embedding'] = self.vector_validator.validate_vector(body['embedding'])
        
        # Validate content length
        if 'content' in body:
            content = str(body['content'])
            if len(content) > 10000:  # 10KB limit
                raise ValidationError(
                    "Content too long", "content", content
                )
            body['content'] = self.input_validator.validate_string(
                content, "content", max_length=10000
            )
        
        return body
    
    async def _validate_embedding_request(self, body: Dict[str, Any]) -> Dict[str, Any]:
        """Validate embedding requests."""
        if 'text' in body:
            body['text'] = self.vector_validator.validate_text_for_embedding(
                body['text']
            )
        
        return body
    
    async def _validate_auth_request(self, body: Dict[str, Any]) -> Dict[str, Any]:
        """Validate authentication requests."""
        if 'username' in body:
            body['username'] = self.input_validator.validate_string(
                body['username'], "username", max_length=64
            )
        
        if 'email' in body:
            body['email'] = self.input_validator.validate_email(body['email'])
        
        if 'password' in body:
            # Don't log password in validation errors
            try:
                self.input_validator.validate_password(
                    body['password'], body.get('username')
                )
            except ValidationError as e:
                # Remove password from error details
                e.value = "[REDACTED]"
                raise
        
        return body


# Global instances
_security_middleware: Optional[SecurityMiddleware] = None
_request_body_validator: Optional[RequestBodyValidator] = None

def get_security_middleware() -> SecurityMiddleware:
    """Get global security middleware instance."""
    global _security_middleware
    if _security_middleware is None:
        _security_middleware = SecurityMiddleware(None)  # App will be set later
    return _security_middleware

def get_request_body_validator() -> RequestBodyValidator:
    """Get global request body validator."""
    global _request_body_validator  
    if _request_body_validator is None:
        _request_body_validator = RequestBodyValidator()
    return _request_body_validator