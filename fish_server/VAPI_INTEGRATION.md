# VAPI Integration Documentation

## Overview

This server provides a custom TTS endpoint for VAPI using Fish Audio's text-to-speech API.

## VAPI Request Format

VAPI sends requests with a nested structure:

```json
{
  "message": {
    "text": "Hello! 👋. I see you're interested in learning more about stocks.",
    "sampleRate": 16000,
    "type": "voice-request",
    "timestamp": 1773515738353,
    "artifact": { ... }
  },
  "call": {
    "id": "019cedc6-69ab-7001-9a71-176e5b4d32e3",
    "type": "webCall",
    "status": "queued",
    ...
  },
  "assistant": {
    "id": "197591bc-b2ac-41fa-b48a-7f3b017f1b68",
    "name": "Jordan",
    "voice": {
      "server": {
        "url": "https://your-server.com/tts"
      },
      "voiceId": "Jordan",
      "provider": "custom-voice"
    },
    ...
  }
}
```

### Key Fields:
- `message.text` - The text to synthesize (required)
- `message.sampleRate` - VAPI sends 16000 Hz (we return 24000 Hz as required)
- `message.type` - Always "voice-request"
- `assistant.voice.voiceId` - Voice identifier (we use default Fish Audio model)

## Our Response Strategy

### 1. Audio Format
We return WAV audio with these specifications:
- **Container**: WAV (RIFF)
- **Codec**: PCM 16-bit signed
- **Sample Rate**: 24000 Hz (VAPI requirement)
- **Channels**: mono (1 channel)
- **Content-Type**: `audio/wav`

### 2. Streaming Approach
- Use Fish Audio's `.stream()` method for lower latency
- Stream chunks to VAPI as they arrive from Fish Audio
- VAPI can start playing audio before full synthesis completes
- Better for conversational turn-taking

### 3. Request Processing Flow

```
VAPI Request
    ↓
Extract message.text
    ↓
Call Fish Audio TTS API (streaming)
  - Format: WAV
  - Sample Rate: 24kHz
  - Model: 0e4d611458414e03bf3ef3b1ef367c79
    ↓
Stream audio chunks to VAPI
    ↓
(Debug Mode: Save to debug_audio/)
```

### 4. Configuration

#### Fish Audio
```python
config = TTSConfig(
    format="wav",
    sample_rate=24000,  # VAPI requirement
    reference_id="0e4d611458414e03bf3ef3b1ef367c79"  # Default voice
)
```

#### FastAPI Response
```python
StreamingResponse(
    stream_with_debug(),
    media_type='audio/wav',
    headers={'Content-Disposition': 'inline'}
)
```

## VAPI Configuration

In your VAPI assistant settings:

```javascript
{
  "voice": {
    "provider": "custom-voice",
    "server": {
      "url": "https://your-server.com/tts"
    },
    "voiceId": "Jordan"  // Optional, not currently used
  }
}
```

## Error Handling

### 422 Unprocessable Entity
- **Cause**: Request body doesn't match expected format
- **Solution**: Ensure `message.text` field is present

### 500 Internal Server Error
- **Cause**: Fish Audio API error or streaming failure
- **Check**: Server logs for detailed error traceback

## Debug Mode

When `DEBUG_MODE=true` in `.env`:
- All requests logged with full JSON body
- Audio responses saved to `debug_audio/` folder
- Files named: `tts_YYYYMMDD_HHMMSS_microseconds.wav`
- Streaming statistics logged (chunk count, total bytes)

## Testing

### Local Test
```bash
curl -X POST http://localhost:8000/tts \
  -H "Content-Type: application/json" \
  -d '{
    "message": {
      "text": "Hello from VAPI!",
      "sampleRate": 16000
    }
  }' \
  --output test.wav
```

### Verify Audio Format
```bash
file test.wav
# Expected: RIFF (little-endian) data, WAVE audio, Microsoft PCM, 16 bit, mono 24000 Hz
```

## Concurrency

FastAPI handles concurrent requests automatically using async/await:
- Each VAPI call gets its own async task
- Multiple assistants can call simultaneously
- No process spawning needed
- Built-in async event loop handles parallelism

## Sample VAPI Logs

```
2026-03-14 12:15:38 - INFO - Raw request body from VAPI: {"message":{"text":"Hello! 👋...
2026-03-14 12:15:38 - INFO - Received VAPI request - text: 'Hello! 👋. I see you're interested...'
2026-03-14 12:15:38 - INFO - Calling Fish Audio stream API
2026-03-14 12:15:38 - INFO - Started streaming audio from Fish Audio API
2026-03-14 12:15:39 - INFO - Streaming complete: 5 chunks, 156234 bytes total
```

## Architecture Decisions

### Why 24kHz output when VAPI sends 16kHz?
VAPI's documentation specifies PCM 16-bit mono 24kHz as the recommended target format for best quality and compatibility.

### Why streaming instead of full response?
Streaming reduces latency - VAPI can start playing audio before Fish Audio finishes synthesizing, improving perceived responsiveness in conversations.

### Why extract only `message.text`?
VAPI sends extensive metadata, but only `message.text` is needed for TTS. We ignore the rest to keep the implementation simple.
