"""
Position management endpoints
"""
from flask import Blueprint, request, jsonify
from app.core.auth import require_api_key, validate_phone_and_keys
from app.services.liquid_service import LiquidService

positions_bp = Blueprint("positions", __name__, url_prefix="/api/v1/positions")


@positions_bp.route("/close", methods=["POST"])
@require_api_key
@validate_phone_and_keys
def close_position():
    """
    Close a position (full or partial)

    Request Body:
        {
            "phone_number": str,
            "symbol": str,          # e.g., "BTC-PERP"
            "size": float           # optional: partial close in coin units (omit for full close)
        }

    Returns:
        Close result with closed_size and status
    """
    try:
        data = request.get_json()
        symbol = data.get("symbol")
        size = data.get("size")

        if not symbol:
            return jsonify({
                "success": False,
                "error": "Missing symbol",
                "detail": "symbol field is required"
            }), 400

        if size is not None and (not isinstance(size, (int, float)) or size <= 0):
            return jsonify({
                "success": False,
                "error": "Invalid size",
                "detail": "size must be a positive number if provided"
            }), 400

        api_key, api_secret = request.liquid_credentials
        liquid = LiquidService(api_key, api_secret)

        result = liquid.close_position(symbol, size)

        return jsonify({
            "success": True,
            "data": result
        }), 200

    except Exception as e:
        return jsonify({
            "success": False,
            "error": "Failed to close position",
            "detail": str(e)
        }), 500


@positions_bp.route("/set_tp_sl", methods=["POST"])
@require_api_key
@validate_phone_and_keys
def set_tp_sl():
    """
    Set take-profit and stop-loss for a position

    Request Body:
        {
            "phone_number": str,
            "symbol": str,          # e.g., "BTC-PERP"
            "tp": float,            # optional: take-profit price
            "sl": float             # optional: stop-loss price
        }

    Returns:
        TP/SL result with status and prices
    """
    try:
        data = request.get_json()
        symbol = data.get("symbol")
        tp = data.get("tp")
        sl = data.get("sl")

        if not symbol:
            return jsonify({
                "success": False,
                "error": "Missing symbol",
                "detail": "symbol field is required"
            }), 400

        if not tp and not sl:
            return jsonify({
                "success": False,
                "error": "Missing TP or SL",
                "detail": "At least one of tp or sl must be provided"
            }), 400

        if tp is not None and (not isinstance(tp, (int, float)) or tp <= 0):
            return jsonify({
                "success": False,
                "error": "Invalid tp",
                "detail": "tp must be a positive number if provided"
            }), 400

        if sl is not None and (not isinstance(sl, (int, float)) or sl <= 0):
            return jsonify({
                "success": False,
                "error": "Invalid sl",
                "detail": "sl must be a positive number if provided"
            }), 400

        api_key, api_secret = request.liquid_credentials
        liquid = LiquidService(api_key, api_secret)

        result = liquid.set_tp_sl(symbol, tp, sl)

        return jsonify({
            "success": True,
            "data": result
        }), 200

    except Exception as e:
        return jsonify({
            "success": False,
            "error": "Failed to set TP/SL",
            "detail": str(e)
        }), 500


@positions_bp.route("/update_leverage", methods=["POST"])
@require_api_key
@validate_phone_and_keys
def update_leverage():
    """
    Update position leverage

    Request Body:
        {
            "phone_number": str,
            "symbol": str,              # e.g., "BTC-PERP"
            "leverage": int,            # 1-200
            "is_cross": bool            # optional: use cross margin (default: false)
        }

    Returns:
        Leverage update result
    """
    try:
        data = request.get_json()
        symbol = data.get("symbol")
        leverage = data.get("leverage")
        is_cross = data.get("is_cross", False)

        if not symbol:
            return jsonify({
                "success": False,
                "error": "Missing symbol",
                "detail": "symbol field is required"
            }), 400

        if not leverage:
            return jsonify({
                "success": False,
                "error": "Missing leverage",
                "detail": "leverage field is required"
            }), 400

        if not isinstance(leverage, int) or leverage < 1 or leverage > 200:
            return jsonify({
                "success": False,
                "error": "Invalid leverage",
                "detail": "leverage must be between 1 and 200"
            }), 400

        api_key, api_secret = request.liquid_credentials
        liquid = LiquidService(api_key, api_secret)

        result = liquid.update_leverage(symbol, leverage, is_cross)

        return jsonify({
            "success": True,
            "data": result
        }), 200

    except Exception as e:
        return jsonify({
            "success": False,
            "error": "Failed to update leverage",
            "detail": str(e)
        }), 500


@positions_bp.route("/update_margin", methods=["POST"])
@require_api_key
@validate_phone_and_keys
def update_margin():
    """
    Update position margin

    Request Body:
        {
            "phone_number": str,
            "symbol": str,              # e.g., "BTC-PERP"
            "amount": float             # positive to add, negative to remove
        }

    Returns:
        Margin update result
    """
    try:
        data = request.get_json()
        symbol = data.get("symbol")
        amount = data.get("amount")

        if not symbol:
            return jsonify({
                "success": False,
                "error": "Missing symbol",
                "detail": "symbol field is required"
            }), 400

        if amount is None:
            return jsonify({
                "success": False,
                "error": "Missing amount",
                "detail": "amount field is required"
            }), 400

        if not isinstance(amount, (int, float)) or amount == 0:
            return jsonify({
                "success": False,
                "error": "Invalid amount",
                "detail": "amount must be a non-zero number"
            }), 400

        api_key, api_secret = request.liquid_credentials
        liquid = LiquidService(api_key, api_secret)

        result = liquid.update_margin(symbol, amount)

        return jsonify({
            "success": True,
            "data": result
        }), 200

    except Exception as e:
        return jsonify({
            "success": False,
            "error": "Failed to update margin",
            "detail": str(e)
        }), 500
