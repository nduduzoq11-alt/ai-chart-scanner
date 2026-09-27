from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional, List

# User Schemas
class UserRegister(BaseModel):
    username: str
    email: EmailStr
    password: str

class UserLogin(BaseModel):
    username: str
    password: str

class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    created_at: datetime
    is_active: bool
    
    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str
    user: UserResponse

# Scan Schemas
class ScanResponse(BaseModel):
    id: int
    symbol: str
    signal: str
    confidence: float
    price: float
    ema20: float
    ema50: float
    ema200: float
    rsi14: float
    support: float
    resistance: float
    trend: str
    reason: str
    volume_ratio: Optional[float]
    created_at: datetime
    
    class Config:
        from_attributes = True

class ScanHistoryResponse(BaseModel):
    symbol: str
    latest_scan: Optional[ScanResponse]
    scan_count: int
    last_scan_date: Optional[datetime]

# Watchlist Schemas
class WatchlistItemCreate(BaseModel):
    symbol: str

class WatchlistItemResponse(BaseModel):
    id: int
    symbol: str
    added_at: datetime
    is_alert_enabled: bool
    
    class Config:
        from_attributes = True

class WatchlistResponse(BaseModel):
    items: List[WatchlistItemResponse]
    count: int

# Alert Schemas
class AlertCreate(BaseModel):
    symbol: str
    alert_type: str
    threshold: Optional[float] = None
    signal_type: Optional[str] = None

class AlertResponse(BaseModel):
    id: int
    symbol: str
    alert_type: str
    threshold: Optional[float]
    signal_type: Optional[str]
    is_active: bool
    created_at: datetime
    triggered_at: Optional[datetime]
    
    class Config:
        from_attributes = True

# Portfolio Schemas
class PositionCreate(BaseModel):
    symbol: str
    quantity: float
    entry_price: float
    position_type: str

class PositionResponse(BaseModel):
    id: int
    symbol: str
    quantity: float
    entry_price: float
    current_price: float
    position_type: str
    opened_at: datetime
    is_open: bool
    
    class Config:
        from_attributes = True

class PortfolioResponse(BaseModel):
    id: int
    user_id: int
    total_value: float
    cash: float
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

# Dashboard Schemas
class DashboardStats(BaseModel):
    total_scans: int
    buy_signals: int
    sell_signals: int
    win_rate: float
    portfolio_value: float
    portfolio_cash: float
    open_positions: int

class DashboardData(BaseModel):
    stats: DashboardStats
    recent_scans: List[ScanResponse]
    watchlist: List[WatchlistItemResponse]
    alerts: List[AlertResponse]
