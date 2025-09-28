"""
Simple logging system for production monitoring
Stores logs in memory with rotation for performance
"""

import logging
import sys
from datetime import datetime
from typing import List, Dict, Any
from collections import deque
import threading

class InMemoryLogHandler(logging.Handler):
    """Custom handler that stores logs in memory with rotation."""
    
    def __init__(self, maxlen: int = 1000):
        super().__init__()
        self.logs = deque(maxlen=maxlen)  # Auto-rotating buffer
        self.lock = threading.Lock()
    
    def emit(self, record):
        """Store log record in memory."""
        with self.lock:
            log_entry = {
                "timestamp": datetime.fromtimestamp(record.created).isoformat(),
                "level": record.levelname,
                "logger": record.name,
                "message": record.getMessage(),
                "module": record.module,
                "function": record.funcName,
                "line": record.lineno
            }
            self.logs.append(log_entry)
    
    def get_logs(self, limit: int = 100, level: str = None) -> List[Dict[str, Any]]:
        """Retrieve logs with optional filtering."""
        with self.lock:
            logs = list(self.logs)
            
            # Filter by level if specified
            if level:
                logs = [log for log in logs if log["level"] == level.upper()]
            
            # Return most recent logs first, limited by limit
            return list(reversed(logs))[-limit:]

# Global log handler instance
log_handler = InMemoryLogHandler(maxlen=1000)

def setup_production_logging():
    """Configure production logging with in-memory storage."""
    
    # Configure root logger
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Console handler (for Render.com dashboard)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    
    # Memory handler (for API endpoint)
    log_handler.setFormatter(formatter)
    
    # Add both handlers
    logger.addHandler(console_handler)
    logger.addHandler(log_handler)
    
    return logger

def get_app_logs(limit: int = 100, level: str = None) -> List[Dict[str, Any]]:
    """Get application logs for API endpoint."""
    return log_handler.get_logs(limit=limit, level=level)

def log_api_access(method: str, path: str, status: int, duration: float, user: str = None):
    """Log API access with structured data."""
    logger = logging.getLogger("api.access")
    user_info = f" - User: {user}" if user else ""
    logger.info(f"{method} {path} - {status} - {duration:.3f}s{user_info}")

def log_auth_event(event: str, user: str, success: bool):
    """Log authentication events."""
    logger = logging.getLogger("api.auth")
    status = "SUCCESS" if success else "FAILED"
    logger.info(f"{event} - {user} - {status}")

def log_data_operation(operation: str, records: int, duration: float):
    """Log data processing operations."""
    logger = logging.getLogger("api.data")
    logger.info(f"{operation} - {records:,} records - {duration:.3f}s")

def log_error(error: Exception, context: str = None):
    """Log errors with context."""
    logger = logging.getLogger("api.error")
    context_info = f" in {context}" if context else ""
    logger.error(f"{type(error).__name__}: {str(error)}{context_info}")