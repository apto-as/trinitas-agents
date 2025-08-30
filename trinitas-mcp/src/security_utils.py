"""
Security utilities for Trinitas v4.0
Provides secure error handling and sanitization
"""

import re
from typing import Optional, Dict, Any
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class SecurityUtils:
    """Security utility functions for safe error handling"""
    
    # Sensitive patterns to remove from error messages
    SENSITIVE_PATTERNS = [
        (r'password["\']?\s*[:=]\s*["\']?[^"\'\s]+', 'password: ***'),
        (r'api[_-]?key["\']?\s*[:=]\s*["\']?[^"\'\s]+', 'api_key: ***'),
        (r'token["\']?\s*[:=]\s*["\']?[^"\'\s]+', 'token: ***'),
        (r'/home/[^/\s]+', '/home/***'),
        (r'/Users/[^/\s]+', '/Users/***'),
        (r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', '***@***.***'),
        (r'\b(?:\d{1,3}\.){3}\d{1,3}\b', '***.***.***.***'),
        (r'line \d+ in .+\.py', 'line *** in ***.py'),
    ]
    
    # Safe error messages for common exceptions
    SAFE_ERROR_MESSAGES = {
        'FileNotFoundError': 'The requested file could not be found',
        'PermissionError': 'Permission denied for this operation',
        'ConnectionError': 'Connection failed',
        'TimeoutError': 'Operation timed out',
        'ValueError': 'Invalid value provided',
        'KeyError': 'Required key not found',
        'AttributeError': 'Invalid attribute access',
        'ImportError': 'Module import failed',
        'OSError': 'Operating system error occurred',
        'RuntimeError': 'Runtime error occurred',
        'MemoryError': 'Insufficient memory available',
        'IOError': 'Input/output operation failed',
        'IndexError': 'Index out of range',
        'TypeError': 'Type mismatch error',
        'ZeroDivisionError': 'Division by zero attempted',
        'AssertionError': 'Assertion failed',
        'NotImplementedError': 'Feature not yet implemented',
        'StopIteration': 'Iteration stopped',
        'GeneratorExit': 'Generator exited',
        'KeyboardInterrupt': 'Operation interrupted by user',
        'SystemExit': 'System exit requested',
        'Exception': 'An error occurred',
    }
    
    @classmethod
    def sanitize_error(cls, error: Exception, context: Optional[Dict[str, Any]] = None) -> str:
        """
        Sanitize error message to prevent information disclosure
        
        Args:
            error: The exception to sanitize
            context: Optional context for better error messages
            
        Returns:
            Safe error message string
        """
        error_type = type(error).__name__
        
        # Get base safe message
        safe_message = cls.SAFE_ERROR_MESSAGES.get(
            error_type, 
            'An unexpected error occurred'
        )
        
        # Add context if available and safe
        if context:
            safe_context = cls._sanitize_context(context)
            if safe_context:
                safe_message = f"{safe_message}. Context: {safe_context}"
        
        # Log the actual error for debugging (but not to user)
        logger.debug(f"Sanitized error - Original: {error}, Safe: {safe_message}")
        
        return safe_message
    
    @classmethod
    def _sanitize_context(cls, context: Dict[str, Any]) -> str:
        """Sanitize context information"""
        safe_items = []
        
        safe_keys = ['operation', 'component', 'action', 'phase', 'step']
        for key in safe_keys:
            if key in context:
                value = str(context[key])
                # Apply sensitive pattern removal
                for pattern, replacement in cls.SENSITIVE_PATTERNS:
                    value = re.sub(pattern, replacement, value, flags=re.IGNORECASE)
                safe_items.append(f"{key}={value}")
        
        return ", ".join(safe_items) if safe_items else ""
    
    @classmethod
    def sanitize_string(cls, text: str) -> str:
        """Remove sensitive information from any string"""
        sanitized = text
        for pattern, replacement in cls.SENSITIVE_PATTERNS:
            sanitized = re.sub(pattern, replacement, sanitized, flags=re.IGNORECASE)
        return sanitized
    
    @classmethod
    def create_error_response(cls, error: Exception, 
                            operation: Optional[str] = None,
                            include_type: bool = False) -> Dict[str, Any]:
        """
        Create a standardized error response
        
        Args:
            error: The exception that occurred
            operation: The operation that failed
            include_type: Whether to include error type
            
        Returns:
            Standardized error response dictionary
        """
        response = {
            "success": False,
            "error": cls.sanitize_error(error)
        }
        
        if operation:
            response["operation"] = operation
            
        if include_type:
            response["error_type"] = type(error).__name__
            
        response["timestamp"] = datetime.now().isoformat()
        
        return response


# Convenience function for direct use
def sanitize_error(error: Exception, context: Optional[Dict[str, Any]] = None) -> str:
    """Convenience function for sanitizing errors"""
    return SecurityUtils.sanitize_error(error, context)