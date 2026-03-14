# Fish Audio TTS Server for VAPI

A FastAPI-based server that integrates Fish Audio TTS and exposes a VAPI-compatible interface for text-to-speech conversion.

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Configure your Fish Audio API key:
   - Copy `.env.example` to `.env`
   - Add your Fish Audio API key to the `.env` file:
     ```
     FISH_AUDIO_API_KEY=your_actual_api_key_here
     ```

3. Run the server:
```bash
python server.py
```

Or with uvicorn directly:
```bash
uvicorn server:app --host 0.0.0.0 --port 8000
```

The server will start on `http://0.0.0.0:8000`

## API Endpoints

### POST /tts

Text-to-Speech conversion endpoint.

**Request:**
```json
{
  "text": "Hello! How can I help you today?",
  "voiceId": "0e4d611458414e03bf3ef3b1ef367c79",
  "sampleRate": 24000,
  "format": "wav"
}
```

**Parameters:**
- `text` (required): The text to synthesize
- `voiceId` (optional): Fish Audio model ID (default: `0e4d611458414e03bf3ef3b1ef367c79`)
- `sampleRate` (optional): Audio sample rate in Hz (default: `24000`)
- `format` (optional): Audio format - `wav` or `pcm` (default: `wav`)

**Response:**
- Status: `200 OK`
- Content-Type: `audio/wav` or `audio/pcm`
- Body: Raw audio bytes

**Error Response:**
```json
{
  "error": "Error description"
}
```

### GET /health

Health check endpoint.

**Response:**
```json
{
  "status": "healthy"
}
```

## API Documentation

Once the server is running, visit:
- Interactive API docs: `http://localhost:8000/docs`
- Alternative docs: `http://localhost:8000/redoc`

## Testing

Test with curl:
```bash
curl -X POST http://localhost:8000/tts \
  -H "Content-Type: application/json" \
  -d '{"text": "Hello, this is a test!"}' \
  --output test.wav
```

## VAPI Integration

Configure VAPI to use this custom voice provider:

```javascript
voice: {
  provider: "custom-voice",
  url: "https://your-server.com/tts"
}
```

## Notes

- The server uses the Fish Audio model ID: `0e4d611458414e03bf3ef3b1ef367c79`
- Version: `s2-pro`
- Default sample rate: 24000 Hz
- For production, deploy behind HTTPS (required by VAPI)
