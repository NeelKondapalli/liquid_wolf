"""
Test script for VAPI-compliant endpoints

This script tests that the /vapi endpoints return the correct VAPI format:
- HTTP 200 status (always)
- Response format: {"results": [{"toolCallId": "...", "result": "..."}]}
- Single-line string responses
"""

import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()

BASE_URL = os.getenv("LIQUID_API_URL", "http://localhost:8001")
API_KEY = os.getenv("LIQUID_API_KEY", "your-secret-key-change-in-production")

# Test phone number - you'll need to use a real phone number from your database
TEST_PHONE = os.getenv("TEST_PHONE_NUMBER", "+15305747238")


def test_vapi_endpoint(endpoint, tool_call_id, function_name, arguments):
    """
    Test a VAPI endpoint with the expected request format
    """
    print(f"\n{'='*60}")
    print(f"Testing: {endpoint}")
    print(f"Tool Call ID: {tool_call_id}")
    print(f"Function: {function_name}")
    print(f"Arguments: {json.dumps(arguments, indent=2)}")
    print(f"{'='*60}")

    request_data = {
        "message": {
            "toolCallId": tool_call_id,
            "type": "function",
            "function": {
                "name": function_name,
                "arguments": arguments
            }
        }
    }

    headers = {
        "Content-Type": "application/json",
        "X-API-Key": API_KEY
    }

    try:
        response = requests.post(
            f"{BASE_URL}{endpoint}",
            json=request_data,
            headers=headers
        )

        print(f"\nHTTP Status: {response.status_code}")

        # VAPI requires HTTP 200 always
        if response.status_code != 200:
            print(f"❌ FAILED: Expected HTTP 200, got {response.status_code}")
            return False

        response_data = response.json()
        print(f"\nResponse: {json.dumps(response_data, indent=2)}")

        # Validate VAPI response format
        if "results" not in response_data:
            print("❌ FAILED: Missing 'results' key in response")
            return False

        if not isinstance(response_data["results"], list):
            print("❌ FAILED: 'results' must be an array")
            return False

        if len(response_data["results"]) != 1:
            print("❌ FAILED: 'results' array must have exactly 1 item")
            return False

        result = response_data["results"][0]

        if "toolCallId" not in result:
            print("❌ FAILED: Missing 'toolCallId' in result")
            return False

        if result["toolCallId"] != tool_call_id:
            print(f"❌ FAILED: toolCallId mismatch. Expected '{tool_call_id}', got '{result['toolCallId']}'")
            return False

        if "result" in result:
            # Success response
            result_str = result["result"]
            if not isinstance(result_str, str):
                print("❌ FAILED: 'result' must be a string")
                return False

            # Check for newlines (VAPI requires single-line strings)
            if '\n' in result_str or '\r' in result_str:
                print("❌ FAILED: 'result' contains newlines (must be single-line)")
                return False

            print(f"\n✅ SUCCESS")
            print(f"Result (truncated): {result_str[:200]}...")
            return True

        elif "error" in result:
            # Error response (still valid VAPI format)
            error_str = result["error"]
            if not isinstance(error_str, str):
                print("❌ FAILED: 'error' must be a string")
                return False

            # Check for newlines
            if '\n' in error_str or '\r' in error_str:
                print("❌ FAILED: 'error' contains newlines (must be single-line)")
                return False

            print(f"\n✅ SUCCESS (Error Response)")
            print(f"Error: {error_str}")
            return True

        else:
            print("❌ FAILED: Result must have either 'result' or 'error' field")
            return False

    except Exception as e:
        print(f"\n❌ EXCEPTION: {str(e)}")
        return False


def main():
    """
    Run all VAPI endpoint tests
    """
    print("\n" + "="*60)
    print("VAPI ENDPOINT TESTS")
    print("="*60)
    print(f"Base URL: {BASE_URL}")
    print(f"API Key: {API_KEY[:20]}...")
    print(f"Test Phone: {TEST_PHONE}")

    tests_passed = 0
    tests_failed = 0

    # Test 1: Get Account Info
    if test_vapi_endpoint(
        "/vapi/get_account_info",
        "call_test_001",
        "get_account_info",
        {"phone_number": TEST_PHONE}
    ):
        tests_passed += 1
    else:
        tests_failed += 1

    # Test 2: Get Positions
    if test_vapi_endpoint(
        "/vapi/get_positions",
        "call_test_002",
        "get_positions",
        {"phone_number": TEST_PHONE}
    ):
        tests_passed += 1
    else:
        tests_failed += 1

    # Test 3: Get Open Orders
    if test_vapi_endpoint(
        "/vapi/get_open_orders",
        "call_test_003",
        "get_open_orders",
        {"phone_number": TEST_PHONE}
    ):
        tests_passed += 1
    else:
        tests_failed += 1

    # Test 4: Missing phone_number (error case)
    if test_vapi_endpoint(
        "/vapi/get_account_info",
        "call_test_004",
        "get_account_info",
        {}  # Missing phone_number
    ):
        tests_passed += 1
    else:
        tests_failed += 1

    # Test 5: Invalid phone_number (error case)
    if test_vapi_endpoint(
        "/vapi/get_account_info",
        "call_test_005",
        "get_account_info",
        {"phone_number": "+1234567890"}  # Likely doesn't exist
    ):
        tests_passed += 1
    else:
        tests_failed += 1

    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    print(f"Tests Passed: {tests_passed}")
    print(f"Tests Failed: {tests_failed}")
    print(f"Total Tests: {tests_passed + tests_failed}")

    if tests_failed == 0:
        print("\n🎉 All tests passed!")
    else:
        print(f"\n⚠️  {tests_failed} test(s) failed")

    print("="*60 + "\n")


if __name__ == "__main__":
    main()
