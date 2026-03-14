"""
Market data endpoints
"""
from flask import Blueprint, request, jsonify
from app.core.auth import require_api_key, validate_phone_and_keys
from app.services.liquid_service import LiquidService

market_data_bp = Blueprint("market_data", __name__, url_prefix="/api/v1/market")


@market_data_bp.route("/markets", methods=["POST"])
@require_api_key
@validate_phone_and_keys
def get_markets():
    """
    Get all tradeable markets

    Request Body:
        {
            "phone_number": str
        }

    Returns:
        List of markets with symbol, ticker, exchange, max_leverage, sz_decimals
    """
    try:
        api_key, api_secret = request.liquid_credentials
        liquid = LiquidService(api_key, api_secret)

        markets = liquid.get_markets()

        return jsonify({
            "success": True,
            "data": markets
        }), 200

    except Exception as e:
        return jsonify({
            "success": False,
            "error": "Failed to fetch markets",
            "detail": str(e)
        }), 500


@market_data_bp.route("/ticker", methods=["POST"])
@require_api_key
@validate_phone_and_keys
def get_ticker():
    """
    Get ticker data for a symbol

    Request Body:
        {
            "phone_number": str,
            "symbol": str  # e.g., "BTC-PERP"
        }

    Returns:
        Ticker data with mark_price, volume_24h, change_24h, funding_rate
    """
    try:
        data = request.get_json()
        symbol = data.get("symbol")

        if not symbol:
            return jsonify({
                "success": False,
                "error": "Missing symbol",
                "detail": "symbol field is required"
            }), 400

        api_key, api_secret = request.liquid_credentials
        liquid = LiquidService(api_key, api_secret)

        ticker = liquid.get_ticker(symbol)

        return jsonify({
            "success": True,
            "data": ticker
        }), 200

    except Exception as e:
        return jsonify({
            "success": False,
            "error": "Failed to fetch ticker",
            "detail": str(e)
        }), 500


@market_data_bp.route("/orderbook", methods=["POST"])
@require_api_key
@validate_phone_and_keys
def get_orderbook():
    """
    Get orderbook for a symbol

    Request Body:
        {
            "phone_number": str,
            "symbol": str,  # e.g., "BTC-PERP"
            "depth": int    # optional, default 20, max 500
        }

    Returns:
        Orderbook with bids and asks
    """
    try:
        data = request.get_json()
        symbol = data.get("symbol")
        depth = data.get("depth", 20)

        if not symbol:
            return jsonify({
                "success": False,
                "error": "Missing symbol",
                "detail": "symbol field is required"
            }), 400

        if not isinstance(depth, int) or depth < 1 or depth > 500:
            return jsonify({
                "success": False,
                "error": "Invalid depth",
                "detail": "depth must be between 1 and 500"
            }), 400

        api_key, api_secret = request.liquid_credentials
        liquid = LiquidService(api_key, api_secret)

        orderbook = liquid.get_orderbook(symbol, depth)

        return jsonify({
            "success": True,
            "data": orderbook
        }), 200

    except Exception as e:
        return jsonify({
            "success": False,
            "error": "Failed to fetch orderbook",
            "detail": str(e)
        }), 500


@market_data_bp.route("/candles", methods=["POST"])
@require_api_key
@validate_phone_and_keys
def get_candles():
    """
    Get candle data for a symbol

    Request Body:
        {
            "phone_number": str,
            "symbol": str,          # e.g., "BTC-PERP"
            "interval": str,        # optional: 1m, 5m, 15m, 30m, 1h, 4h, 1d (default: 1h)
            "limit": int,           # optional: 1-1000 (default: 100)
            "start": int,           # optional: start timestamp in seconds
            "end": int              # optional: end timestamp in seconds
        }

    Returns:
        List of candles with timestamp, open, high, low, close, volume
    """
    try:
        data = request.get_json()
        symbol = data.get("symbol")
        interval = data.get("interval", "1h")
        limit = data.get("limit", 100)
        start = data.get("start")
        end = data.get("end")

        if not symbol:
            return jsonify({
                "success": False,
                "error": "Missing symbol",
                "detail": "symbol field is required"
            }), 400

        valid_intervals = ["1m", "5m", "15m", "30m", "1h", "4h", "1d"]
        if interval not in valid_intervals:
            return jsonify({
                "success": False,
                "error": "Invalid interval",
                "detail": f"interval must be one of: {', '.join(valid_intervals)}"
            }), 400

        if not isinstance(limit, int) or limit < 1 or limit > 1000:
            return jsonify({
                "success": False,
                "error": "Invalid limit",
                "detail": "limit must be between 1 and 1000"
            }), 400

        api_key, api_secret = request.liquid_credentials
        liquid = LiquidService(api_key, api_secret)

        candles = liquid.get_candles(symbol, interval, limit, start, end)

        return jsonify({
            "success": True,
            "data": candles
        }), 200

    except Exception as e:
        return jsonify({
            "success": False,
            "error": "Failed to fetch candles",
            "detail": str(e)
        }), 500
