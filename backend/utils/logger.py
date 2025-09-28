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
    """Ultra-fast thread-safe logger optimized for high performance."""
    
    def __init__(self, max_logs: int = 50):  # Reduced for speed
        self.max_logs = max_logs
        self.logs = deque(maxlen=max_logs)  # Smaller buffer for faster iteration
        self.stats = {
            'total_requests': 0,
            'success_count': 0,
            'response_times': deque(maxlen=20)  # Only keep last 20 for avg calculation
        }
        self.setup_logging()
    
    def setup_logging(self):
        """Minimal logging setup for performance."""
        self.logger = logging.getLogger("marketing_api")
        self.logger.setLevel(logging.INFO)
    
    def log_request(self, method: str, path: str, client_ip: str, 
                   status_code: int, response_time: float = None, 
                   user_email: str = None, error: str = None):
        """Optimized request logging with minimal overhead."""
        
        timestamp = datetime.now()
        
        # Fast level determination
        level = "ERROR" if status_code >= 500 else "WARNING" if status_code >= 400 else "SUCCESS"
        
        # Pre-format strings for speed
        time_str = timestamp.strftime("%H:%M:%S")
        response_time_ms = round(response_time * 1000, 2) if response_time else None
        
        # Complete log entry (não truncar dados)
        log_entry = {
            "timestamp": timestamp.isoformat(),
            "time_formatted": time_str,
            "method": method,
            "path": path,  # Mostrar path completo
            "client_ip": client_ip,
            "status_code": status_code,
            "level": level,
            "response_time_ms": response_time_ms,
            "user": user_email or "anonymous",  # Usuário completo
            "error": error  # Erro completo
        }
        
        # Update stats efficiently (avoid recalculation)
        if method != "SYSTEM":
            self.stats['total_requests'] += 1
            if level == "SUCCESS":
                self.stats['success_count'] += 1
            if response_time_ms:
                self.stats['response_times'].append(response_time_ms)
        
        # Add to buffer
        self.logs.append(log_entry)
        
        # Log to Python logger (como antes)
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
        """Get pre-calculated stats for maximum performance."""
        # Use pre-calculated values instead of iterating through logs
        total = self.stats['total_requests']
        success_rate = round((self.stats['success_count'] / max(total, 1)) * 100, 2) if total > 0 else 0
        
        # Fast average from deque
        response_times = list(self.stats['response_times'])
        avg_time = round(sum(response_times) / len(response_times), 2) if response_times else 0
        
        # Quick status code count from recent logs
        recent_logs = list(self.logs)[-10:]  # Only check last 10 for speed
        status_codes = {}
        for log in recent_logs:
            if log.get("method") != "SYSTEM":
                code = log["status_code"]
                status_codes[code] = status_codes.get(code, 0) + 1
        
        return {
            "total_requests": total,
            "success_rate": success_rate,
            "average_response_time": avg_time,
            "status_codes": status_codes,
            "active_logs_count": len(self.logs)  # Corrigir o nome do campo
        }

# Global logger instance
api_logger = APILogger()