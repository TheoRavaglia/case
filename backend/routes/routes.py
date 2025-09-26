from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional
from datetime import timedelta
from models.models import LoginRequest, LoginResponse, MetricsFilters, MetricsResponse
from auth.auth import authenticate_user, create_access_token, verify_token, get_user_by_email, ACCESS_TOKEN_EXPIRE_MINUTES
from services.services import get_filtered_metrics

router = APIRouter()
security = HTTPBearer(auto_error=False)

@router.get("/")
async def root():
    """API Root endpoint - Health check and information."""
    return {
        "message": "Marketing Analytics API funcionando",
        "version": "1.0.0",
        "status": "active",
        "endpoints": {
            "login": "/api/login",
            "metrics": "/api/metrics",
            "user_info": "/api/me",
            "documentation": "/docs",
            "openapi": "/openapi.json"
        },
        "description": "API for marketing metrics analysis with JWT authentication and smart pagination"
    }

def get_current_user(credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)):
    """Get current authenticated user."""
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization header missing",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    token = credentials.credentials
    email = verify_token(token)
    user = get_user_by_email(email)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    return user

@router.post("/login", response_model=LoginResponse)
async def login(login_data: LoginRequest):
    """Authenticate user and return JWT token."""
    user = authenticate_user(login_data.email, login_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user['email']}, expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": user
    }

@router.get("/me")
async def get_current_user_info(current_user: dict = Depends(get_current_user)):
    """Get current user information."""
    return current_user

@router.post("/metrics")
async def get_metrics(
    filters: MetricsFilters,
    current_user: dict = Depends(get_current_user)
):
    """Get filtered metrics data with pagination for large datasets."""
    try:
        page = filters.page or 1
        page_size = min(filters.page_size or 20, 100)  # Default 20 records, max 100 per page
        
        metrics_data = get_filtered_metrics(filters, current_user, page, page_size)
        
        # For non-admin users, remove cost_micros from response
        if current_user.get('role') != 'admin':
            response_dict = metrics_data.dict()
            for metric in response_dict['metrics']:
                if 'cost_micros' in metric:
                    del metric['cost_micros']
            return response_dict
        
        return metrics_data
    except Exception as e:
        print(f"API Error: {str(e)}")  # Debug log
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving metrics: {str(e)}"
        )