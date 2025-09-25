from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class LoginRequest(BaseModel):
    email: str
    password: str

class LoginResponse(BaseModel):
    access_token: str
    token_type: str
    user: dict

class UserInfo(BaseModel):
    email: str
    name: str
    role: str

class MetricData(BaseModel):
    date: str
    campaign_name: str
    impressions: int
    clicks: int
    cost_micros: Optional[int] = None
    conversions: float
    conversion_rate: float

class MetricsResponse(BaseModel):
    metrics: List[MetricData]
    total_count: int
    page: int
    page_size: int
    total_pages: int

class MetricsFilters(BaseModel):
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    sort_by: Optional[str] = None
    sort_order: Optional[str] = "asc"
    search: Optional[str] = None
    page: Optional[int] = 1
    page_size: Optional[int] = 20