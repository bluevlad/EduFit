"""데일리 리포트 모델"""
from sqlalchemy import Column, Integer, String, Float, Text, Date, DateTime, ForeignKey, UniqueConstraint, ARRAY
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from ..core.database import Base


class DailyReport(Base):
    __tablename__ = "daily_reports"
    __table_args__ = (UniqueConstraint("report_date", "teacher_id"),)

    id = Column(Integer, primary_key=True, index=True)
    report_date = Column(Date, nullable=False, index=True)
    teacher_id = Column(Integer, ForeignKey("teachers.id", ondelete="CASCADE"), index=True)

    mention_count = Column(Integer, default=0)
    post_mention_count = Column(Integer, default=0)
    comment_mention_count = Column(Integer, default=0)

    positive_count = Column(Integer, default=0)
    negative_count = Column(Integer, default=0)
    neutral_count = Column(Integer, default=0)
    avg_sentiment_score = Column(Float)

    difficulty_easy_count = Column(Integer, default=0)
    difficulty_medium_count = Column(Integer, default=0)
    difficulty_hard_count = Column(Integer, default=0)

    recommendation_count = Column(Integer, default=0)

    mention_change = Column(Integer, default=0)
    sentiment_change = Column(Float)

    summary = Column(Text)
    top_keywords = Column(ARRAY(String))

    created_at = Column(DateTime, server_default=func.now())

    teacher = relationship("Teacher", back_populates="daily_reports")
