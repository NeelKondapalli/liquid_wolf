import os
import io
import wave
import logging
from datetime import datetime
from pathlib import Path
from fastapi import FastAPI, HTTPException, Response, Request
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field, ConfigDict
from dotenv import load_dotenv
import httpx
from fishaudio import AsyncFishAudio
from fishaudio.types import TTSConfig, Prosody

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

app = FastAPI(
    title="Fish Audio TTS Server",
    description="VAPI-compatible Text-to-Speech API using Fish Audio",
    version="1.0.0"
)

# Fish Audio configuration
FISH_API_KEY = os.getenv('FISH_AUDIO_API_KEY')
DEFAULT_MODEL_ID = '0e4d611458414e03bf3ef3b1ef367c79'
DEBUG_MODE = os.getenv('DEBUG_MODE', 'false').lower() == 'true'

if not FISH_API_KEY:
    raise ValueError("FISH_AUDIO_API_KEY not found in .env file")

# Initialize Fish Audio client with custom headers to specify s2-pro model
# Based on curl API: -H "model: s2-pro"
httpx_client = httpx.AsyncClient(
    base_url="https://api.fish.audio",
    headers={"model": "s2-pro"}
)
client = AsyncFishAudio(api_key=FISH_API_KEY, httpx_client=httpx_client)

# Create debug directory if debug mode is enabled
if DEBUG_MODE:
    DEBUG_DIR = Path("debug_audio")
    DEBUG_DIR.mkdir(exist_ok=True)
    logger.info(f"Debug mode enabled - audio files will be saved to {DEBUG_DIR}")


class VoiceMessage(BaseModel):
    """VAPI message structure"""
    text: str
    sampleRate: int = 16000
    type: str = "voice-request"
    timestamp: int = 0

class VAPIRequestModel(BaseModel):
    """Request model for VAPI TTS endpoint

    VAPI sends nested structure with message.text
    Output format: WAV with PCM 16-bit, mono, 24kHz
    """
    message: VoiceMessage


class HealthResponse(BaseModel):
    """Response model for health check"""
    status: str


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}


@app.post("/tts")
async def text_to_speech(request: VAPIRequestModel):
    """
    Text-to-Speech endpoint for VAPI integration.

    VAPI sends: {"message": {"text": "...", "sampleRate": 16000}}
    Returns: WAV audio with PCM 16-bit, mono, 24kHz
    """
    try:
        # Extract text from VAPI's nested structure
        text = request.message.text

        # Log the incoming request
        logger.info(f"Received VAPI request - text: '{text[:100]}...', sampleRate: {request.message.sampleRate}")

        # Validate text
        if not text.strip():
            logger.warning("Empty text received in request")
            raise HTTPException(status_code=400, detail="Text cannot be empty")

        # Generate audio using Fish Audio with VAPI-compatible settings
        # VAPI requires: WAV with PCM 16-bit, mono, 24kHz
        logger.info(f"Calling Fish Audio API for TTS conversion (streaming)")

        # Create config for VAPI: WAV format, 16kHz sample rate
        # Generate WAV (good quality) then extract PCM for VAPI
        config = TTSConfig(
            format="wav",
            sample_rate=16000,  # Match VAPI's request sampleRate
            reference_id=DEFAULT_MODEL_ID,
            latency="balanced"
        )

        # Generator function to stream PCM chunks from WAV stream
        async def stream_with_debug():
            debug_wav_buffer = io.BytesIO() if DEBUG_MODE else None
            debug_pcm_buffer = io.BytesIO() if DEBUG_MODE else None
            chunk_count = 0
            total_wav_bytes = 0
            total_pcm_bytes = 0
            header_buffer = b""
            header_skipped = False
            header_size = None

            # Use stream() for lower latency - VAPI can start playing audio sooner
            # For AsyncFishAudio, stream() is a coroutine that returns an async iterable
            logger.info(f"Calling Fish Audio stream API")
            audio_stream_obj = await client.tts.stream(
                text=text,
                config=config
            )
            logger.info(f"Started streaming audio from Fish Audio API")

            # Stream chunks, skipping WAV header and sending raw PCM
            try:
                async for chunk in audio_stream_obj:
                    chunk_count += 1
                    total_wav_bytes += len(chunk)

                    # Save WAV to debug buffer if enabled
                    if DEBUG_MODE:
                        debug_wav_buffer.write(chunk)

                    # Parse and skip WAV header
                    if not header_skipped:
                        header_buffer += chunk

                        # Check if we have enough data to parse the header
                        if len(header_buffer) >= 44:
                            # Parse WAV header to find data chunk offset
                            # Standard WAV: RIFF header (12 bytes) + fmt chunk (24 bytes) + data chunk header (8 bytes) = 44 bytes
                            # But some WAVs have extra chunks, so we search for "data" chunk
                            data_offset = header_buffer.find(b'data')
                            if data_offset != -1:
                                # Found data chunk, skip header (data offset + 8 bytes for "data" + size)
                                header_size = data_offset + 8
                                pcm_chunk = header_buffer[header_size:]
                                header_skipped = True
                                logger.info(f"Skipped {header_size} byte WAV header, streaming PCM data")
                            else:
                                # Haven't found data chunk yet, keep buffering
                                continue
                        else:
                            # Need more data to parse header
                            continue
                    else:
                        # Subsequent chunks are pure PCM data
                        pcm_chunk = chunk

                    total_pcm_bytes += len(pcm_chunk)

                    # Save PCM to debug buffer if enabled
                    if DEBUG_MODE:
                        debug_pcm_buffer.write(pcm_chunk)

                    # Stream PCM chunk to VAPI immediately (low latency)
                    yield pcm_chunk

            except Exception as e:
                logger.error(f"Error during streaming: {e}")
                raise

            logger.info(f"Streaming complete: {chunk_count} WAV chunks, {total_wav_bytes} WAV bytes, {total_pcm_bytes} PCM bytes streamed")

            # Save debug files after streaming completes
            if DEBUG_MODE:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")

                # Save WAV file
                wav_filename = DEBUG_DIR / f"tts_{timestamp}.wav"
                with open(wav_filename, "wb") as f:
                    f.write(debug_wav_buffer.getvalue())
                logger.info(f"Debug: Saved WAV audio to {wav_filename}")

                # Save PCM file
                pcm_filename = DEBUG_DIR / f"tts_{timestamp}.pcm"
                with open(pcm_filename, "wb") as f:
                    f.write(debug_pcm_buffer.getvalue())
                logger.info(f"Debug: Saved PCM audio to {pcm_filename}")

        # Return streaming response with raw PCM (low latency)
        # Convert WAV to PCM by streaming: skip header, stream PCM chunks
        return StreamingResponse(
            stream_with_debug(),
            media_type='application/octet-stream',
            headers={
                'Content-Disposition': 'inline'
            }
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing TTS request: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "name": "Fish Audio TTS Server",
        "version": "1.0.0",
        "endpoints": {
            "health": "/health",
            "tts": "/tts",
            "docs": "/docs"
        }
    }


if __name__ == '__main__':
    import uvicorn
    port = int(os.getenv('PORT', 8000))
    uvicorn.run(app, host='0.0.0.0', port=port)
