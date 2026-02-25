"""수집 소스 모델"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from ..core.database import Base


class CollectionSource(Base):
    __tablename__ = "collection_sources"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    code = Column(String(50), unique=True, nullable=False)
    base_url = Column(String(300))
    source_type = Column(String(50))
    is_active = Column(Boolean, default=True)
    config = Column(JSONB)
    last_crawled_at = Column(DateTime)
    created_at = Column(DateTime, server_default=func.now())

    posts = relationship("Post", back_populates="source")
    crawl_logs = relationship("CrawlLog", back_populates="source")
