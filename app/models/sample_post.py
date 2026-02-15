"""
샘플 게시물 모델 (인증 불필요한 공개 리소스 예제)
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime
from app.core.database import Base


class SamplePost(Base):
    """
    샘플 게시물 모델 - 공개 리소스 예제
    누구나 조회 가능, 인증 없이 생성 가능
    """
    __tablename__ = "sample_posts"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False, index=True)
    content = Column(Text, nullable=False)
    author_name = Column(String(100), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
