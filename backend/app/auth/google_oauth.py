"""
EduFit Google OAuth 관리자 인증 - OAuth 라우터
"""
import logging

from authlib.integrations.starlette_client import OAuth
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import RedirectResponse

from .config import auth_settings
from .dependencies import require_admin
from .jwt_handler import create_access_token

logger = logging.getLogger("google_oauth")

# OAuth 클라이언트 초기화
oauth = OAuth()
oauth.register(
    name="google",
    client_id=auth_settings.google_client_id,
    client_secret=auth_settings.google_client_secret,
    server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
    client_kwargs={"scope": "openid email profile"},
)

router = APIRouter(prefix="/auth", tags=["Google OAuth Admin"])


@router.get("/google/login")
async def google_login(request: Request):
    """Google OAuth 관리자 로그인 시작"""
    if not auth_settings.google_client_id:
        raise HTTPException(status_code=503, detail="Google OAuth is not configured")
    redirect_uri = f"{auth_settings.backend_url}/api/auth/google/callback"
    return await oauth.google.authorize_redirect(request, redirect_uri)


@router.get("/google/callback")
async def google_callback(request: Request):
    """Google OAuth 콜백 처리"""
    try:
        token = await oauth.google.authorize_access_token(request)
        user_info = token.get("userinfo")

        if not user_info:
            raise HTTPException(status_code=400, detail="Failed to get user info from Google")

        email = user_info.get("email", "")
        name = user_info.get("name", email.split("@")[0])
        picture = user_info.get("picture")

        # 관리자 이메일 확인
        if not auth_settings.is_super_admin(email):
            logger.warning("Non-admin Google login attempt: %s", email)
            return RedirectResponse(
                url=f"{auth_settings.frontend_url}/login?error=not_admin"
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

        return RedirectResponse(
            url=f"{auth_settings.frontend_url}/auth/callback?token={access_token}"
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error("Google OAuth error: %s", e)
        return RedirectResponse(
            url=f"{auth_settings.frontend_url}/login?error=oauth_failed"
        )


@router.get("/me")
async def get_me(admin=Depends(require_admin)):
    """현재 인증된 관리자 정보"""
    return admin
