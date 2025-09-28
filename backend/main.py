from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from routes.routes import router
from utils.app_logging import setup_production_logging, log_api_access
import time

# Setup logging system
logger = setup_production_logging()
logger.info("Starting Marketing Analytics API...")

app = FastAPI(
    title="Marketing Analytics API", 
    version="1.0.0",
    description="Professional API for marketing metrics analysis with JWT authentication",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Logging middleware
@app.middleware("http")
async def logging_middleware(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    duration = time.time() - start_time
    
    # Log API access
    log_api_access(
        method=request.method,
        path=request.url.path,
        status=response.status_code,
        duration=duration
    )
    
    return response

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173", "http://localhost:5174", "http://localhost:5175"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Root endpoint (when accessing http://localhost:8001 directly)
@app.get("/")
async def root():
    """API root endpoint - General information and status."""
    return {
        "api_name": "Marketing Analytics API",
        "version": "1.0.0", 
        "status": "ONLINE",
        "message": "API working correctly",
        "frontend_url": "http://localhost:5174",
        "documentation": {
            "swagger_ui": "http://localhost:8001/docs",
            "redoc": "http://localhost:8001/redoc",
            "openapi_json": "http://localhost:8001/openapi.json"
        },
        "api_endpoints": {
            "base_url": "http://localhost:8001/api",
            "auth": "/api/login",
            "metrics": "/api/metrics", 
            "user_profile": "/api/me"
        },
        "features": [
            "JWT Authentication",
            "Smart Pagination",
            "Date Filters",
            "Aggregated Metrics",
            "Permission Control"
        ]
    }

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check for monitoring."""
    return {
        "status": "healthy",
        "timestamp": "2025-09-25",
        "service": "Marketing Analytics API"
    }

# Include routes
app.include_router(router, prefix="/api")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)