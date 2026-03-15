# Vapi Integration for Liquid Wolf Trading

This integration allows your Vapi voice assistant to execute trading operations by calling your Liquid Wolf server directly.

## Architecture

```
User calls Vapi → Vapi assistant (with tools) → HTTP POST → Your Liquid Wolf Server → Liquid API
```

The Vapi assistant is configured with "tools" (functions) that make direct HTTP requests to your server endpoints.

## Setup

### 1. Start Your Server

```bash
# Make sure you're in the liquid_server directory
python -m app.main
```

Your server should start on port 8001.

### 2. Expose Your Server (for testing)

Use ngrok to make your local server publicly accessible:

```bash
# Install ngrok if you haven't: https://ngrok.com/download
ngrok http 8001
```

You'll get a URL like: `https://abc123-def456.ngrok-free.app`

**Important**: Copy this URL, you'll need it in the next step.

### 3. Update Your Vapi Assistant

Run the update script with your ngrok URL:

```bash
python -m vapi_integration.update_assistant --server-url https://your-ngrok-url.ngrok-free.app
```

Example:
```bash
python -m vapi_integration.update_assistant --server-url https://abc123-def456.ngrok-free.app
```

This will configure your Vapi assistant (ID: `197591bc-b2ac-41fa-b48a-7f3b017f1b68`) with these tools:
- `place_order` - Place buy/sell orders
- `get_account_info` - Get account balance and positions
- `get_positions` - Get detailed position info
- `get_open_orders` - Get pending orders

## How It Works

### VAPI Tool Call Format

The server now has **two sets of endpoints**:

1. **Standard API endpoints** (`/api/v1/*`) - For regular client apps
2. **VAPI-compliant endpoints** (`/vapi/*`) - For VAPI voice assistant integration

### VAPI Request/Response Flow

When a user says something like "buy $100 of Bitcoin", the VAPI assistant:

1. **Recognizes the intent** and calls the `place_order` tool
2. **Makes an HTTP POST** request to `https://your-server.com/vapi/place_order`
3. **Sends the VAPI-formatted payload**:
   ```json
   {
     "message": {
       "toolCallId": "call_abc123",
       "type": "function",
       "function": {
         "name": "place_order",
         "arguments": {
           "phone_number": "+15305747238",
           "symbol": "BTC-PERP",
           "side": "buy",
           "size": 100,
           "leverage": 1,
           "type": "market"
         }
       }
     }
   }
   ```
4. **Receives the VAPI-formatted response**:
   ```json
   {
     "results": [
       {
         "toolCallId": "call_abc123",
         "result": "{\"success\":true,\"data\":{...}}"
       }
     ]
   }
   ```
   - Always returns HTTP 200 (even for errors)
   - Result is a single-line JSON string
   - Errors use `"error"` field instead of `"result"`

5. **Speaks the result** to the user

### Authentication

All requests include the `X-API-Key` header (configured in the tool definitions).

### Phone Number

The user's phone number is automatically included in all tool calls. VAPI provides this from the call context.

## Available Voice Commands

Once set up, users can say:

**Account Info:**
- "What's my balance?"
- "How much money do I have?"
- "Show my account"

**View Positions:**
- "What positions am I in?"
- "Show my positions"
- "How's my Bitcoin position doing?"

**Place Orders:**
- "Buy $100 of Bitcoin"
- "Sell $50 worth of Ethereum"
- "Short SOL with 10x leverage"
- "Buy $200 of BTC-PERP with 5x leverage"

**Check Orders:**
- "Do I have any open orders?"
- "Show my pending orders"

## Tool Definitions

See `tool_definitions.py` for the complete tool schemas. Each tool has:
- **function**: OpenAI-style function definition with parameters
- **server**: Server URL and headers for the HTTP request

## Deployment

### For Production

1. **Deploy your server** to a permanent host (Render, AWS, etc.)
2. **Update the assistant** with your production URL:
   ```bash
   python -m vapi_integration.update_assistant --server-url https://your-production-server.com
   ```

### Re-deploying

If you change your server URL or update tool definitions:

```bash
python -m vapi_integration.update_assistant --server-url https://new-url.com
```

## Debugging

### Check if assistant was updated

Use the Vapi dashboard or API to inspect your assistant configuration:

```bash
curl -H "Authorization: Bearer YOUR_VAPI_KEY" \
  https://api.vapi.ai/assistant/197591bc-b2ac-41fa-b48a-7f3b017f1b68
```

### Test server endpoint manually

Test the standard API endpoint:
```bash
curl -X POST http://localhost:8001/api/v1/account/info \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-secret-key-change-in-production" \
  -d '{"phone_number": "+15305747238"}'
```

Test the VAPI-compliant endpoint:
```bash
curl -X POST http://localhost:8001/vapi/get_account_info \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-secret-key-change-in-production" \
  -d '{
    "message": {
      "toolCallId": "test_123",
      "type": "function",
      "function": {
        "name": "get_account_info",
        "arguments": {
          "phone_number": "+15305747238"
        }
      }
    }
  }'
```

Or run the test script:
```bash
python -m vapi_integration.test_vapi_endpoints
```

### View ngrok requests

ngrok provides a web interface at `http://localhost:4040` to see all HTTP requests.

## Files

- `update_assistant.py` - Script to configure VAPI assistant with tools
- `tool_definitions.py` - Tool/function definitions pointing to `/vapi/*` endpoints
- `test_vapi_endpoints.py` - Test script to verify VAPI-compliant responses
- `.env` - VAPI API credentials
- `README.md` - This file
- `INSTRUCTIONS.md` - Original project goals

## VAPI Endpoints

All VAPI endpoints are under `/vapi/` prefix:

- `POST /vapi/place_order` - Place a trading order
- `POST /vapi/get_account_info` - Get account info with positions
- `POST /vapi/get_positions` - Get all open positions
- `POST /vapi/get_open_orders` - Get all open orders
- `POST /vapi/cancel_order` - Cancel a specific order

These endpoints:
- Accept VAPI's `message.toolCallId` and `message.function.arguments` format
- Return VAPI's `{"results": [{"toolCallId": "...", "result": "..."}]}` format
- Always return HTTP 200 (errors use `"error"` field instead of `"result"`)
- Return single-line JSON strings (no newlines)

## Troubleshooting

**"Assistant not found"**
- Check that `VAPI_API_KEY` is set correctly in `.env`
- Verify the assistant ID is correct

**"Server not reachable"**
- Make sure your server is running on port 8001
- Check that ngrok is active
- Try accessing the ngrok URL in your browser

**"Authentication failed"**
- Verify `API_SECRET_KEY` in `liquid_server/.env` matches the one in tool definitions

**"Tool not being called"**
- Check Vapi dashboard logs to see what the assistant understood
- Try being more explicit: "use the place order function to buy bitcoin"
