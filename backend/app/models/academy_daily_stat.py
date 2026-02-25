"""학원별 데일리 통계 모델"""
from sqlalchemy import Column, Integer, Float, Date, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from ..core.database import Base


class AcademyDailyStat(Base):
    __tablename__ = "academy_daily_stats"
    __table_args__ = (UniqueConstraint("report_date", "academy_id"),)

    id = Column(Integer, primary_key=True, index=True)
    report_date = Column(Date, nullable=False)
    academy_id = Column(Integer, ForeignKey("academies.id", ondelete="CASCADE"))

    total_mentions = Column(Integer, default=0)
    total_teachers_mentioned = Column(Integer, default=0)
    avg_sentiment_score = Column(Float)
    top_teacher_id = Column(Integer, ForeignKey("teachers.id"))

    created_at = Column(DateTime, server_default=func.now())

    academy = relationship("Academy", back_populates="daily_stats")
