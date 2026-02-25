"""강사 멘션 모델"""
from sqlalchemy import Column, Integer, String, Text, Float, Boolean, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from ..core.database import Base


class TeacherMention(Base):
    __tablename__ = "teacher_mentions"
    __table_args__ = (
        UniqueConstraint("teacher_id", "post_id", "comment_id", "mention_type"),
    )

    id = Column(Integer, primary_key=True, index=True)
    teacher_id = Column(Integer, ForeignKey("teachers.id", ondelete="CASCADE"), index=True)
    post_id = Column(Integer, ForeignKey("posts.id", ondelete="CASCADE"), index=True)
    comment_id = Column(Integer, ForeignKey("comments.id", ondelete="CASCADE"))

    mention_type = Column(String(20), nullable=False)
    matched_text = Column(String(200))
    context = Column(Text)

    sentiment = Column(String(20))
    sentiment_score = Column(Float)
    difficulty = Column(String(20))
    is_recommended = Column(Boolean)

    analyzed_at = Column(DateTime, server_default=func.now(), index=True)

    teacher = relationship("Teacher", back_populates="mentions")
    post = relationship("Post", back_populates="mentions")
    comment = relationship("Comment", back_populates="mentions")
