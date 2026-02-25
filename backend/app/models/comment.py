"""댓글 모델"""
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from ..core.database import Base


class Comment(Base):
    __tablename__ = "comments"

    id = Column(Integer, primary_key=True, index=True)
    post_id = Column(Integer, ForeignKey("posts.id", ondelete="CASCADE"), index=True)
    external_id = Column(String(100))
    content = Column(Text)
    author = Column(String(100))
    comment_date = Column(DateTime)
    like_count = Column(Integer, default=0)
    collected_at = Column(DateTime, server_default=func.now())

    post = relationship("Post", back_populates="comments")
    mentions = relationship("TeacherMention", back_populates="comment")
