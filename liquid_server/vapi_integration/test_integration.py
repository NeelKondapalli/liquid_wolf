"""
Test Vapi Integration

This script tests that your Vapi assistant can make calls to your server.
Run this after updating the assistant.
"""

import os
import requests
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))

VAPI_API_KEY = os.getenv("VAPI_API_KEY")
ASSISTANT_ID = "197591bc-b2ac-41fa-b48a-7f3b017f1b68"


def test_get_assistant():
    """Verify we can access the assistant"""
    print("Testing Vapi API access...")

    url = f"https://api.vapi.ai/assistant/{ASSISTANT_ID}"
    headers = {
        "Authorization": f"Bearer {VAPI_API_KEY}"
    }

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        data = response.json()
        print(f"✅ Assistant found: {data.get('name', 'Unknown')}")

        # Check tools
        tools = data.get("tools", [])
        print(f"\n📋 Tools configured: {len(tools)}")

        for i, tool in enumerate(tools, 1):
            func = tool.get("function", {})
            server = tool.get("server", {})
            print(f"\n{i}. {func.get('name')}")
            print(f"   URL: {server.get('url')}")
            print(f"   Description: {func.get('description', '')[:80]}...")

        return True
    else:
        print(f"❌ Error: {response.status_code}")
        print(response.text)
        return False


def test_server_endpoint(server_url: str):
    """Test that the server endpoint is accessible"""
    print(f"\nTesting server endpoint: {server_url}")

    # Test health endpoint
    try:
        response = requests.get(f"{server_url}/health", timeout=5)
        if response.status_code == 200:
            print(f"✅ Server is accessible")
            print(f"   Response: {response.json()}")
            return True
        else:
            print(f"❌ Server returned: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Cannot reach server: {e}")
        return False


if __name__ == "__main__":
    print("🧪 Vapi Integration Test\n")
    print("=" * 60)

    # Test 1: Vapi API access
    if not test_get_assistant():
        print("\n❌ Failed to access Vapi API")
        print("Check that VAPI_API_KEY is set correctly in .env")
        exit(1)

    print("\n" + "=" * 60)
    print("\n📝 Next steps:")
    print("1. Start your server: python -m app.main")
    print("2. Start ngrok: ngrok http 8001")
    print("3. Update assistant: python -m vapi_integration.update_assistant --server-url https://your-ngrok-url")
    print("4. Test by calling your Vapi number!")
