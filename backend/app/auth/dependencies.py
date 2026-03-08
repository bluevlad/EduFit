"""
EduFit Google OAuth 관리자 인증 - FastAPI 의존성

사용법:
  from app.auth.dependencies import require_admin

  @router.get("/admin/dashboard")
  async def dashboard(admin = Depends(require_admin)):
      return {"email": admin["email"]}
"""
from typing import Optional

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from .jwt_handler import verify_token

security = HTTPBearer(auto_error=False)


async def get_current_admin(
    request: Request = None,
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
) -> Optional[dict]:
    """현재 인증된 관리자 정보 반환 (미인증 시 None)"""
    token = None

    # Bearer 토큰에서 추출
    if credentials:
        token = credentials.credentials

    # 쿠키에서 추출 (폴백)
    if not token and request:
        token = request.cookies.get("admin_token")

    if not token:
        return None

    payload = verify_token(token)
    if not payload:
        return None

    if payload.get("role") != "super_admin":
        return None

    return {
        "email": payload.get("email"),
        "name": payload.get("name"),
        "picture": payload.get("picture"),
        "role": payload.get("role"),
    }


async def require_admin(
    credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer()),
) -> dict:
    """관리자 인증 필수 - 401/403 발생"""
    token = credentials.credentials
    payload = verify_token(token)

    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if payload.get("role") != "super_admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Super admin access required",
        )

    return {
        "email": payload.get("email"),
        "name": payload.get("name"),
        "picture": payload.get("picture"),
        "role": payload.get("role"),
    }
