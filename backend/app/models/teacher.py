"""강사 모델"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, ARRAY
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from ..core.database import Base


class Teacher(Base):
    __tablename__ = "teachers"

    id = Column(Integer, primary_key=True, index=True)
    academy_id = Column(Integer, ForeignKey("academies.id", ondelete="SET NULL"))
    subject_id = Column(Integer, ForeignKey("subjects.id", ondelete="SET NULL"))
    name = Column(String(100), nullable=False, index=True)
    aliases = Column(ARRAY(String))
    profile_url = Column(String(300))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    academy = relationship("Academy", back_populates="teachers")
    subject = relationship("Subject", back_populates="teachers")
    mentions = relationship("TeacherMention", back_populates="teacher")
    daily_reports = relationship("DailyReport", back_populates="teacher")
