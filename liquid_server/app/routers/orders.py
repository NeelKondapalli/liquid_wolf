"""
Order management endpoints
"""
from flask import Blueprint, request, jsonify
from app.core.auth import require_api_key, validate_phone_and_keys
from app.services.liquid_service import LiquidService

orders_bp = Blueprint("orders", __name__, url_prefix="/api/v1/orders")


@orders_bp.route("/place", methods=["POST"])
@require_api_key
@validate_phone_and_keys
def place_order():
    """
    Place a new order

    Request Body:
        {
            "phone_number": str,
            "symbol": str,              # e.g., "BTC-PERP"
            "side": str,                # "buy" or "sell"
            "type": str,                # "market" or "limit" (default: "market")
            "size": float,              # USD notional (must be > 0)
            "price": float,             # required for limit orders
            "leverage": int,            # 1-200 (default: 1)
            "time_in_force": str,       # "gtc" or "ioc" (default: "gtc")
            "tp": float,                # optional take-profit price
            "sl": float,                # optional stop-loss price
            "reduce_only": bool         # optional (default: false)
        }

    Returns:
        Order details
    """
    try:
        data = request.get_json()

        # Required fields
        symbol = data.get("symbol")
        side = data.get("side")
        size = data.get("size")

        if not all([symbol, side, size]):
            return jsonify({
                "success": False,
                "error": "Missing required fields",
                "detail": "symbol, side, and size are required"
            }), 400

        if side not in ["buy", "sell"]:
            return jsonify({
                "success": False,
                "error": "Invalid side",
                "detail": "side must be 'buy' or 'sell'"
            }), 400

        if not isinstance(size, (int, float)) or size <= 0:
            return jsonify({
                "success": False,
                "error": "Invalid size",
                "detail": "size must be a positive number"
            }), 400

        # Optional fields
        order_type = data.get("type", "market")
        price = data.get("price")
        leverage = data.get("leverage", 1)
        time_in_force = data.get("time_in_force", "gtc")
        tp = data.get("tp")
        sl = data.get("sl")
        reduce_only = data.get("reduce_only", False)

        if order_type not in ["market", "limit"]:
            return jsonify({
                "success": False,
                "error": "Invalid type",
                "detail": "type must be 'market' or 'limit'"
            }), 400

        if order_type == "limit" and not price:
            return jsonify({
                "success": False,
                "error": "Missing price",
                "detail": "price is required for limit orders"
            }), 400

        if not isinstance(leverage, int) or leverage < 1 or leverage > 200:
            return jsonify({
                "success": False,
                "error": "Invalid leverage",
                "detail": "leverage must be between 1 and 200"
            }), 400

        api_key, api_secret = request.liquid_credentials
        liquid = LiquidService(api_key, api_secret)

        order = liquid.place_order(
            symbol=symbol,
            side=side,
            size=size,
            type=order_type,
            price=price,
            leverage=leverage,
            time_in_force=time_in_force,
            tp=tp,
            sl=sl,
            reduce_only=reduce_only,
        )

        return jsonify({
            "success": True,
            "data": order
        }), 200

    except Exception as e:
        return jsonify({
            "success": False,
            "error": "Failed to place order",
            "detail": str(e)
        }), 500


@orders_bp.route("/open", methods=["POST"])
@require_api_key
@validate_phone_and_keys
def get_open_orders():
    """
    Get all open orders

    Request Body:
        {
            "phone_number": str
        }

    Returns:
        List of open orders
    """
    try:
        api_key, api_secret = request.liquid_credentials
        liquid = LiquidService(api_key, api_secret)

        orders = liquid.get_open_orders()

        return jsonify({
            "success": True,
            "data": orders
        }), 200

    except Exception as e:
        return jsonify({
            "success": False,
            "error": "Failed to fetch open orders",
            "detail": str(e)
        }), 500


@orders_bp.route("/get", methods=["POST"])
@require_api_key
@validate_phone_and_keys
def get_order():
    """
    Get a specific order by ID

    Request Body:
        {
            "phone_number": str,
            "order_id": str
        }

    Returns:
        Order details
    """
    try:
        data = request.get_json()
        order_id = data.get("order_id")

        if not order_id:
            return jsonify({
                "success": False,
                "error": "Missing order_id",
                "detail": "order_id field is required"
            }), 400

        api_key, api_secret = request.liquid_credentials
        liquid = LiquidService(api_key, api_secret)

        order = liquid.get_order(order_id)

        return jsonify({
            "success": True,
            "data": order
        }), 200

    except Exception as e:
        return jsonify({
            "success": False,
            "error": "Failed to fetch order",
            "detail": str(e)
        }), 500


@orders_bp.route("/cancel", methods=["POST"])
@require_api_key
@validate_phone_and_keys
def cancel_order():
    """
    Cancel a specific order

    Request Body:
        {
            "phone_number": str,
            "order_id": str
        }

    Returns:
        Success status
    """
    try:
        data = request.get_json()
        order_id = data.get("order_id")

        if not order_id:
            return jsonify({
                "success": False,
                "error": "Missing order_id",
                "detail": "order_id field is required"
            }), 400

        api_key, api_secret = request.liquid_credentials
        liquid = LiquidService(api_key, api_secret)

        result = liquid.cancel_order(order_id)

        return jsonify({
            "success": True,
            "data": {"cancelled": result}
        }), 200

    except Exception as e:
        return jsonify({
            "success": False,
            "error": "Failed to cancel order",
            "detail": str(e)
        }), 500


@orders_bp.route("/cancel_all", methods=["POST"])
@require_api_key
@validate_phone_and_keys
def cancel_all_orders():
    """
    Cancel all open orders

    Request Body:
        {
            "phone_number": str
        }

    Returns:
        Count of cancelled orders
    """
    try:
        api_key, api_secret = request.liquid_credentials
        liquid = LiquidService(api_key, api_secret)

        count = liquid.cancel_all_orders()

        return jsonify({
            "success": True,
            "data": {"cancelled_count": count}
        }), 200

    except Exception as e:
        return jsonify({
            "success": False,
            "error": "Failed to cancel all orders",
            "detail": str(e)
        }), 500
