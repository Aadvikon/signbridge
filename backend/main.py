"""
SignBridge FastAPI Backend
Entry point for the SignBridge API server.
Handles video processing requests and sign language generation.
"""

from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
import uvicorn
import os
from dotenv import load_dotenv

# Import route modules
from routes.auth import router as auth_router
from routes.video import router as video_router
from routes.subscription import router as subscription_router

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(
    title="SignBridge API",
    description="Real-time sign language translation for business videos",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure rate limiting
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Add rate limiting middleware
app.add_middleware(SlowAPIMiddleware)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("CORS_ORIGINS", "*").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add trusted host middleware for security
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["*"] if os.getenv("ENVIRONMENT") == "development" else ["yourdomain.com"]
)

# Include route modules
app.include_router(
    auth_router,
    prefix="/api/auth",
    tags=["Authentication"]
)

app.include_router(
    video_router,
    prefix="/api/video",
    tags=["Video Processing"]
)

app.include_router(
    subscription_router,
    prefix="/api/subscription",
    tags=["Subscription & Billing"]
)


@app.get("/")
def read_root():
    """
    Root endpoint - health check
    """
    return {"message": "SignBridge API is running"}


@app.get("/health")
def health_check():
    """
    Health check endpoint for monitoring
    """
    return {
        "status": "healthy",
        "service": "SignBridge API",
        "version": "0.1.0"
    }


if __name__ == "__main__":
    # Get config from environment
    host = os.getenv("API_HOST", "0.0.0.0")
    port = int(os.getenv("API_PORT", 8000))
    reload = os.getenv("API_RELOAD", "True").lower() == "true"
    
    # Run the server
    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=reload
    )
