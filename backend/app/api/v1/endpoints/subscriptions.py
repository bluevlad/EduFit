"""구독 API 엔드포인트"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ....core.database import get_db
from ....schemas.subscription import (
    SubscriptionRequest,
    SubscriptionResponse,
    VerificationRequest,
)
from ....services import subscription_service

router = APIRouter(prefix="/subscriptions", tags=["Subscriptions"])


@router.post("/request", response_model=SubscriptionResponse)
def request_subscription(
    data: SubscriptionRequest,
    db: Session = Depends(get_db),
):
    """구독 신청 (인증번호 이메일 발송)"""
    result = subscription_service.request_subscription(db, data.email)
    return SubscriptionResponse(**result)


@router.post("/verify", response_model=SubscriptionResponse)
def verify_subscription(
    data: VerificationRequest,
    db: Session = Depends(get_db),
):
    """인증번호 확인"""
    result = subscription_service.verify_subscription(db, data.email, data.code)
    return SubscriptionResponse(**result)
