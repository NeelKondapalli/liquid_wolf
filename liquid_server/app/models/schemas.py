"""
Pydantic models for request/response validation
"""
from pydantic import BaseModel, Field
from typing import Optional, Literal
from datetime import datetime


# ============================================================================
# Database Models
# ============================================================================

class User(BaseModel):
    """User database model"""
    phone_number: str
    created_at: datetime
    updated_at: datetime


class LiquidKey(BaseModel):
    """Liquid API key database model"""
    id: str
    phone_number: str
    api_key: str
    api_secret: str
    is_active: bool
    created_at: datetime
    updated_at: datetime


# ============================================================================
# Request Models
# ============================================================================

class OrderRequest(BaseModel):
    """Request to place an order"""
    phone_number: str = Field(..., description="User's phone number")
    symbol: str = Field(..., description="Trading symbol (e.g., BTC-PERP)")
    side: Literal["buy", "sell"] = Field(..., description="Order side")
    type: Literal["market", "limit"] = Field(default="market", description="Order type")
    size: float = Field(..., gt=0, description="Order size in USD notional")
    price: Optional[float] = Field(None, gt=0, description="Limit price (required for limit orders)")
    leverage: int = Field(default=1, ge=1, le=200, description="Leverage (1-200)")
    time_in_force: Literal["gtc", "ioc"] = Field(default="gtc", description="Time in force")
    tp: Optional[float] = Field(None, gt=0, description="Take-profit price")
    sl: Optional[float] = Field(None, gt=0, description="Stop-loss price")
    reduce_only: bool = Field(default=False, description="Only reduce existing position")


class CancelOrderRequest(BaseModel):
    """Request to cancel an order"""
    phone_number: str = Field(..., description="User's phone number")
    order_id: str = Field(..., description="Order ID to cancel")


class ClosePositionRequest(BaseModel):
    """Request to close a position"""
    phone_number: str = Field(..., description="User's phone number")
    symbol: str = Field(..., description="Trading symbol")
    size: Optional[float] = Field(None, gt=0, description="Partial close size in coin units (omit for full close)")


class SetTpSlRequest(BaseModel):
    """Request to set take-profit and stop-loss"""
    phone_number: str = Field(..., description="User's phone number")
    symbol: str = Field(..., description="Trading symbol")
    tp: Optional[float] = Field(None, gt=0, description="Take-profit price")
    sl: Optional[float] = Field(None, gt=0, description="Stop-loss price")


class UpdateLeverageRequest(BaseModel):
    """Request to update leverage"""
    phone_number: str = Field(..., description="User's phone number")
    symbol: str = Field(..., description="Trading symbol")
    leverage: int = Field(..., ge=1, le=200, description="New leverage (1-200)")
    is_cross: bool = Field(default=False, description="Use cross margin")


class UpdateMarginRequest(BaseModel):
    """Request to update margin"""
    phone_number: str = Field(..., description="User's phone number")
    symbol: str = Field(..., description="Trading symbol")
    amount: float = Field(..., description="Amount to add (positive) or remove (negative)")


class MarketDataRequest(BaseModel):
    """Request for market data endpoints"""
    phone_number: str = Field(..., description="User's phone number")
    symbol: Optional[str] = Field(None, description="Trading symbol (optional for markets list)")


class OrderbookRequest(BaseModel):
    """Request for orderbook data"""
    phone_number: str = Field(..., description="User's phone number")
    symbol: str = Field(..., description="Trading symbol")
    depth: int = Field(default=20, ge=1, le=500, description="Orderbook depth")


class CandlesRequest(BaseModel):
    """Request for candle data"""
    phone_number: str = Field(..., description="User's phone number")
    symbol: str = Field(..., description="Trading symbol")
    interval: Literal["1m", "5m", "15m", "30m", "1h", "4h", "1d"] = Field(
        default="1h",
        description="Candle interval"
    )
    limit: int = Field(default=100, ge=1, le=1000, description="Number of candles")
    start: Optional[int] = Field(None, description="Start timestamp (seconds)")
    end: Optional[int] = Field(None, description="End timestamp (seconds)")


class AccountRequest(BaseModel):
    """Request for account data"""
    phone_number: str = Field(..., description="User's phone number")


# ============================================================================
# Response Models
# ============================================================================

class APIResponse(BaseModel):
    """Standard API response wrapper"""
    success: bool
    data: Optional[dict] = None
    message: Optional[str] = None


class ErrorResponse(BaseModel):
    """Error response"""
    success: bool = False
    error: str
    detail: Optional[str] = None
