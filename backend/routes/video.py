"""
Video Processing Routes
Handles video upload, processing, and sign detection results.
"""

from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Optional
import uuid
import os
import logging
from pathlib import Path
import json
from datetime import datetime

from services.landmark_extraction import LandmarkExtractor
from services.predictor import SignPredictor
from routes.auth import get_current_user_dependency

# Initialize router
router = APIRouter()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create uploads directory
UPLOAD_DIR = Path("data/raw/uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

# Initialize services
landmark_extractor = LandmarkExtractor()
predictor = None


def get_predictor() -> SignPredictor:
    global predictor
    if predictor is None:
        try:
            predictor = SignPredictor()
        except Exception as e:
            logger.error(f"Unable to initialize SignPredictor: {e}")
            raise
    return predictor


class VideoUploadResponse(BaseModel):
    """Video upload response model."""
    video_id: str
    filename: str
    size: int
    upload_time: str


class SignDetection(BaseModel):
    """Sign detection result model."""
    sign: str
    confidence: float
    start_time: float
    end_time: float


class VideoProcessingResponse(BaseModel):
    """Video processing response model."""
    video_id: str
    status: str
    processing_time: float
    detected_signs: List[SignDetection]


class VideoResultResponse(BaseModel):
    """Video result response model."""
    video_id: str
    filename: str
    upload_time: str
    processing_time: Optional[float]
    status: str
    detected_signs: Optional[List[SignDetection]]


@router.post("/upload", response_model=VideoUploadResponse)
async def upload_video(
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user_dependency)
):
    """
    Upload a video file for processing.

    Args:
        file: Video file to upload
        current_user: Current authenticated user

    Returns:
        Upload response with video ID

    Raises:
        HTTPException: If upload fails or file type is invalid
    """
    try:
        # Validate file type
        allowed_extensions = {".mp4", ".avi", ".mov", ".mkv", ".webm"}
        file_extension = Path(file.filename).suffix.lower()

        if file_extension not in allowed_extensions:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unsupported file type. Allowed: {', '.join(allowed_extensions)}"
            )

        # Validate file size (max 100MB)
        max_size = 100 * 1024 * 1024  # 100MB
        file_content = await file.read()
        file_size = len(file_content)

        if file_size > max_size:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail="File too large. Maximum size: 100MB"
            )

        # Generate unique video ID
        video_id = str(uuid.uuid4())

        # Save file
        video_path = UPLOAD_DIR / f"{video_id}{file_extension}"
        with open(video_path, "wb") as f:
            f.write(file_content)

        # Create metadata file
        metadata = {
            "video_id": video_id,
            "filename": file.filename,
            "original_filename": file.filename,
            "size": file_size,
            "upload_time": datetime.utcnow().isoformat(),
            "user_id": current_user["user_id"],
            "status": "uploaded",
            "file_path": str(video_path)
        }

        metadata_path = UPLOAD_DIR / f"{video_id}_metadata.json"
        with open(metadata_path, "w") as f:
            json.dump(metadata, f, indent=2)

        logger.info(f"Video uploaded: {video_id} by user {current_user['email']}")

        return VideoUploadResponse(
            video_id=video_id,
            filename=file.filename,
            size=file_size,
            upload_time=metadata["upload_time"]
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Upload failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Upload failed"
        )


@router.post("/process/{video_id}", response_model=VideoProcessingResponse)
async def process_video(
    video_id: str,
    current_user: dict = Depends(get_current_user_dependency)
):
    """
    Process uploaded video for sign detection.

    Args:
        video_id: ID of the uploaded video
        current_user: Current authenticated user

    Returns:
        Processing results with detected signs

    Raises:
        HTTPException: If video not found or processing fails
    """
    try:
        # Load metadata
        metadata_path = UPLOAD_DIR / f"{video_id}_metadata.json"
        if not metadata_path.exists():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Video not found"
            )

        with open(metadata_path, "r") as f:
            metadata = json.load(f)

        # Check ownership
        if metadata["user_id"] != current_user["user_id"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )

        # Check if already processed
        if metadata.get("status") == "processed":
            # Return cached results
            detected_signs = metadata.get("detected_signs", [])
            return VideoProcessingResponse(
                video_id=video_id,
                status="completed",
                processing_time=metadata.get("processing_time", 0),
                detected_signs=[SignDetection(**sign) for sign in detected_signs]
            )

        # Get video path
        video_path = Path(metadata["file_path"])
        if not video_path.exists():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Video file not found"
            )

        start_time = datetime.utcnow()

        # Extract landmarks
        logger.info(f"Extracting landmarks for video: {video_id}")
        landmark_results = landmark_extractor.process_video(str(video_path))

        # For now, create a simple sign detection result
        # In a real implementation, you'd process the landmark sequence
        # and use the predictor to identify signs with timestamps
        detected_signs = []

        # Mock sign detection for demonstration
        # In production, this would analyze the landmark sequence
        if landmark_results["total_frames"] > 0:
            # Simulate detecting signs at different timestamps
            detected_signs = [
                SignDetection(
                    sign="HELLO",
                    confidence=94.2,
                    start_time=0.0,
                    end_time=2.0
                ),
                SignDetection(
                    sign="THANK_YOU",
                    confidence=87.5,
                    start_time=2.5,
                    end_time=4.5
                )
            ]

        processing_time = (datetime.utcnow() - start_time).total_seconds()

        # Update metadata
        metadata["status"] = "processed"
        metadata["processing_time"] = processing_time
        metadata["detected_signs"] = [sign.dict() for sign in detected_signs]

        with open(metadata_path, "w") as f:
            json.dump(metadata, f, indent=2)

        logger.info(f"Video processed: {video_id}, detected {len(detected_signs)} signs")

        return VideoProcessingResponse(
            video_id=video_id,
            status="completed",
            processing_time=processing_time,
            detected_signs=detected_signs
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Processing failed for video {video_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Processing failed"
        )


@router.get("/result/{video_id}", response_model=VideoResultResponse)
async def get_video_result(
    video_id: str,
    current_user: dict = Depends(get_current_user_dependency)
):
    """
    Get processing results for a video.

    Args:
        video_id: ID of the processed video
        current_user: Current authenticated user

    Returns:
        Video processing results

    Raises:
        HTTPException: If video not found or access denied
    """
    try:
        # Load metadata
        metadata_path = UPLOAD_DIR / f"{video_id}_metadata.json"
        if not metadata_path.exists():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Video not found"
            )

        with open(metadata_path, "r") as f:
            metadata = json.load(f)

        # Check ownership
        if metadata["user_id"] != current_user["user_id"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )

        # Prepare response
        detected_signs = None
        if metadata.get("status") == "processed":
            detected_signs = [
                SignDetection(**sign) for sign in metadata.get("detected_signs", [])
            ]

        return VideoResultResponse(
            video_id=video_id,
            filename=metadata["filename"],
            upload_time=metadata["upload_time"],
            processing_time=metadata.get("processing_time"),
            status=metadata["status"],
            detected_signs=detected_signs
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get video result {video_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve results"
        )