"""이메일 발송 서비스"""
import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from ..core.config import settings

logger = logging.getLogger(__name__)


def send_verification_email(to_email: str, code: str) -> bool:
    """인증번호 이메일 발송"""
    subject = "[EduFit] 구독 인증번호"
    html_body = f"""
    <div style="font-family: 'Apple SD Gothic Neo', sans-serif; max-width: 480px; margin: 0 auto; padding: 32px;">
        <h2 style="color: #1976d2;">EduFit 구독 인증</h2>
        <p>아래 인증번호를 입력해 주세요.</p>
        <div style="background: #f5f5f5; border-radius: 8px; padding: 24px; text-align: center; margin: 24px 0;">
            <span style="font-size: 32px; font-weight: bold; letter-spacing: 8px; color: #1976d2;">{code}</span>
        </div>
        <p style="color: #888; font-size: 13px;">인증번호는 10분간 유효합니다.</p>
    </div>
    """

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = f"{settings.smtp_from_name} <{settings.smtp_user}>"
    msg["To"] = to_email
    msg.attach(MIMEText(html_body, "html", "utf-8"))

    try:
        with smtplib.SMTP(settings.smtp_host, settings.smtp_port) as server:
            server.starttls()
            server.login(settings.smtp_user, settings.smtp_password)
            server.send_message(msg)
        logger.info(f"인증 이메일 발송 완료: {to_email}")
        return True
    except Exception as e:
        logger.error(f"이메일 발송 실패: {e}")
        return False
