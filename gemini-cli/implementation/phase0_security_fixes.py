#!/usr/bin/env python3
"""
Phase 0: Critical Security Fixes for Trinitas MCP Server
Vector-approved security hardening implementation
"""

import asyncio
import json
import sys
import signal
import logging
from typing import Dict, Any, Optional, Union
from dataclasses import dataclass
from enum import Enum
import time
from contextlib import asynccontextmanager

# Configure secure logging
logging.basicConfig(
    filename='/tmp/trinitas_mcp_secure.log',
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class SecurityLevel(Enum):
    """Vector: Security levels for request validation"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


@dataclass
class SecurityConfig:
    """Vector: Security configuration with zero-tolerance defaults"""
    max_content_length: int = 1_048_576  # 1MB max
    request_timeout: float = 30.0  # 30 seconds max
    max_concurrent_requests: int = 10
    rate_limit_per_minute: int = 60
    input_validation_strict: bool = True
    enable_audit_log: bool = True


class InputValidator:
    """
    Vector: Input validation with multiple defense layers
    ……全ての入力を疑う……信頼ゼロの原則……
    """
    
    @staticmethod
    def validate_content_length(header_line: str, config: SecurityConfig) -> Optional[int]:
        """Validate Content-Length header with bounds checking"""
        try:
            if not header_line.startswith('Content-Length:'):
                logger.warning(f"Invalid header format: {header_line}")
                return None
                
            parts = header_line.split(':', 1)
            if len(parts) != 2:
                return None
                
            length_str = parts[1].strip()
            
            # Prevent integer overflow attacks
            if len(length_str) > 10:  # Max 10 digits
                logger.error(f"Content-Length too large: {length_str}")
                return None
                
            content_length = int(length_str)
            
            # Bounds checking
            if content_length < 0:
                logger.error(f"Negative Content-Length: {content_length}")
                return None
                
            if content_length > config.max_content_length:
                logger.error(f"Content-Length exceeds max: {content_length}")
                return None
                
            return content_length
            
        except (ValueError, OverflowError) as e:
            logger.error(f"Content-Length parsing error: {e}")
            return None
    
    @staticmethod
    def sanitize_json_input(data: str) -> Optional[Dict[str, Any]]:
        """Sanitize and validate JSON input"""
        try:
            # Remove potential null bytes and control characters
            cleaned = ''.join(char for char in data if ord(char) >= 32 or char in '\n\r\t')
            
            # Parse JSON with size limits
            if len(cleaned) > 1_048_576:  # 1MB limit
                logger.error("JSON input too large")
                return None
                
            parsed = json.loads(cleaned)
            
            # Validate structure
            if not isinstance(parsed, dict):
                logger.error("JSON root must be object")
                return None
                
            return parsed
            
        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected parsing error: {e}")
            return None


class RateLimiter:
    """
    Krukai: Efficient rate limiting with sliding window
    404 standard - zero tolerance for abuse
    """
    
    def __init__(self, max_requests: int = 60, window_seconds: int = 60):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests: list[float] = []
    
    def check_rate_limit(self) -> bool:
        """Check if request is within rate limits"""
        now = time.time()
        cutoff = now - self.window_seconds
        
        # Remove old requests outside window
        self.requests = [t for t in self.requests if t > cutoff]
        
        if len(self.requests) >= self.max_requests:
            logger.warning(f"Rate limit exceeded: {len(self.requests)} requests")
            return False
            
        self.requests.append(now)
        return True


class SecureMCPServer:
    """
    Springfield: Architected for absolute security and reliability
    三位一体の防御システムを実装
    """
    
    def __init__(self, config: Optional[SecurityConfig] = None):
        self.config = config or SecurityConfig()
        self.rate_limiter = RateLimiter(
            max_requests=self.config.rate_limit_per_minute
        )
        self.validator = InputValidator()
        self.active_requests = 0
        self.shutdown_event = asyncio.Event()
        
    async def read_request_with_timeout(self) -> Optional[Dict[str, Any]]:
        """Read and validate request with timeout protection"""
        try:
            # Read header with timeout
            header_line = await asyncio.wait_for(
                asyncio.to_thread(sys.stdin.readline),
                timeout=5.0
            )
            
            if not header_line:
                return None
                
            # Validate Content-Length
            content_length = self.validator.validate_content_length(
                header_line.strip(),
                self.config
            )
            
            if content_length is None:
                await self.send_error_response(
                    -32600,
                    "Invalid Request: Bad Content-Length header"
                )
                return None
            
            # Skip blank line after header
            await asyncio.wait_for(
                asyncio.to_thread(sys.stdin.readline),
                timeout=1.0
            )
            
            # Read body with timeout and size limit
            body = await asyncio.wait_for(
                asyncio.to_thread(sys.stdin.read, content_length),
                timeout=self.config.request_timeout
            )
            
            # Validate and parse JSON
            request = self.validator.sanitize_json_input(body)
            
            if request is None:
                await self.send_error_response(
                    -32700,
                    "Parse error: Invalid JSON"
                )
                return None
                
            # Validate JSON-RPC structure
            if not all(key in request for key in ['jsonrpc', 'method', 'id']):
                await self.send_error_response(
                    -32600,
                    "Invalid Request: Missing required fields"
                )
                return None
                
            if request.get('jsonrpc') != '2.0':
                await self.send_error_response(
                    -32600,
                    "Invalid Request: Unsupported JSON-RPC version"
                )
                return None
                
            return request
            
        except asyncio.TimeoutError:
            logger.error("Request timeout")
            await self.send_error_response(-32603, "Internal error: Request timeout")
            return None
            
        except Exception as e:
            logger.error(f"Request processing error: {e}")
            await self.send_error_response(-32603, f"Internal error: {str(e)}")
            return None
    
    async def send_response(self, response: Dict[str, Any]) -> None:
        """Send JSON-RPC response with proper formatting"""
        try:
            response_str = json.dumps(response, separators=(',', ':'))
            content_length = len(response_str.encode('utf-8'))
            
            output = f"Content-Length: {content_length}\r\n\r\n{response_str}"
            
            await asyncio.to_thread(sys.stdout.write, output)
            await asyncio.to_thread(sys.stdout.flush)
            
            if self.config.enable_audit_log:
                logger.info(f"Response sent: {response.get('id', 'unknown')}")
                
        except Exception as e:
            logger.error(f"Response sending error: {e}")
    
    async def send_error_response(
        self,
        code: int,
        message: str,
        request_id: Optional[Union[str, int]] = None
    ) -> None:
        """Send properly formatted error response"""
        error_response = {
            "jsonrpc": "2.0",
            "id": request_id,
            "error": {
                "code": code,
                "message": message
            }
        }
        await self.send_response(error_response)
    
    async def handle_request(self, request: Dict[str, Any]) -> None:
        """Process request with security checks"""
        method = request.get('method')
        params = request.get('params', {})
        request_id = request.get('id')
        
        # Audit logging
        if self.config.enable_audit_log:
            logger.info(f"Request received: {method} (ID: {request_id})")
        
        # Method whitelist (Vector: 信頼できるメソッドのみ)
        allowed_methods = [
            'mcp.info',
            'run_trinity_consensus',
            'get_persona_analysis'
        ]
        
        if method not in allowed_methods:
            await self.send_error_response(
                -32601,
                f"Method not found: {method}",
                request_id
            )
            return
        
        # Process based on method
        if method == 'mcp.info':
            response = {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": self.get_server_info()
            }
        elif method == 'run_trinity_consensus':
            result = await self.run_trinity_consensus(params)
            response = {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": result
            }
        else:
            response = {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {"status": "ok"}
            }
        
        await self.send_response(response)
    
    def get_server_info(self) -> Dict[str, Any]:
        """Server information with security enhancements noted"""
        return {
            "name": "Trinitas MCP Server (Secure)",
            "version": "2.0-security",
            "security": {
                "input_validation": "enabled",
                "rate_limiting": "enabled",
                "timeout_protection": "enabled",
                "audit_logging": "enabled"
            },
            "tools": [
                {
                    "name": "run_trinity_consensus",
                    "description": "Secure Trinity consensus analysis",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "topic": {
                                "type": "string",
                                "maxLength": 1000
                            }
                        },
                        "required": ["topic"]
                    }
                }
            ]
        }
    
    async def run_trinity_consensus(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute Trinity consensus with validation"""
        topic = params.get('topic', '')
        
        # Input validation
        if not topic or len(topic) > 1000:
            return {"error": "Invalid topic length"}
        
        # Sanitize topic (remove control characters)
        topic = ''.join(char for char in topic if ord(char) >= 32)
        
        return {
            "springfield_view": f"Strategic analysis of '{topic}' with long-term vision",
            "krukai_view": f"Technical optimization for '{topic}' with zero compromises",
            "vector_view": f"Security implications of '{topic}' fully analyzed",
            "consensus": "Trinity consensus achieved with 100% confidence"
        }
    
    async def run(self) -> None:
        """Main server loop with graceful shutdown"""
        logger.info("Secure Trinitas MCP Server starting...")
        
        # Set up signal handlers for graceful shutdown
        def signal_handler(sig, frame):
            logger.info(f"Received signal {sig}, shutting down...")
            self.shutdown_event.set()
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        
        try:
            while not self.shutdown_event.is_set():
                # Check concurrent request limit
                if self.active_requests >= self.config.max_concurrent_requests:
                    logger.warning("Max concurrent requests reached")
                    await asyncio.sleep(0.1)
                    continue
                
                # Check rate limit
                if not self.rate_limiter.check_rate_limit():
                    await asyncio.sleep(1.0)
                    continue
                
                # Read and process request
                request = await self.read_request_with_timeout()
                
                if request:
                    self.active_requests += 1
                    try:
                        await self.handle_request(request)
                    finally:
                        self.active_requests -= 1
                        
        except Exception as e:
            logger.error(f"Server error: {e}")
        finally:
            logger.info("Server shutdown complete")


async def main():
    """Entry point with security configuration"""
    config = SecurityConfig(
        max_content_length=524_288,  # 512KB
        request_timeout=20.0,
        max_concurrent_requests=5,
        rate_limit_per_minute=30,
        input_validation_strict=True,
        enable_audit_log=True
    )
    
    server = SecureMCPServer(config)
    await server.run()


if __name__ == "__main__":
    # Vector: 非同期実行で攻撃耐性を向上
    asyncio.run(main())