"""
EduFit Google OAuth 관리자 인증 - JWT 핸들러
"""
from datetime import datetime, timedelta, timezone
from typing import Optional

import jwt

from .config import auth_settings


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """JWT 액세스 토큰 생성"""
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=auth_settings.jwt_expire_minutes)
    )
    to_encode.update({"exp": expire, "type": "access"})
    return jwt.encode(
        to_encode,
        auth_settings.jwt_secret_key,
        algorithm=auth_settings.jwt_algorithm,
    )


def verify_token(token: str) -> Optional[dict]:
    """JWT 토큰 검증 후 페이로드 반환 (실패 시 None)"""
    try:
        return jwt.decode(
            token,
            auth_settings.jwt_secret_key,
            algorithms=[auth_settings.jwt_algorithm],
        )
    except (jwt.InvalidTokenError, jwt.ExpiredSignatureError):
        return None
