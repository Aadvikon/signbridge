"""Claude AI service using AWS Bedrock."""

import logging
import os
import json
from dotenv import load_dotenv
import boto3
from botocore.exceptions import ClientError

load_dotenv()

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

MODEL_ID = "anthropic.claude-3-5-haiku-20241022-v1:0"


def get_bedrock_client():
    """Initialize and return the AWS Bedrock runtime client."""
    bearer_token = os.getenv("AWS_BEARER_TOKEN_BEDROCK")
    region = os.getenv("AWS_REGION", "eu-north-1")
    session_token = os.getenv("AWS_SESSION_TOKEN")
    secret_key = os.getenv("AWS_SECRET_ACCESS_KEY")

    if not bearer_token:
        raise ValueError(
            "AWS_BEARER_TOKEN_BEDROCK is required. Configure it in the .env file."
        )

    # Support two formats:
    # 1) key:secret
    # 2) key only + AWS_SECRET_ACCESS_KEY set separately
    try:
        if ":" in bearer_token:
            access_key, secret_key = bearer_token.split(":", 1)
        elif not secret_key:
            raise ValueError(
                "Bearer token format invalid. Use key:secret or set AWS_SECRET_ACCESS_KEY separately."
            )
        else:
            access_key = bearer_token
    except Exception as e:
        logger.error("Failed to parse bearer token: %s", str(e))
        raise

    client_kwargs = {
        "service_name": "bedrock-runtime",
        "region_name": region,
        "aws_access_key_id": access_key,
        "aws_secret_access_key": secret_key,
    }
    if session_token:
        client_kwargs["aws_session_token"] = session_token

    return boto3.client(**client_kwargs)


def ask_claude(user_message: str, system: str = "") -> str:
    """Send a message to Claude via AWS Bedrock and return the response."""
    try:
        bedrock = get_bedrock_client()

        if not system:
            system = "You are SignBridge AI assistant for sign language accessibility."

        body = json.dumps(
            {
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": 1024,
                "system": system,
                "messages": [{"role": "user", "content": user_message}],
            }
        )

        response = bedrock.invoke_model(modelId=MODEL_ID, body=body)
        result = json.loads(response["body"].read())
        return result["content"][0]["text"]
    except ClientError as error:
        logger.error(
            "AWS Bedrock API error - Code: %s | Message: %s",
            error.response["Error"]["Code"],
            error.response["Error"]["Message"],
        )
        raise
    except Exception as error:
        logger.error(
            "AWS Bedrock request failed - Error Type: %s | Message: %s",
            type(error).__name__,
            str(error),
        )
        raise


def simplify_for_isl(transcript: str) -> str:
    """Simplify transcript for Indian Sign Language (ISL) users."""
    return ask_claude(
        f"Convert this to simple ISL-friendly sentences: {transcript}",
        system="You are an Indian Sign Language expert. Simplify content for deaf and hard-of-hearing users.",
    )


def accessibility_audit(content: str) -> str:
    """Audit content for accessibility gaps."""
    return ask_claude(
        f"Audit this content for deaf/HoH accessibility gaps: {content}",
        system="You are an accessibility compliance expert for RPWD Act and WCAG standards.",
    )


def support_chat(question: str) -> str:
    """Handle customer support queries."""
    return ask_claude(
        question,
        system="You are SignBridge customer support. Help users with the platform in a friendly and professional manner.",
    )
