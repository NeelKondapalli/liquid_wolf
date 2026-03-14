"""
Main Flask application
"""
import os
from flask import Flask, jsonify
from flask_cors import CORS
from app.core.config import Config
from app.routers.market_data import market_data_bp
from app.routers.account import account_bp
from app.routers.orders import orders_bp
from app.routers.positions import positions_bp
from app.routers.user import user_bp
from app.services.supabase_service import supabase_service


def create_app():
    """Create and configure the Flask application"""

    app = Flask(__name__)
    app.config.from_object(Config)

    # Enable CORS
    CORS(app, resources={r"/api/*": {"origins": "*"}})

    # Register blueprints
    app.register_blueprint(user_bp)
    app.register_blueprint(market_data_bp)
    app.register_blueprint(account_bp)
    app.register_blueprint(orders_bp)
    app.register_blueprint(positions_bp)

    # Health check endpoint
    @app.route("/health", methods=["GET"])
    def health_check():
        """Health check endpoint"""
        return jsonify({
            "status": "ok",
            "version": Config.APP_VERSION,
            "app": Config.APP_NAME
        }), 200

    # Supabase test endpoint
    @app.route("/test", methods=["GET"])
    def test_supabase():
        """Test Supabase connection and keys"""
        try:
            # Try to query the users table to test connection
            response = supabase_service.client.table("users").select("phone_number").limit(1).execute()

            return jsonify({
                "success": True,
                "message": "Supabase connection successful",
                "config": {
                    "supabase_url": Config.SUPABASE_URL,
                    "has_key": bool(Config.SUPABASE_KEY),
                    "key_length": len(Config.SUPABASE_KEY) if Config.SUPABASE_KEY else 0
                },
                "test_query": {
                    "table": "users",
                    "status": "success",
                    "records_found": len(response.data)
                }
            }), 200
        except Exception as e:
            return jsonify({
                "success": False,
                "message": "Supabase connection failed",
                "error": str(e),
                "config": {
                    "supabase_url": Config.SUPABASE_URL,
                    "has_key": bool(Config.SUPABASE_KEY),
                    "key_length": len(Config.SUPABASE_KEY) if Config.SUPABASE_KEY else 0
                }
            }), 500

    # Root endpoint
    @app.route("/", methods=["GET"])
    def root():
        """Root endpoint with API info"""
        return jsonify({
            "app": Config.APP_NAME,
            "version": Config.APP_VERSION,
            "endpoints": {
                "health": "/health",
                "test": "/test",
                "user": "/api/v1/user/*",
                "market_data": "/api/v1/market/*",
                "account": "/api/v1/account/*",
                "orders": "/api/v1/orders/*",
                "positions": "/api/v1/positions/*"
            },
            "documentation": "See API_REFERENCE.md for complete API documentation"
        }), 200

    # Error handlers
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            "success": False,
            "error": "Not found",
            "detail": "The requested endpoint does not exist"
        }), 404

    @app.errorhandler(405)
    def method_not_allowed(error):
        return jsonify({
            "success": False,
            "error": "Method not allowed",
            "detail": "The requested method is not allowed for this endpoint"
        }), 405

    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({
            "success": False,
            "error": "Internal server error",
            "detail": str(error)
        }), 500

    return app


# Create the app instance
app = create_app()


if __name__ == "__main__":
    # Get port from environment or use 8000
    port = int(os.getenv("PORT", "8000"))
    app.run(
        host="0.0.0.0",
        port=port,
        debug=Config.DEBUG
    )
