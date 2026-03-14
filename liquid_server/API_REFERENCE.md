# Liquid Wolf Server API Reference

Complete API reference for the Liquid Wolf Server - a Flask-based wrapper for the Liquid Trading API with Supabase authentication.

## Table of Contents

- [Overview](#overview)
- [Authentication](#authentication)
- [Base URL](#base-url)
- [Response Format](#response-format)
- [Error Handling](#error-handling)
- [Endpoints](#endpoints)
  - [Health Check](#health-check)
  - [Market Data](#market-data)
  - [Account](#account)
  - [Orders](#orders)
  - [Positions](#positions)

---

## Overview

The Liquid Wolf Server acts as a middleware between your frontend and the Liquid Trading API. It:

1. **Authenticates requests** using a secret API key (X-API-Key header)
2. **Validates users** by checking phone numbers in Supabase
3. **Retrieves Liquid API credentials** from Supabase for each user
4. **Proxies requests** to the Liquid Trading API
5. **Returns structured responses** with consistent error handling

---

## Authentication

All endpoints (except `/health`) require two levels of authentication:

### 1. API Key Authentication

Include your server API key in the request header:

```
X-API-Key: your-secret-key-here
```

This key is configured in your `.env` file as `API_SECRET_KEY`.

### 2. User Phone Number

Include the user's phone number in the request body:

```json
{
  "phone_number": "+1234567890"
}
```

The server will:
- Check if the user exists in Supabase
- Verify they have active Liquid API keys
- Use their credentials to call the Liquid API

---

## Base URL

```
http://localhost:5000
```

In production, this will be your deployed server URL.

---

## Response Format

All responses follow a consistent format:

### Success Response

```json
{
  "success": true,
  "data": { ... }
}
```

### Error Response

```json
{
  "success": false,
  "error": "Error type",
  "detail": "Detailed error message"
}
```

---

## Error Handling

### HTTP Status Codes

| Code | Description |
|------|-------------|
| 200  | Success |
| 400  | Bad request - invalid parameters |
| 401  | Unauthorized - missing or invalid API key |
| 404  | Not found - user or resource doesn't exist |
| 422  | Validation error |
| 429  | Rate limit exceeded |
| 500  | Internal server error |

### Common Errors

#### Missing API Key (401)
```json
{
  "success": false,
  "error": "Missing API key",
  "detail": "X-API-Key header is required"
}
```

#### User Not Found (404)
```json
{
  "success": false,
  "error": "User not found",
  "detail": "No user found with phone number: +1234567890"
}
```

#### No Active Keys (404)
```json
{
  "success": false,
  "error": "No active API keys",
  "detail": "User +1234567890 has no active Liquid API keys"
}
```

---

## Endpoints

### Health Check

**GET** `/health`

Check if the server is running. Does not require authentication.

#### Response

```json
{
  "status": "ok",
  "version": "1.0.0",
  "app": "Liquid Wolf Server"
}
```

---

## Market Data

### Get All Markets

**POST** `/api/v1/market/markets`

Get list of all tradeable markets.

#### Request

```bash
curl -X POST http://localhost:5000/api/v1/market/markets \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-secret-key" \
  -d '{
    "phone_number": "+1234567890"
  }'
```

#### Response

```json
{
  "success": true,
  "data": [
    {
      "symbol": "BTC-PERP",
      "ticker": "BTC",
      "exchange": "hyperliquid",
      "max_leverage": 40,
      "sz_decimals": 5
    },
    {
      "symbol": "ETH-PERP",
      "ticker": "ETH",
      "exchange": "hyperliquid",
      "max_leverage": 25,
      "sz_decimals": 4
    }
  ]
}
```

---

### Get Ticker

**POST** `/api/v1/market/ticker`

Get current ticker data for a symbol.

#### Request

```bash
curl -X POST http://localhost:5000/api/v1/market/ticker \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-secret-key" \
  -d '{
    "phone_number": "+1234567890",
    "symbol": "BTC-PERP"
  }'
```

#### Request Body

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| phone_number | string | Yes | User's phone number |
| symbol | string | Yes | Trading symbol (e.g., "BTC-PERP") |

#### Response

```json
{
  "success": true,
  "data": {
    "symbol": "BTC-PERP",
    "mark_price": "69420.50",
    "volume_24h": "1234567.89",
    "change_24h": "2.34",
    "funding_rate": "0.0001"
  }
}
```

---

### Get Orderbook

**POST** `/api/v1/market/orderbook`

Get orderbook data for a symbol.

#### Request Body

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| phone_number | string | Yes | - | User's phone number |
| symbol | string | Yes | - | Trading symbol |
| depth | integer | No | 20 | Orderbook depth (1-500) |

#### Response

```json
{
  "success": true,
  "data": {
    "symbol": "BTC-PERP",
    "bids": [
      {"price": "69400.00", "size": "1.25", "count": 3}
    ],
    "asks": [
      {"price": "69420.00", "size": "0.80", "count": 2}
    ],
    "timestamp": null
  }
}
```

---

### Get Candles

**POST** `/api/v1/market/candles`

Get OHLCV candle data for a symbol.

#### Request Body

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| phone_number | string | Yes | - | User's phone number |
| symbol | string | Yes | - | Trading symbol |
| interval | string | No | "1h" | Candle interval: 1m, 5m, 15m, 30m, 1h, 4h, 1d |
| limit | integer | No | 100 | Number of candles (1-1000) |
| start | integer | No | - | Start timestamp in seconds |
| end | integer | No | - | End timestamp in seconds |

#### Response

```json
{
  "success": true,
  "data": [
    {
      "timestamp": 1700000000000,
      "open": "68000.0",
      "high": "68200.0",
      "low": "67850.0",
      "close": "68120.0",
      "volume": "1234.56"
    }
  ]
}
```

---

## Account

### Get Account Info

**POST** `/api/v1/account/info`

Get basic account information.

#### Request Body

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| phone_number | string | Yes | User's phone number |

#### Response

```json
{
  "success": true,
  "data": {
    "equity": "10523.45",
    "margin_used": "2100.00",
    "available_balance": "8423.45",
    "account_value": "10523.45"
  }
}
```

---

### Get Balances

**POST** `/api/v1/account/balances`

Get detailed balance information.

#### Response

```json
{
  "success": true,
  "data": {
    "equity": "10523.45",
    "margin_used": "2100.00",
    "available_balance": "8423.45",
    "account_value": "10523.45",
    "cross_margin": {
      "account_value": "10523.45",
      "total_margin_used": "2100.00",
      "total_ntl_pos": "5000.00"
    }
  }
}
```

---

### Get Positions

**POST** `/api/v1/account/positions`

Get all open positions.

#### Response

```json
{
  "success": true,
  "data": [
    {
      "symbol": "BTC-PERP",
      "side": "long",
      "size": "0.05",
      "entry_price": "69000.00",
      "mark_price": "69420.50",
      "leverage": 5,
      "unrealized_pnl": "21.00",
      "liquidation_price": "55200.00",
      "margin_used": "690.00"
    }
  ]
}
```

---

## Orders

### Place Order

**POST** `/api/v1/orders/place`

Place a new market or limit order.

#### Request Body

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| phone_number | string | Yes | - | User's phone number |
| symbol | string | Yes | - | Trading symbol (e.g., "BTC-PERP") |
| side | string | Yes | - | "buy" or "sell" |
| type | string | No | "market" | "market" or "limit" |
| size | float | Yes | - | Order size in USD notional |
| price | float | Limit only | - | Limit price (required for limit orders) |
| leverage | integer | No | 1 | Leverage (1-200) |
| time_in_force | string | No | "gtc" | "gtc" or "ioc" |
| tp | float | No | - | Take-profit price |
| sl | float | No | - | Stop-loss price |
| reduce_only | boolean | No | false | Only reduce existing position |

#### Example: Market Buy

```bash
curl -X POST http://localhost:5000/api/v1/orders/place \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-secret-key" \
  -d '{
    "phone_number": "+1234567890",
    "symbol": "BTC-PERP",
    "side": "buy",
    "type": "market",
    "size": 100.0,
    "leverage": 5,
    "tp": 72000.0,
    "sl": 68000.0
  }'
```

#### Example: Limit Sell

```bash
curl -X POST http://localhost:5000/api/v1/orders/place \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-secret-key" \
  -d '{
    "phone_number": "+1234567890",
    "symbol": "ETH-PERP",
    "side": "sell",
    "type": "limit",
    "size": 50.0,
    "price": 4200.0,
    "leverage": 3
  }'
```

#### Response

```json
{
  "success": true,
  "data": {
    "order_id": "ord_abc123",
    "symbol": "BTC-PERP",
    "side": "buy",
    "type": "market",
    "size": "100.0",
    "price": "69420.50",
    "leverage": 5,
    "status": "filled",
    "exchange": "hyperliquid",
    "tp": "72000.0",
    "sl": "68000.0",
    "reduce_only": false,
    "created_at": "2025-01-15T12:00:00Z"
  }
}
```

---

### Get Open Orders

**POST** `/api/v1/orders/open`

Get all open orders.

#### Request Body

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| phone_number | string | Yes | User's phone number |

#### Response

```json
{
  "success": true,
  "data": [
    {
      "order_id": "ord_abc123",
      "symbol": "BTC-PERP",
      "side": "buy",
      "type": "limit",
      "size": "100.0",
      "price": "68000.0",
      "status": "open"
    }
  ]
}
```

---

### Get Order

**POST** `/api/v1/orders/get`

Get a specific order by ID.

#### Request Body

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| phone_number | string | Yes | User's phone number |
| order_id | string | Yes | Order ID to fetch |

#### Response

```json
{
  "success": true,
  "data": {
    "order_id": "ord_abc123",
    "symbol": "BTC-PERP",
    "side": "buy",
    "type": "limit",
    "size": "100.0",
    "price": "68000.0",
    "status": "open"
  }
}
```

---

### Cancel Order

**POST** `/api/v1/orders/cancel`

Cancel a specific order.

#### Request Body

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| phone_number | string | Yes | User's phone number |
| order_id | string | Yes | Order ID to cancel |

#### Response

```json
{
  "success": true,
  "data": {
    "cancelled": true
  }
}
```

---

### Cancel All Orders

**POST** `/api/v1/orders/cancel_all`

Cancel all open orders.

#### Request Body

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| phone_number | string | Yes | User's phone number |

#### Response

```json
{
  "success": true,
  "data": {
    "cancelled_count": 3
  }
}
```

---

## Positions

### Close Position

**POST** `/api/v1/positions/close`

Close a position (full or partial).

#### Request Body

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| phone_number | string | Yes | User's phone number |
| symbol | string | Yes | Trading symbol |
| size | float | No | Partial close size in coin units (omit for full close) |

**Note:** `size` is in coin units (e.g., 0.025 BTC), not USD notional.

#### Example: Full Close

```bash
curl -X POST http://localhost:5000/api/v1/positions/close \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-secret-key" \
  -d '{
    "phone_number": "+1234567890",
    "symbol": "BTC-PERP"
  }'
```

#### Example: Partial Close

```bash
curl -X POST http://localhost:5000/api/v1/positions/close \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-secret-key" \
  -d '{
    "phone_number": "+1234567890",
    "symbol": "BTC-PERP",
    "size": 0.025
  }'
```

#### Response

```json
{
  "success": true,
  "data": {
    "symbol": "BTC-PERP",
    "closed_size": 0.025,
    "status": "ok",
    "message": "Partial close executed"
  }
}
```

---

### Set Take-Profit / Stop-Loss

**POST** `/api/v1/positions/set_tp_sl`

Set or update take-profit and stop-loss for a position.

#### Request Body

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| phone_number | string | Yes | User's phone number |
| symbol | string | Yes | Trading symbol |
| tp | float | No | Take-profit price |
| sl | float | No | Stop-loss price |

At least one of `tp` or `sl` must be provided.

#### Example

```bash
curl -X POST http://localhost:5000/api/v1/positions/set_tp_sl \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-secret-key" \
  -d '{
    "phone_number": "+1234567890",
    "symbol": "BTC-PERP",
    "tp": 75000.0,
    "sl": 65000.0
  }'
```

#### Response

```json
{
  "success": true,
  "data": {
    "tp": {
      "status": "set",
      "price": 75000.0
    },
    "sl": {
      "status": "set",
      "price": 65000.0
    }
  }
}
```

---

### Update Leverage

**POST** `/api/v1/positions/update_leverage`

Update leverage for a position.

#### Request Body

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| phone_number | string | Yes | - | User's phone number |
| symbol | string | Yes | - | Trading symbol |
| leverage | integer | Yes | - | New leverage (1-200) |
| is_cross | boolean | No | false | Use cross margin |

#### Example

```bash
curl -X POST http://localhost:5000/api/v1/positions/update_leverage \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-secret-key" \
  -d '{
    "phone_number": "+1234567890",
    "symbol": "ETH-PERP",
    "leverage": 10,
    "is_cross": false
  }'
```

#### Response

```json
{
  "success": true,
  "data": {
    "symbol": "ETH-PERP",
    "leverage": 10,
    "is_cross": false
  }
}
```

---

### Update Margin

**POST** `/api/v1/positions/update_margin`

Adjust isolated margin for a position.

#### Request Body

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| phone_number | string | Yes | User's phone number |
| symbol | string | Yes | Trading symbol |
| amount | float | Yes | Amount to add (positive) or remove (negative) |

#### Example

```bash
curl -X POST http://localhost:5000/api/v1/positions/update_margin \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-secret-key" \
  -d '{
    "phone_number": "+1234567890",
    "symbol": "BTC-PERP",
    "amount": 500.0
  }'
```

#### Response

```json
{
  "success": true,
  "data": {
    "symbol": "BTC-PERP",
    "margin_adjusted": 500.0
  }
}
```

---

## Testing

See the `tests/` directory for example test scripts and usage examples.

To run tests:

```bash
# Install dependencies
pip install -r requirements.txt

# Set up environment
cp .env.example .env
# Edit .env with your credentials

# Run the server
python -m app.main

# In another terminal, run tests
python tests/test_api.py
```

---

## Rate Limits

Rate limits are enforced by the Liquid API:

- **Free Tier:** 10 requests/second, 2 order mutations/second
- Headers returned: `X-RateLimit-Limit`, `X-RateLimit-Remaining`, `X-RateLimit-Reset`
- HTTP 429 when throttled with `Retry-After: 1`

---

## Security Notes

1. **Never commit** your `.env` file with real credentials
2. **Use HTTPS** in production
3. **Rotate API keys** regularly
4. **Implement rate limiting** on your server
5. **Validate** all user inputs
6. **Encrypt** API secrets in Supabase database (see `supabase/SUPABASE_MODEL.md`)

---

## Support

For issues or questions:
- Check the Liquid SDK docs: https://sdk.tryliquid.xyz/docs/
- Review Supabase docs: https://supabase.com/docs
- Contact support: [your-support-email]
