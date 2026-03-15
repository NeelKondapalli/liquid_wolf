"""
VAPI-compliant wrapper for tool call endpoints

This blueprint wraps all tool endpoints to match VAPI's required format:
- Accepts requests with message.toolCallList array
- Returns responses in the format: {"results": [{"toolCallId": "...", "result": ...}]}
- Always returns HTTP 200 (even for errors)

VAPI Request Format:
{
  "message": {
    "timestamp": 1678901234567,
    "type": "tool-calls",
    "toolCallList": [
      {
        "id": "toolu_01DTPAzUm5Gk3zxrpJ969oMF",
        "name": "get_weather",
        "arguments": {
          "location": "San Francisco"
        }
      }
    ]
  }
}

VAPI Response Format:
{
  "results": [
    {
      "toolCallId": "toolu_01DTPAzUm5Gk3zxrpJ969oMF",
      "result": "San Francisco's weather today is 62°C, partly cloudy."
    }
  ]
}

Or for errors:
{
  "results": [
    {
      "toolCallId": "toolu_01DTPAzUm5Gk3zxrpJ969oMF",
      "error": "Error message describing what went wrong"
    }
  ]
}
"""
import json
import logging
from flask import Blueprint, request, jsonify
from app.core.auth import require_api_key, validate_phone_and_keys
from app.services.liquid_service import LiquidService

# Set up logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

vapi_bp = Blueprint("vapi", __name__, url_prefix="/vapi")


def parse_vapi_arguments(args_raw):
    """
    Parse VAPI arguments which can be either a JSON string or an object
    VAPI sends arguments as a JSON string that needs to be parsed
    """
    if isinstance(args_raw, str):
        return json.loads(args_raw)
    return args_raw


def vapi_response(tool_call_id, result=None, error=None):
    """
    Format response according to VAPI spec
    Always returns HTTP 200, even for errors
    Result can be string, number, object, array - any JSON-serializable data
    """
    response_data = {
        "results": [
            {
                "toolCallId": tool_call_id
            }
        ]
    }

    if error:
        response_data["results"][0]["error"] = str(error)
    else:
        response_data["results"][0]["result"] = result

    return jsonify(response_data), 200


@vapi_bp.route("/place_order", methods=["POST"])
@require_api_key
def vapi_place_order():
    """
    VAPI wrapper for place_order

    Expected in message.toolCallList[0].arguments:
    {
        "phone_number": str,
        "symbol": str,
        "side": str,
        "size": float,
        "leverage": int (optional),
        "type": str (optional),
        "price": float (optional)
    }
    """
    try:
        data = request.get_json()
        logger.info("="*60)
        logger.info("VAPI REQUEST - place_order")
        logger.info(f"Full request body: {json.dumps(data, indent=2)}")
        logger.info("="*60)

        message = data.get("message", {})
        tool_call_list = message.get("toolCallList", [])

        if not tool_call_list:
            return vapi_response("unknown", error="Missing toolCallList in request")

        tool_call = tool_call_list[0]
        tool_call_id = tool_call.get("id")

        # Parse arguments - can be JSON string or object
        function_data = tool_call.get("function", {})
        args = parse_vapi_arguments(function_data.get("arguments", {}))

        # Extract phone_number
        phone_number = args.get("phone_number")
        if not phone_number:
            return vapi_response(tool_call_id, error="Missing phone_number")

        # Validate user and get credentials
        from app.services.supabase_service import supabase_service

        try:
            user_exists = supabase_service.check_user_exists(phone_number)
            if not user_exists:
                return vapi_response(tool_call_id, error=f"User not found: {phone_number}")
        except Exception as e:
            return vapi_response(tool_call_id, error=f"Database error: {str(e)}")

        try:
            keys = supabase_service.get_active_liquid_keys(phone_number)
            if not keys:
                return vapi_response(tool_call_id, error=f"No active API keys for {phone_number}")
            api_key, api_secret = keys
        except Exception as e:
            return vapi_response(tool_call_id, error=f"Failed to get API keys: {str(e)}")

        # Extract order parameters
        symbol = args.get("symbol")
        side = args.get("side")
        size = args.get("size")

        if not all([symbol, side, size]):
            return vapi_response(tool_call_id, error="Missing required fields: symbol, side, and size are required")

        if side not in ["buy", "sell"]:
            return vapi_response(tool_call_id, error="Invalid side: must be 'buy' or 'sell'")

        if not isinstance(size, (int, float)) or size <= 0:
            return vapi_response(tool_call_id, error="Invalid size: must be a positive number")

        # Optional fields
        order_type = args.get("type", "market")
        price = args.get("price")
        leverage = args.get("leverage", 1)
        time_in_force = args.get("time_in_force", "gtc")
        tp = args.get("tp")
        sl = args.get("sl")
        reduce_only = args.get("reduce_only", False)

        if order_type not in ["market", "limit"]:
            return vapi_response(tool_call_id, error="Invalid type: must be 'market' or 'limit'")

        if order_type == "limit" and not price:
            return vapi_response(tool_call_id, error="Missing price: required for limit orders")

        if not isinstance(leverage, int) or leverage < 1 or leverage > 200:
            return vapi_response(tool_call_id, error="Invalid leverage: must be between 1 and 200")

        # Place order
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

        return vapi_response(tool_call_id, result=order)

    except Exception as e:
        tool_call_id = "unknown"
        if 'data' in locals():
            tool_call_list = data.get("message", {}).get("toolCallList", [])
            if tool_call_list:
                tool_call_id = tool_call_list[0].get("id", "unknown")
        return vapi_response(tool_call_id, error=f"Failed to place order: {str(e)}")


@vapi_bp.route("/get_account_info", methods=["POST"])
@require_api_key
def vapi_get_account_info():
    """
    VAPI wrapper for get_account_info

    Expected in message.toolCallList[0].function.arguments:
    {
        "phone_number": str
    }
    """
    try:
        data = request.get_json()
        logger.info("="*60)
        logger.info("VAPI REQUEST - get_account_info")
        logger.info(f"Full request body: {json.dumps(data, indent=2)}")
        logger.info("="*60)

        message = data.get("message", {})
        tool_call_list = message.get("toolCallList", [])

        if not tool_call_list:
            return vapi_response("unknown", error="Missing toolCallList in request")

        tool_call = tool_call_list[0]
        tool_call_id = tool_call.get("id")

        # Parse arguments - can be JSON string or object
        function_data = tool_call.get("function", {})
        args = parse_vapi_arguments(function_data.get("arguments", {}))

        phone_number = args.get("phone_number")
        if not phone_number:
            return vapi_response(tool_call_id, error="Missing phone_number")

        # Validate user and get credentials
        from app.services.supabase_service import supabase_service

        try:
            user_exists = supabase_service.check_user_exists(phone_number)
            if not user_exists:
                return vapi_response(tool_call_id, error=f"User not found: {phone_number}")
        except Exception as e:
            return vapi_response(tool_call_id, error=f"Database error: {str(e)}")

        try:
            keys = supabase_service.get_active_liquid_keys(phone_number)
            if not keys:
                return vapi_response(tool_call_id, error=f"No active API keys for {phone_number}")
            api_key, api_secret = keys
        except Exception as e:
            return vapi_response(tool_call_id, error=f"Failed to get API keys: {str(e)}")

        # Get account info
        liquid = LiquidService(api_key, api_secret)
        account = liquid.get_account()
        positions = liquid.get_positions()
        account["positions"] = positions

        return vapi_response(tool_call_id, result=account)

    except Exception as e:
        tool_call_id = "unknown"
        if 'data' in locals():
            tool_call_list = data.get("message", {}).get("toolCallList", [])
            if tool_call_list:
                tool_call_id = tool_call_list[0].get("id", "unknown")
        return vapi_response(tool_call_id, error=f"Failed to fetch account info: {str(e)}")


@vapi_bp.route("/get_positions", methods=["POST"])
@require_api_key
def vapi_get_positions():
    """
    VAPI wrapper for get_positions

    Expected in message.toolCallList[0].function.arguments:
    {
        "phone_number": str
    }
    """
    try:
        data = request.get_json()
        logger.info("="*60)
        logger.info("VAPI REQUEST - get_positions")
        logger.info(f"Full request body: {json.dumps(data, indent=2)}")
        logger.info("="*60)

        message = data.get("message", {})
        tool_call_list = message.get("toolCallList", [])

        if not tool_call_list:
            return vapi_response("unknown", error="Missing toolCallList in request")

        tool_call = tool_call_list[0]
        tool_call_id = tool_call.get("id")

        # Parse arguments - can be JSON string or object
        function_data = tool_call.get("function", {})
        args = parse_vapi_arguments(function_data.get("arguments", {}))

        phone_number = args.get("phone_number")
        if not phone_number:
            return vapi_response(tool_call_id, error="Missing phone_number")

        # Validate user and get credentials
        from app.services.supabase_service import supabase_service

        try:
            user_exists = supabase_service.check_user_exists(phone_number)
            if not user_exists:
                return vapi_response(tool_call_id, error=f"User not found: {phone_number}")
        except Exception as e:
            return vapi_response(tool_call_id, error=f"Database error: {str(e)}")

        try:
            keys = supabase_service.get_active_liquid_keys(phone_number)
            if not keys:
                return vapi_response(tool_call_id, error=f"No active API keys for {phone_number}")
            api_key, api_secret = keys
        except Exception as e:
            return vapi_response(tool_call_id, error=f"Failed to get API keys: {str(e)}")

        # Get positions
        liquid = LiquidService(api_key, api_secret)
        positions = liquid.get_positions()

        return vapi_response(tool_call_id, result=positions)

    except Exception as e:
        tool_call_id = "unknown"
        if 'data' in locals():
            tool_call_list = data.get("message", {}).get("toolCallList", [])
            if tool_call_list:
                tool_call_id = tool_call_list[0].get("id", "unknown")
        return vapi_response(tool_call_id, error=f"Failed to fetch positions: {str(e)}")


@vapi_bp.route("/get_open_orders", methods=["POST"])
@require_api_key
def vapi_get_open_orders():
    """
    VAPI wrapper for get_open_orders

    Expected in message.toolCallList[0].function.arguments:
    {
        "phone_number": str
    }
    """
    try:
        data = request.get_json()
        logger.info("="*60)
        logger.info("VAPI REQUEST - get_open_orders")
        logger.info(f"Request headers: {dict(request.headers)}")
        logger.info(f"Request method: {request.method}")
        logger.info(f"Request path: {request.path}")
        logger.info(f"Remote address: {request.remote_addr}")
        logger.info(f"Full request body: {json.dumps(data, indent=2)}")
        logger.info("="*60)

        message = data.get("message", {})
        tool_call_list = message.get("toolCallList", [])

        if not tool_call_list:
            return vapi_response("unknown", error="Missing toolCallList in request")

        tool_call = tool_call_list[0]
        tool_call_id = tool_call.get("id")

        # Parse arguments - can be JSON string or object
        function_data = tool_call.get("function", {})
        args = parse_vapi_arguments(function_data.get("arguments", {}))

        phone_number = args.get("phone_number")
        logger.info(f">>> Extracted phone_number: '{phone_number}' (length: {len(phone_number) if phone_number else 0})")
        logger.info(f">>> Raw arguments dict: {args}")

        if not phone_number:
            return vapi_response(tool_call_id, error="Missing phone_number")

        # Validate user and get credentials
        from app.services.supabase_service import supabase_service

        try:
            user_exists = supabase_service.check_user_exists(phone_number)
            if not user_exists:
                return vapi_response(tool_call_id, error=f"User not found: {phone_number}")
        except Exception as e:
            return vapi_response(tool_call_id, error=f"Database error: {str(e)}")

        try:
            keys = supabase_service.get_active_liquid_keys(phone_number)
            if not keys:
                return vapi_response(tool_call_id, error=f"No active API keys for {phone_number}")
            api_key, api_secret = keys
            logger.info(f"Retrieved API Key (first 10 chars): {api_key[:10]}...")
            logger.info(f"Retrieved API Secret (first 10 chars): {api_secret[:10]}...")
        except Exception as e:
            return vapi_response(tool_call_id, error=f"Failed to get API keys: {str(e)}")

        # Get open orders
        logger.info(f"Calling Liquid API with credentials...")
        try:
            liquid = LiquidService(api_key, api_secret)
            orders = liquid.get_open_orders()
            logger.info(f"Successfully retrieved {len(orders)} open orders")
            return vapi_response(tool_call_id, result=orders)
        except Exception as liquid_error:
            logger.error(f"Liquid API error: {type(liquid_error).__name__}: {str(liquid_error)}")
            # Return the actual Liquid API error to help debug
            return vapi_response(tool_call_id, error=f"Liquid API error: {str(liquid_error)}")

    except Exception as e:
        tool_call_id = "unknown"
        if 'data' in locals():
            tool_call_list = data.get("message", {}).get("toolCallList", [])
            if tool_call_list:
                tool_call_id = tool_call_list[0].get("id", "unknown")
        logger.error(f"VAPI endpoint error: {type(e).__name__}: {str(e)}")
        return vapi_response(tool_call_id, error=f"Server error: {str(e)}")


@vapi_bp.route("/cancel_order", methods=["POST"])
@require_api_key
def vapi_cancel_order():
    """
    VAPI wrapper for cancel_order

    Expected in message.toolCallList[0].function.arguments:
    {
        "phone_number": str,
        "order_id": str
    }
    """
    try:
        data = request.get_json()
        logger.info("="*60)
        logger.info("VAPI REQUEST - cancel_order")
        logger.info(f"Full request body: {json.dumps(data, indent=2)}")
        logger.info("="*60)

        message = data.get("message", {})
        tool_call_list = message.get("toolCallList", [])

        if not tool_call_list:
            return vapi_response("unknown", error="Missing toolCallList in request")

        tool_call = tool_call_list[0]
        tool_call_id = tool_call.get("id")

        # Parse arguments - can be JSON string or object
        function_data = tool_call.get("function", {})
        args = parse_vapi_arguments(function_data.get("arguments", {}))

        phone_number = args.get("phone_number")
        order_id = args.get("order_id")

        if not phone_number:
            return vapi_response(tool_call_id, error="Missing phone_number")

        if not order_id:
            return vapi_response(tool_call_id, error="Missing order_id")

        # Validate user and get credentials
        from app.services.supabase_service import supabase_service

        try:
            user_exists = supabase_service.check_user_exists(phone_number)
            if not user_exists:
                return vapi_response(tool_call_id, error=f"User not found: {phone_number}")
        except Exception as e:
            return vapi_response(tool_call_id, error=f"Database error: {str(e)}")

        try:
            keys = supabase_service.get_active_liquid_keys(phone_number)
            if not keys:
                return vapi_response(tool_call_id, error=f"No active API keys for {phone_number}")
            api_key, api_secret = keys
        except Exception as e:
            return vapi_response(tool_call_id, error=f"Failed to get API keys: {str(e)}")

        # Cancel order
        liquid = LiquidService(api_key, api_secret)
        result = liquid.cancel_order(order_id)

        return vapi_response(tool_call_id, result={"cancelled": result})

    except Exception as e:
        tool_call_id = "unknown"
        if 'data' in locals():
            tool_call_list = data.get("message", {}).get("toolCallList", [])
            if tool_call_list:
                tool_call_id = tool_call_list[0].get("id", "unknown")
        return vapi_response(tool_call_id, error=f"Failed to cancel order: {str(e)}")
