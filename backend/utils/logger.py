"""
Real-time request logging system for API monitoring.
Captures HTTP requests, responses, and system events.
"""

import logging
from datetime import datetime
from typing import List, Dict, Any
from collections import deque
import json

class APILogger:
    """Thread-safe logger for capturing API requests and system events."""
    
    def __init__(self, max_logs: int = 100):
        self.max_logs = max_logs
        self.logs = deque(maxlen=max_logs)  # Thread-safe circular buffer
        self.setup_logging()
    
    def setup_logging(self):
        """Setup Python logging configuration."""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger("marketing_api")
    
    def log_request(self, method: str, path: str, client_ip: str, 
                   status_code: int, response_time: float = None, 
                   user_email: str = None, error: str = None):
        """Log HTTP request with details."""
        
        timestamp = datetime.now()
        
        # Determine log level based on status code
        if status_code >= 500:
            level = "ERROR"
        elif status_code >= 400:
            level = "WARNING"  
        else:
            level = "SUCCESS"
        
        # Create log entry
        log_entry = {
            "timestamp": timestamp.isoformat(),
            "time_formatted": timestamp.strftime("%H:%M:%S"),
            "method": method,
            "path": path,
            "client_ip": client_ip,
            "status_code": status_code,
            "level": level,
            "response_time_ms": round(response_time * 1000, 2) if response_time else None,
            "user": user_email or "anonymous",
            "error": error
        }
        
        # Add to circular buffer (thread-safe)
        self.logs.append(log_entry)
        
        # Also log to Python logger
        log_message = f"{method} {path} - {status_code} - {client_ip}"
        if user_email:
            log_message += f" - User: {user_email}"
        if response_time:
            log_message += f" - {response_time*1000:.2f}ms"
        
        if level == "ERROR":
            self.logger.error(log_message + (f" - Error: {error}" if error else ""))
        elif level == "WARNING":
            self.logger.warning(log_message)
        else:
            self.logger.info(log_message)
    
    def log_system_event(self, event: str, details: str = None):
        """Log system events (startup, errors, etc.)."""
        
        timestamp = datetime.now()
        
        log_entry = {
            "timestamp": timestamp.isoformat(),
            "time_formatted": timestamp.strftime("%H:%M:%S"),
            "method": "SYSTEM",
            "path": event,
            "client_ip": "internal",
            "status_code": 200,
            "level": "INFO",
            "response_time_ms": None,
            "user": "system",
            "error": details
        }
        
        self.logs.append(log_entry)
        self.logger.info(f"SYSTEM EVENT: {event}" + (f" - {details}" if details else ""))
    
    def get_recent_logs(self, limit: int = None) -> List[Dict[str, Any]]:
        """Get recent logs (most recent first)."""
        logs_list = list(self.logs)
        
        # Reverse to show most recent first
        logs_list.reverse()
        
        if limit:
            logs_list = logs_list[:limit]
            
        return logs_list
    
    def get_stats(self) -> Dict[str, Any]:
        """Get API usage statistics."""
        logs_list = list(self.logs)
        
        if not logs_list:
            return {
                "total_requests": 0,
                "success_rate": 0,
                "average_response_time": 0,
                "status_codes": {}
            }
        
        # Calculate stats
        total_requests = len([log for log in logs_list if log["method"] != "SYSTEM"])
        success_count = len([log for log in logs_list if log["level"] == "SUCCESS"])
        
        # Response times (excluding None values)
        response_times = [log["response_time_ms"] for log in logs_list 
                         if log["response_time_ms"] is not None]
        
        # Status code distribution
        status_codes = {}
        for log in logs_list:
            if log["method"] != "SYSTEM":
                code = log["status_code"]
                status_codes[code] = status_codes.get(code, 0) + 1
        
        return {
            "total_requests": total_requests,
            "success_rate": round((success_count / max(total_requests, 1)) * 100, 2),
            "average_response_time": round(sum(response_times) / max(len(response_times), 1), 2) if response_times else 0,
            "status_codes": status_codes,
            "active_logs_count": len(logs_list)
        }

# Global logger instance
api_logger = APILogger()