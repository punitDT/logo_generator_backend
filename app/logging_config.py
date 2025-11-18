"""
Logging Configuration for Production GPU Backend
Provides JSON and text logging with detailed request/response tracking
"""

import logging
import sys
import json
from datetime import datetime
from typing import Any, Dict
from app.config import Config


class JSONFormatter(logging.Formatter):
    """Custom JSON formatter for structured logging"""
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON"""
        log_data: Dict[str, Any] = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        
        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)
        
        # Add extra fields
        if hasattr(record, "request_id"):
            log_data["request_id"] = record.request_id
        
        if hasattr(record, "duration_ms"):
            log_data["duration_ms"] = record.duration_ms
        
        if hasattr(record, "status_code"):
            log_data["status_code"] = record.status_code
        
        if hasattr(record, "endpoint"):
            log_data["endpoint"] = record.endpoint
        
        if hasattr(record, "gpu_memory_gb"):
            log_data["gpu_memory_gb"] = record.gpu_memory_gb
        
        return json.dumps(log_data)


class TextFormatter(logging.Formatter):
    """Custom text formatter with colors for development"""
    
    COLORS = {
        'DEBUG': '\033[36m',      # Cyan
        'INFO': '\033[32m',       # Green
        'WARNING': '\033[33m',    # Yellow
        'ERROR': '\033[31m',      # Red
        'CRITICAL': '\033[35m',   # Magenta
        'RESET': '\033[0m'        # Reset
    }
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record with colors"""
        color = self.COLORS.get(record.levelname, self.COLORS['RESET'])
        reset = self.COLORS['RESET']
        
        # Format timestamp
        timestamp = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
        
        # Build message
        message = f"{color}[{timestamp}] {record.levelname:8s}{reset} | {record.name:20s} | {record.getMessage()}"
        
        # Add exception if present
        if record.exc_info:
            message += f"\n{self.formatException(record.exc_info)}"
        
        return message


def setup_logging() -> None:
    """
    Configure logging based on environment settings.
    Sets up JSON logging for production, text logging for development.
    """
    # Get log level from config
    log_level = getattr(logging, Config.LOG_LEVEL.upper(), logging.INFO)
    
    # Create root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    
    # Remove existing handlers
    root_logger.handlers.clear()
    
    # Create console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    
    # Set formatter based on config
    if Config.LOG_FORMAT.lower() == "json":
        formatter = JSONFormatter()
    else:
        formatter = TextFormatter()
    
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)
    
    # Set specific log levels for noisy libraries
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    
    # Log startup message
    logger = logging.getLogger(__name__)
    logger.info(f"Logging configured: level={Config.LOG_LEVEL}, format={Config.LOG_FORMAT}")


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance with the specified name.
    
    Args:
        name: Logger name (typically __name__)
        
    Returns:
        Configured logger instance
    """
    return logging.getLogger(name)


# Request logging utilities
class RequestLogger:
    """Utility class for logging HTTP requests with context"""
    
    @staticmethod
    def log_request(
        logger: logging.Logger,
        request_id: str,
        endpoint: str,
        method: str,
        **kwargs
    ) -> None:
        """Log incoming request"""
        extra = {
            "request_id": request_id,
            "endpoint": endpoint,
            "method": method,
            **kwargs
        }
        logger.info(f"Request received: {method} {endpoint}", extra=extra)
    
    @staticmethod
    def log_response(
        logger: logging.Logger,
        request_id: str,
        endpoint: str,
        status_code: int,
        duration_ms: float,
        **kwargs
    ) -> None:
        """Log outgoing response"""
        extra = {
            "request_id": request_id,
            "endpoint": endpoint,
            "status_code": status_code,
            "duration_ms": duration_ms,
            **kwargs
        }
        logger.info(f"Response sent: {status_code} ({duration_ms:.2f}ms)", extra=extra)

