"""
User management endpoints for frontend integration
"""
from flask import Blueprint, request, jsonify
from app.core.auth import require_api_key
from app.services.supabase_service import supabase_service

user_bp = Blueprint("user", __name__, url_prefix="/api/v1/user")


@user_bp.route("/check", methods=["POST"])
@require_api_key
def check_user():
    """
    Check if user exists in the database

    Request Body:
        {
            "phone_number": str
        }

    Returns:
        {
            "success": true,
            "data": {
                "exists": bool
            }
        }
    """
    try:
        data = request.get_json()

        if not data:
            return jsonify({
                "success": False,
                "error": "Invalid request",
                "detail": "Request body must be JSON"
            }), 400

        phone_number = data.get("phone_number")

        if not phone_number:
            return jsonify({
                "success": False,
                "error": "Missing phone_number",
                "detail": "phone_number field is required"
            }), 400

        exists = supabase_service.check_user_exists(phone_number)

        return jsonify({
            "success": True,
            "data": {"exists": exists}
        }), 200

    except Exception as e:
        return jsonify({
            "success": False,
            "error": "Failed to check user",
            "detail": str(e)
        }), 500


@user_bp.route("/create", methods=["POST"])
@require_api_key
def create_user():
    """
    Create a new user in the database

    Request Body:
        {
            "phone_number": str
        }

    Returns:
        {
            "success": true,
            "data": {
                "created": bool,
                "message": str (optional)
            }
        }
    """
    try:
        data = request.get_json()

        if not data:
            return jsonify({
                "success": False,
                "error": "Invalid request",
                "detail": "Request body must be JSON"
            }), 400

        phone_number = data.get("phone_number")

        if not phone_number:
            return jsonify({
                "success": False,
                "error": "Missing phone_number",
                "detail": "phone_number field is required"
            }), 400

        # Check if user already exists
        exists = supabase_service.check_user_exists(phone_number)
        if exists:
            return jsonify({
                "success": True,
                "data": {
                    "created": False,
                    "message": "User already exists"
                }
            }), 200

        # Create user
        created = supabase_service.create_user(phone_number)

        return jsonify({
            "success": True,
            "data": {
                "created": created,
                "message": "User created successfully"
            }
        }), 200

    except Exception as e:
        return jsonify({
            "success": False,
            "error": "Failed to create user",
            "detail": str(e)
        }), 500


@user_bp.route("/has_keys", methods=["POST"])
@require_api_key
def has_keys():
    """
    Check if user has active Liquid API keys

    Request Body:
        {
            "phone_number": str
        }

    Returns:
        {
            "success": true,
            "data": {
                "has_keys": bool
            }
        }
    """
    try:
        data = request.get_json()

        if not data:
            return jsonify({
                "success": False,
                "error": "Invalid request",
                "detail": "Request body must be JSON"
            }), 400

        phone_number = data.get("phone_number")

        if not phone_number:
            return jsonify({
                "success": False,
                "error": "Missing phone_number",
                "detail": "phone_number field is required"
            }), 400

        has_keys = supabase_service.has_active_keys(phone_number)

        return jsonify({
            "success": True,
            "data": {"has_keys": has_keys}
        }), 200

    except Exception as e:
        return jsonify({
            "success": False,
            "error": "Failed to check keys",
            "detail": str(e)
        }), 500


@user_bp.route("/save_keys", methods=["POST"])
@require_api_key
def save_keys():
    """
    Save or update user's Liquid API keys

    Request Body:
        {
            "phone_number": str,
            "api_key": str,        # Liquid API key (lq_...)
            "api_secret": str      # Liquid API secret (sk_...)
        }

    Returns:
        {
            "success": true,
            "data": {
                "saved": bool,
                "message": str
            }
        }
    """
    try:
        data = request.get_json()

        if not data:
            return jsonify({
                "success": False,
                "error": "Invalid request",
                "detail": "Request body must be JSON"
            }), 400

        phone_number = data.get("phone_number")
        api_key = data.get("api_key")
        api_secret = data.get("api_secret")

        if not all([phone_number, api_key, api_secret]):
            return jsonify({
                "success": False,
                "error": "Missing required fields",
                "detail": "phone_number, api_key, and api_secret are required"
            }), 400

        # Basic validation
        if not api_key.startswith("lq_"):
            return jsonify({
                "success": False,
                "error": "Invalid API key format",
                "detail": "API key should start with 'lq_'"
            }), 400

        if not api_secret.startswith("sk_"):
            return jsonify({
                "success": False,
                "error": "Invalid API secret format",
                "detail": "API secret should start with 'sk_'"
            }), 400

        # Verify user exists
        exists = supabase_service.check_user_exists(phone_number)
        if not exists:
            return jsonify({
                "success": False,
                "error": "User not found",
                "detail": f"No user found with phone number: {phone_number}"
            }), 404

        # TODO: Optionally test the keys with Liquid API before saving
        # from app.services.liquid_service import LiquidService
        # try:
        #     liquid = LiquidService(api_key, api_secret)
        #     liquid.get_account()  # Test call
        # except Exception as e:
        #     return jsonify({
        #         "success": False,
        #         "error": "Invalid Liquid API credentials",
        #         "detail": str(e)
        #     }), 400

        # Save keys (this will replace existing keys if any)
        saved = supabase_service.add_liquid_keys(phone_number, api_key, api_secret)

        return jsonify({
            "success": True,
            "data": {
                "saved": saved,
                "message": "API keys saved successfully"
            }
        }), 200

    except Exception as e:
        return jsonify({
            "success": False,
            "error": "Failed to save keys",
            "detail": str(e)
        }), 500


@user_bp.route("/delete_keys", methods=["POST"])
@require_api_key
def delete_keys():
    """
    Deactivate user's Liquid API keys

    Request Body:
        {
            "phone_number": str
        }

    Returns:
        {
            "success": true,
            "data": {
                "deactivated": bool
            }
        }
    """
    try:
        data = request.get_json()

        if not data:
            return jsonify({
                "success": False,
                "error": "Invalid request",
                "detail": "Request body must be JSON"
            }), 400

        phone_number = data.get("phone_number")

        if not phone_number:
            return jsonify({
                "success": False,
                "error": "Missing phone_number",
                "detail": "phone_number field is required"
            }), 400

        deactivated = supabase_service.deactivate_liquid_keys(phone_number)

        return jsonify({
            "success": True,
            "data": {
                "deactivated": deactivated,
                "message": "API keys deactivated successfully"
            }
        }), 200

    except Exception as e:
        return jsonify({
            "success": False,
            "error": "Failed to deactivate keys",
            "detail": str(e)
        }), 500
