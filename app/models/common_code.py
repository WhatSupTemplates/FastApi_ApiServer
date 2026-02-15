"""
공통 코드 데이터베이스 모델 (단일 테이블 방식)
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Text, Index
from app.core.database import Base


class CommonCode(Base):
    """
    공통 코드 모델 (그룹과 코드를 하나의 테이블로 관리)
    
    - 그룹: group_code="CODE_GROUP", code="USER_STATUS", name="사용자 상태"
    - 코드: group_code="USER_STATUS", code="ACTIVE", name="활성"
    """
    __tablename__ = "common_codes"

    id = Column(Integer, primary_key=True, autoincrement=True)
    group_code = Column(String(50), nullable=False, index=True, comment="그룹 코드 (그룹 자체는 'CODE_GROUP')")
    code = Column(String(50), nullable=False, index=True, comment="코드값")
    name = Column(String(100), nullable=False, comment="코드명")
    description = Column(Text, nullable=True, comment="설명")
    order = Column(Integer, default=0, nullable=False, comment="정렬 순서")
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # 복합 유니크 인덱스: (group_code, code) 조합은 유일해야 함
    __table_args__ = (
        Index('idx_group_code', 'group_code', 'code', unique=True),
    )

    def __repr__(self):
        return f"<CommonCode(group_code={self.group_code}, code={self.code}, name={self.name})>"
