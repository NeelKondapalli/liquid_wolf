#!/bin/bash

# Liquid Wolf Server - Manual cURL Test Script
# This script demonstrates how to call the API using cURL

# Configuration
BASE_URL="http://localhost:5000"
API_KEY="your-secret-key-change-in-production"
TEST_PHONE="+1234567890"  # Update with real user
TEST_SYMBOL="BTC-PERP"

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}================================${NC}"
echo -e "${BLUE}Liquid Wolf Server cURL Tests${NC}"
echo -e "${BLUE}================================${NC}"
echo ""

# Test 1: Health Check
echo -e "${GREEN}1. Health Check${NC}"
curl -s -X GET "$BASE_URL/health" | jq '.'
echo ""

# Test 2: Get Markets
echo -e "${GREEN}2. Get Markets${NC}"
curl -s -X POST "$BASE_URL/api/v1/market/markets" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: $API_KEY" \
  -d "{\"phone_number\": \"$TEST_PHONE\"}" | jq '.'
echo ""

# Test 3: Get Ticker
echo -e "${GREEN}3. Get Ticker for $TEST_SYMBOL${NC}"
curl -s -X POST "$BASE_URL/api/v1/market/ticker" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: $API_KEY" \
  -d "{
    \"phone_number\": \"$TEST_PHONE\",
    \"symbol\": \"$TEST_SYMBOL\"
  }" | jq '.'
echo ""

# Test 4: Get Orderbook
echo -e "${GREEN}4. Get Orderbook${NC}"
curl -s -X POST "$BASE_URL/api/v1/market/orderbook" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: $API_KEY" \
  -d "{
    \"phone_number\": \"$TEST_PHONE\",
    \"symbol\": \"$TEST_SYMBOL\",
    \"depth\": 5
  }" | jq '.'
echo ""

# Test 5: Get Account Info
echo -e "${GREEN}5. Get Account Info${NC}"
curl -s -X POST "$BASE_URL/api/v1/account/info" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: $API_KEY" \
  -d "{\"phone_number\": \"$TEST_PHONE\"}" | jq '.'
echo ""

# Test 6: Get Positions
echo -e "${GREEN}6. Get Positions${NC}"
curl -s -X POST "$BASE_URL/api/v1/account/positions" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: $API_KEY" \
  -d "{\"phone_number\": \"$TEST_PHONE\"}" | jq '.'
echo ""

# Test 7: Get Open Orders
echo -e "${GREEN}7. Get Open Orders${NC}"
curl -s -X POST "$BASE_URL/api/v1/orders/open" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: $API_KEY" \
  -d "{\"phone_number\": \"$TEST_PHONE\"}" | jq '.'
echo ""

echo -e "${BLUE}================================${NC}"
echo -e "${BLUE}Tests Complete${NC}"
echo -e "${BLUE}================================${NC}"
