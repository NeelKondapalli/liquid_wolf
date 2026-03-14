"""
Account endpoints
"""
from flask import Blueprint, request, jsonify
from app.core.auth import require_api_key, validate_phone_and_keys
from app.services.liquid_service import LiquidService

account_bp = Blueprint("account", __name__, url_prefix="/api/v1/account")


@account_bp.route("/info", methods=["POST"])
@require_api_key
@validate_phone_and_keys
def get_account_info():
    """
    Get account information with positions

    Request Body:
        {
            "phone_number": str
        }

    Returns:
        Account data with equity, margin_used, available_balance, account_value, and positions array
    """
    try:
        api_key, api_secret = request.liquid_credentials
        liquid = LiquidService(api_key, api_secret)

        # Get account info
        account = liquid.get_account()

        # Get positions and include in the response
        positions = liquid.get_positions()
        account["positions"] = positions

        return jsonify({
            "success": True,
            "data": account
        }), 200

    except Exception as e:
        return jsonify({
            "success": False,
            "error": "Failed to fetch account info",
            "detail": str(e)
        }), 500


@account_bp.route("/balances", methods=["POST"])
@require_api_key
@validate_phone_and_keys
def get_balances():
    """
    Get detailed balance information

    Request Body:
        {
            "phone_number": str
        }

    Returns:
        Detailed balance data including cross_margin info
    """
    try:
        api_key, api_secret = request.liquid_credentials
        liquid = LiquidService(api_key, api_secret)

        balances = liquid.get_balances()

        return jsonify({
            "success": True,
            "data": balances
        }), 200

    except Exception as e:
        return jsonify({
            "success": False,
            "error": "Failed to fetch balances",
            "detail": str(e)
        }), 500


@account_bp.route("/positions", methods=["POST"])
@require_api_key
@validate_phone_and_keys
def get_positions():
    """
    Get all open positions

    Request Body:
        {
            "phone_number": str
        }

    Returns:
        List of open positions
    """
    try:
        api_key, api_secret = request.liquid_credentials
        liquid = LiquidService(api_key, api_secret)

        positions = liquid.get_positions()

        return jsonify({
            "success": True,
            "data": positions
        }), 200

    except Exception as e:
        return jsonify({
            "success": False,
            "error": "Failed to fetch positions",
            "detail": str(e)
        }), 500
