"""
Vapi Tool Definitions for Liquid Wolf Trading

These tools configure Vapi to make direct HTTP calls to your Liquid Wolf server.
Each tool has a function definition and a server URL that points to your API endpoint.

When you expose your server via ngrok, update the BASE_URL in .env file.
"""

import os
from dotenv import load_dotenv

# Load env
load_dotenv()

# Your server URL (set this in .env as LIQUID_API_URL)
BASE_URL = os.getenv("LIQUID_API_URL", "http://localhost:8001")
API_KEY = os.getenv("LIQUID_API_KEY", "your-secret-key-change-in-production")


# Tool 1: Place Order (Buy/Sell positions)
PLACE_ORDER_TOOL = {
    "type": "function",
    "function": {
        "name": "place_order",
        "description": (
            "Place a trading order to buy or sell a cryptocurrency position. "
            "Use this when the user wants to open a new position, go long/short, "
            "or buy/sell a specific cryptocurrency. "
            "Examples: 'buy $100 of Bitcoin', 'sell ETH', 'short SOL with 10x leverage'"
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "phone_number": {
                    "type": "string",
                    "description": "User's phone number in E.164 format (e.g., +15305747238)"
                },
                "symbol": {
                    "type": "string",
                    "description": "Trading symbol - use perpetual futures symbols ending in -PERP. For example, BTC-PERP for Bitcoin.",
                },
                "side": {
                    "type": "string",
                    "description": "'buy' for long positions (betting price goes up), 'sell' for short positions (betting price goes down)",
                    "enum": ["buy", "sell"]
                },
                "size": {
                    "type": "number",
                    "description": "Order size in USD notional value (must be positive). This is how much USD value you want to trade.",
                    "minimum": 1
                },
                "leverage": {
                    "type": "integer",
                    "description": "Leverage multiplier (1-200). Default is 1 for no leverage. 10x means 10 times leverage.",
                    "minimum": 1,
                    "maximum": 200,
                    "default": 1
                },
                "type": {
                    "type": "string",
                    "description": "'market' for immediate execution at current price, 'limit' for execution at specified price",
                    "enum": ["market", "limit"],
                    "default": "market"
                },
                "price": {
                    "type": "number",
                    "description": "Limit price (required only for limit orders). The price at which you want the order to execute.",
                    "minimum": 0
                }
            },
            "required": ["phone_number", "symbol", "side", "size"]
        }
    },
    "server": {
        "url": f"{BASE_URL}/vapi/place_order",
        "timeoutSeconds": 30,
        "headers": {
            "X-API-Key": API_KEY
        }
    }
}

# Tool 2: Get Account Info
GET_ACCOUNT_INFO_TOOL = {
    "type": "function",
    "function": {
        "name": "get_account_info",
        "description": (
            "Get the user's trading account information including balance, equity, "
            "margin usage, and open positions. Use this when the user asks about "
            "their account, balance, how much money they have, or what positions they're in. "
            "Examples: 'what's my balance?', 'how much do I have?', 'show my account', "
            "'what positions am I in?'"
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "phone_number": {
                    "type": "string",
                    "description": "User's phone number in E.164 format (e.g., +15305747238)"
                }
            },
            "required": ["phone_number"]
        }
    },
    "server": {
        "url": f"{BASE_URL}/vapi/get_account_info",
        "timeoutSeconds": 30,
        "headers": {
            "X-API-Key": API_KEY
        }
    }
}

# Tool 3: Get Open Positions
GET_POSITIONS_TOOL = {
    "type": "function",
    "function": {
        "name": "get_positions",
        "description": (
            "Get all currently open trading positions with details like entry price, "
            "current profit/loss, and liquidation price. Use this when user asks "
            "specifically about their positions or wants detailed position information. "
            "Examples: 'show my positions', 'what am I trading?', 'how's my Bitcoin position doing?'"
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "phone_number": {
                    "type": "string",
                    "description": "User's phone number in E.164 format (e.g., +15305747238)"
                }
            },
            "required": ["phone_number"]
        }
    },
    "server": {
        "url": f"{BASE_URL}/vapi/get_positions",
        "timeoutSeconds": 30,
        "headers": {
            "X-API-Key": API_KEY
        }
    }
}

# Tool 4: Get Open Orders
GET_OPEN_ORDERS_TOOL = {
    "type": "function",
    "function": {
        "name": "get_open_orders",
        "description": (
            "Get all currently open orders that haven't been executed yet. "
            "These are typically limit orders waiting to be filled. "
            "Use when user asks about pending orders or limit orders. "
            "Examples: 'do I have any open orders?', 'show my pending orders'"
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "phone_number": {
                    "type": "string",
                    "description": "User's phone number in E.164 format (e.g., +15305747238)"
                }
            },
            "required": ["phone_number"]
        }
    },
    "server": {
        "url": f"{BASE_URL}/vapi/get_open_orders",
        "timeoutSeconds": 30,
        "headers": {
            "X-API-Key": API_KEY
        }
    }
}

# Tool 5: Cancel Order
CANCEL_ORDER_TOOL = {
    "type": "function",
    "function": {
        "name": "cancel_order",
        "description": (
            "Cancel a specific open order by its ID. Use this when the user wants to "
            "cancel or remove a pending order. You'll need to get the order ID first "
            "by calling get_open_orders. "
            "Examples: 'cancel my order', 'remove that pending order'"
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "phone_number": {
                    "type": "string",
                    "description": "User's phone number in E.164 format (e.g., +15305747238)"
                },
                "order_id": {
                    "type": "string",
                    "description": "The unique order ID to cancel (obtained from get_open_orders)"
                }
            },
            "required": ["phone_number", "order_id"]
        }
    },
    "server": {
        "url": f"{BASE_URL}/vapi/cancel_order",
        "timeoutSeconds": 30,
        "headers": {
            "X-API-Key": API_KEY
        }
    }
}

# All tools list
ALL_TOOLS = [
    PLACE_ORDER_TOOL,
    GET_ACCOUNT_INFO_TOOL,
    GET_POSITIONS_TOOL,
    GET_OPEN_ORDERS_TOOL,
    CANCEL_ORDER_TOOL
]
