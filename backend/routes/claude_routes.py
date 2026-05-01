"""
Claude routes for SignBridge via AWS Bedrock.
Provides endpoints for chat, transcript simplification, and accessibility auditing.
"""

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
import logging

from claude_service import (
    ask_claude,
    simplify_for_isl,
    accessibility_audit,
    support_chat,
)

logger = logging.getLogger(__name__)
router = APIRouter()


class MessageRequest(BaseModel):
    """Generic message request model."""
    message: str


class MessageResponse(BaseModel):
    """Generic message response model."""
    response: str


@router.post("/chat", response_model=MessageResponse)
async def chat(request: MessageRequest):
    """Support chatbot endpoint."""
    if not request.message or not request.message.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The 'message' field is required.",
        )

    try:
        response = support_chat(request.message)
        return MessageResponse(response=response)
    except ValueError as error:
        logger.error("Configuration error: %s", error)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Configuration error: {str(error)}",
        )
    except Exception as error:
        logger.error("Anthropic API error details: %s | Type: %s", error, type(error).__name__)
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Claude API error: {str(error)}",
        )


@router.post("/simplify-transcript", response_model=MessageResponse)
async def simplify_transcript_endpoint(request: MessageRequest):
    """Simplify transcript for ISL users."""
    if not request.message or not request.message.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The 'message' field is required.",
        )

    try:
        response = simplify_for_isl(request.message)
        return MessageResponse(response=response)
    except ValueError as error:
        logger.error("Configuration error: %s", error)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Service configuration error.",
        )
    except Exception as error:
        logger.error("Bedrock API error: %s", error)
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Claude API error. Please try again later.",
        )


@router.post("/accessibility-audit", response_model=MessageResponse)
async def accessibility_audit_endpoint(request: MessageRequest):
    """Audit content for accessibility gaps."""
    if not request.message or not request.message.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The 'message' field is required.",
        )

    try:
        response = accessibility_audit(request.message)
        return MessageResponse(response=response)
    except ValueError as error:
        logger.error("Configuration error: %s", error)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Service configuration error.",
        )
    except Exception as error:
        logger.error("Bedrock API error: %s", error)
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Claude API error. Please try again later.",
        )
