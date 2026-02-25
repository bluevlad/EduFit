"""학원 모델"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ARRAY
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from ..core.database import Base


class Academy(Base):
    __tablename__ = "academies"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    name_en = Column(String(50))
    code = Column(String(50), unique=True, nullable=False)
    website = Column(String(200))
    logo_url = Column(String(300))
    keywords = Column(ARRAY(String))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    teachers = relationship("Teacher", back_populates="academy")
    daily_stats = relationship("AcademyDailyStat", back_populates="academy")
