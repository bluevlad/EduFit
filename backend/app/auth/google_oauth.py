"""
EduFit Google OAuth 관리자 인증 - ID 토큰 검증 방식

프론트엔드에서 Google Identity Services로 받은 credential을 검증하고,
관리자 이메일 확인 후 JWT 토큰을 발급합니다.
"""
import logging

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from .config import auth_settings
from .dependencies import require_admin
from .jwt_handler import create_access_token

logger = logging.getLogger("google_oauth")

router = APIRouter(prefix="/auth", tags=["Google OAuth Admin"])


class GoogleTokenRequest(BaseModel):
    """Google ID 토큰 검증 요청"""
    credential: str


def _verify_google_id_token(credential: str) -> dict:
    """Google ID 토큰 검증 후 사용자 정보 반환"""
    from google.auth.transport import requests as google_requests
    from google.oauth2 import id_token

    try:
        idinfo = id_token.verify_oauth2_token(
            credential,
            google_requests.Request(),
            auth_settings.google_client_id,
        )
        if idinfo["iss"] not in ("accounts.google.com", "https://accounts.google.com"):
            raise ValueError("Invalid issuer")
        return idinfo
    except ValueError as e:
        logger.error("Google ID token verification failed: %s", e)
        raise


@router.post("/google/verify")
async def google_verify(body: GoogleTokenRequest):
    """Google ID 토큰 검증 후 JWT 발급

    프론트엔드에서 Google Identity Services로 받은 credential을 검증하고,
    관리자 이메일 확인 후 JWT 토큰을 반환합니다.
    """
    try:
        idinfo = _verify_google_id_token(body.credential)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Google credential",
        )

    email = idinfo.get("email", "")
    name = idinfo.get("name", email.split("@")[0] if email else "User")
    picture = idinfo.get("picture")

    # 관리자 이메일 확인
    if not auth_settings.is_super_admin(email):
        logger.warning("Non-admin Google login attempt: %s", email)
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="not_admin",
        )

    logger.info("Admin Google login: %s", email)

    access_token = create_access_token(data={
        "sub": email,
        "email": email,
        "name": name,
        "picture": picture,
        "role": "super_admin",
        "auth_type": "google",
    })

    return {
        "access_token": access_token,
        "user": {
            "email": email,
            "name": name,
            "picture": picture,
            "role": "super_admin",
        },
    }


@router.get("/me")
async def get_me(admin=Depends(require_admin)):
    """현재 인증된 관리자 정보"""
    return admin
