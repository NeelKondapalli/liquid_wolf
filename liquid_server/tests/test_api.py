"""
Test script for Liquid Wolf Server API

This script creates test users, adds fake API keys to the database,
and tests all API endpoints. It cleans up after itself.
"""

import requests
import json
import sys
import time
from typing import Dict, Any, Optional

# Configuration
BASE_URL = "http://localhost:8000"
API_KEY = "your-secret-key-change-in-production"  # Must match .env

# Test data - will be created automatically
TEST_PHONE = "+15551234567"  # Test user (will be created)
TEST_SYMBOL = "BTC-PERP"

# Fake Liquid API credentials for testing
FAKE_API_KEY = "test_liquid_key_12345"
FAKE_API_SECRET = "test_liquid_secret_67890"


class Colors:
    """ANSI color codes for terminal output"""
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    END = '\033[0m'


def print_test(name: str):
    """Print test name"""
    print(f"\n{Colors.BLUE}{'='*60}")
    print(f"Testing: {name}")
    print(f"{'='*60}{Colors.END}")


def print_success(message: str):
    """Print success message"""
    print(f"{Colors.GREEN}✓ {message}{Colors.END}")


def print_error(message: str):
    """Print error message"""
    print(f"{Colors.RED}✗ {message}{Colors.END}")


def print_warning(message: str):
    """Print warning message"""
    print(f"{Colors.YELLOW}⚠ {message}{Colors.END}")


def make_request(
    method: str,
    endpoint: str,
    data: Dict[str, Any] = None,
    expect_success: bool = True
) -> Dict[str, Any]:
    """
    Make an API request and print results

    Args:
        method: HTTP method (GET, POST)
        endpoint: API endpoint
        data: Request body data
        expect_success: Whether we expect success=True in response

    Returns:
        Response JSON
    """
    url = f"{BASE_URL}{endpoint}"
    headers = {
        "Content-Type": "application/json",
        "X-API-Key": API_KEY
    }

    try:
        if method == "GET":
            response = requests.get(url, headers=headers)
        else:
            response = requests.post(url, headers=headers, json=data)

        print(f"\nRequest: {method} {endpoint}")
        if data:
            print(f"Body: {json.dumps(data, indent=2)}")

        print(f"\nStatus: {response.status_code}")

        try:
            result = response.json()
            print(f"Response: {json.dumps(result, indent=2)}")

            if expect_success:
                if result.get("success"):
                    print_success("Request succeeded")
                else:
                    print_error(f"Request failed: {result.get('error')}")
            else:
                if not result.get("success"):
                    print_success("Got expected error")
                else:
                    print_warning("Expected error but got success")

            return result

        except json.JSONDecodeError:
            print(f"Raw response: {response.text}")
            return {}

    except requests.exceptions.ConnectionError:
        print_error("Could not connect to server. Is it running?")
        print("Start the server with: python -m app.main")
        sys.exit(1)
    except Exception as e:
        print_error(f"Request failed: {str(e)}")
        return {}


def test_health():
    """Test health check endpoint"""
    print_test("Health Check")
    make_request("GET", "/health")


def test_auth_missing_key():
    """Test missing API key"""
    print_test("Missing API Key (Should Fail)")

    url = f"{BASE_URL}/api/v1/market/markets"
    headers = {"Content-Type": "application/json"}
    data = {"phone_number": TEST_PHONE}

    response = requests.post(url, headers=headers, json=data)
    result = response.json()

    print(f"Response: {json.dumps(result, indent=2)}")
    if not result.get("success") and "API key" in result.get("error", ""):
        print_success("Correctly rejected request with missing API key")
    else:
        print_error("Should have rejected request")


def test_auth_invalid_key():
    """Test invalid API key"""
    print_test("Invalid API Key (Should Fail)")

    url = f"{BASE_URL}/api/v1/market/markets"
    headers = {
        "Content-Type": "application/json",
        "X-API-Key": "invalid-key"
    }
    data = {"phone_number": TEST_PHONE}

    response = requests.post(url, headers=headers, json=data)
    result = response.json()

    print(f"Response: {json.dumps(result, indent=2)}")
    if not result.get("success") and "Invalid" in result.get("error", ""):
        print_success("Correctly rejected request with invalid API key")
    else:
        print_error("Should have rejected request")


def test_user_not_found():
    """Test with non-existent user"""
    print_test("Non-existent User (Should Fail)")
    make_request(
        "POST",
        "/api/v1/market/markets",
        {"phone_number": "+9999999999"},
        expect_success=False
    )


def test_get_markets():
    """Test getting markets"""
    print_test("Get Markets")
    make_request(
        "POST",
        "/api/v1/market/markets",
        {"phone_number": TEST_PHONE}
    )


def test_get_ticker():
    """Test getting ticker"""
    print_test("Get Ticker")
    make_request(
        "POST",
        "/api/v1/market/ticker",
        {
            "phone_number": TEST_PHONE,
            "symbol": TEST_SYMBOL
        }
    )


def test_get_orderbook():
    """Test getting orderbook"""
    print_test("Get Orderbook")
    make_request(
        "POST",
        "/api/v1/market/orderbook",
        {
            "phone_number": TEST_PHONE,
            "symbol": TEST_SYMBOL,
            "depth": 10
        }
    )


def test_get_candles():
    """Test getting candles"""
    print_test("Get Candles")
    make_request(
        "POST",
        "/api/v1/market/candles",
        {
            "phone_number": TEST_PHONE,
            "symbol": TEST_SYMBOL,
            "interval": "1h",
            "limit": 5
        }
    )


def test_get_account_info():
    """Test getting account info"""
    print_test("Get Account Info")
    make_request(
        "POST",
        "/api/v1/account/info",
        {"phone_number": TEST_PHONE}
    )


def test_get_balances():
    """Test getting balances"""
    print_test("Get Balances")
    make_request(
        "POST",
        "/api/v1/account/balances",
        {"phone_number": TEST_PHONE}
    )


def test_get_positions():
    """Test getting positions"""
    print_test("Get Positions")
    make_request(
        "POST",
        "/api/v1/account/positions",
        {"phone_number": TEST_PHONE}
    )


def test_get_open_orders():
    """Test getting open orders"""
    print_test("Get Open Orders")
    make_request(
        "POST",
        "/api/v1/orders/open",
        {"phone_number": TEST_PHONE}
    )


def test_user_check():
    """Test checking if user exists"""
    print_test("User Check")
    result = make_request(
        "POST",
        "/api/v1/user/check",
        {"phone_number": TEST_PHONE}
    )
    return result


def test_user_create():
    """Test creating a new user"""
    print_test("User Create")
    result = make_request(
        "POST",
        "/api/v1/user/create",
        {"phone_number": TEST_PHONE}
    )
    return result


def test_user_has_keys():
    """Test checking if user has keys"""
    print_test("User Has Keys")
    result = make_request(
        "POST",
        "/api/v1/user/has_keys",
        {"phone_number": TEST_PHONE}
    )
    return result


def test_user_save_keys():
    """Test saving API keys for user"""
    print_test("User Save Keys")
    result = make_request(
        "POST",
        "/api/v1/user/save_keys",
        {
            "phone_number": TEST_PHONE,
            "api_key": FAKE_API_KEY,
            "api_secret": FAKE_API_SECRET
        }
    )
    return result


def cleanup_test_user():
    """Clean up test user from database"""
    print_test("Cleanup Test User")

    try:
        from app.services.supabase_service import supabase_service

        # Delete liquid keys first (foreign key)
        supabase_service.client.table("liquid_keys").delete().eq(
            "phone_number", TEST_PHONE
        ).execute()
        print_success("Deleted test user's API keys")

        # Delete user
        supabase_service.client.table("users").delete().eq(
            "phone_number", TEST_PHONE
        ).execute()
        print_success("Deleted test user")

    except Exception as e:
        print_warning(f"Cleanup failed (may not exist): {str(e)}")


def test_validation_errors():
    """Test various validation errors"""
    print_test("Validation Errors")

    # Missing phone number
    print("\n--- Missing phone number ---")
    make_request(
        "POST",
        "/api/v1/user/check",
        {},
        expect_success=False
    )

    # Invalid phone number format
    print("\n--- Invalid phone format ---")
    make_request(
        "POST",
        "/api/v1/user/check",
        {"phone_number": "invalid"},
        expect_success=False
    )


def setup_test_user():
    """Create test user and add fake API keys"""
    print(f"\n{Colors.YELLOW}{'='*60}")
    print("SETTING UP TEST USER")
    print(f"{'='*60}{Colors.END}")

    # Clean up any existing test data first
    cleanup_test_user()

    # Check if user exists
    result = test_user_check()
    if result.get("data", {}).get("exists"):
        print_warning("Test user already exists, cleaning up...")
        cleanup_test_user()

    # Create user
    result = test_user_create()
    if not result.get("success"):
        print_error("Failed to create test user!")
        sys.exit(1)

    # Verify user was created
    result = test_user_check()
    if not result.get("data", {}).get("exists"):
        print_error("User creation verification failed!")
        sys.exit(1)

    # Check if user has keys (should be false)
    result = test_user_has_keys()
    if result.get("data", {}).get("has_keys"):
        print_warning("User already has keys (unexpected)")

    # Save fake API keys
    result = test_user_save_keys()
    if not result.get("success"):
        print_error("Failed to save API keys!")
        sys.exit(1)

    # Verify keys were saved
    result = test_user_has_keys()
    if not result.get("data", {}).get("has_keys"):
        print_error("API keys verification failed!")
        sys.exit(1)

    print(f"\n{Colors.GREEN}{'='*60}")
    print("TEST USER SETUP COMPLETE")
    print(f"{'='*60}{Colors.END}\n")


def run_all_tests():
    """Run all tests with automatic setup and cleanup"""
    print(f"\n{Colors.YELLOW}{'='*60}")
    print("LIQUID WOLF SERVER API TESTS")
    print(f"{'='*60}{Colors.END}")
    print(f"\nBase URL: {BASE_URL}")
    print(f"API Key: {API_KEY}")
    print(f"Test Phone: {TEST_PHONE}")
    print(f"Test Symbol: {TEST_SYMBOL}")
    print(f"Fake Liquid Key: {FAKE_API_KEY}")

    print_warning("\nMake sure the server is running: python -m app.main")
    print_warning("This script will create a test user and clean up afterward.\n")

    try:
        # Setup test user with fake credentials
        setup_test_user()

        # Basic tests
        test_health()

        # Auth tests
        test_auth_missing_key()
        test_auth_invalid_key()
        test_user_not_found()

        # Validation tests
        test_validation_errors()

        print(f"\n{Colors.GREEN}{'='*60}")
        print("ALL TESTS COMPLETED")
        print(f"{'='*60}{Colors.END}\n")

        print_warning("\nNote: Market data and account endpoints require real Liquid API keys")
        print_warning("The fake keys allow user management testing but won't work for trading operations")

    finally:
        # Always clean up
        print("\n")
        cleanup_test_user()
        print_success("\nTest cleanup complete!")


if __name__ == "__main__":
    run_all_tests()
