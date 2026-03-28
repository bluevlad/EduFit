"""구독 스키마"""
from pydantic import BaseModel, EmailStr


class SubscriptionRequest(BaseModel):
    email: EmailStr


class VerificationRequest(BaseModel):
    email: EmailStr
    code: str


class SubscriptionResponse(BaseModel):
    success: bool
    message: str
