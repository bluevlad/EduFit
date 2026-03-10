"""미등록 인물 후보 모델"""
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Index
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from ..core.database import Base


class UnregisteredCandidate(Base):
    __tablename__ = "unregistered_candidates"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    mention_count = Column(Integer, default=1)
    first_seen_at = Column(DateTime, server_default=func.now())
    last_seen_at = Column(DateTime, server_default=func.now())

    sample_contexts = Column(JSONB, default=[])
    source_distribution = Column(JSONB, default={})

    # pending / registered / ignored
    status = Column(String(20), default="pending")
    resolved_at = Column(DateTime)
    resolved_teacher_id = Column(Integer, ForeignKey("teachers.id"), nullable=True)

    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    resolved_teacher = relationship("Teacher")

    __table_args__ = (
        Index("idx_unregistered_name", "name"),
        Index("idx_unregistered_status", "status"),
    )
