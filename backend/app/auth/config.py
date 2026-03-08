"""
EduFit Google OAuth 관리자 인증 - 설정

환경변수:
  GOOGLE_CLIENT_ID      - Google OAuth Client ID
  GOOGLE_CLIENT_SECRET  - Google OAuth Client Secret
  SUPER_ADMIN_EMAILS    - 관리자 이메일 목록 (콤마 구분)
  JWT_SECRET_KEY        - JWT 서명 키 (필수)
  JWT_ALGORITHM         - JWT 알고리즘 (기본: HS256)
  JWT_EXPIRE_MINUTES    - JWT 만료 시간 (기본: 1440 = 24시간)
  FRONTEND_URL          - 프론트엔드 URL (OAuth 콜백 리디렉트)
  BACKEND_URL           - 백엔드 URL (OAuth 콜백 URI 생성)
"""
import os
from typing import List

from pydantic_settings import BaseSettings


class AuthSettings(BaseSettings):
    # Google OAuth
    google_client_id: str = ""
    google_client_secret: str = ""

    # 관리자 이메일 목록 (콤마 구분)
    super_admin_emails: str = ""

    # JWT
    jwt_secret_key: str = os.environ.get("JWT_SECRET_KEY", "")
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 1440  # 24시간

    # URLs (EduFit 기본값)
    frontend_url: str = "http://localhost:4070"
    backend_url: str = "http://localhost:9070"

    class Config:
        env_file = ".env"
        extra = "ignore"

    def get_super_admin_emails(self) -> List[str]:
        """콤마로 구분된 관리자 이메일 목록을 리스트로 반환"""
        if not self.super_admin_emails:
            return []
        return [e.strip().lower() for e in self.super_admin_emails.split(",") if e.strip()]

    def is_super_admin(self, email: str) -> bool:
        """이메일이 관리자 목록에 포함되어 있는지 확인"""
        return email.lower().strip() in self.get_super_admin_emails()


auth_settings = AuthSettings()
