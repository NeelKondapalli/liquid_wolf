"""
Authentication middleware for Flask
"""
from functools import wraps
from flask import request, jsonify
from app.core.config import Config
from app.services.supabase_service import supabase_service


def require_api_key(f):
    """
    Decorator to require API key authentication
    Checks X-API-Key header against configured API_SECRET_KEY
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        api_key = request.headers.get("X-API-Key")

        if not api_key:
            return jsonify({
                "success": False,
                "error": "Missing API key",
                "detail": "X-API-Key header is required"
            }), 401

        if api_key != Config.API_SECRET_KEY:
            return jsonify({
                "success": False,
                "error": "Invalid API key",
                "detail": "The provided API key is invalid"
            }), 401

        return f(*args, **kwargs)

    return decorated_function


def validate_phone_and_keys(f):
    """
    Decorator to validate phone number exists and has active Liquid API keys
    Expects phone_number in request JSON body
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
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
                "error": "Missing phone number",
                "detail": "phone_number field is required"
            }), 400

        # Check if user exists
        try:
            user_exists = supabase_service.check_user_exists(phone_number)
            if not user_exists:
                return jsonify({
                    "success": False,
                    "error": "User not found",
                    "detail": f"No user found with phone number: {phone_number}"
                }), 404
        except Exception as e:
            return jsonify({
                "success": False,
                "error": "Database error",
                "detail": str(e)
            }), 500

        # Check if user has active keys
        try:
            keys = supabase_service.get_active_liquid_keys(phone_number)
            if not keys:
                return jsonify({
                    "success": False,
                    "error": "No active API keys",
                    "detail": f"User {phone_number} has no active Liquid API keys"
                }), 404

            # Attach keys to request for use in endpoint
            request.liquid_credentials = keys

        except Exception as e:
            return jsonify({
                "success": False,
                "error": "Database error",
                "detail": str(e)
            }), 500

        return f(*args, **kwargs)

    return decorated_function
