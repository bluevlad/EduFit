"""
EduFit Google OAuth 관리자 인증 모듈

Google ID 토큰 방식으로 관리자 로그인을 구현합니다.
SUPER_ADMIN_EMAILS 환경변수에 등록된 이메일만 로그인 허용됩니다.

사용법:
    from app.auth.google_oauth import router as auth_router
    from app.auth.dependencies import require_admin

    app.include_router(auth_router, prefix="/api")

필수 환경변수:
    GOOGLE_CLIENT_ID, SUPER_ADMIN_EMAILS, JWT_SECRET_KEY
"""
