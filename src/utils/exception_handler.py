"""Global exception handler with custom exceptions and error logging."""
import logging
import traceback
from typing import Optional, Dict, Any
from functools import wraps
from src.utils.logger import setup_logger


# Initialize logger for exception handler
exception_logger = setup_logger(
    name="exception_handler",
    log_file="logs/exceptions.log",
    level="ERROR"
)


class BaseApplicationError(Exception):
    """Base exception class for application errors."""
    
    def __init__(self, message: str, error_code: str = "APP_ERROR", details: Optional[Dict[str, Any]] = None):
        """Initialize base application error.
        
        Args:
            message: Error message
            error_code: Error code for categorization
            details: Additional error details
        """
        self.message = message
        self.error_code = error_code
        self.details = details or {}
        super().__init__(self.message)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert exception to dictionary format.
        
        Returns:
            Dictionary representation of the error
        """
        return {
            "error": self.message,
            "error_code": self.error_code,
            "details": self.details
        }


class ConfigurationError(BaseApplicationError):
    """Exception raised for configuration errors."""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, error_code="CONFIG_ERROR", details=details)


class DatabaseError(BaseApplicationError):
    """Exception raised for database/vector store errors."""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, error_code="DB_ERROR", details=details)


class LLMError(BaseApplicationError):
    """Exception raised for LLM API errors."""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, error_code="LLM_ERROR", details=details)


class DocumentProcessingError(BaseApplicationError):
    """Exception raised for document processing errors."""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, error_code="DOC_PROCESSING_ERROR", details=details)


class ValidationError(BaseApplicationError):
    """Exception raised for validation errors."""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, error_code="VALIDATION_ERROR", details=details)


def log_exception(exc: Exception, context: Optional[str] = None, extra_info: Optional[Dict[str, Any]] = None):
    """Log exception with full traceback and context.
    
    Args:
        exc: Exception to log
        context: Context where exception occurred
        extra_info: Additional information to log
    """
    error_msg = f"Exception occurred"
    if context:
        error_msg += f" in {context}"
    error_msg += f": {type(exc).__name__}: {str(exc)}"
    
    # Log the error message
    exception_logger.error(error_msg)
    
    # Log additional info if provided
    if extra_info:
        exception_logger.error(f"Additional info: {extra_info}")
    
    # Log full traceback
    exception_logger.error(f"Traceback:\n{traceback.format_exc()}")


def handle_exceptions(context: Optional[str] = None, reraise: bool = True, default_return: Any = None):
    """Decorator to handle exceptions with logging.
    
    Args:
        context: Context description for logging
        reraise: Whether to reraise the exception after logging
        default_return: Default value to return if exception occurs and reraise=False
        
    Returns:
        Decorated function
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                # Log the exception
                func_context = context or f"{func.__module__}.{func.__name__}"
                log_exception(e, context=func_context, extra_info={
                    "function": func.__name__,
                    "args": str(args)[:200],  # Limit args length
                    "kwargs": str(kwargs)[:200]  # Limit kwargs length
                })
                
                # Reraise or return default
                if reraise:
                    raise
                else:
                    return default_return
        
        return wrapper
    return decorator


def safe_execute(func, *args, default=None, context: Optional[str] = None, **kwargs):
    """Safely execute a function with exception handling.
    
    Args:
        func: Function to execute
        *args: Positional arguments for the function
        default: Default value to return on exception
        context: Context description for logging
        **kwargs: Keyword arguments for the function
        
    Returns:
        Function result or default value on exception
    """
    try:
        return func(*args, **kwargs)
    except Exception as e:
        func_context = context or f"{func.__module__}.{func.__name__}"
        log_exception(e, context=func_context)
        return default

