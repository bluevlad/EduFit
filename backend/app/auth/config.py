"""
EduFit Google OAuth 관리자 인증 - 설정

환경변수:
  GOOGLE_CLIENT_ID      - Google OAuth Client ID (ID 토큰 방식 - SECRET 불필요)
  SUPER_ADMIN_EMAILS    - 관리자 이메일 목록 (콤마 구분)
  JWT_SECRET_KEY        - JWT 서명 키 (필수)
  JWT_ALGORITHM         - JWT 알고리즘 (기본: HS256)
  JWT_EXPIRE_MINUTES    - JWT 만료 시간 (기본: 1440 = 24시간)
"""
import os
from typing import List

from pydantic_settings import BaseSettings


class AuthSettings(BaseSettings):
    # Google OAuth (ID 토큰 방식 - CLIENT_SECRET 불필요)
    google_client_id: str = os.getenv("GOOGLE_CLIENT_ID", "")

    # JWT
    jwt_secret_key: str = os.environ["JWT_SECRET_KEY"]  # 필수 - 환경변수 미설정 시 서버 시작 실패
    jwt_algorithm: str = os.getenv("JWT_ALGORITHM", "HS256")
    jwt_expire_minutes: int = int(os.getenv("JWT_EXPIRE_MINUTES", "1440"))  # 24시간

    # Super Admin
    super_admin_emails: str = os.getenv("SUPER_ADMIN_EMAILS", "")

    class Config:
        env_file = ".env"
        extra = "ignore"

    def get_super_admin_emails(self) -> List[str]:
        """콤마로 구분된 관리자 이메일 목록을 리스트로 반환"""
        if not self.super_admin_emails.strip():
            return []
        return [e.strip().lower() for e in self.super_admin_emails.split(",") if e.strip()]

    def is_super_admin(self, email: str) -> bool:
        """이메일이 관리자 목록에 포함되어 있는지 확인"""
        if not email:
            return False
        return email.strip().lower() in self.get_super_admin_emails()


auth_settings = AuthSettings()
