"""
Update Vapi Assistant with Liquid Wolf Trading Tools

This script:
1. Creates tools in Vapi (if they don't exist)
2. Updates your assistant to use those tools

Usage:
python -m vapi_integration.update_assistant --server-url https://your-ngrok-url.ngrok-free.app

Required: Set VAPI_API_KEY in vapi_integration/.env
"""

import os
import sys
import requests
import argparse
from dotenv import load_dotenv

# Load environment
load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))

VAPI_API_KEY = os.getenv("VAPI_API_KEY")
VAPI_ORG_ID = os.getenv("VAPI_ORG_ID")
ASSISTANT_ID = "197591bc-b2ac-41fa-b48a-7f3b017f1b68"

if not VAPI_API_KEY:
    print("Error: VAPI_API_KEY not found in .env")
    sys.exit(1)


def create_tool_definitions(server_url: str, api_key: str):
    """
    Create tool definitions for Vapi

    Args:
        server_url: Your ngrok or server URL
        api_key: Your Liquid Wolf API key

    Returns:
        List of tool definitions
    """
    # Shared server config
    server_config = {
        "timeoutSeconds": 30,
        "headers": {
            "X-API-Key": api_key,
            "Content-Type": "application/json"
        }
    }

    tools = [
        # Tool 1: Place Order
        {
            "type": "function",
            "function": {
                "name": "place_order",
                "description": (
                    "Place a trading order to buy or sell cryptocurrency. "
                    "Use when user wants to open a position, go long/short, or trade crypto. "
                    "Examples: 'buy $100 of Bitcoin', 'short ETH with 5x leverage'"
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "phone_number": {
                            "type": "string",
                            "description": "User's phone number from the call in E.164 format"
                        },
                        "symbol": {
                            "type": "string",
                            "description": "Trading symbol. Use BTC-PERP for Bitcoin, ETH-PERP for Ethereum, SOL-PERP for Solana."
                        },
                        "side": {
                            "type": "string",
                            "description": "'buy' for long (price up), 'sell' for short (price down)",
                            "enum": ["buy", "sell"]
                        },
                        "size": {
                            "type": "number",
                            "description": "USD amount (e.g., 100 = $100)",
                            "minimum": 1
                        },
                        "leverage": {
                            "type": "integer",
                            "description": "Leverage 1-200. Default 1.",
                            "minimum": 1,
                            "maximum": 200,
                            "default": 1
                        },
                        "type": {
                            "type": "string",
                            "enum": ["market", "limit"],
                            "default": "market"
                        }
                    },
                    "required": ["phone_number", "symbol", "side", "size"]
                }
            },
            "server": {
                **server_config,
                "url": f"{server_url}/vapi/place_order"
            }
        },

        # Tool 2: Get Account Info
        {
            "type": "function",
            "function": {
                "name": "get_account_info",
                "description": (
                    "Get account balance, equity, margin, and positions. "
                    "Use when user asks: 'what's my balance?', 'how much do I have?', 'show my account'"
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "phone_number": {
                            "type": "string",
                            "description": "User's phone number from the call"
                        }
                    },
                    "required": ["phone_number"]
                }
            },
            "server": {
                **server_config,
                "url": f"{server_url}/vapi/get_account_info"
            }
        },

        # Tool 3: Get Positions
        {
            "type": "function",
            "function": {
                "name": "get_positions",
                "description": (
                    "Get detailed info on open positions with PnL, entry price, liquidation price."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "phone_number": {
                            "type": "string",
                            "description": "User's phone number from the call"
                        }
                    },
                    "required": ["phone_number"]
                }
            },
            "server": {
                **server_config,
                "url": f"{server_url}/vapi/get_positions"
            }
        },

        # Tool 4: Get Open Orders
        {
            "type": "function",
            "function": {
                "name": "get_open_orders",
                "description": "Get pending orders that haven't executed yet.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "phone_number": {
                            "type": "string",
                            "description": "User's phone number from the call"
                        }
                    },
                    "required": ["phone_number"]
                }
            },
            "server": {
                **server_config,
                "url": f"{server_url}/vapi/get_open_orders"
            }
        }
    ]

    return tools


def get_existing_tools():
    """Get all existing tools from Vapi"""
    url = "https://api.vapi.ai/tool"
    headers = {
        "Authorization": f"Bearer {VAPI_API_KEY}"
    }

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        return response.json()
    else:
        print(f"Warning: Could not fetch existing tools: {response.status_code}")
        return []


def create_tool(tool_def):
    """Create a tool in Vapi"""
    url = "https://api.vapi.ai/tool"
    headers = {
        "Authorization": f"Bearer {VAPI_API_KEY}",
        "Content-Type": "application/json"
    }

    response = requests.post(url, headers=headers, json=tool_def)

    if response.status_code in [200, 201]:
        data = response.json()
        return data.get("id")
    else:
        print(f"Error creating tool: {response.status_code}")
        print(response.text)
        return None


def get_assistant(assistant_id: str):
    """Get assistant configuration"""
    url = f"https://api.vapi.ai/assistant/{assistant_id}"
    headers = {
        "Authorization": f"Bearer {VAPI_API_KEY}"
    }

    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    return None


def update_assistant(assistant_id: str, tool_ids: list):
    """
    Update the assistant to use the specified tools

    Args:
        assistant_id: Vapi assistant ID
        tool_ids: List of tool IDs to attach
    """
    url = f"https://api.vapi.ai/assistant/{assistant_id}"
    headers = {
        "Authorization": f"Bearer {VAPI_API_KEY}",
        "Content-Type": "application/json"
    }

    # Get current assistant to see what fields exist
    current = get_assistant(assistant_id)
    if not current:
        print("Could not fetch current assistant config")
        return False

    print(f"\nCurrent assistant fields: {list(current.keys())}")

    # Try different possible field names for tools
    possible_fields = ["toolIds", "tools", "tool_ids", "serverTools"]

    for field_name in possible_fields:
        payload = {field_name: tool_ids}
        print(f"\nTrying field name: '{field_name}'...")

        response = requests.patch(url, headers=headers, json=payload)

        if response.status_code == 200:
            print(f"\n✅ Assistant updated successfully with field '{field_name}'!")
            return True
        else:
            print(f"  ✗ Failed with '{field_name}': {response.status_code}")
            if response.status_code != 400:
                print(f"     {response.text}")

    print(f"\n❌ Could not find correct field name for tools")
    print(f"Last response: {response.text}")
    return False


def main():
    parser = argparse.ArgumentParser(description="Update Vapi assistant with Liquid Wolf tools")
    parser.add_argument(
        "--server-url",
        required=True,
        help="Your server URL (e.g., https://abc123.ngrok-free.app)"
    )
    parser.add_argument(
        "--api-key",
        default="your-secret-key-change-in-production",
        help="Liquid Wolf API key"
    )

    args = parser.parse_args()

    server_url = args.server_url.rstrip("/")
    if not server_url.startswith("http"):
        print("Error: Server URL must start with http:// or https://")
        sys.exit(1)

    print(f"Vapi Assistant ID: {ASSISTANT_ID}")
    print(f"Liquid Server URL: {server_url}")
    print(f"Liquid API Key: {args.api_key}\n")

    # Step 1: Create tool definitions
    print("Creating tool definitions...")
    tool_defs = create_tool_definitions(server_url, args.api_key)

    # Step 2: Check existing tools
    print("Checking existing tools...")
    existing_tools = get_existing_tools()
    existing_names = {t.get("function", {}).get("name"): t.get("id") for t in existing_tools}

    # Step 3: Create or reuse tools
    tool_ids = []
    for tool_def in tool_defs:
        tool_name = tool_def["function"]["name"]

        if tool_name in existing_names:
            tool_id = existing_names[tool_name]
            print(f"✓ Tool '{tool_name}' already exists (ID: {tool_id})")
            tool_ids.append(tool_id)
        else:
            print(f"Creating tool '{tool_name}'...")
            tool_id = create_tool(tool_def)
            if tool_id:
                print(f"✓ Created tool '{tool_name}' (ID: {tool_id})")
                tool_ids.append(tool_id)
            else:
                print(f"✗ Failed to create tool '{tool_name}'")

    if not tool_ids:
        print("\n❌ No tools were created or found")
        sys.exit(1)

    print(f"\nTotal tools: {len(tool_ids)}")

    # Step 4: Update assistant
    print(f"\nUpdating assistant {ASSISTANT_ID}...")
    success = update_assistant(ASSISTANT_ID, tool_ids)

    if success:
        print("\n🎉 Done! Your Vapi assistant is ready to trade!")
        print(f"\nTest it by calling your Vapi number and saying:")
        print("  - 'What's my balance?'")
        print("  - 'Buy $50 of Bitcoin'")
        print("  - 'Show my positions'")
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()
