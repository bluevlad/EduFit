"""구독 서비스"""
import random
import string
from datetime import datetime, timedelta

from sqlalchemy.orm import Session

from ..models.subscription import Subscription
from .email_service import send_verification_email


def _generate_code(length: int = 6) -> str:
    """6자리 숫자 인증번호 생성"""
    return "".join(random.choices(string.digits, k=length))


def request_subscription(db: Session, email: str) -> dict:
    """구독 신청 → 인증번호 발송"""
    sub = db.query(Subscription).filter(Subscription.email == email).first()

    if sub and sub.is_verified and sub.is_active:
        return {"success": False, "message": "이미 구독 중인 이메일입니다."}

    code = _generate_code()
    expires_at = datetime.now() + timedelta(minutes=10)

    if sub:
        sub.verification_code = code
        sub.verification_expires_at = expires_at
    else:
        sub = Subscription(
            email=email,
            verification_code=code,
            verification_expires_at=expires_at,
        )
        db.add(sub)

    db.commit()

    if not send_verification_email(email, code):
        return {"success": False, "message": "이메일 발송에 실패했습니다. 잠시 후 다시 시도해 주세요."}

    return {"success": True, "message": "인증번호가 이메일로 발송되었습니다."}


def verify_subscription(db: Session, email: str, code: str) -> dict:
    """인증번호 확인 → 구독 활성화"""
    sub = db.query(Subscription).filter(Subscription.email == email).first()

    if not sub:
        return {"success": False, "message": "구독 신청 내역이 없습니다."}

    if sub.is_verified and sub.is_active:
        return {"success": False, "message": "이미 인증 완료된 이메일입니다."}

    if sub.verification_expires_at and datetime.now() > sub.verification_expires_at:
        return {"success": False, "message": "인증번호가 만료되었습니다. 다시 신청해 주세요."}

    if sub.verification_code != code:
        return {"success": False, "message": "인증번호가 일치하지 않습니다."}

    sub.is_verified = True
    sub.is_active = True
    sub.verified_at = datetime.now()
    sub.verification_code = None
    sub.verification_expires_at = None
    db.commit()

    return {"success": True, "message": "구독이 완료되었습니다."}
