"""
Authentication Routes
Handles user registration, login, and profile management.
"""

from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr
from typing import Optional
import logging
import os
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import JWT utilities
jwt_utils = None
try:
    from utils.jwt_handler import (
        get_password_hash,
        verify_password,
        create_user_token,
        get_current_user
    )
    jwt_utils = True
except ImportError as e:
    logger.warning(f"JWT utilities not available: {e}. Using mock implementations.")
    jwt_utils = False

    # Mock implementations
    def get_password_hash(password: str) -> str:
        return f"mock_hash_{password}"

    def verify_password(plain_password: str, hashed_password: str) -> bool:
        return hashed_password == f"mock_hash_{plain_password}"

    def create_user_token(user_data: dict) -> str:
        return f"mock_token_{user_data['id']}"

    def get_current_user(token: str) -> Optional[dict]:
        if token.startswith("mock_token_"):
            return {"user_id": token.replace("mock_token_", ""), "email": "test@example.com", "name": "Test User"}
        return None

# Load environment variables
load_dotenv()

# Initialize Supabase client
supabase = None
try:
    from supabase import create_client, Client
    supabase = create_client(
        os.getenv("SUPABASE_URL"),
        os.getenv("SUPABASE_KEY")
    )
except Exception as e:
    logger.warning(f"Supabase not available: {e}. Using mock client.")

# Initialize router
router = APIRouter()
security = HTTPBearer()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class UserRegister(BaseModel):
    """User registration request model."""
    name: str
    email: EmailStr
    password: str
    company_name: str


class UserLogin(BaseModel):
    """User login request model."""
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    """User response model."""
    id: str
    name: str
    email: EmailStr
    company_name: str
    created_at: str


class AuthResponse(BaseModel):
    """Authentication response model."""
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


def get_current_user_dependency(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """
    Dependency to get current authenticated user.

    Args:
        credentials: HTTP authorization credentials

    Returns:
        Current user data

    Raises:
        HTTPException: If token is invalid
    """
    token = credentials.credentials
    user = get_current_user(token)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user


@router.post("/register", response_model=AuthResponse)
async def register_user(user_data: UserRegister):
    """
    Register a new user.

    Args:
        user_data: User registration data

    Returns:
        Authentication response with token and user data

    Raises:
        HTTPException: If user already exists or registration fails
    """
    try:
        # Check if user already exists
        if supabase:
            existing_user = supabase.table("users").select("*").eq("email", user_data.email).execute()
            if existing_user.data:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="User with this email already exists"
                )
        else:
            # Mock check - assume no existing user
            pass

        # Hash password
        hashed_password = get_password_hash(user_data.password)

        # Create user in Supabase
        user_record = {
            "name": user_data.name,
            "email": user_data.email,
            "password_hash": hashed_password,
            "company_name": user_data.company_name
        }

        if supabase:
            result = supabase.table("users").insert(user_record).execute()
            if not result.data:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to create user"
                )
            created_user = result.data[0]
        else:
            # Mock user creation
            created_user = {
                "id": "mock-user-id",
                "name": user_data.name,
                "email": user_data.email,
                "company_name": user_data.company_name,
                "created_at": datetime.utcnow().isoformat()
            }

        # Create JWT token
        token = create_user_token(created_user)

        # Prepare response
        user_response = UserResponse(
            id=created_user["id"],
            name=created_user["name"],
            email=created_user["email"],
            company_name=created_user["company_name"],
            created_at=created_user["created_at"]
        )

        logger.info(f"User registered: {user_data.email}")

        return AuthResponse(
            access_token=token,
            user=user_response
        )

    except Exception as e:
        logger.error(f"Registration failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Registration failed"
        )


@router.post("/login", response_model=AuthResponse)
async def login_user(login_data: UserLogin):
    """
    Authenticate a user.

    Args:
        login_data: User login credentials

    Returns:
        Authentication response with token and user data

    Raises:
        HTTPException: If credentials are invalid
    """
    try:
        # Get user from database
        if supabase:
            result = supabase.table("users").select("*").eq("email", login_data.email).execute()
            if not result.data:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid email or password"
                )
            user = result.data[0]
        else:
            # Mock user for testing
            if login_data.email == "test@example.com" and login_data.password == "password":
                user = {
                    "id": "mock-user-id",
                    "name": "Test User",
                    "email": login_data.email,
                    "password_hash": get_password_hash("password"),
                    "company_name": "Test Company",
                    "created_at": datetime.utcnow().isoformat()
                }
            else:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid email or password"
                )

        # Verify password
        if not verify_password(login_data.password, user["password_hash"]):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )

        # Create JWT token
        token = create_user_token(user)

        # Prepare response
        user_response = UserResponse(
            id=user["id"],
            name=user["name"],
            email=user["email"],
            company_name=user["company_name"],
            created_at=user["created_at"]
        )

        logger.info(f"User logged in: {login_data.email}")

        return AuthResponse(
            access_token=token,
            user=user_response
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Login failed"
        )


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: dict = Depends(get_current_user_dependency)):
    """
    Get current user information.

    Args:
        current_user: Current authenticated user

    Returns:
        User information
    """
    try:
        # Get full user data from database
        if supabase:
            result = supabase.table("users").select("*").eq("id", current_user["user_id"]).execute()
            if not result.data:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User not found"
                )
            user = result.data[0]
        else:
            # Mock user data
            user = {
                "id": current_user["user_id"],
                "name": current_user["name"],
                "email": current_user["email"],
                "company_name": current_user.get("company", "Test Company"),
                "created_at": datetime.utcnow().isoformat()
            }

        return UserResponse(
            id=user["id"],
            name=user["name"],
            email=user["email"],
            company_name=user["company_name"],
            created_at=user["created_at"]
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get user info: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get user information"
        )