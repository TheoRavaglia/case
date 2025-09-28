"""
FastAPI middleware for automatic request logging.
Captures all HTTP requests and responses for monitoring.
"""

import time
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response as StarletteResponse
from utils.logger import api_logger

class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Middleware to automatically log all HTTP requests."""
    
    def __init__(self, app):
        super().__init__(app)
        # Log system startup
        api_logger.log_system_event("API_STARTUP", "FastAPI server started successfully")
    
    async def dispatch(self, request: Request, call_next):
        """Process request and log details."""
        
        start_time = time.time()
        
        # Get client IP (handle proxy headers)
        client_ip = self.get_client_ip(request)
        
        # Get user from token if present (optional)
        user_email = await self.extract_user_from_request(request)
        
        response = None
        error_message = None
        
        try:
            # Process the request
            response = await call_next(request)
            
        except Exception as e:
            # Handle any errors
            error_message = str(e)
            # Create error response
            response = Response(
                content=f'{{"error": "Internal server error", "detail": "{str(e)}"}}',
                status_code=500,
                media_type="application/json"
            )
        
        # Calculate response time
        process_time = time.time() - start_time
        
        # Log the request
        api_logger.log_request(
            method=request.method,
            path=str(request.url.path) + (f"?{request.url.query}" if request.url.query else ""),
            client_ip=client_ip,
            status_code=response.status_code,
            response_time=process_time,
            user_email=user_email,
            error=error_message
        )
        
        # Add response time header
        response.headers["X-Process-Time"] = str(process_time)
        
        return response
    
    def get_client_ip(self, request: Request) -> str:
        """Extract client IP considering proxy headers."""
        
        # Check common proxy headers
        forwarded_for = request.headers.get("x-forwarded-for")
        if forwarded_for:
            # Take the first IP (original client)
            return forwarded_for.split(",")[0].strip()
        
        real_ip = request.headers.get("x-real-ip")
        if real_ip:
            return real_ip
        
        # Fallback to direct connection
        return request.client.host if request.client else "unknown"
    
    async def extract_user_from_request(self, request: Request) -> str:
        """Fast user extraction with minimal overhead."""
        
        # Skip user extraction for public paths (faster)
        path = request.url.path
        if path in {"/", "/docs", "/openapi.json", "/api/logs", "/api/logs/json", "/health"}:
            return None
        
        # Quick header check
        auth_header = request.headers.get("authorization", "")
        if not auth_header.startswith("Bearer "):
            return None
        
        try:
            # Fast token extraction and verification
            token = auth_header[7:]  # Remove "Bearer " (faster than replace)
            from auth import verify_token
            return verify_token(token)
        except Exception:
            return None