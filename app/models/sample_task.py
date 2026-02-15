"""
샘플 할일 모델 (인증 필요한 사용자 전용 리소스 예제)
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base


class SampleTask(Base):
    """
    샘플 할일 모델 - 인증 필요 리소스 예제
    로그인한 사용자만 자신의 할일을 CRUD 가능
    """
    __tablename__ = "sample_tasks"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False, index=True)
    description = Column(Text, nullable=True)
    is_completed = Column(Boolean, default=False, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # 관계 정의
    owner = relationship("User", back_populates="sample_tasks")
