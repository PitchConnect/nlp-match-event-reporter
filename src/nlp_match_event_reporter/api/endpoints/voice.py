"""
Voice processing API endpoints.
"""

import time
from typing import Optional
from fastapi import APIRouter, HTTPException, UploadFile, File, Form, Depends
from sqlalchemy.orm import Session
from loguru import logger

from ...services.voice_processing import (
    whisper_service,
    tts_service,
    hotword_service,
    decode_audio_base64,
    encode_audio_base64,
    TranscriptionResult,
    TTSResult,
)
from ...models.database import VoiceProcessingLog
from ...core.database import get_database_session
from ...core.exceptions import VoiceProcessingError
from ...core.config import settings

from ...models.schemas import (
    VoiceTranscriptionResponse,
    TTSResponse,
    HotwordStatusResponse,
)

router = APIRouter()


@router.post("/transcribe", response_model=VoiceTranscriptionResponse)
async def transcribe_audio(
    audio_file: UploadFile = File(...),
    match_id: Optional[int] = Form(default=None),
    language: str = Form(default="sv"),
    db: Session = Depends(get_database_session),
) -> VoiceTranscriptionResponse:
    """Transcribe audio file to text using Whisper."""
    start_time = time.time()

    try:
        logger.info(f"Transcribing audio file: {audio_file.filename}")

        # Validate file type
        if not audio_file.content_type.startswith("audio/"):
            raise HTTPException(status_code=400, detail="File must be an audio file")

        # Read audio data
        audio_bytes = await audio_file.read()

        # Transcribe using Whisper
        try:
            result = await whisper_service.transcribe_audio(
                audio_data=audio_bytes,
                language=language
            )

            # Log successful processing
            log_entry = VoiceProcessingLog(
                operation_type="transcribe",
                status="success",
                input_data=f"file:{audio_file.filename}",
                output_data=result.text,
                processing_time_ms=int(result.processing_time * 1000),
                confidence_score=result.confidence,
                match_id=match_id,
            )
            db.add(log_entry)
            db.commit()

            logger.info(f"Transcription completed: {result.text[:100]}...")

            # TODO: Extract match events from transcription if match_id provided
            detected_events = []
            if match_id:
                # Placeholder for event extraction logic
                # In a real implementation, you would use NLP to extract events
                pass

            return VoiceTranscriptionResponse(
                text=result.text,
                confidence=result.confidence,
                language=result.language,
                duration=result.processing_time,
                detected_events=detected_events
            )

        except VoiceProcessingError as e:
            # Log failed processing
            log_entry = VoiceProcessingLog(
                operation_type="transcribe",
                status="error",
                input_data=f"file:{audio_file.filename}",
                error_message=str(e),
                processing_time_ms=int((time.time() - start_time) * 1000),
                match_id=match_id,
            )
            db.add(log_entry)
            db.commit()

            raise HTTPException(status_code=500, detail=str(e))

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error transcribing audio: {e}")

        # Log unexpected error
        log_entry = VoiceProcessingLog(
            operation_type="transcribe",
            status="error",
            input_data=f"file:{audio_file.filename if audio_file else 'unknown'}",
            error_message=str(e),
            processing_time_ms=int((time.time() - start_time) * 1000),
            match_id=match_id,
        )
        db.add(log_entry)
        db.commit()

        raise HTTPException(status_code=500, detail="Failed to transcribe audio")


@router.post("/speak", response_model=TTSResponse)
async def text_to_speech(
    text: str = Form(...),
    voice: str = Form(default="default"),
    speed: float = Form(default=1.0, ge=0.5, le=2.0),
    db: Session = Depends(get_database_session),
) -> TTSResponse:
    """Convert text to speech using TTS engine."""
    start_time = time.time()

    try:
        logger.info(f"Converting text to speech: {text[:50]}...")

        # Synthesize speech using Kokoro TTS
        try:
            result = await tts_service.synthesize_speech(
                text=text,
                voice=voice,
                speed=speed
            )

            # Save audio to temporary file
            import tempfile
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
                temp_file.write(result.audio_data)
                audio_file_path = temp_file.name

            # Log successful processing
            log_entry = VoiceProcessingLog(
                operation_type="tts",
                status="success",
                input_data=text[:500],
                output_data=audio_file_path,
                processing_time_ms=int(result.processing_time * 1000),
                output_file_path=audio_file_path,
            )
            db.add(log_entry)
            db.commit()

            logger.info(f"TTS synthesis completed: {result.duration:.2f}s audio")

            return TTSResponse(
                message="Text converted to speech successfully",
                audio_url=audio_file_path,
                duration=result.duration,
                voice_used=voice,
                speed_used=speed
            )

        except VoiceProcessingError as e:
            # Log failed processing
            log_entry = VoiceProcessingLog(
                operation_type="tts",
                status="error",
                input_data=text[:500],
                error_message=str(e),
                processing_time_ms=int((time.time() - start_time) * 1000),
            )
            db.add(log_entry)
            db.commit()

            raise HTTPException(status_code=500, detail=str(e))

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error converting text to speech: {e}")

        # Log unexpected error
        log_entry = VoiceProcessingLog(
            operation_type="tts",
            status="error",
            input_data=text[:500] if text else "unknown",
            error_message=str(e),
            processing_time_ms=int((time.time() - start_time) * 1000),
        )
        db.add(log_entry)
        db.commit()

        raise HTTPException(status_code=500, detail="Failed to convert text to speech")


@router.get("/hotword/status", response_model=HotwordStatusResponse)
async def get_hotword_status(
    db: Session = Depends(get_database_session),
) -> HotwordStatusResponse:
    """Get current hotword detection status."""
    try:
        logger.info("Getting hotword detection status")

        # Get actual status from hotword service
        is_active = hotword_service.is_listening

        # Get detection statistics from database
        from datetime import datetime, timezone, timedelta
        today = datetime.now(timezone.utc).date()

        detections_today = db.query(VoiceProcessingLog).filter(
            VoiceProcessingLog.operation_type == "hotword",
            VoiceProcessingLog.status == "success",
            VoiceProcessingLog.created_at >= today
        ).count()

        # Get last detection
        last_detection_log = db.query(VoiceProcessingLog).filter(
            VoiceProcessingLog.operation_type == "hotword",
            VoiceProcessingLog.status == "success"
        ).order_by(VoiceProcessingLog.created_at.desc()).first()

        last_detection = None
        if last_detection_log:
            last_detection = last_detection_log.created_at.isoformat()

        return HotwordStatusResponse(
            active=is_active,
            sensitivity=settings.HOTWORD_SENSITIVITY,
            model_loaded=hotword_service._initialized,
            detections_today=detections_today,
            last_detection=last_detection,
            audio_device="Default Microphone"
        )

    except Exception as e:
        logger.error(f"Error getting hotword status: {e}")
        raise HTTPException(status_code=500, detail="Failed to get hotword status")


@router.post("/hotword/start")
async def start_hotword_detection(
    keywords: str = Form(default="referee,domare"),
    sensitivity: float = Form(default=None),
    db: Session = Depends(get_database_session),
) -> dict:
    """Start hotword detection service."""
    try:
        logger.info("Starting hotword detection")

        if hotword_service.is_listening:
            return {
                "message": "Hotword detection already active",
                "status": "active"
            }

        # Parse keywords
        keyword_list = [kw.strip() for kw in keywords.split(",")]

        # Define callback for hotword detection
        def on_hotword_detected(keyword: str):
            logger.info(f"Hotword detected: {keyword}")

            # Log detection to database
            log_entry = VoiceProcessingLog(
                operation_type="hotword",
                status="success",
                input_data=keyword,
                output_data=f"detected:{keyword}",
                processing_time_ms=0,
            )
            # Note: We can't use the db session here directly due to async context
            # In a real implementation, you'd use a queue or async callback

        # Start hotword detection
        await hotword_service.start_listening(
            keywords=keyword_list,
            callback=on_hotword_detected,
            sensitivity=sensitivity
        )

        return {
            "message": "Hotword detection started successfully",
            "status": "active",
            "keywords": keyword_list,
            "sensitivity": sensitivity or settings.HOTWORD_SENSITIVITY
        }

    except Exception as e:
        logger.error(f"Error starting hotword detection: {e}")
        raise HTTPException(status_code=500, detail="Failed to start hotword detection")


@router.post("/hotword/stop")
async def stop_hotword_detection() -> dict:
    """Stop hotword detection service."""
    try:
        logger.info("Stopping hotword detection")

        if not hotword_service.is_listening:
            return {
                "message": "Hotword detection already inactive",
                "status": "inactive"
            }

        # Stop hotword detection
        await hotword_service.stop_listening()

        return {
            "message": "Hotword detection stopped successfully",
            "status": "inactive"
        }

    except Exception as e:
        logger.error(f"Error stopping hotword detection: {e}")
        raise HTTPException(status_code=500, detail="Failed to stop hotword detection")


@router.post("/hotword/configure")
async def configure_hotword_detection(
    sensitivity: float = Form(default=0.5, ge=0.0, le=1.0),
    model_path: Optional[str] = Form(default=None),
) -> dict:
    """Configure hotword detection settings."""
    try:
        logger.info(f"Configuring hotword detection: sensitivity={sensitivity}")
        
        # TODO: Implement hotword configuration
        # - Update Porcupine sensitivity
        # - Load new model if provided
        # - Restart detection if active
        
        return {
            "message": "Hotword detection configured successfully",
            "sensitivity": sensitivity,
            "model_path": model_path or "default"
        }
        
    except Exception as e:
        logger.error(f"Error configuring hotword detection: {e}")
        raise HTTPException(status_code=500, detail="Failed to configure hotword detection")
