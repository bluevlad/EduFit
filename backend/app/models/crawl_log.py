"""크롤링 작업 로그 모델"""
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from ..core.database import Base


class CrawlLog(Base):
    __tablename__ = "crawl_logs"

    id = Column(Integer, primary_key=True, index=True)
    source_id = Column(Integer, ForeignKey("collection_sources.id"))
    started_at = Column(DateTime, nullable=False)
    finished_at = Column(DateTime)
    status = Column(String(20), nullable=False)
    posts_collected = Column(Integer, default=0)
    comments_collected = Column(Integer, default=0)
    mentions_found = Column(Integer, default=0)
    error_message = Column(Text)

    created_at = Column(DateTime, server_default=func.now())

    source = relationship("CollectionSource", back_populates="crawl_logs")
