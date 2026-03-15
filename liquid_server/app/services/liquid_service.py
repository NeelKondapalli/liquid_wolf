"""
Liquid API service wrapper
"""
import logging
from liquidtrading import LiquidClient
from liquidtrading.errors import (
    LiquidError,
    InvalidApiKeyError,
    InvalidSignatureError,
    InsufficientScopeError,
    InsufficientBalanceError,
    OrderRejectedError,
    SymbolNotFoundError,
    RateLimitError,
    ValidationError,
    NotFoundError,
)
from typing import Any, Dict, Optional, List
from app.core.config import Config

# Set up logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


class LiquidService:
    """Service for interacting with Liquid Trading API"""

    def __init__(self, api_key: str, api_secret: str):
        """
        Initialize Liquid client with user credentials

        Args:
            api_key: User's Liquid API key
            api_secret: User's Liquid API secret
        """
        logger.info("="*60)
        logger.info("LIQUID CLIENT INITIALIZATION")
        logger.info(f"API Key (first 10 chars): {api_key[:10]}...")
        logger.info(f"API Secret (first 10 chars): {api_secret[:10]}...")
        logger.info(f"Base URL: {Config.LIQUID_BASE_URL}")
        logger.info("="*60)

        self.client = LiquidClient(
            api_key=api_key,
            api_secret=api_secret,
            base_url=Config.LIQUID_BASE_URL,
            timeout=30.0,
        )

    # ========================================================================
    # Market Data Methods
    # ========================================================================

    def get_markets(self) -> List[Dict[str, Any]]:
        """Get all tradeable markets"""
        try:
            return self.client.get_markets()
        except LiquidError as e:
            raise self._handle_liquid_error(e)

    def get_ticker(self, symbol: str) -> Dict[str, Any]:
        """Get ticker data for a symbol"""
        try:
            ticker = self.client.get_ticker(symbol)
            return {
                "symbol": ticker.symbol,
                "mark_price": ticker.mark_price,
                "volume_24h": ticker.volume_24h,
                "change_24h": ticker.change_24h,
                "funding_rate": ticker.funding_rate,
            }
        except LiquidError as e:
            raise self._handle_liquid_error(e)

    def get_orderbook(self, symbol: str, depth: int = 20) -> Dict[str, Any]:
        """Get orderbook for a symbol"""
        try:
            book = self.client.get_orderbook(symbol, depth=depth)
            return {
                "symbol": book.symbol,
                "bids": [
                    {"price": bid.price, "size": bid.size, "count": bid.count}
                    for bid in book.bids
                ],
                "asks": [
                    {"price": ask.price, "size": ask.size, "count": ask.count}
                    for ask in book.asks
                ],
                "timestamp": book.timestamp,
            }
        except LiquidError as e:
            raise self._handle_liquid_error(e)

    def get_candles(
        self,
        symbol: str,
        interval: str = "1h",
        limit: int = 100,
        start: Optional[int] = None,
        end: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        """Get candle data for a symbol"""
        try:
            candles = self.client.get_candles(
                symbol=symbol,
                interval=interval,
                limit=limit,
                start=start,
                end=end,
            )
            return [
                {
                    "timestamp": c.timestamp,
                    "open": c.open,
                    "high": c.high,
                    "low": c.low,
                    "close": c.close,
                    "volume": c.volume,
                }
                for c in candles
            ]
        except LiquidError as e:
            raise self._handle_liquid_error(e)

    # ========================================================================
    # Account Methods
    # ========================================================================

    def get_account(self) -> Dict[str, Any]:
        """Get account information"""
        logger.info("="*60)
        logger.info("LIQUID API - GET ACCOUNT")

        try:
            account = self.client.get_account()
            result = {
                "equity": account.equity,
                "margin_used": account.margin_used,
                "available_balance": account.available_balance,
                "account_value": account.account_value,
            }

            logger.info(f"SUCCESS - Response: {result}")
            logger.info("="*60)
            return result

        except LiquidError as e:
            logger.error(f"LIQUID API ERROR - {type(e).__name__}: {str(e)}")
            logger.info("="*60)
            raise self._handle_liquid_error(e)

    def get_balances(self) -> Dict[str, Any]:
        """Get detailed balance information"""
        try:
            balances = self.client.get_balances()
            return {
                "equity": balances.equity,
                "margin_used": balances.margin_used,
                "available_balance": balances.available_balance,
                "account_value": balances.account_value,
                "cross_margin": (
                    {
                        "account_value": balances.cross_margin.account_value,
                        "total_margin_used": balances.cross_margin.total_margin_used,
                        "total_ntl_pos": balances.cross_margin.total_ntl_pos,
                    }
                    if balances.cross_margin
                    else None
                ),
            }
        except LiquidError as e:
            raise self._handle_liquid_error(e)

    def get_positions(self) -> List[Dict[str, Any]]:
        """Get all open positions"""
        logger.info("="*60)
        logger.info("LIQUID API - GET POSITIONS")

        try:
            positions = self.client.get_positions()
            result = [
                {
                    "symbol": pos.symbol,
                    "side": pos.side,
                    "size": pos.size,
                    "entry_price": pos.entry_price,
                    "mark_price": pos.mark_price,
                    "leverage": pos.leverage,
                    "unrealized_pnl": pos.unrealized_pnl,
                    "liquidation_price": pos.liquidation_price,
                    "margin_used": pos.margin_used,
                }
                for pos in positions
            ]

            logger.info(f"SUCCESS - Found {len(result)} positions")
            logger.info(f"Response: {result}")
            logger.info("="*60)
            return result

        except LiquidError as e:
            logger.error(f"LIQUID API ERROR - {type(e).__name__}: {str(e)}")
            logger.info("="*60)
            raise self._handle_liquid_error(e)

    # ========================================================================
    # Order Methods
    # ========================================================================

    def place_order(
        self,
        symbol: str,
        side: str,
        size: float,
        type: str = "market",
        price: Optional[float] = None,
        leverage: int = 1,
        time_in_force: str = "gtc",
        tp: Optional[float] = None,
        sl: Optional[float] = None,
        reduce_only: bool = False,
    ) -> Dict[str, Any]:
        """Place a new order"""
        logger.info("="*60)
        logger.info("LIQUID API - PLACE ORDER")
        logger.info(f"Arguments: symbol={symbol}, side={side}, size={size}, type={type}, price={price}, leverage={leverage}, tif={time_in_force}, tp={tp}, sl={sl}, reduce_only={reduce_only}")

        try:
            order = self.client.place_order(
                symbol=symbol,
                side=side,
                type=type,
                size=size,
                price=price,
                leverage=leverage,
                time_in_force=time_in_force,
                tp=tp,
                sl=sl,
                reduce_only=reduce_only,
            )

            response = {
                "order_id": order.order_id,
                "symbol": order.symbol,
                "side": order.side,
                "type": order.type,
                "size": order.size,
                "price": order.price,
                "leverage": order.leverage,
                "status": order.status,
                "exchange": order.exchange,
                "tp": order.tp,
                "sl": order.sl,
                "reduce_only": order.reduce_only,
                "created_at": order.created_at,
            }

            logger.info(f"SUCCESS - Response: {response}")
            logger.info("="*60)
            return response

        except LiquidError as e:
            logger.error(f"LIQUID API ERROR - {type(e).__name__}: {str(e)}")
            logger.info("="*60)
            raise self._handle_liquid_error(e)

    def get_open_orders(self) -> List[Dict[str, Any]]:
        """Get all open orders"""
        logger.info("="*60)
        logger.info("LIQUID API - GET OPEN ORDERS")

        try:
            orders = self.client.get_open_orders()

            result = [
                {
                    "order_id": order.order_id,
                    "symbol": order.symbol,
                    "side": order.side,
                    "type": order.type,
                    "size": order.size,
                    "price": order.price,
                    "status": order.status,
                }
                for order in orders
            ]

            logger.info(f"SUCCESS - Found {len(result)} open orders")
            logger.info(f"Response: {result}")
            logger.info("="*60)
            return result

        except LiquidError as e:
            logger.error(f"LIQUID API ERROR - {type(e).__name__}: {str(e)}")
            logger.info("="*60)
            raise self._handle_liquid_error(e)

    def get_order(self, order_id: str) -> Dict[str, Any]:
        """Get a specific order by ID"""
        try:
            order = self.client.get_order(order_id)
            return {
                "order_id": order.order_id,
                "symbol": order.symbol,
                "side": order.side,
                "type": order.type,
                "size": order.size,
                "price": order.price,
                "status": order.status,
            }
        except LiquidError as e:
            raise self._handle_liquid_error(e)

    def cancel_order(self, order_id: str) -> bool:
        """Cancel a specific order"""
        try:
            return self.client.cancel_order(order_id)
        except LiquidError as e:
            raise self._handle_liquid_error(e)

    def cancel_all_orders(self) -> int:
        """Cancel all open orders"""
        try:
            return self.client.cancel_all_orders()
        except LiquidError as e:
            raise self._handle_liquid_error(e)

    # ========================================================================
    # Position Methods
    # ========================================================================

    def close_position(self, symbol: str, size: Optional[float] = None) -> Dict[str, Any]:
        """Close a position (full or partial)"""
        try:
            result = self.client.close_position(symbol, size=size)
            return {
                "symbol": result.symbol,
                "closed_size": result.closed_size,
                "status": result.status,
                "message": result.message,
            }
        except LiquidError as e:
            raise self._handle_liquid_error(e)

    def set_tp_sl(
        self,
        symbol: str,
        tp: Optional[float] = None,
        sl: Optional[float] = None,
    ) -> Dict[str, Any]:
        """Set take-profit and stop-loss"""
        try:
            result = self.client.set_tp_sl(symbol, tp=tp, sl=sl)
            return {
                "tp": {
                    "status": result.tp.status,
                    "price": result.tp.price,
                }
                if result.tp
                else None,
                "sl": {
                    "status": result.sl.status,
                    "price": result.sl.price,
                }
                if result.sl
                else None,
            }
        except LiquidError as e:
            raise self._handle_liquid_error(e)

    def update_leverage(
        self, symbol: str, leverage: int, is_cross: bool = False
    ) -> Dict[str, Any]:
        """Update position leverage"""
        try:
            result = self.client.update_leverage(symbol, leverage, is_cross)
            return {
                "symbol": result.symbol,
                "leverage": result.leverage,
                "is_cross": result.is_cross,
            }
        except LiquidError as e:
            raise self._handle_liquid_error(e)

    def update_margin(self, symbol: str, amount: float) -> Dict[str, Any]:
        """Update position margin"""
        try:
            result = self.client.update_margin(symbol, amount)
            return {
                "symbol": result.symbol,
                "margin_adjusted": result.margin_adjusted,
            }
        except LiquidError as e:
            raise self._handle_liquid_error(e)

    # ========================================================================
    # Error Handling
    # ========================================================================

    def _handle_liquid_error(self, error: LiquidError) -> Exception:
        """Convert Liquid errors to HTTP exceptions"""
        error_map = {
            InvalidApiKeyError: ("Invalid API key", 401),
            InvalidSignatureError: ("Invalid API signature", 401),
            InsufficientScopeError: ("Insufficient permissions", 403),
            InsufficientBalanceError: ("Insufficient balance", 400),
            OrderRejectedError: ("Order rejected by exchange", 400),
            SymbolNotFoundError: ("Symbol not found", 404),
            RateLimitError: ("Rate limit exceeded", 429),
            ValidationError: ("Validation error", 422),
            NotFoundError: ("Resource not found", 404),
        }

        error_type = type(error)
        message, status_code = error_map.get(
            error_type, (str(error), 500)
        )

        # Return the exception to be raised by Flask route
        return Exception(f"{message} (HTTP {status_code})")
