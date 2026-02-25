"""게시글 모델"""
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from ..core.database import Base


class Post(Base):
    __tablename__ = "posts"
    __table_args__ = (UniqueConstraint("source_id", "external_id"),)

    id = Column(Integer, primary_key=True, index=True)
    source_id = Column(Integer, ForeignKey("collection_sources.id"), index=True)
    external_id = Column(String(100))
    title = Column(String(500), nullable=False)
    content = Column(Text)
    url = Column(String(500))
    author = Column(String(100))
    post_date = Column(DateTime, index=True)
    view_count = Column(Integer, default=0)
    like_count = Column(Integer, default=0)
    comment_count = Column(Integer, default=0)
    collected_at = Column(DateTime, server_default=func.now(), index=True)

    source = relationship("CollectionSource", back_populates="posts")
    comments = relationship("Comment", back_populates="post", cascade="all, delete-orphan")
    mentions = relationship("TeacherMention", back_populates="post")
