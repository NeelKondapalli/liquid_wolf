#!/bin/bash

# Test the TTS endpoint with curl

echo "Testing Fish Audio TTS Server..."
echo ""

# Test 1: Basic request with default settings
echo "Test 1: Basic TTS request"
curl -X POST http://localhost:8000/tts \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Hello! This is a test of the Fish Audio TTS server. How does it sound?"
  }' \
  --output test_output.wav

echo ""
echo "Saved to test_output.wav"
echo ""

# Test 2: Custom voice and settings
echo "Test 2: Custom settings"
curl -X POST http://localhost:8000/tts \
  -H "Content-Type: application/json" \
  -d '{
    "text": "This is a custom test with specific settings.",
    "voiceId": "0e4d611458414e03bf3ef3b1ef367c79",
    "sampleRate": 24000,
    "format": "wav"
  }' \
  --output test_custom.wav

echo ""
echo "Saved to test_custom.wav"
echo ""

# Test 3: Health check
echo "Test 3: Health check"
curl -X GET http://localhost:8000/health

echo ""
echo ""
echo "Done! Check test_output.wav and test_custom.wav to hear the results."
