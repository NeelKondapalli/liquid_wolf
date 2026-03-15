# Vapi Integration - Project Goals

## Goal
Make my Vapi assistant with ID: `197591bc-b2ac-41fa-b48a-7f3b017f1b68` a Liquid API "broker"

## Use Case
Users call me via Vapi and say things like:
- "Hey I wanted to check in and ask if you are interested in buying..."
- "Buy $100 of Bitcoin"
- "What's my balance?"
- "Show my positions"

Vapi handles the conversation, and when the user wants to check their account or make a trade, Vapi calls the Liquid Wolf server tools.

## Implementation

### Architecture
```
User → Vapi Voice Assistant → HTTP POST with tools → Liquid Wolf Server → Liquid API
```

### Tools Implemented
The Vapi assistant now has these tools that call your Liquid Wolf server directly:

1. **place_order** - POST `/api/v1/orders/place`
   - Buy/sell crypto positions
   - Supports leverage, market/limit orders
   - Example: "Buy $100 of BTC-PERP with 5x leverage"

2. **get_account_info** - POST `/api/v1/account/info`
   - Get balance, equity, margin, positions
   - Example: "What's my balance?"

3. **get_positions** - POST `/api/v1/account/positions`
   - Get detailed position info with PnL
   - Example: "Show my positions"

4. **get_open_orders** - POST `/api/v1/orders/open`
   - Get pending orders
   - Example: "Do I have any open orders?"

### How It Works

1. User calls Vapi phone number
2. Vapi assistant (powered by GPT-4) listens and understands intent
3. When user wants to trade or check account, Vapi calls the appropriate tool
4. Tool makes HTTP POST to your Liquid Wolf server (via ngrok or production URL)
5. Server validates with `X-API-Key` header
6. Server processes request using user's `phone_number`
7. Server returns JSON response
8. Vapi speaks the result to the user

### Files Created

- `update_assistant.py` - Script to configure Vapi assistant with tools
- `tool_definitions.py` - Tool schemas (reference)
- `test_integration.py` - Test script
- `README.md` - Complete setup instructions
- `.env` - Vapi credentials

## Quick Start

1. **Start server**:
   ```bash
   python -m app.main
   ```

2. **Expose via ngrok**:
   ```bash
   ngrok http 8001
   ```

3. **Update Vapi assistant**:
   ```bash
   python -m vapi_integration.update_assistant --server-url https://your-ngrok-url.ngrok-free.app
   ```

4. **Test**: Call your Vapi number and say "What's my balance?"

## Next Steps

### Current Status (Phase 1)
✅ Basic trading tools (place orders, check account, view positions)

### Future Enhancements (Phase 2)
- Close positions tool
- Set TP/SL tool
- Cancel orders tool
- Update leverage tool
- Market data queries (current price, charts)

### Future Enhancements (Phase 3)
- Voice-based trade confirmations
- Risk warnings for high leverage
- PnL alerts during calls
- Integration with character voices/personalities

## API Reference

The Vapi API docs: https://docs.vapi.ai/api-reference/assistants/list

Your assistant: https://dashboard.vapi.ai/assistants/197591bc-b2ac-41fa-b48a-7f3b017f1b68
