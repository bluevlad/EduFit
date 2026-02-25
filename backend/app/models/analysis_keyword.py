"""분석 키워드 사전 모델"""
from sqlalchemy import Column, Integer, String, Float, Boolean, UniqueConstraint

from ..core.database import Base


class AnalysisKeyword(Base):
    __tablename__ = "analysis_keywords"
    __table_args__ = (UniqueConstraint("category", "keyword"),)

    id = Column(Integer, primary_key=True, index=True)
    category = Column(String(50), nullable=False)
    keyword = Column(String(100), nullable=False)
    weight = Column(Float, default=1.0)
    is_active = Column(Boolean, default=True)
