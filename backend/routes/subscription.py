"""
Subscription Routes
Handles subscription plans, Stripe checkout, and billing management.
"""

from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel
from typing import List, Optional
import logging
import os
from dotenv import load_dotenv

from routes.auth import get_current_user_dependency

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Stripe
stripe = None
try:
    import stripe
    stripe.api_key = os.getenv("STRIPE_SECRET_KEY")
except Exception as e:
    logger.warning(f"Stripe not available: {e}. Using mock client.")

# Initialize router
router = APIRouter()


class SubscriptionPlan(BaseModel):
    """Subscription plan model."""
    id: str
    name: str
    price: int
    currency: str = "usd"
    interval: str = "month"
    features: List[str]


class SubscriptionPlansResponse(BaseModel):
    """Subscription plans response model."""
    plans: List[SubscriptionPlan]


class CheckoutSessionRequest(BaseModel):
    """Checkout session creation request."""
    plan_id: str
    success_url: str
    cancel_url: str


class CheckoutSessionResponse(BaseModel):
    """Checkout session response model."""
    session_id: str
    url: str


class SubscriptionStatus(BaseModel):
    """User subscription status model."""
    plan_name: Optional[str]
    status: str
    current_period_end: Optional[str]
    usage_stats: dict


# Define subscription plans
SUBSCRIPTION_PLANS = {
    "starter": SubscriptionPlan(
        id="starter",
        name="Starter",
        price=299,
        currency="usd",
        interval="month",
        features=[
            "5 videos per month",
            "Basic sign detection",
            "Email support",
            "Standard processing speed"
        ]
    ),
    "business": SubscriptionPlan(
        id="business",
        name="Business",
        price=899,
        currency="usd",
        interval="month",
        features=[
            "50 videos per month",
            "Advanced sign detection",
            "Priority support",
            "Fast processing speed",
            "Custom vocabulary",
            "API access"
        ]
    ),
    "enterprise": SubscriptionPlan(
        id="enterprise",
        name="Enterprise",
        price=0,  # Custom pricing
        currency="usd",
        interval="month",
        features=[
            "Unlimited videos",
            "Premium sign detection",
            "Dedicated support",
            "Real-time processing",
            "Custom AI training",
            "White-label solution",
            "SLA guarantee"
        ]
    )
}


@router.get("/plans", response_model=SubscriptionPlansResponse)
async def get_subscription_plans():
    """
    Get available subscription plans.

    Returns:
        List of available subscription plans
    """
    try:
        plans = list(SUBSCRIPTION_PLANS.values())
        return SubscriptionPlansResponse(plans=plans)

    except Exception as e:
        logger.error(f"Failed to get plans: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve plans"
        )


@router.post("/create", response_model=CheckoutSessionResponse)
async def create_checkout_session(
    request: CheckoutSessionRequest,
    current_user: dict = Depends(get_current_user_dependency)
):
    """
    Create a Stripe checkout session for subscription.

    Args:
        request: Checkout session request
        current_user: Current authenticated user

    Returns:
        Checkout session information

    Raises:
        HTTPException: If plan not found or session creation fails
    """
    try:
        # Validate plan
        if request.plan_id not in SUBSCRIPTION_PLANS:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid plan ID"
            )

        plan = SUBSCRIPTION_PLANS[request.plan_id]

        # For enterprise, redirect to contact page
        if plan.id == "enterprise":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Enterprise plan requires custom pricing. Please contact sales."
            )

        # Create Stripe checkout session
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': plan.currency,
                    'product_data': {
                        'name': f'SignBridge {plan.name} Plan',
                        'description': f'{plan.name} subscription - ${plan.price}/{plan.interval}',
                    },
                    'unit_amount': plan.price * 100,  # Convert to cents
                    'recurring': {
                        'interval': plan.interval,
                    },
                },
                'quantity': 1,
            }],
            mode='subscription',
            success_url=request.success_url,
            cancel_url=request.cancel_url,
            client_reference_id=current_user["user_id"],
            metadata={
                'user_id': current_user["user_id"],
                'plan_id': plan.id
            }
        )

        logger.info(f"Checkout session created for user {current_user['email']}: {session.id}")

        return CheckoutSessionResponse(
            session_id=session.id,
            url=session.url
        )

    except stripe.error.StripeError as e:
        logger.error(f"Stripe error: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Payment processing error"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to create checkout session: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create checkout session"
        )


@router.get("/status", response_model=SubscriptionStatus)
async def get_subscription_status(
    current_user: dict = Depends(get_current_user_dependency)
):
    """
    Get current user's subscription status and usage.

    Args:
        current_user: Current authenticated user

    Returns:
        Subscription status and usage information
    """
    try:
        # In a real implementation, you would query your database
        # for the user's subscription status from Stripe/webhooks

        # For now, return mock data
        # In production, this would integrate with Stripe API
        # and your database to get real subscription data

        mock_status = SubscriptionStatus(
            plan_name="Starter",
            status="active",
            current_period_end="2026-05-24T00:00:00Z",
            usage_stats={
                "videos_processed": 3,
                "videos_limit": 5,
                "usage_percentage": 60.0
            }
        )

        return mock_status

    except Exception as e:
        logger.error(f"Failed to get subscription status: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve subscription status"
        )