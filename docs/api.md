# API Documentation

## Overview

The NLP Match Event Reporter provides a RESTful API for managing real-time soccer match event reporting through voice interaction and natural language processing.

## Base URL

```
http://localhost:8000/api/v1
```

## Authentication

Currently, the API does not require authentication for development. Production deployment will include proper authentication mechanisms.

## Endpoints

### Health Checks

#### GET /health/
Basic health check endpoint.

**Response:**
```json
{
  "status": "healthy",
  "version": "0.1.0",
  "environment": "development"
}
```

#### GET /health/detailed
Detailed health check with service status.

**Response:**
```json
{
  "status": "healthy",
  "version": "0.1.0",
  "environment": "development",
  "services": {
    "api": "healthy",
    "database": "healthy",
    "fogis_client": "healthy",
    "voice_processing": "healthy"
  },
  "configuration": {
    "debug": true,
    "log_level": "INFO",
    "whisper_model": "base",
    "tts_engine": "kokoro"
  }
}
```

### Matches

#### GET /matches/
Get list of matches from FOGIS API.

**Parameters:**
- `limit` (int, optional): Number of matches to return (1-100, default: 10)
- `offset` (int, optional): Number of matches to skip (default: 0)
- `status` (string, optional): Filter by match status

**Response:**
```json
{
  "matches": [
    {
      "id": 123456,
      "home_team": "AIK",
      "away_team": "Hammarby",
      "date": "2025-08-20",
      "time": "19:00",
      "venue": "Friends Arena",
      "status": "scheduled",
      "competition": "Allsvenskan"
    }
  ],
  "total": 25,
  "limit": 10,
  "offset": 0
}
```

#### GET /matches/{match_id}
Get detailed information about a specific match.

**Response:**
```json
{
  "id": 123456,
  "home_team": "AIK",
  "away_team": "Hammarby",
  "date": "2025-08-20",
  "time": "19:00",
  "venue": "Friends Arena",
  "status": "scheduled",
  "competition": "Allsvenskan",
  "home_team_id": 1001,
  "away_team_id": 1002,
  "referee_id": 5001,
  "events": []
}
```

#### POST /matches/{match_id}/start
Start event reporting for a match.

**Response:**
```json
{
  "message": "Event reporting started for match 123456",
  "match_id": 123456,
  "status": "active"
}
```

#### POST /matches/{match_id}/stop
Stop event reporting for a match.

**Response:**
```json
{
  "message": "Event reporting stopped for match 123456",
  "match_id": 123456,
  "status": "completed"
}
```

### Events

#### GET /events/
Get list of match events.

**Parameters:**
- `match_id` (int, optional): Filter events by match ID
- `limit` (int, optional): Number of events to return (1-200, default: 50)
- `offset` (int, optional): Number of events to skip (default: 0)

**Response:**
```json
{
  "events": [
    {
      "id": 1,
      "match_id": 123456,
      "event_type": "goal",
      "minute": 15,
      "player_name": "Erik Karlsson",
      "team": "AIK",
      "description": "Goal scored by Erik Karlsson",
      "timestamp": "2025-08-20T19:15:00Z",
      "synced_to_fogis": true
    }
  ],
  "total": 12,
  "limit": 50,
  "offset": 0
}
```

#### POST /events/
Create a new match event.

**Request Body:**
```json
{
  "match_id": 123456,
  "event_type": "goal",
  "minute": 15,
  "player_name": "Erik Karlsson",
  "team": "AIK",
  "description": "Goal scored by Erik Karlsson"
}
```

**Response:**
```json
{
  "message": "Event created successfully",
  "event": {
    "id": 999,
    "match_id": 123456,
    "event_type": "goal",
    "minute": 15,
    "player_name": "Erik Karlsson",
    "team": "AIK",
    "description": "Goal scored by Erik Karlsson",
    "timestamp": "2025-08-20T19:30:00Z",
    "synced_to_fogis": false
  }
}
```

### Voice Processing

#### POST /voice/transcribe
Transcribe audio file to text using Whisper.

**Request:**
- `audio_file` (file): Audio file to transcribe
- `match_id` (int, optional): Match ID for event extraction
- `language` (string, optional): Language code (default: "sv")

**Response:**
```json
{
  "text": "Mål av Erik Karlsson i femtonde minuten",
  "confidence": 0.95,
  "language": "sv",
  "duration": 2.5,
  "detected_events": [
    {
      "event_type": "goal",
      "player_name": "Erik Karlsson",
      "minute": 15,
      "confidence": 0.92
    }
  ]
}
```

#### POST /voice/speak
Convert text to speech using TTS engine.

**Request:**
- `text` (string): Text to convert to speech
- `voice` (string, optional): Voice to use (default: "default")
- `speed` (float, optional): Speech speed (0.5-2.0, default: 1.0)

**Response:**
```json
{
  "message": "Text converted to speech successfully",
  "audio_url": "/tmp/tts_output_123.wav",
  "duration": 3.2,
  "voice_used": "default",
  "speed_used": 1.0
}
```

## Error Responses

All endpoints may return error responses in the following format:

```json
{
  "error": "Error message",
  "detail": "Detailed error information",
  "timestamp": "2025-08-20T19:30:00Z"
}
```

Common HTTP status codes:
- `400` - Bad Request (validation errors)
- `401` - Unauthorized
- `403` - Forbidden
- `404` - Not Found
- `422` - Unprocessable Entity
- `500` - Internal Server Error
- `502` - Bad Gateway (external service errors)
- `503` - Service Unavailable
